## TypeScript的基础用法

> 祁玉  2019/7/17

### 历史小知识

JavaScript是1996年被开发出来的，97年提交给ECMA国际用于标准化工作即ECMAScript(简称ES5)。

Typescript是微软开发的脚本语言，是JS的超集，遵循ES6语言规范。

TS代码转换为JS的原因：现在很多浏览器都没有支持ES6规范，TS写出的代码并不能在有的浏览器上跑，而JS的代码可以兼容所有的浏览器。

### ts是什么

JS，一种轻量级的解释性脚本语言、可嵌入到HTML页面、可在浏览器端执行、能够在浏览器端进行丰富的交互。
特点：

- 无需编译，只要嵌入HTML代码中即可；
- 在浏览器端执行，不访问本地硬盘；
- 基于事件驱动，只根据用户的操作做出相应的反应处理；
- 跨平台语言：只依赖于浏览器，与操作系统的因素无关；
- 没有 类、继承、重载的功能



TS，面向对象语言、是JS的超集、可以载入JS代码运行、扩展了JS的语法。

特点：

- Microsoft推出的开源语言，使用Apach协议；
- 增加了静态类型、类、模块、接口、类型注解
- 可用于开发大型的应用；
- 易学易理解

### ts与js的关系

### ts基础语法

#### 运行

```
1,安装
npm install -g typescript   #在编译器里安装typescript
tsc -v    #查看安装的ts版本号
2，执行
tsc test.sh   #将ts代码转化为js代码
node test.js  #执行js文件，输出结果
```

#### 注释

```
单行：Ctrl+/
多行：Ctrl+Shift+/
```

#### 基本操作

```typescript
// 001,第一个测试语句
/*const hello:string="Hello world!"
console.log(hello)*/

//002,面向对象
/*class Site{
    name():void{
        console.log("Runoob")
    }
}
var obj=new Site();
obj.name();*/

//003,基础类型
/*//1,number
let binaryLiteral:number=0b1010;
let octalLiteral:number=0o744;
let decLiteral:number=77;
let hexLiteral:number=0xf00d;
console.log("二进制值："+binaryLiteral);
//2,string
let uname:string="Runoob";
let years:number=5;
let words:string=`你好呀，今年是${uname} 发布${years+1}周年`;
console.log("内嵌表达式："+words);
//3.boolean
let flag:boolean=true;
console.log("布尔型："+flag);
//4,数组
let arr1:number[]=[1,2];
let arr2:Array<number>=[3,4];
console.log("数组1："+arr1);
console.log("数组2："+arr2);
//5,元组
let x:[string,number];
x=['Qiyu',118]
//6,枚举
enum Color {Red,Blue,Green}
let c:Color=Color.Blue
console.log("枚举值："+c);
//7,void 表示方法的返回值类型，没有返回值
function hello():void{
    alert("Hello Qiyu");
}
//8,null 表示对象值缺失
//9,undefined 用于初始化变量是一个未定义的值
//10,any
let xx:any=1;
xx='I am a student!';
xx=false;*/

//004,变量
/*var uname:string="Runoob";
var score1:number=59;
var score2:number=56.7
var sum=score1+score2
console.log("姓名："+uname)
console.log("科目一成绩："+score1)
console.log("科目二成绩："+score2)
console.log("总成绩："+sum)*/

//005,变量作用域
/*var global_num=12;          //全局变量
class Numbers{
    num_val=13;             //类变量
    static sval=10;         //静态变量
    storeNum():void{
        var local_num=14;   //局部变量
    }
}
console.log("全局变量："+global_num);
console.log("静态变量："+Numbers.sval);
var obj=new Numbers();
console.log("类变量："+obj.num_val);*/

//006,条件语句
/*var num:number=2
if (num>0){
    console.log(num+"是正数");
} else if (num<0){
    console.log(num+"是负数");
}else {
    console.log(num+"不是正数也不是负数");
}

var grade:string='A'
switch (grade) {
    case 'A':{
        console.log('优秀');
        break;
    }
    case 'B':{
        console.log("良好");
        break;
    }
    case 'C':{
        console.log("及格");
        break;
    }
    case "D":{
        console.log("不及格");
        break;
    }
    default:{
        console.log("非法输入");
        break;
    }
}*/

//007,循环
/*var num:number=5;
var i:number;
var temp=1;
for(i=num;i>=1;i--){
    temp*=i;
}
console.log(temp);

var j:any
var n:any="a b c"
for(j in n){
    console.log(n[j])
}*/

/*var num:number=1;
var count:number=0;
for(num=1;num<=5;num++){
    if(num%2==0){
        count++;
        continue;
    }
    // count++;
}
console.log("1-5之间的偶数个数是："+count);*/

//008,函数
/*function add(x:number,y:number):number {
    return x+y;
}
console.log(add(1,2));
//可选参数
function calculate(price:number,rate:number=0.5){
    var dis=price*rate;
    console.log("折扣是："+dis);
}
calculate(1000);
calculate(1000,0.3)
//参数个数不确定
function buildName(firstName:string,...restOfName:string[]) {
    return firstName+" "+restOfName.join(" ");
}
let employeeName=buildName("Qiyu","John","liMINg","Rose");
console.log(employeeName);
//参数个数不确定
function addNums(...nums:number[]) {
    var i;
    var sum:number=0;

    for(i=0;i<nums.length;i++){
        sum+=nums[i]
    }
    console.log("和是："+sum);
}
addNums(1,2,3);
addNums(10,10,10,10,10);
//匿名函数，函数表达式
var res=function (a:number,b:number) {
    return a*b;
};
console.log(res(12,2));
//lambda函数
var foo=(x:number,y:number)=>x+y;
console.log(foo(10,100));
//重载：函数名相同，函数参数不同
function disp(n1:number,s1:string):void;
function disp(x:any,y:any):void {
    console.log(x);
    console.log(y);
}
disp(1,"yyy");*/

//009,Number
/*console.log("ts的Number属性：");
console.log("最大值："+Number.MAX_VALUE);
console.log("最小值："+Number.MIN_VALUE);
console.log("正无穷大："+Number.POSITIVE_INFINITY);
console.log("负无穷大："+Number.NEGATIVE_INFINITY)

var month=0;
if(month<=0 || month>12){
    month=Number.NaN;
    console.log("月份是："+month);
} else{
    console.log("输入月份的值正确。")
}

function employee(id,name) {
    this.id=id;
    this.name=name;
}
var emp=new employee(123,"admin");
employee.prototype.email="admin@huawei.com";
console.log("工号："+emp.id);
console.log("姓名："+emp.name);
console.log("邮箱："+emp.email);*/

//010,数组
/*var nums:number[]=[1,2,3,4];
console.log(nums[0]);
console.log(nums[3]);

var sites:string[]=new Array("baidu","google","taobao");
for(var i=0;i<sites.length;i++){
    console.log(sites[i]);
}

var multi:number[][]=[[1,2,3],[23,24,25]]
console.log(multi[0][0]);
console.log(multi[1][2]);*/

//011,元组，元素的数据类型可以不同
/*var mytuple=[10,"qiyu"];
console.log("改变前元组的元素个数："+mytuple.length);
mytuple.push("你好呀");
console.log("添加元素后元组的长度："+mytuple.length);*/

//012,联合类型
/*var val:string|number;
val=13;
console.log("数字为："+val);
val="Runoob";
console.log("字符串为："+val);*/

//013,接口
/*
interface IPerson{
    firstName:string,
    lastName:string,
    sayHi:()=>string
}

var custom:IPerson={
    firstName:"Tom",
    lastName:"Hanks",
    sayHi:():string=>{return "Hi there"}
};

console.log("custom对象");
console.log(custom.firstName);
console.log(custom.lastName);
console.log(custom.sayHi());

var employee:IPerson={
    firstName:"Jim",
    lastName:"Blacks",
    sayHi:():string=>{return "Hello!!!"}
};
console.log("employ对象：");
console.log(employee.firstName);
console.log(employee.lastName);
console.log(employee.sayHi());

//接口继承
interface Person{
    age:number
}
interface Musician extends Person{
    instrument:string
}
 var drummer=<Musician>{};
drummer.age=27;
drummer.instrument="Drums";
console.log("年龄："+drummer.age);
console.log("喜欢的乐器："+drummer.instrument);
*/

//014,类
/*class Car{
    engine:string;
    constructor(engine:string){
        this.engine=engine
    }
    disp():void{
        console.log("在函数中显示发动机型号："+this.engine)
    }
}

var obj=new Car("XXSSS");
console.log("读取发动机型号："+obj.engine);
obj.disp();*/
//类的继承
/*
class Shape{
    Area:number
    constructor(a:number){
        this.Area=a
    }
}

class Circle extends Shape{
    disp():void{
        console.log("圆的面积："+this.Area)
    }
}

var obj=new Circle(190);
obj.disp();
*/

//015，对象【键值对】
var sites={
    site1:"Qiyu",
    site2:"Lizzie",
    sayHello: function () {}
};
console.log(sites.site1);
console.log(sites.site2);
sites.sayHello=function () {
   console.log("hello"+sites.site1);
};
sites.sayHello();

```

### ts类型系统

相对于ES6来说，TS最大的改善就是增加了类型系统。

类型系统会对数据进行类型检查，以避免不必要的错误。

1，倘若已经定义了数据的类型，后面赋值时不符合便会报错；

2，未定义具体的数据类型，系统会根据用户的输入来判断数据类型

### ts前端服务

### ts后端服务
