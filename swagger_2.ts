/*校验swagger文件，*/

const SwaggerParser = require("swagger-parser");

export class JudgeSwagger {

    /*以下是规则校验函数*/

    //校验规则1：swagger文件的基本校验
    public async judgeBase(swaggerFile: any) {
        let resultFlag = true;
        let showMessage = "";
        let res;
        let result = new Promise((resolve, reject) => {
            SwaggerParser.validate(swaggerFile, (err, api) => {
                if (err) {
                    resultFlag = false;
                    showMessage = err.message;
                } else {
                    resultFlag = true;
                    showMessage = "pass";
                }
                res = {resultFlag: resultFlag, errMessage: showMessage};
                resolve(showMessage);
            });

        });
        let resultFlagNew = await result;
        return resultFlagNew;
    }

    //校验2：某些字段是否符合正则表达
    public judgeIsMeetRegularList(swaggerFile: any, regularList: any) {
        let itemResList:any=[];
        for (const regular of regularList) {
            let res = this.judgeIsMeetRegular(swaggerFile, regular.field, regular.parameter);
            itemResList.push(res);
        }
        return itemResList;
    }

    //校验3：某些字段是否存在且不为空
    public judgeExistFieldsList(swaggerFile: any, existFieldsList: any) {
        //遍历配置文件中existFieldsList的内容，依此进行比较
        let itemResList:any=[];
        for (const existField of existFieldsList) {
            let resList = this.judgeIsExistField(swaggerFile, existField.field, existField.parameter);
            for(const itemRes of resList){
                if(itemRes.resultFlag===false){
                    itemResList.push(itemRes);
                }
            }
        }
        return itemResList;
    }

    //校验4：某些字段是否满足继承的关系
    public judgeIsInheritList(swaggerFile: any, inheritList: any) {
        let itemResList:any=[];
        for (const inherit of inheritList) {
            let resList = this.judgeIsInherit(swaggerFile, inherit.firstField, inherit.lastField, inherit.parameter);
            if(resList.resultFlag===true){
            }else{
                for(const itemRes of resList){
                    itemResList.push(itemRes);
                }
            }
        }
        return itemResList;
    }

    /*校验小分支*/

    //判断某字段是否符合正则表达式
    public judgeIsMeetRegular(swaggerFile: any, field: any, parameter: any) {
        let flag;
        let showMessage;
        let showPosition;
        let res;

        let startPosition = this.splitField(field).startPosition;
        let endPosition = this.splitField(field).endPosition;
        let item = swaggerFile[startPosition][endPosition];

        let judgeVersionResult = this.regularCheck(item.toString(), parameter);
        if (judgeVersionResult) {
            res = {resultFlag: true, errMessage: "正则规则校验pass"};
            return res;
        } else {
            flag = judgeVersionResult;
            showPosition = "Invalid " + startPosition + '.' + endPosition + ": " + item;
            if (endPosition === "version") {
                showMessage = 'API version number must be a string (e.g. 1.0.0)；' + showPosition;
                res = {resultFlag: flag, errMessage: showMessage};
                return res;
            }
            if (endPosition === "title") {
                showMessage = 'title中只能包含数字、字母、下划线、空格；' + showPosition;
                res = {resultFlag: flag, errMessage: showMessage};
                return res;
            }
        }
    }

    //判断是否存在某字段
    public judgeIsExistField(swaggerFile: any, field: any, parameter: any) {

        let resList:any=[];
        let resListNew:any=[];

        let startPosition = this.splitField(field).startPosition;
        let endPosition = this.splitField(field).endPosition;

        let resultFlag;
        let showMessage;
        let res;

        for (const uri of Object.keys(swaggerFile[startPosition])) {
            const restEndPoint = swaggerFile[startPosition][uri];
            for (const method of Object.keys(restEndPoint)) {
                let rest = restEndPoint[method];
                if (parameter && (!rest.hasOwnProperty(endPosition))) {
                    //不存在
                    showMessage = "Missing required field: " + startPosition + '.' + uri.substring(1) + '.' + method + "." + endPosition;
                    resultFlag = false;
                    res = {resultFlag: resultFlag, errMessage: showMessage};
                    resList.push(res);
                    //return res;
                } else {
                    //存在
                    let flag;
                    if (typeof rest[endPosition] === "string") {
                        flag = (rest[endPosition].length === 0);
                    } else {
                        flag = this.isEmptyValue(rest[endPosition])
                    }
                    if (flag) {
                        //值空
                        showMessage = "fields can/t set null：" + startPosition + '.' + uri.substring(1) + '.' + method + "." + endPosition;
                        resultFlag = false;
                        res = {resultFlag: resultFlag, errMessage: showMessage};
                        resList.push(res);
                        //return res;
                    } else {
                        //非空
                        resultFlag = true;
                        res = {resultFlag: true, errMessage: "存在-pass: "+endPosition};
                        resList.push(res);
                    }
                }
            }
        }
        resListNew=this.getErrMessage(resList);
        return resListNew;
    }

    public getErrMessage(itemResList:any){
        let newList:any=[];
        for(const itemRes of itemResList){
            if(itemRes.resultFlag===false){
                newList.push(itemRes);
            }
        }
        return newList;
    }

    //判断是否满足继承关系
    public judgeIsInherit(swaggerFile: any, firstField: any, lastField: any, parameter: any) {
        let resList:any=[];

        let res;
        if (parameter) {
            let existResult;
            let emptyResult;
            if (swaggerFile.hasOwnProperty(firstField)) {
                existResult = true;
            }
            emptyResult = this.isEmptyValue(swaggerFile[firstField]);

            if (existResult) {
                //存在
                if (!emptyResult) {
                    //非空
                    res = {resultFlag: true, errMessage: "pass--存在: "+firstField};
                    resList.push(res);
                    return res;
                } else {
                    //空
                    return this.judgeIsExistField(swaggerFile, lastField, parameter);
                }
            } else {
                //不存在,需要看后续paths里面的方法是否赋值了consumes
                return this.judgeIsExistField(swaggerFile, lastField, parameter);
            }
        }
    }


    /*以下是一些功能的具体实现*/

    //正则校验
    public regularCheck(testItem: any, format: any) {
        let flag = false;
        let re = new RegExp(format);
        if (re.test(testItem)) {
            flag = true;
        }
        return flag;
    }

    //判断数组是否为空，true:空，false:非空
    public isEmptyValue(array: any) {
        let result = (Array.isArray(array) && array.length === 0) || (Object.prototype.isPrototypeOf(array) && Object.keys(array).length === 0);
        return result;
    }

    //拆分field参数[paths.2.tags]
    public splitField(field: any) {
        let arr = field.split(".");
        if (arr.length === 3) {
            let startPosition = arr[0];
            let middleNum = arr[1];
            let endPosition = arr[2];
            return {startPosition: startPosition, middleNum: middleNum, endPosition: endPosition}
        }
        if (arr.length === 2) {
            let startPosition = arr[0];
            let endPosition = arr[1];
            return {startPosition: startPosition, endPosition: endPosition}
        }
    }
}




