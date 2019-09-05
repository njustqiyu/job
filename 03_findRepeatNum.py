#!/usr/bin/env python
# -*- coding:utf-8 -*-

import numpy as np
class Solution():
    def findRepeatNum(self,numList):
        if not numList:
            return None
        result=[]
        length=len(numList)
        hashTable=np.zeros(length)
        for num in numList:
            hashTable[num]+=1
        for i in range(length):
            if hashTable[i]>1:
                result.append(i)
        return result

if __name__=="__main__":
    sol=Solution()
    numList=[2,3,5,4,3,2,6,7]
    result=sol.findRepeatNum(numList)
    print(result)

import {mx} from '@/components/graph/GraphBase';
import {CodecDocument} from '@/components/graph/CodecDocument';
import {ModelChangeAndStore} from "@/components/graph/ModelChangeAndStore";
import {
    CellStyle,
    CellHeight,
    CellWidth,
    offset,
} from "@/components/graph/GraphConstAndEnumPublic";
import {GraphCellDefinePublic} from "@/components/graph/GraphCellDefinePublic";
import {AggregateDefinePublic} from "@/components/graph/AggregateDefinePublic";
import {GraphCellGeneratePublic} from "@/components/graph/GraphCellGeneratePublic";
import {GraphPositionSetDefine} from "@/components/graph/GraphPositionSetDefine";
import {GraphColorSetDefine} from "@/components/graph/GraphColorSetDefine";
import axios from "axios";

axios.defaults.timeout = 3000;
axios.defaults.headers = {'bodirection': 'true'};

export class AggregateGenerate {
    // 生成aggregate之前的画布信息
    public oldGraphmodel = '';
    // 所有的aggregate组
    public lifecycleMapList: any[] = [];
    // 所有出现的Aggregate对象
    public aggregateList: any[] = [];
    // 所有出现的Aggregate以及Group对象
    public aggregateAndGroupList: any[] = [];
    // 每个aggrName的内容的出现次数(防重复)
    public aggregateNameAndTimesMap = new Map();
    // 每个生命周期里所有objectid组成的list以及对应的rootobj
    public lifecycleIdListRootObjMap = new Map();
    // 每个rootObject以及其对应的lifecycleMap
    public rootObjLifecycleMapMap = new Map();
    // 每个Aggregate的指定的rootId(如果有的话)以及Aggregate的组标号
    public rootIdAndLifecycleGroupMap = new Map();
    // 每个Aggregate的Aggregate的组标号以及指定的rootId(如果有的话)
    public lifecycleGroupAndRootIdMap = new Map();
    //界面提示信息的设置，消息类型、时长(ms)
    private messageType = "error";
    private messageDuration = 5000;
    //标记需要执行的操作是针对Aggregate内部还是跨Aggregate
    private typeFlagIn = "In";
    private typeFlagCross = "Cross";
    //进行检测的lineObject的类型【aggregate内部+跨aggregate】
    private lineObjectType = "";
    //进行检测的remark的类型【aggregate内部+跨aggregate】
    private remarkType = "";

    protected gphDefPub: GraphCellDefinePublic = new GraphCellDefinePublic();
    protected aggrDefPub: AggregateDefinePublic = new AggregateDefinePublic();
    protected gphGenPub: GraphCellGeneratePublic = new GraphCellGeneratePublic();
    protected gphPosDef: GraphPositionSetDefine = new GraphPositionSetDefine();
    protected gphColorSetDef: GraphColorSetDefine = new GraphColorSetDefine();

    private $store: any = null;
    private $message: any = null;
    private $bus: any = null;
    private modelChangeAndStore: ModelChangeAndStore = new ModelChangeAndStore();

    public setStore(store: any) {
        this.$store = store;
    }

    public setBus(bus: any) {
        this.$bus = bus;
    }

    public setMessage(message: any) {
        this.$message = message;
    }

    // aggregate更改后重生成
    public async ReGenerateAggrate(graphModel: any) {
        // 初始化
        this.lifecycleMapList.splice(0, this.lifecycleMapList.length);
        this.aggregateList.splice(0, this.aggregateList.length);
        this.aggregateAndGroupList.splice(0, this.aggregateAndGroupList.length);
        this.lifecycleIdListRootObjMap.clear();
        this.rootObjLifecycleMapMap.clear();
        this.rootIdAndLifecycleGroupMap.clear();
        this.lifecycleGroupAndRootIdMap.clear();

        // 首先刷新create模型
        this.modelChangeAndStore.setStore(this.$store);

        // 记录生成aggregate之前的model内容
        this.storeModel(graphModel);

        let nodejsonChildArray = this.gphDefPub.getJsonChildArrayFromGraph(graphModel);

        //读取规则配置文件
        let userConfig:any=await this.getAggregateRuleFile();

        //校验规则1：画布中最少的object数量
        let objectLeastCountResult = this.judgeLeastObjectAmount(nodejsonChildArray, userConfig.defaultObjectCount);
        if (objectLeastCountResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        //校验规则2：校验object的默认类型【注：object是指用户不确定类型，这里依据配置文件指定其具体类型】
        this.judgeObjectDefaultStyleAndSet(nodejsonChildArray, userConfig.defaultObjectType);

        // 虚线实化
        this.solidAllDashedLine(nodejsonChildArray);
        const allLineList = this.getAllLineObjectList(nodejsonChildArray);

        // 将所有箭头对象以及multiplicity对象【线上的标注】放入最底部
        this.aggrDefPub.adjustJsonArrayOrder(nodejsonChildArray);

        // 获取目前所有的aggregate对象(包括手动和自动生成的)
        this.getAllAggregateObject(nodejsonChildArray);

        // 先按标签分类，获取多个aggregate
        this.getLifeCycleMapList(nodejsonChildArray);

        // 判断是否一个Aggregate内存在多个rootObject
        const countRootObjectAmountResult = this.countRootObjectAmount(nodejsonChildArray);
        if (countRootObjectAmountResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        // 去掉所有已有的group对象
        this.removeAllGroupObject(nodejsonChildArray);

        //校验规则3：校验aggregate内部实体之间的指向
        this.lineObjectType = "In";
        const judgeIsLegalPointingInterAggregateResult = this.judgeIllegalPointing(this.lineObjectType, nodejsonChildArray, allLineList, userConfig.illegalPointingListInterAgg);
        if (judgeIsLegalPointingInterAggregateResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        //校验规则3.5：校验每个object入度和出度，防止环以及孤立点的出现
        const judgeIsLegalPointingCountInterAggregateResult = this.judgeIsLegalPointingCountInterAggregate(nodejsonChildArray, allLineList);
        if (judgeIsLegalPointingCountInterAggregateResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        //校验规则4：校验aggregate内line上下游标记以及连线有向否是否合法
        this.remarkType = "In";
        const judgeIsLegalLineRemarkInterAggregateResult = this.judgeIsLegalLineRemark(this.remarkType, nodejsonChildArray, allLineList, userConfig.illegalLineMarkListInterAgg);
        if (judgeIsLegalLineRemarkInterAggregateResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        // 寻找根节点，通过依次排查entity的方式
        const getRootObjectFromLifecycleMapResult = this.getRootObjectFromLifecycleMap(nodejsonChildArray, allLineList);
        if (getRootObjectFromLifecycleMapResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        //校验规则5：校验跨aggregate实体之间的非法指向
        this.lineObjectType = "Cross";
        const judgeIsLegalPointingBetweenAggregateResult = this.judgeIllegalPointing(this.lineObjectType, nodejsonChildArray, allLineList, userConfig.illegalPointingListBetweenAgg);
        if (judgeIsLegalPointingBetweenAggregateResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        //校验规则6：校验跨aggregate的line上下游标记以及连线有向否是否合法
        this.remarkType = "Cross";
        const judgeIsLegalLineRemarkBetweenAggregateResult = this.judgeIsLegalLineRemark(this.remarkType, nodejsonChildArray, allLineList, userConfig.illegalLineMarkListBetweenAgg);
        if (judgeIsLegalLineRemarkBetweenAggregateResult === false) {
            this.backToBefore(graphModel);
            return false;
        }

        // 执行分类
        this.generateAggerateAndComposite(nodejsonChildArray);

        // 重新设定各元素位置
        this.gphPosDef.resetGraphCellPosition(nodejsonChildArray, true);

        //重新画框
        this.reSetAggregateSize(nodejsonChildArray);

        //更改Aggregate布局
        this.gphPosDef.resetAggregatePosition(nodejsonChildArray);

        // 跨Aggregate的连线需要虚化(包含需要改向的有向线段和不需要改向的无向线段)
        this.aggrDefPub.dashDiffAggrLine(nodejsonChildArray);

        // 更改跨Aggr线段颜色
        this.gphColorSetDef.changeEdgeColorBetweenAggr(nodejsonChildArray);

        // 将所有线段的parent设为1
        this.aggrDefPub.setAllLineParent(nodejsonChildArray);

        // 最后进行组装
        this.gphDefPub.decodeJsonArrayToGraph(graphModel, nodejsonChildArray);

        // 更改跨Aggr连线的坐标和样式
        this.gphPosDef.changeLinePosition(graphModel);

        // 刷新graphModel
        nodejsonChildArray = this.refreshGraphModel(graphModel);

        // 处理全局变量和事件
        this.processGlobalParamAfterDecode(nodejsonChildArray);

        // 返回值
        return true;
    }

    public async getAggregateRuleFile(){
        let resultNew;
        if(sessionStorage.getItem('aggregateRule')){
            resultNew= JSON.parse(sessionStorage.getItem('aggregateRule'));
        }else{
            let result=new Promise((resolve, reject) => {
                axios.get('/v1/aggregate/rule', {
                    headers: {
                        accessToken: sessionStorage.getItem('token')
                    }
                }).then((res) => {
                        resolve(res.data);
                    }, (error) => {
                        if (error.message === "Request failed with status code 401"){
                            window.location.href = "#/login";
                        }
                    },
                );
            });
            resultNew=await result;
            sessionStorage.setItem('aggregateRule',JSON.stringify(resultNew));
        }
        return resultNew;
    }

    /*以下是规则校验函数*/

    //校验规则1：画布中含有的最少object数量
    public judgeLeastObjectAmount(nodejsonChildArray: any, defaultObjectCount: any) {
        let objectCount = this.countObjectAmount(nodejsonChildArray);
        if (objectCount < defaultObjectCount) {
            const showMessage = 'fail,can\'t find enough object';
            this.errorMessage(showMessage);
            return false;
        }
    }

    //校验规则2：校验object的默认类型
    public judgeObjectDefaultStyleAndSet(nodejsonChildArray: any, defaultObjectType: any) {
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.style === "Object") {
                //jsonObject的style
                jsonObject.style = defaultObjectType;
                //value的style
                let newValue = this.setNewValueStyleOfObject(defaultObjectType, jsonObject);
                jsonObject.value = newValue;
            }
        }
    }

    //校验规则3和5：校验lineObject的指向是否合法
    public judgeIllegalPointing(typeFlag: any, nodejsonChildArray: any, allLineList: any, illegalPointingList: any) {
        //如果两个实体的类型是illegalPointing中的任意一个组合，报错：非法指向
        let result;
        for (const lifecycleMap of this.lifecycleMapList) {
            const idObjectMap = new Map();
            const idList = [];
            const vri = lifecycleMap.entries();
            let next = vri.next().value;
            while (next !== undefined) {
                idList.push(next[0].id);
                idObjectMap.set(next[0].id, next[0]);
                next = vri.next().value;
            }

            for (const lineObject of allLineList) {
                //判断lineObject的类型（agg内or跨agg）,再比较是否违法
                result = this.judgeAndCompareLineObject(typeFlag, lineObject, idList, nodejsonChildArray, illegalPointingList);
                if (result === false) {
                    return false;
                }
            }
        }
        return result;
    }

    //校验规则3.5：校验Aggregate内部是否是一棵树
    public judgeIsLegalPointingCountInterAggregate(nodejsonChildArray: any, allLineList: any) {
        let result;
        for (const lifecycleMap of this.lifecycleMapList) {
            let idObjectMap = new Map();
            let idList = [];
            let vri = lifecycleMap.entries();
            let next = vri.next().value;
            while (next !== undefined) {
                idList.push(next[0].id);
                idObjectMap.set(next[0].id, next[0]);
                next = vri.next().value;
            }
            result = this.numberOfInAndOutInLifecycleMap(vri, lifecycleMap, next, idList, allLineList);
        }
        return result;
    }

    //校验规则4和6：校验aggregate内line上下游标记以及连线有向否是否合法
    public judgeIsLegalLineRemark(typeFlag: any, nodejsonChildArray: any, allLineList: any, illegalLineMarkList: any) {
        let result;
        for (const lifecycleMap of this.lifecycleMapList) {
            const idObjectMap = new Map();
            const idList = [];
            const vri = lifecycleMap.entries();
            let next = vri.next().value;
            while (next !== undefined) {
                idList.push(next[0].id);
                idObjectMap.set(next[0].id, next[0]);
                next = vri.next().value;
            }

            for (const lineObject of allLineList) {
                result = this.judgeAndCompareRemark(typeFlag, lineObject, idList, nodejsonChildArray, illegalLineMarkList);
                if (result === false) {
                    return false
                }
            }
        }
        return result;
    }

    /*以下是一些函数的具体实现*/

    //统计object的数量
    public countObjectAmount(nodejsonChildArray: any) {
        let objectCount = 0;
        for (const jsonObject of nodejsonChildArray) {
            if (this.gphDefPub.judgeIsObject(jsonObject)) {
                objectCount++;
            }
        }
        return objectCount;
    }

    //获取lineObject的源object
    public getSourceObjectOfLineObject(nodejsonChildArray: any, lineObject: any) {
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.id === lineObject.source) {
                return jsonObject;
            }
        }
    }

    //获取lineObject所指向的object
    public getTargetObjectOfLineObject(nodejsonChildArray: any, lineObject: any) {
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.id === lineObject.target) {
                return jsonObject;
            }
        }
    }

    //拷贝/获取lineObject对应的sourcePoint和targetPoint
    public getSourceAndTargetPointOfLineObject(nodejsonChildArray: any, lineObject: any) {
        //copy一份lineObject的起始点和终点关系标记
        let copyStartPoint;
        let copyEndPoint;
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.parent === lineObject.id && (String(jsonObject.children[0].x) === '-1')
                && jsonObject.style === CellStyle.Multiplicity) {
                copyStartPoint = JSON.parse(JSON.stringify(jsonObject));
            } else if (jsonObject.parent === lineObject.id && (String(jsonObject.children[0].x) === '1')
                && jsonObject.style === CellStyle.Multiplicity) {
                copyEndPoint = JSON.parse(JSON.stringify(jsonObject));
            }
        }
        return {startPoint: copyStartPoint, endPoint: copyEndPoint};
    }

    //改变object-->value-->style的取值，style
    public setNewValueStyleOfObject(newStyle: any, jsonObject: any) {
        let oldValue = JSON.parse(jsonObject.value);
        let newValue = JSON.stringify({
            objectId: oldValue.objectId,
            style: newStyle,
            label: oldValue.label,
            iconColor: oldValue.iconColor,
            boId: oldValue.boId,
        });
        return newValue;
    }

    //违反规则时的错误反馈信息提示
    public errorMessage(showMessage: any) {
        this.$message({
            type: this.messageType,
            message: showMessage,
            duration: this.messageDuration
        });
    }

    //依据lineObject的类型分别执行与非法指向list的比较
    public judgeAndCompareLineObject(typeFlag: any, lineObject: any, idList: any, nodejsonChildArray: any, illegalPointingList: any) {
        //Aggregate内部的line [1，源点在idList里；2，终点在idList里]
        let result;
        if (typeFlag === this.typeFlagIn) {
            let lineObjectType = this.judgeLineObjectType(lineObject, idList);
            if (lineObjectType === "lineInAggregate") {
                result = this.compareWithIllegalPointingList(typeFlag, lineObject, nodejsonChildArray, illegalPointingList);
            }
        }
        //跨Aggregate的line [1，源点在idList里；2，终点不在idList里]
        if (typeFlag === this.typeFlagCross) {
            let lineObjectType = this.judgeLineObjectType(lineObject, idList);
            if (lineObjectType === "lineCrossAggregate") {
                result = this.compareWithIllegalPointingList(typeFlag, lineObject, nodejsonChildArray, illegalPointingList);
            }
        }
        return result;
    }

    //判断lineObject的类型
    public judgeLineObjectType(lineObject: any, idList: any) {
        let lineType;
        if (idList.includes(lineObject.source) && idList.includes(lineObject.target)) {
            lineType = "lineInAggregate";
        }
        if (idList.includes(lineObject.source) && !idList.includes(lineObject.target)) {
            lineType = "lineCrossAggregate"
        }
        return lineType;
    }

    //将lineObject与illegalPointingList的数据进行对比
    public compareWithIllegalPointingList(typeFlag: any, lineObject: any, nodejsonChildArray: any, illegalPointingList: any) {
        //1，获取source及target的类型
        let sourceType;//同一个aggregate内source的类型
        let targetType;//同一个aggregate内target的类型
        sourceType = this.getSourceObjectOfLineObject(nodejsonChildArray, lineObject).style;
        targetType = this.getTargetObjectOfLineObject(nodejsonChildArray, lineObject).style;
        //获取object名称，用于错误提醒显示
        const sourceName = this.gphDefPub.getObjName(this.getSourceObjectOfLineObject(nodejsonChildArray, lineObject));
        const targetName = this.gphDefPub.getObjName(this.getTargetObjectOfLineObject(nodejsonChildArray, lineObject));

        //2,遍历配置文件中illegalPointing的内容，依此进行比较
        for (const illegalPointing of illegalPointingList) {
            let illegalSourceType = illegalPointing.sourceObjectType;
            let illegalTargetType = illegalPointing.targetObjectType;
            if ((sourceType === illegalSourceType) && (targetType === illegalTargetType)) {
                let showMessage;
                if (typeFlag === this.typeFlagIn) {
                    showMessage = sourceType + ' : ' + sourceName + ' can\'t point to ' + targetType + ' : ' + targetName;
                }
                if (typeFlag === this.typeFlagCross) {
                    showMessage = "Cross-aggregate can only point to the Root-Object " + " : " + sourceName;
                }
                this.errorMessage(showMessage);
                return false;
            }
        }
    }

    //统计一个生命周期里面每个object的入度和出度数量
    public numberOfInAndOutInLifecycleMap(vri: any, lifecycleMap: any, next: any, idList: any, allLineList: any) {
        let result;
        let objectCount = 0;
        vri = lifecycleMap.entries();
        next = vri.next().value;
        while (next !== undefined) {
            if (this.gphDefPub.judgeIsObject(next[0])) {
                objectCount++;
            }
            next = vri.next().value;
        }

        if (objectCount === 1) {
            //排除Aggregate里面只有一个object的情况
        } else {
            vri = lifecycleMap.entries();
            next = vri.next().value;

            result = this.inAndOutNumberOfObject(next, idList, allLineList, vri);
        }
        return result;
    }

    //依据object的入度和出度数量做处理
    public inAndOutNumberOfObject(next: any, idList: any, allLineList: any, vri: any) {
        while (next != undefined) {
            let inCount = 0;
            let outCount = 0;
            if (this.gphDefPub.judgeIsObject(next[0])) {
                for (const lineObject of allLineList) {
                    if ((idList.includes(lineObject.source)) && (idList.includes(lineObject.target))) {
                        //统计每个object的入度
                        if (lineObject.target === next[0].id) {
                            inCount++;
                        }
                        //统计每个object的出度
                        if (lineObject.source === next[0].id) {
                            outCount++;
                        }
                    }
                }

                const objectName = this.gphDefPub.getObjName(next[0]);
                let showMessage;
                //入度>1报错
                if (inCount > 1) {
                    showMessage = "Aggregate internal object cannot be repeatedly pointed: " + objectName;
                    this.errorMessage(showMessage);
                    return false;
                }
                //入度=0，出度=0，报错
                if (inCount === 0 && outCount == 0) {
                    showMessage = "Aggregate internal object cannot be isolated: " + objectName;
                    this.errorMessage(showMessage);
                    return false;
                }
            }
            next = vri.next().value;
        }
    }

    //依据lineObject的类型分别执行与illegalLineMarkList的比较
    public judgeAndCompareRemark(typeFlag: any, lineObject: any, idList: any, nodejsonChildArray: any, illegalLineMarkList: any) {
        let result;
        //Aggregate内部的line [1，源点在idList里；2，终点在idList里]
        if (typeFlag === this.typeFlagIn) {
            let lineObjectType = this.judgeLineObjectType(lineObject, idList);
            if (lineObjectType === "lineInAggregate") {
                result = this.compareWithIllegalRemarkList(typeFlag, lineObject, nodejsonChildArray, illegalLineMarkList);
            }
        }
        //跨Aggregate的line [1，源点在idList里；2，终点不在idList里]
        if (typeFlag === this.typeFlagCross) {
            let lineObjectType = this.judgeLineObjectType(lineObject, idList);
            if (lineObjectType === "lineCrossAggregate") {
                result = this.compareWithIllegalRemarkList(typeFlag, lineObject, nodejsonChildArray, illegalLineMarkList);
            }
        }
        return result;
    }

    //将lineObject与illegalLineMarkList的数据进行对比
    public compareWithIllegalRemarkList(typeFlag: any, lineObject: any, nodejsonChildArray: any, illegalLineMarkList: any) {
        let result;
        //1，获取起点以及终点object的标记
        let startPoint;
        let endPoint;
        let startRemarkFirstChar;
        let endMarkFirstChar;
        startPoint = this.getSourceAndTargetPointOfLineObject(nodejsonChildArray, lineObject).startPoint;
        endPoint = this.getSourceAndTargetPointOfLineObject(nodejsonChildArray, lineObject).endPoint;
        startRemarkFirstChar = (startPoint.value).substr(0, 1);
        endMarkFirstChar = (endPoint.value).substr(0, 1);

        //2,判断line是否有向
        let lineType;
        if (!this.gphDefPub.judgeIsNoDirectionLine(lineObject)) {
            //有向
            lineType = "DirectionLine"
        } else {
            lineType = "NoDirectionLine"
        }

        //3,获取target的数据类型
        let targetJsonObject;
        let targetType;
        targetJsonObject = this.getTargetObjectOfLineObject(nodejsonChildArray, lineObject);
        targetType = targetJsonObject.style;

        //4,遍历配置文件中illegalRemark的内容，依次进行比较
        for (const illegalMark of illegalLineMarkList) {
            let illegalSourceMark = illegalMark.sourceFirstChar;
            let illegalTargetMark = illegalMark.targetFirstChar;
            let illegalLineType = illegalMark.lineType;
            if ((startRemarkFirstChar === illegalSourceMark) && (endMarkFirstChar === illegalTargetMark) && (lineType === illegalLineType)) {
                const sourceName = this.gphDefPub.getObjName(this.getSourceObjectOfLineObject(nodejsonChildArray, lineObject));
                const targetName = this.gphDefPub.getObjName(this.getTargetObjectOfLineObject(nodejsonChildArray, lineObject));
                result = this.illegalRemarkMessage(typeFlag, startRemarkFirstChar, endMarkFirstChar, targetType, startPoint, sourceName, targetName);
                if (result === false) {
                    return false;
                }
            }
        }
        return result;
    }

    //object之间标记非法的消息提示
    public illegalRemarkMessage(typeFlag: any, startRemarkFirstChar: any, endMarkFirstChar: any, targetType: any, startPoint: any, sourceName: any, targetName: any) {
        if (typeFlag === this.typeFlagIn) {
            if (startRemarkFirstChar === "1" && endMarkFirstChar === "1" && targetType === "Value-Object") {
            } else {
                //给出具体报错信息
                if (startRemarkFirstChar === "0") {
                    const showMessage = " Remark cannot set as " + startPoint.value + " : " + sourceName;
                    this.errorMessage(showMessage);
                } else if (endMarkFirstChar === "1") {
                    const showMessage = " invalid, try to set multiplicity of  targetMark  be 0 or set it as ValueObject " + " : " + targetName;
                    this.errorMessage(showMessage);
                }
                return false;
            }
        }
        if (typeFlag === this.typeFlagCross) {
            const showMessage = " Illegal relationship across aggregates " + " : " + sourceName + " to " + targetName;
            this.errorMessage(showMessage);
            return false;
        }
    }

    //寻找根节点
    public getRootObjectFromLifecycleMap(nodejsonChildArray: any, allLineList: any) {
        let result;
        const idAndObjectMap = this.aggrDefPub.getIdAndObjectMapInArray(nodejsonChildArray);
        for (const lifecycleMap of this.lifecycleMapList) {
            const idObjectMap = new Map();
            const idList = [];
            let isValid = true;
            let rootNameStr = '';
            let rootAmount = 0;
            let rootObject;
            let lifecycleValue;
            let vri = lifecycleMap.entries();
            let next = vri.next().value;
            while (next !== undefined) {
                idList.push(next[0].id);
                idObjectMap.set(next[0].id, next[0]);
                lifecycleValue = next[1];
                next = vri.next().value;
            }
            vri = lifecycleMap.entries();
            next = vri.next().value;
            while (next !== undefined) {
                // 逐一判断每个entity是否符合条件(自身为source的情况下总是，自身为target的情况下若source为entity则不是，若被vo明确指向则报错)
                if (this.gphDefPub.judgeIsNotValueObject(next[0])) {
                    for (const lineObject of allLineList) {
                        if (lineObject.target === next[0].id) {
                            const sourceId = lineObject.source;
                            if (idList.includes(sourceId) && this.gphDefPub.judgeIsNotValueObject(idObjectMap.get(sourceId))) {
                                isValid = false;
                                break;
                            }
                        }
                    }
                    if (isValid) {
                        rootAmount++;
                        rootNameStr = rootNameStr + this.gphDefPub.getObjName(next[0]) + ' ';
                        rootObject = next[0];
                    }
                    isValid = true;
                }
                next = vri.next().value;
            }
            result = this.illegalRootMessage(rootAmount, rootNameStr, lifecycleValue, rootObject, idAndObjectMap);
            if (result === false) {
                return false
            }
            // rootObject样式调整
            this.gphDefPub.changeStyleEntityToRoot(rootObject);
            this.rootObjLifecycleMapMap.set(rootObject, lifecycleMap);
            this.lifecycleIdListRootObjMap.set(idList, rootObject);
        }
    }

    //根节点违反规则的提示信息
    public illegalRootMessage(rootAmount: any, rootNameStr: any, lifecycleValue: any, rootObject: any, idAndObjectMap: any) {
        if (rootAmount >= 2) {
            const showMessage = " multiple root is unacceptable: " + " : " + rootNameStr;
            this.errorMessage(showMessage);
            return false;
        } else if (rootAmount === 0) {
            const showMessage = 'error,lifecycleGroup ' + lifecycleValue + ' have no root';
            this.errorMessage(showMessage);
            return false;
        } else {
            // 判断规则选出的这个root和用户指定的是否一致
            if (this.lifecycleGroupAndRootIdMap.has(lifecycleValue)) {
                if (this.lifecycleGroupAndRootIdMap.get(lifecycleValue) !== rootObject.id) {
                    const pluralRootName = this.gphDefPub.getObjName(idAndObjectMap.get(this.lifecycleGroupAndRootIdMap.get(lifecycleValue)))
                        + " " + this.gphDefPub.getObjName(rootObject);
                    const showMessage = "error,find plural amount of rootObject in LifecycleGroup " + lifecycleValue + " :" + pluralRootName;
                    this.errorMessage(showMessage);
                    return false;
                }
            }
        }
    }

    // 判断是否一个Aggregate内存在多个rootObject
    public countRootObjectAmount(nodejsonChildArray: any) {
        for (const lifecycleMap of this.lifecycleMapList) {
            let rootAmount = 0;
            let lifecycleGroup = "";
            let rootName = "";
            let rootId = "";
            const vri = lifecycleMap.entries();
            let next = vri.next().value;
            while (next !== undefined) {
                if (next[0].style === CellStyle.RootObject) {
                    rootAmount++;
                    rootName = rootName + this.gphDefPub.getObjName(next[0]) + " ";
                    rootId = next[0].id;
                    lifecycleGroup = next[0].parent;
                }
                next = vri.next().value;
            }
            if (rootAmount >= 2) {
                const showMessage = "rootObject's amount can't have more than one in the same group:" + rootName;
                this.errorMessage(showMessage);
                return false;
            }
            // 如果有指定root，则记录
            if (rootAmount === 1) {
                this.rootIdAndLifecycleGroupMap.set(rootId, lifecycleGroup);
                this.lifecycleGroupAndRootIdMap.set(lifecycleGroup, rootId);
            }
        }
        return true;
    }

    //获取所有的连线【实线+虚线】
    public getAllLineObjectList(nodejsonChildArray: any) {
        const allLineList = [];
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.edge === "1") {
                allLineList.push(jsonObject);
            }
        }
        return allLineList;
    }

    //获取目前所有的aggregate对象
    public getAllAggregateObject(nodejsonChildArray: any) {
        for (const jsonObject of nodejsonChildArray) {
            if (this.gphDefPub.judgeIsAggrOrGroup(jsonObject)) {
                this.aggregateAndGroupList.push(jsonObject);
            }
        }
    }

    //虚线实化，将虚线换成实线
    public solidAllDashedLine(nodejsonChildArray: any) {
        for (const jsonObject of nodejsonChildArray) {
            if (jsonObject.edge === "1" && this.gphDefPub.judgeIsDashedLine(jsonObject)) {
                this.gphDefPub.solidLineFromDash(jsonObject);
            }
        }
    }

    // 重新生成的aggregate,后面增加的，一个object相当于一个aggregate
    public getLifeCycleMapList(nodejsonChildArray: any) {
        // 首先收集所有在已生成的aggregate框里的object
        for (const aggregateObject of this.aggregateAndGroupList) {
            if (aggregateObject.style !== CellStyle.Group) {
                this.aggregateList.push(aggregateObject);
                this.aggregateNameAndTimesMap.set(aggregateObject.value, 0);
            }
            const aggrName = this.gphDefPub.getAggregateName(aggregateObject);
            const dict = new Map();
            for (const jsonObject of nodejsonChildArray) {
                if (jsonObject.parent === aggregateObject.id) {
                    dict.set(jsonObject, aggrName);
                }
            }
            if (dict.size !== 0) {
                this.lifecycleMapList.push(dict);
            }
        }
        // 再收集后面增加的,一个object对应一个aggregate
        for (const jsonObject of nodejsonChildArray) {
            if (this.gphDefPub.judgeIsObject(jsonObject) && jsonObject.parent === '1') {
                const dict = new Map();
                dict.set(jsonObject, this.gphDefPub.getObjName(jsonObject));
                this.lifecycleMapList.push(dict);
            }
        }
    }

    // 删除已有group，object改Parent，object增加之前减掉的偏移量
    public removeAllGroupObject(nodejsonChildArray: any) {
        let len = nodejsonChildArray.length;
        for (let i = 0; i < len; i++) {
            if (nodejsonChildArray[i].style === CellStyle.Group) {
                for (const jsonObjectInAggregate of nodejsonChildArray) {
                    if (jsonObjectInAggregate.parent === nodejsonChildArray[i].id) {
                        jsonObjectInAggregate.parent = '1';
                        // 获取group这个父对象消失后里面各object的绝对坐标
                        jsonObjectInAggregate.children[0].x = jsonObjectInAggregate.children[0].x + nodejsonChildArray[i].children[0].x;
                        jsonObjectInAggregate.children[0].y = jsonObjectInAggregate.children[0].y + nodejsonChildArray[i].children[0].y;
                    }
                }
                nodejsonChildArray.splice(i, 1);
                i--;
                len--;
            }
        }
    }

    //执行分类
    public generateAggerateAndComposite(nodejsonChildArray: any) {
        const timestamp = (new Date()).getTime();
        const tenantId = this.$store.state.activeSession.tenantId;
        const aggrId = tenantId + "_" + timestamp + "_";
        const rootObjLifecycleMapVri = this.rootObjLifecycleMapMap.entries();
        let rootObjLifecycleMapNext = rootObjLifecycleMapVri.next().value;
        // 插入aggregate对象的位置
        let insertPosition = 0;
        while (rootObjLifecycleMapNext !== undefined) {
            let leftUpX = Number.MAX_VALUE;
            let leftUpY = Number.MAX_VALUE;
            let rightDownX = 0;
            let rightDownY = 0;

            const idList = [];
            const rootObject = rootObjLifecycleMapNext[0];
            const lifecycleMap = rootObjLifecycleMapNext[1];
            if (rootObject.parent !== '1') {
                rootObjLifecycleMapNext = rootObjLifecycleMapVri.next().value;
                continue;
            }
            let lifeObjectVri = lifecycleMap.entries();
            let lifeObjectNext = lifeObjectVri.next().value;
            while (lifeObjectNext !== undefined) {
                idList.push(lifeObjectNext[0].id);
                if (leftUpX > lifeObjectNext[0].children[0].x) {
                    leftUpX = lifeObjectNext[0].children[0].x;
                }
                if (leftUpY > lifeObjectNext[0].children[0].y) {
                    leftUpY = lifeObjectNext[0].children[0].y;
                }
                if (rightDownX < (lifeObjectNext[0].children[0].x + lifeObjectNext[0].children[0].width)) {
                    rightDownX = (lifeObjectNext[0].children[0].x + lifeObjectNext[0].children[0].width);
                }
                if (rightDownY < (lifeObjectNext[0].children[0].y + lifeObjectNext[0].children[0].height)) {
                    rightDownY = (lifeObjectNext[0].children[0].y + lifeObjectNext[0].children[0].height);
                }
                lifeObjectNext = lifeObjectVri.next().value;
            }
            leftUpX -= offset;
            leftUpY -= offset;
            const width = rightDownX - leftUpX + offset;
            const height = rightDownY - leftUpY + offset;
            lifeObjectVri = lifecycleMap.entries();
            lifeObjectNext = lifeObjectVri.next().value;
            // 在aggregate这个父对象下面重新给各object生成相对坐标
            const objectid = this.aggrDefPub.getMaxIdInModel(nodejsonChildArray);
            while (lifeObjectNext !== undefined) {
                if (this.gphDefPub.judgeIsObject(lifeObjectNext[0])) {
                    const objBeforeStr = JSON.stringify(lifeObjectNext[0]);
                    lifeObjectNext[0].children[0].x = lifeObjectNext[0].children[0].x - leftUpX;
                    lifeObjectNext[0].children[0].y = lifeObjectNext[0].children[0].y - leftUpY;
                    lifeObjectNext[0].parent = String(objectid);
                    lifeObjectNext = lifeObjectVri.next().value;
                } else {
                    lifeObjectNext = lifeObjectVri.next().value;
                }

            }
            // 校验Aggr名称，防止重复
            const aggrName = "Aggregate_" + this.gphDefPub.getObjName(rootObject);
            let aggrNameIsExist = false;
            let aggrDuplicatedName = aggrName;
            while (this.aggregateNameAndTimesMap.has(aggrDuplicatedName)) {
                const times = this.aggregateNameAndTimesMap.get(aggrName) + 1;
                this.aggregateNameAndTimesMap.set(aggrName, times);
                aggrDuplicatedName = aggrName + String(times);
                aggrNameIsExist = true;
            }
            if (!aggrNameIsExist) {
                this.aggregateNameAndTimesMap.set(aggrName, 0);
            }
            const aggregateObjIndex = this.$store.state.activeProject.aggregateObjIndex;
            let aggrAmount = 0;
            if (aggregateObjIndex === -1) {
                aggrAmount = this.aggrDefPub.getAggrAmountInModel(nodejsonChildArray);
            } else {
                aggrAmount = aggregateObjIndex;
            }
            const aggregateCell = this.gphGenPub.generateAggerateCancul(leftUpX, leftUpY, width, height, objectid,
                aggrDuplicatedName, aggrId, CellWidth, CellHeight, aggrAmount);
            if (insertPosition === 0) {
                insertPosition = this.aggrDefPub.getLastAggregateIndex(nodejsonChildArray);
            }
            nodejsonChildArray.splice(insertPosition + 1, 0, aggregateCell);
            insertPosition++;
            aggrAmount++;
            this.$store.commit('activeProject/setAggregateObjIndex', aggrAmount);
            rootObjLifecycleMapNext = rootObjLifecycleMapVri.next().value;
        }
    }

    //重新画框
    public reSetAggregateSize(nodejsonChildArray:any[]) {
        const rootObjLifecycleMapVri = this.rootObjLifecycleMapMap.entries();
        let rootObjLifecycleMapNext = rootObjLifecycleMapVri.next().value;
        while (rootObjLifecycleMapNext !== undefined) {
            let leftUpX = Number.MAX_VALUE;
            let leftUpY = Number.MAX_VALUE;
            let rightDownX = 0;
            let rightDownY = 0;
            const rootObject = rootObjLifecycleMapNext[0];
            const lifecycleMap = rootObjLifecycleMapNext[1];
            let lifeObjectVri = lifecycleMap.entries();
            let lifeObjectNext = lifeObjectVri.next().value;
            while (lifeObjectNext !== undefined) {

                if (leftUpX > lifeObjectNext[0].children[0].x) {
                    leftUpX = lifeObjectNext[0].children[0].x;
                }

                if (leftUpY > lifeObjectNext[0].children[0].y) {
                    leftUpY = lifeObjectNext[0].children[0].y;
                }
                if (rightDownX < (lifeObjectNext[0].children[0].x + lifeObjectNext[0].children[0].width)) {
                    rightDownX = (lifeObjectNext[0].children[0].x + lifeObjectNext[0].children[0].width);
                }
                if (rightDownY < (lifeObjectNext[0].children[0].y + lifeObjectNext[0].children[0].height)) {
                    rightDownY = (lifeObjectNext[0].children[0].y + lifeObjectNext[0].children[0].height);
                }
                lifeObjectNext = lifeObjectVri.next().value;
            }
            const width = rightDownX - leftUpX + 2 * offset;
            const height = rightDownY - leftUpY + 2 * offset;
            nodejsonChildArray.forEach(function (val:any,index:any,val_arr:any) {
                if(val_arr[index].id==rootObject.parent){
                    val_arr[index].children[0].width=width;
                    val_arr[index].children[0].height=height
                }
            });
            rootObjLifecycleMapNext = rootObjLifecycleMapVri.next().value;
        }
    }

    //刷新graphModel
    public refreshGraphModel(graphModel: any) {
        const nodejsonChildArray = this.gphDefPub.getJsonChildArrayFromGraph(graphModel);
        this.gphDefPub.decodeJsonArrayToGraph(graphModel, nodejsonChildArray);
        return nodejsonChildArray;
    }

    //处理全局变量和事件
    public processGlobalParamAfterDecode(nodejsonChildArray: any) {
        const nodeShow = this.gphDefPub.compositeCompleteJsonChildArray(nodejsonChildArray);
        this.$store.commit('activeProject/setGraphModelInCheck', nodeShow);
        // 将所有的rootId放入store中
        const rootObjList = [];
        const vri = this.rootObjLifecycleMapMap.entries();
        const idList = [];
        let next = vri.next().value;
        while (next !== undefined) {
            rootObjList.push(next[0]);
            idList.push(next[0].id);
            next = vri.next().value;
        }
        this.$store.commit("boRepository/changeObjectsStyleToRoot", rootObjList);
        this.$store.commit("activeProject/setRootObjectIdList", idList);
        this.$store.commit('activeProject/setGroupObjIndex', 0);
        this.$bus.emit("chgBtnStyToNoAggrInCheckByOpr", true);
    }

    public backToBefore(graphModel: any) {
        return () => {
            const doc = new CodecDocument();
            const codec = new mx.mxCodec(doc);
            doc.fillFromJSON(this.oldGraphmodel);
            codec.decode(doc, graphModel);
        };
    }

    public storeModel(graphModel: any) {
        const modelBefore = graphModel;
        const beforedoc = new CodecDocument();
        const beforecodec = new mx.mxCodec(beforedoc);
        const beforenode = beforecodec.encode(modelBefore);
        const beforenodejsonObject = beforenode.outputToJson(2);
        this.oldGraphmodel = beforenodejsonObject;
    }

}
