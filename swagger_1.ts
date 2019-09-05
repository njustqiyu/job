import * as path from "path";
import {Util} from "../lib/util";
import {swaggerPackageJsonTpl} from "../template/swagger_node/packageJsonTpl";
import {swaggerClientHtmlTpl} from "../template/swagger_node/swaggerClientHtmlTpl";
import {swaggerClientJsTpl} from "../template/swagger_node/swaggerClientJsTpl";
import {NodeGen} from "./NodeGen";
import {config} from "../lib/config";
import {DbFactory} from "../lib/dbFactory";
import {JudgeSwagger} from "../lib/judgeSwagger";
import * as fs from "fs";
import {getLogger} from "../lib/logger";
import {BOSwaggerMetadataDao} from "../dao/BOSwaggerMetadataDao";
import {aggregateNodeGen} from "./AggregateNodeGen";

const Swagger = require('swagger-client');
const jsf = require('json-schema-faker');
const uuid = require('node-uuid');

const logger = getLogger();

class MetadataResult {
    static ERROR_CODE = '500';
    static SUCCESS_CODE = '200';
    private resCode: string;
    private resMsg: string;
    private result: any;

    public setResCode (resCode: string) {
        this.resCode = resCode;
    }

    public setResMsg (resMsg: string) {
        this.resMsg = resMsg;
    }

    public setResult (result: any) {
        this.result = result;
    }
}

class FileUploadStatus {
    static ERROR_STATUS = 0;
    static SUCCESS_STATUS = 1;
    private fileName: string;
    private status: number;
    private info: string;

    constructor(fileName: string) {
        this.fileName = fileName;
    }

    public setStatus (status: number) {
        this.status = status;
    }

    public getStatus () {
        return this.status;
    }

    public setInfo (info: string) {
        this.info = info;
    }
}

class BoSwaggerMetadataNodeGen extends NodeGen {
    private db = DbFactory.getDB("bo");
    public genBoSwaggerMetadataNodes(req, res, next){
        let body=req.body;
        let tenantId=req.ctx.tenantId||req.get("tenantId");
        boSwaggerMetadataNodeGen.nodeGenHandler(res,body);
    }
    public async nodeGenHandler(res: any, serviceSpec: any) {
        let type = serviceSpec.type;
        delete serviceSpec.type;
        switch (type) {
            case "insert":
                res.send(await this.insertMetadata(serviceSpec.data));
                break;
            case "delete":
                res.send(await this.deleteMetadata(serviceSpec.data));
                break;
            case "get":
                res.send(await this.getMetadataList(serviceSpec));
                break;
            case "create":
                await this.createBO(res, serviceSpec);
                break;
        }
    }

    public async insertMetadata(metadatas: any) {
        let metadataUploadResult = new MetadataResult();
        //本次元数据上传的结果，默认1，代表成功
        let metadataUploadFlag: number = FileUploadStatus.SUCCESS_STATUS;
        //元数据上传结果 example {"fileName": "sfs.json","status": 1,"info": "Successful"}
        let result = [];
        for (let index in metadatas) {
            let tenantId = metadatas[index].tenantId,
                filename = metadatas[index].filename,
                data = metadatas[index].data;

            //FileUploadStatus记录单个元数据的导入状态
            let fileUploadStatus = new FileUploadStatus(filename);

            //loadFile
            data = this.loadFile(filename,data,fileUploadStatus);
            if (fileUploadStatus.getStatus() == FileUploadStatus.ERROR_STATUS) {
                metadataUploadFlag = metadataUploadFlag & fileUploadStatus.getStatus();
                result.push(fileUploadStatus);
                continue
            }

            //校验swagger文件
            //1，基本校验
            try {
                let swaggerFile = JSON.parse(data);
                let res = await this.swaggerBaseJudge(swaggerFile);
                //console.log("Base校验结果："+JSON.stringify(res));
                if (res.resultFlag === false) {
                    fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                    fileUploadStatus.setInfo(res.errMessage.toString());
                    metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
                    result.push(fileUploadStatus);
                    continue;
                }
            } catch (err) {
                fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                fileUploadStatus.setInfo(err.toString());
                metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
            }

            //2,自定义校验
            try {
                const judgeConfig = require("../../config/judgeSwaggerConfig.json");
                let swaggerFile = JSON.parse(data);
                let res = await this.swaggerJudge(judgeConfig, swaggerFile);
                //console.log("自定义校验结果："+JSON.stringify(res));
                if (!this.isEmptyValue(res)) {
                    fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                    fileUploadStatus.setInfo(res);
                    metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
                    result.push(fileUploadStatus);
                    continue;
                }
            } catch (err) {
                fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                fileUploadStatus.setInfo(err.toString());
                metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
            }

            //元数据解析入库
            try {
                let metadata = await this.swaggerBuild(JSON.parse(data));
                if (metadata) {
                    let res = await this.insertToDB(tenantId, filename, metadata);
                    if ((res.insertedCount && res.insertedCount >= 1) || (res.modifiedCount && res.modifiedCount >= 1)) {
                        fileUploadStatus.setStatus(FileUploadStatus.SUCCESS_STATUS);
                        fileUploadStatus.setInfo('Successful');
                        metadataUploadFlag = metadataUploadFlag & FileUploadStatus.SUCCESS_STATUS;
                    } else {
                        fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                        fileUploadStatus.setInfo('Insert to database failed');
                        metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
                    }
                } else {
                    logger.error("insert " + filename + " failed: " + 'failed to parse file');
                    fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                    fileUploadStatus.setInfo('Failed to parse file');
                    metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
                }
            } catch (err) {
                logger.error("insert " + filename + " failed: " + err.toString());
                fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                fileUploadStatus.setInfo(err.toString());
                metadataUploadFlag = metadataUploadFlag & FileUploadStatus.ERROR_STATUS;
            } finally {
                result.push(fileUploadStatus);
            }
        }

        if (metadataUploadFlag == FileUploadStatus.SUCCESS_STATUS) {
            metadataUploadResult.setResCode(MetadataResult.SUCCESS_CODE);
            metadataUploadResult.setResMsg("Success");
        } else {
            metadataUploadResult.setResCode(MetadataResult.ERROR_CODE);
            metadataUploadResult.setResMsg("Some files failed to upload, specific information view result");
        }
        metadataUploadResult.setResult(result);
        //console.log("metadataUploadResult: "+JSON.stringify(metadataUploadResult));

        return metadataUploadResult;
    }

    //判断数组是否为空，true:空，false:非空
    public isEmptyValue(array: any) {
        let result = (Array.isArray(array) && array.length === 0) || (Object.prototype.isPrototypeOf(array) && Object.keys(array).length === 0);
        return result;
    }

    private loadFile(filename: string, data: any, fileUploadStatus: FileUploadStatus):string {
        const yaml = require('yamljs');
        const filePath = "./" + filename;
        if (filename.endsWith("yaml")) {
            try {
                fs.writeFileSync(filePath, data);
                data = yaml.load(filePath);
                fs.unlinkSync(filePath);
            } catch (err) {
                fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
                fileUploadStatus.setInfo(err.toString());
            }
            data = JSON.stringify(data);
        } else if (!filename.endsWith("json")) {
            fileUploadStatus.setStatus(FileUploadStatus.ERROR_STATUS);
            fileUploadStatus.setInfo("File format error");
        }
        return data;
    }

    private async insertToDB(tenantId: string, filename: string, metadata: any){
        let title = (metadata.info && metadata.info.title) ? metadata.info.title : '';
        let version = (metadata.info && metadata.info.version) ? metadata.info.version : '';
        let description = (metadata.info && metadata.info.description) ? metadata.info.description : '';
        let res = await this.db.save("bo_swagger_metadata",
            {
                tenantId: tenantId,
                filename: filename,
                version: version
            },
            {
                id: uuid.v4(),
                tenantId: tenantId,
                filename: filename,
                metadata: metadata,
                title: title,
                version: version,
                description: description,
                createTime: new Date()
            }
        );
        return res;
    }

    public async deleteMetadata(metadatas: any) {
        let result = {};
        for (let index in metadatas) {
            let res = await this.db.deleteByCondition("bo_swagger_metadata",
                {
                    tenantId: metadatas[index].tenantId,
                    id: metadatas[index].id
                }
            );
            if (res.deletedCount && res.deletedCount >= 1) {
                result[metadatas[index].filename] = "deleteSuccess";
            } else {
                result[metadatas[index].filename] = "deleteFailed";
            }
        }
        return result;
    }

    public async getMetadataList(serviceSpec: any) {
        let dao = new BOSwaggerMetadataDao();
        let result = new MetadataResult(),
            tenantId = serviceSpec.tenantId,
            filename = serviceSpec.filename,
            title = serviceSpec.title,
            page = serviceSpec.page,
            size = serviceSpec.size,
            offset:number = 0,
            limit:number = 1;
        if (this.isNumber(page) && this.isNumber(size) && parseInt(page) > 0){
            limit = parseInt(size);
            offset = (parseInt(page) - 1) * limit;
        }
        let queryList = await dao.query(tenantId,filename,title,offset,limit);
        result.setResCode(MetadataResult.SUCCESS_CODE);
        result.setResMsg("Success");
        result.setResult(queryList);
        return result;
    }

    public async createBO(res: any, serviceSpec: any) {
        let dao = new BOSwaggerMetadataDao(),
            id = serviceSpec.id;
        let metadata = await dao.findById(id);
        try {
            if (metadata && metadata.length > 0) {
                await this.createRomaNode(res, metadata[0]);
            }
        } catch (e) {
            logger.error(e);
        }
        return;
    }

    public async deleteChinese(str) {
        let title = "";
        if (str) {
            for (var i = 0; i < str.length; i++) {
                var c = str.substr(i, 1);
                var ts = escape(c);
                if (ts.substring(0, 2) !== "%u" && c !== "(" && c !== ")") {
                    title += c;
                }
            }
        }
        return title;
    }

    public async checkVersion(version) {
        if (version) {
            while (version.split(".").length < 3) {
                version += ".0";
            }
            return version;
        } else {
            return "1.0.0";
        }
    }

    private async createRomaNode(res: any, metadataRecord: any) {
        let serviceSpec = metadataRecord.metadata;
        // todo: 节点名称待完善，此处若title为全中文会出现节点安装出错的问题
        serviceSpec.info.title = await this.deleteChinese(serviceSpec.info.title);
        serviceSpec.info.version = await this.checkVersion(serviceSpec.info.version);
        let destNodeDir = path.join(config.nodeBaseDir, (serviceSpec.info.title.trim().replace(/ /gi, "-").toLowerCase() + serviceSpec.basePath.trim().replace(/\//gi, "-").toLowerCase()).replace(/-$/, ""));
        if (serviceSpec.host.trim()) {
            const fileName = serviceSpec.info.title.trim().replace(/ /gi, "-").toLowerCase() + serviceSpec.basePath.trim().replace(/\//gi, "-").toLowerCase().replace(/-$/, "") + ".json";

            Util.mkDirs(config.nodeBaseDir, destNodeDir);

            serviceSpec.nodeReqPath = "swagger/" + serviceSpec.info.title.trim().replace(/ /gi, "-").toLowerCase() + serviceSpec.basePath.trim().replace(/\//gi, "-").toLowerCase().replace(/-$/, "");
            serviceSpec.swaggerSpecName = fileName;
            serviceSpec.nodeName = serviceSpec.info.title.trim().replace(/ /gi, "-").toLowerCase() + serviceSpec.basePath.trim().replace(/\//gi, "-").toLowerCase().replace(/-$/, "");

            serviceSpec.info.version = await Util.updateVersion(serviceSpec.nodeName) || serviceSpec.info.version;

            serviceSpec.apis = JSON.stringify(serviceSpec.apis);
            const swaggerPackageJson = this.compiledTemplates.swaggerPackageJsonTpl(serviceSpec);
            const swaggerClientHtml = this.compiledTemplates.swaggerClientHtmlTpl(serviceSpec);
            const swaggerClientJs = this.compiledTemplates.swaggerClientJsTpl(serviceSpec);
            Util.writeFile2DirSync("swaggerClient.html", destNodeDir , swaggerClientHtml);
            Util.writeFile2DirSync("swaggerClient.js", destNodeDir, swaggerClientJs);
            Util.writeFile2DirSync("package.json", destNodeDir, swaggerPackageJson);

            let keywords = [];
            keywords.push(serviceSpec.title);
            if (serviceSpec.tags) {
                serviceSpec.tags.forEach((item, index) => {
                    keywords.push(item.name);
                });
            }

            Util.publishNode2NpmCallBack(destNodeDir, config.BoServerUrl, config.npmRegistry, [{
                description: serviceSpec.info.description,
                id: serviceSpec.nodeName,
                // index: serviceSpec.nodeName + ',' + serviceSpec.title + ',' + serviceSpec.schemes.toString(),
                keywords,
                // timestamp: new Date().getTime(),
                types: [
                    "system service",
                ],
                updated_at: new Date().toISOString(),
                // url: serviceSpec.termsOfService,
                version: serviceSpec.info.version,
            }], res,"",function () {
                fs.unlinkSync(path.join(destNodeDir,"swaggerClient.html"));
                fs.unlinkSync(path.join(destNodeDir,"swaggerClient.js"));
                fs.unlinkSync(path.join(destNodeDir,"package.json"));
                fs.rmdirSync(destNodeDir);
            });

        }
    }

    private async swaggerBaseJudge(swaggerFile: any) {
        let judgeSwagger = new JudgeSwagger();
        let showMessage = await judgeSwagger.judgeBase(swaggerFile);
        if (showMessage !== "pass") {
            let resultFlag = false;
            let res0 = {resultFlag: resultFlag, errMessage: showMessage};
            return res0;
        }
        let result = {resultFlag: true, errMessage: "Base校验pass"};
        return result;
    }

    private async swaggerJudge(judgeConfig: any, swaggerFile: any) {

        let errResList:any=[];
        let judgeSwagger = new JudgeSwagger();
        //console.log("errResList: "+JSON.stringify(errResList));

        let res1 = judgeSwagger.judgeIsMeetRegularList(swaggerFile, judgeConfig.regularList);
        if(!this.isEmptyValue(res1)){
            this.getErrMessage(res1,errResList);
        }
        //console.log("errResList1: "+JSON.stringify(errResList));

        let res2 = judgeSwagger.judgeExistFieldsList(swaggerFile, judgeConfig.existFieldsList);
        if(!this.isEmptyValue(res2)){
            this.getErrMessage(res2,errResList);
        }
        //console.log("errResList2: "+JSON.stringify(errResList));

        let res3 = judgeSwagger.judgeIsInheritList(swaggerFile, judgeConfig.inheritList);
        if(!this.isEmptyValue(res3)){
            this.getErrMessage(res3,errResList);
        }
        //console.log("errResList3: "+JSON.stringify(errResList));

        return errResList;
    }

    public getErrMessage(itemResList:any,errResList:any){
        for(const itemRes of itemResList){
            if(itemRes.resultFlag===false){
                errResList.push(itemRes.errMessage);
            }
        }
        return errResList;
    }

    private async swaggerBuild(serviceSpec: any) {

        let services: any = await this.build(serviceSpec);
        serviceSpec.apis = services;
        serviceSpec.apiFlows = [];
        serviceSpec.apisIndex = [];
        let resource2api_Map = {};
        Object.keys(services).forEach(resourceName => {
            Object.keys(services[resourceName]).forEach(apiName => {
                    let api = services[resourceName][apiName];
                    serviceSpec.apiFlows.push({
                        "name": api.apiId,
                        "description": api.description || "no description!",
                        "inputSample": JSON.stringify(api.example)
                    });
                    for (let resourceName of api.resource) {
                        if (!resource2api_Map[resourceName]) {
                            resource2api_Map[resourceName] = [];
                        }
                        resource2api_Map[resourceName].push({"name": api.apiId})
                    }
                }
            );
        });
        Object.keys(resource2api_Map).forEach(resourceName => {
            serviceSpec.apisIndex.push({
                "resourceName": resourceName,
                "apis": JSON.stringify(resource2api_Map[resourceName])

            });
        });
        return serviceSpec;
    }

    private buildExample(example, para) {

        if (!para || !para.in || !para.name) {
            return;
        }
        let schema = para.schema;
        if (!schema) {
            schema = para;
        }
        jsf.option({
            requiredOnly: false, alwaysFakeOptionals: true
            , useDefaultValue: true, useExamplesValue: true, maxItems: 1.1
            , minItems: 1, maxLength: 5, minLength: 4
        });
        let demoJSON = schema["example"] || schema["x-example"];

        if (demoJSON && para.in === "body") {
            demoJSON = JSON.parse(demoJSON);
        } else if (!demoJSON) {
            try {
                demoJSON = jsf.generate(schema);
            } catch (e) {
                //generate failed!
                demoJSON = "";
            }

        }

        if (para.in === "body" && para.name === "body" ) {
            example[para.in] = demoJSON;
        } else if (para.in === "form" ) {
            example[para.in] = demoJSON;
        }else if (para.in === "path") {
            if (!example[para.in]) {
                example[para.in] = {};
            }
            example[para.in][para.name] = para.name;
        } else {
            if (!example[para.in]) {
                example[para.in] = {};
            }
            example[para.in][para.name] = demoJSON;
        }
    }

    private async build(json: any) {
        let serviceRet = {};

        let client = await Swagger({spec: json});

        const sourceUrl = client.url;
        const spec = client.spec;
        const baseUrl = '://' + spec.host + spec.basePath;
        const default_Content_Type = spec.consumes;
        const default_Accept = spec.produces;
        const methods = ["post", "get", "put", "head", "delete", "options", "patch"];
        const schemas = spec.schemes;
        Object.keys(spec["paths"]).forEach(uri => {
            const restEndPoint = spec["paths"][uri];
            Object.keys(restEndPoint).forEach(method => {
                if (!methods.includes(method.toLowerCase())) {
                    return;
                }
                let rest = restEndPoint[method];
                let api: any = {
                    sourceUrl: sourceUrl,
                    baseUrl: baseUrl,
                    uri: uri,
                    method: method,
                    consumes: default_Accept,
                    produces: default_Content_Type
                };
                api["consumes"] = rest["consumes"] || api["consumes"];
                api["produces"] = rest["produces"] || api["produces"];
                api.resource = rest.tags;
                api.apiId = rest.operationId;
                api.parameters = {};
                api.example = {};
                api.example.protocol=schemas;
                if (!rest.parameters) {
                    rest.parameters = [];
                }
                rest.parameters.forEach(p => {
                    if (!api.parameters[p["in"]]) {
                        api.parameters[p["in"]] = [];
                    }
                    api.parameters[p["in"]].push(p);
                    this.buildExample(api.example, p);

                });
                for (let tag of rest["tags"]) {
                    this.addApi(serviceRet, tag, rest["operationId"], api);
                }
            });
        });
        return serviceRet;
    }

    private addApi(serviceRet, resource, apiId, api) {
        if (serviceRet[resource]) {
            return serviceRet[resource][apiId] = api;
        } else {
            serviceRet[resource] = {};
            return this.addApi(serviceRet, resource, apiId, api);
        }
    }

    private isNumber(s: any):boolean {
        let reg = /^[0-9]*$/;
        return s ? reg.test(s) : false;
    }
}

const swaggerNodeTpls: any = {};
swaggerNodeTpls.swaggerClientJsTpl = swaggerClientJsTpl;
swaggerNodeTpls.swaggerClientHtmlTpl = swaggerClientHtmlTpl;
swaggerNodeTpls.swaggerPackageJsonTpl = swaggerPackageJsonTpl;

export const boSwaggerMetadataNodeGen = new BoSwaggerMetadataNodeGen(swaggerNodeTpls);
