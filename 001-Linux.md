## Linux常用操作

> 祁玉  2019/7/11

### 基本命令

```
ls	#列出所有文件
pwd #列出当前路径
mkdir filename	#创建文件夹
rmdir filename	#删除文件夹
vim file.txt	#创建新文件
rm file.txt		#删除文件
cd directory	#改变路径到directory目录
cd ..			#回到上级目录
cp 1.txt ../a2  #向a2文件夹中复制1.txt
rm 2.txt ../a2  #将2.txt文件移到a2文件夹下
cat 1.txt		#在屏幕上输出文件内容
tail 1.txt		#倒着在屏幕上输出10行内容
tail -n 1.txt   #输出倒数n行的内容
```

![1562837199763](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562837199763.png)

![1562841321814](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562841321814.png)

### grep

正则匹配项，过滤出需要的输出

- ```
  ls|grep txt
  ```

  说明：列出所有的txt文件

  ![1562829744841](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562829744841.png)

- ```
  grep qwe *html
  ```

  说明：过滤出后缀是html，内容包含qwe的文件

  ![1562829465304](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562829465304.png)

- ```
  ps|grep 11
  ```

  说明：过滤出含有11的进程信息

  ![1562829610173](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562829610173.png)

### ps

显示当前进程的状态

```
ps -A//显示所有进程信息
ps -u root//显示root进程用户信息
ps -ef//显示所有命令
```

![1562830348854](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562830348854.png)

![1562830416324](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562830416324.png)

### netstat

监控TCP/IP网络的工具，用于显示各种网络相关信息，显示与IP、TCP、UDP和ICMP协议相关的统计数据，一般用于检查本机各端口的网络连接情况。

```
netstat -h//参数说明
netstat -anp//列出所有端口
netstat -antp//列出所有tcp端口
netstat -anup//列出所有udp端口
netstat -lnp//显示所有监听端口
netstat -ltnp//列出所有监听tcp的端口
netstat -lunp//列出所有监听udp的端口
netstat -lxnp//列出所有监听unix端口
netstat -anp|grep ssh//找出程序运行的端口【只有root才有权限】
netstat -anp|grep ':3306'//找出运行在指定端口的进程 【root】
netstat -s//显示所有端口的统计信息
```



### kill

kill是向进程发送信号的命令，前台进程可以使用Ctrl+C，后台进程使用kill命令终止，可以先使用ps、top等命令获得进程的PID，然后使用kill命令杀掉该进程。

```
kill pid//让程序正确退出
kill -15 pid//同上
kill -9 pid//异常进程的处理
```

### vim编辑器

vim是从vi发展出来的一个文本编辑器。

3种模式：命令模式、输入模式、底线命令模式

#### 命令模式

用户刚启动vim便进入命令模式，输入字符会被识别为命令而非字符，例如：

- i 切换到输入模式，
- x 删除当前光标处所所在的字符
- ：切换到底线命令模式

#### 输入模式

退出：ESC

#### 底线命令模式

首先，按：进入底线命令模式

常用:

​	w 保存文件

​    q  退出程序

​    wq  存储后退出

### shell脚本

```
1,进入编辑器  vim test.sh
2，编写 
   #!/bin/bash
   echo "Hello world"
3，运行
   chmod +x ./test.sh  #使脚本具有执行权限
   ./test.sh     #执行脚本
   【或者直接使用： sh test.sh】
   【sh -x test.sh  这里可以看执行的具体细节，便于调试】
```

![1562843149156](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562843149156.png)

变量

```bash
#!/bin/bash
##注释
a=1
b=10
sum=$[$a+$b]
echo "sum is $sum"

echo "please input a number:"
read x
echo "please input another number:"
read y
sum=$[$x+$y]
echo "The sum of the two numbers is: $sum"

```

![1562845224018](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562845224018.png)
