BoBuilder2.0
介绍
基于DDD设计，围绕BO搭建的SAAS平台

详见​ http://plm-pms-riki.huawei.com/pages/viewpage.action?pageId=266905500

目录结构：
目前bobuilder有4个服务组件：portal, node_generator, node-runtime, spark, 目录结构如下

├── portal     -- 系统登录，建模服务
│   ├── config     -- 远程服务地址配置
│   ├── public     -- 第三方js,css,图片文件
│   └── src     -- 源代码目录
│   ├── tests/unit -- 单元测试文件
├── node_generator       -- node-red节点生成、安装服务
│   ├── config  -- 远程服务地址、日志配置
│   ├── src     -- 源代码目录
│       ├── core -- 镜像生成与部署，swagger生成
│       ├── lib  -- 工具库
│       ├── metadata  -- 映射BO数据成为节点数据
│       ├── nodeGenerators  -- 节点生成逻辑
│       ├── template  -- 节点前后端模板
├── node-runtime          -- 多租，流程编排服务
│   ├── nodes      -- 各个节点前后端逻辑
│   ├── public     -- 第三方库
│   ├── red        -- 运行逻辑
│   ├── test       -- 测试用例
├── spark           -- es数据关联服务
│   ├── src/main/java -- 关联逻辑
│   ├── src/main/resource -- 环境配置
工具安装与环境配置：
手动安装gitbash（http://isource-pages.huawei.com/iSource/Help//#noviceguide/git-install.html ）

node.js，python，webstorm等必要工具根据脚本提示安装。

工程下载与配置
windows下
在脚本目录中右键运Git Bash Here，使用命令“ source ./environment.sh"命令运行自动化脚本。根据程序提示一步步操作。
Linux下
在~/目录下运行“scp -r bo2.0@100.101.58.110:/home/bo2.0/linux.sh ./”下载脚本文件，密码bo2.0，然后使用命令“ ./linux.sh"命令运行自动化脚本，在提示的地方进行确认。
在命令行提示复制字符时候，点击iSource平台，在“Add SSH Key”里粘贴到“Public Key”栏，保存即可确认。项目保存在~/bobuilder文件夹中
开发规范
提issue

统一tslint

上传前消warning

cleancode规范

代码结构
XX模块（portal/boserver/node_gen/UI_BLOCK/node_run）
职责

流程

功能点

portal模块
源码文件结构：

├── portal     -- 系统登录，建模服务
│   ├── ...
│   └── src     -- 源代码目录
│       ├── assets -- 模块依赖的png图片
│       ├── components  -- 模块逻辑代码
│           ├── bo-detail  -- BO相关界面
│           ├── graph  -- mxgraph绘图逻辑
│           ├── home  -- 首页界面
│           ├── main-frame-cmps  -- 前端界面框架
│           └── store   -- 全局变量存储
│           └── style   -- 模块依赖的scss样式
│           └── views   -- 前端界面
│           └── parts   -- 侧边栏，头部，底部界面
│           └── serve   -- node-red侧边栏，UiBlock界面
│           └── side-bar-cmps   -- 首页界面，Aggregate编辑界面
职责：

       Aggregate模型编排，BO模型生成
流程：



功能点：

     登录，Aggregate生成，object配置，自动排版，连线走向调整，颜色变化
node_runtime模块
源码文件结构：

├── node-runtime          -- 多租，流程编排服务
│   ├── nodes      -- 各个节点前后端逻辑
│   ├── public     -- 第三方库
│   ├── red        -- 运行逻辑
│   ├── test       -- 测试用例
职责：

提供node-red所具备的流程编排服务，保证不同的租户间数据不会互相干扰

流程：

后台服务，提供node编排时的逻辑支撑
功能点：

多租，单实例多工程
设计文档
portal模块
使用技术：

    前端：vue

    后端：nodejs、mxgraph
常用数据结构 ：

     vue emit/$bus.emit

     store里的一系列全局变量

     nodeJsonArray
接口概述

      boserver接口，mxgraph生成Aggregate接口
设计细节

      全局变量统一放store，类自带逻辑与自身变量放一起

      界面分块，用框架进行具体的渲染，复用度高，定制化程度强

      数据库交互以nodered编排得到的http接口进行处理，充分解耦
注意事项

    vue事件发送与监听有些混乱，有可能出现某一组件事件被其他组件劫持的情况
node_runtime模块
由于内容过于庞杂，请参见**node-red代码分析.docx**中的内容
工程部署
打包脚本，dockerfile，k8s yaml

具体流程

测试指南
测试工具

测试方案（具体场景）

测试脚本/界面
FAQ
