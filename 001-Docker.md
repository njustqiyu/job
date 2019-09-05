## Docker常用操作

> 祁玉  2019/7/12

[Docker学习]: https://yeasy.gitbooks.io/docker_practice/

### 1，docker基本概念

Docker包括三个基本概念：镜像（Image）、容器（Container）、仓库（Repository）

例子：在本地准备材料建造一套房子，打算在外地建一个一模一样的。将盖好的房子复制一份，做成镜像，放在背包中，到了外地就复制一下这个镜像，拎包入住，OK---。

上述例子中，

​	镜像就是Docker镜像；

​	背包就是Docker仓库；

​	在外地，用魔法造的房子就是Docker容器

#### 镜像

Docker镜像是一个特殊的文件系统，除了提供容器运行时所需的程序、库、资源、配置等文件外，还包含了一些为运行时准备的一些配置参数（如匿名卷、环境变量、用户等）。镜像不包含任何动态数据，其内容在构建之后也不会被改变。

镜像只是一个虚拟的概念，其实际体现并非由一个文件组成，而是由一组文件系统组成，或者说，由多层文件系统联合组成。

镜像在构建时会一层层构建，前一层是后一层的基础。分层存储使得镜像的复用、定制变得更容易。甚至可以在之前构建好的镜像的基础上添加自己的需求，以构建新的镜像。

#### 容器

镜像和容器的关系就是“类”和“实例”的关系。

镜像是静态的定义，容器是镜像运行时的实体。

容器可以被创建、启动、停止、删除、暂停。

容器的实质是进程，其运行在一个隔离的环境里。容器运行时，是以镜像为基础层，在其上创建一个当前容器的存储层。

容器存储层的生存周期和容器一样，容器不应该向其存储层写入任何数据

#### 仓库

镜像构建完成后，可以很容易在当前宿主上运行，但若在其他服务器上使用这个镜像就需要一个集中的存储、分发镜像的服务【即Docker Registry】。

一个Docker Registry中可以包含多个仓库，每个仓库可以包含多个标签。

<仓库名>:<标签>    ubantu:16.04  

### 2，docker启动

```
sudo service docker start
#注意，这里需要使用root权限登录
```

![1562919398837](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562919398837.png)

```
docker run hello-world
```

![1562920065217](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562920065217.png)

### 3，docker镜像

获取镜像、创建镜像

#### 安装镜像

安装常用的镜像有两种方法：pull  +  dockerfile

1. 方法一：

   ```
   docker search tomcat  #在Docker Hub上查找镜像
   docker pull tomcat    #拉取官方的镜像
   docker image|grep tomcat #查看是否下载成功
   ```

   ```
   docker run --name tomcat7 -p 8087:8080 -v $PWD/test:/usr/local/tomcat/webapps/test
   ```

   运行，容器名称：tomcat7

   **-p 8087:8080：**将容器的8080端口映射到主机的8087端口

   **-v $PWD/test:/usr/local/tomcat/webapps/test：**将主机中当前目录下的test挂载到容器的/test

   可以在浏览器查看结果：

   ![1563240721573](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563240721573.png)

   

2. 方法二：

   使用Dockerfile的方式构建

#### 获取镜像

```
root@SZX1000519923:/home/q50004926/dockerQ# docker run -it --rm \
> ubuntu:18.04 \
> bash
root@5f2ad8695272:/# cat /etc/os-release
```

`docker run` 运行容器

`-it` 包含两个操作，`-i`:交互式操作 `-t`终端 

`--rm` 容器退出后将其删除

`ubantu:18.04` 表示使用 `ubantu:18.04` 镜像作为基础来启动容器

`bash` 具体命令

`\`表示可以进行换行输入

最后，使用`exit`退出

![1562920989962](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1562920989962.png)

#### 创建镜像

#### 列出镜像

```
docker image ls
或者docker images
```

![1563153007434](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563153007434.png)

说明：

这里列出了 仓库名、所占用的空间、标签、镜像ID、创建时间

**镜像ID**是镜像的唯一标识，一个镜像可以对应多个标签

这里标识的镜像占用的空间与Docker Hub上的不同，原因在于Docker Hub显示的体积是压缩后的体积，`docker image ls` 显示的是镜像下载到本地后展开的大小。

### 4，删除本地镜像

```
docker image rm <镜像>
#其中<镜像>可以是：镜像Id、镜像名、镜像摘要
docker image ls --digests  #获取镜像摘要
```

![1563154208601](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563154208601.png)

注意事项：

有的时候直接使用上述语句是不能删除对应的镜像的，原因是：

```
[yaxin@ubox ~]$docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
eg_sshd             latest              ed9c93747fe1        45 hours ago        329.8 MB
CentOS65            latest              e55a74a32125        2 days ago          360.6 MB
[yaxin@ubox ~]$docker rmi ed9c93747fe1
Untagged: ed9c93747fe16627be822ad3f7feeb8b4468200e5357877d3046aa83cc44c6af
[yaxin@ubox ~]$docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
<none>              <none>              ed9c93747fe1        45 hours ago        329.8 MB
CentOS65            latest              e55a74a32125        2 days ago          360.6 MB

[yaxin@ubox ~]$docker rmi ed9c93747fe1
Error: image_delete: Conflict, ed9c93747fe1 wasn't deleted
2014/03/22 15:58:27 Error: failed to remove one or more images
```

这里可以看到，image并未被删除，而是删除了其对应的TAG，再次执行则会报错。

这里是因为该镜像被某个容器在使用，若不将对应的容器删除，image就不能被删除。

可以，1）通过 `docker ps` 查看正在运行的容器，或者`docker ps -a` 查看运行过的容器

![1563155790275](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563155790275.png)

2）使用 `docker rm 容器ID`,若删除不了这说明该容器在运行中，先使用命令`docker stop 容器ID`

![1563170104959](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563170104959.png)

可以参考：[删除本地镜像](http://yaxin-cn.github.io/Docker/how-to-delete-a-docker-image.html )

### 5，镜像构成 commit

```
docker run --name webserver -d -p 80:80 nginx

```

使用该命令会用 `nginx` 镜像启动一个容器，命名为 `webserver`，可以使用浏览器进行访问：本地使用http://localhost, 我这里使用的虚拟机，换成具体的地址：http://100.101.58.110 ,结果如下:

![1563157807179](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563157807179.png)

可以对这个页面进行修改：

```
root@SZX1000519923:/home/q50004926/dockerQ# docker exec -it webserver bash
root@0d60efd5254b:/# echo '<h1>hello,Qiyu!</h1>'>/usr/share/nginx/html/index.html
root@0d60efd5254b:/# exit
exit

```

![1563158691651](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563158691651.png)

可以使用 `docker diff webserver` 查看具体的改动

对于这种变化，可以使用 `docker commit` 进行保存，

**但是，但是**，这种操作是不推荐的：一切的操作只有制作镜像的人知道进行了哪些改动（抑或ta自己都忘记啦）；维护很不方便。

这里只是理解一下，镜像的制作其实就是在存储层上进行的一些改变，而实际操作不会选择这种方法。

### 6，dockerfile定制镜像

镜像的定制实际上就是制定每一层所添加的配置文件。倘若将每一层的修改、安装、构建、操作的命令都写入一个脚本，用一个脚本来构建，这个脚本就是Dockerfile。

使用Dockerfile定制镜像的步骤：

1. 在一个空白目录中，创建一个文本文件，命名 `Dockerfile`

   ```
   mkdir mynginx
   cd mynginx
   vim Dockerfile
   #其中，Dockerfile文件的内容是：
   FROM nginx
   RUN echo '<h1>Hello,Docker!</h1>' > /usr/share/nginx/html/index.html
   
   ```

   说明：

   FROM 是指定基础镜像

   RUN 执行命令

2. 在 `Dockerfile` 文件所在目录下执行以下操作：

   ```
   docker build -t nginx:v3 .
   
   ```

   ![1563171493773](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563171493773.png)

   注意：后面有个 `.`，表示当前的上下文路径

   > docker build的工作原理：Docker在运行时分为Docker引擎（服务端守护进程）和客户端工具。表面上我们好像是在本机执行docker各种功能，实际上一切都是在使用远程调用形式在服务端（Docker引擎）完成。那如何才能让服务端获得本地文件呢？所以，在build时，用户需要指定构建镜像上下文的路径，在得知这个路径后，会将路径下的所有内容打包，然后上传给Docker引擎。

3. 运行

   ```
   docker run --name w3 -d -p 83:80 nginx:v3
   
   ```

   ![1563173242599](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563173242599.png)

### 7，Dockerfile指令详解

#### RUN

作用：执行命令行命令

两种格式：shell格式  exec格式

1， `RUN <命令>`

```
RUN echo '<h1>Hello,Docker!</h1>' /usr/share/nginx/html

```

2，RUN ["可执行文件"，"参数1"，"参数2"]

```
RUN apt-get update
RUN apt-get install -y gcc libc6-dev make wget

```

注意：Dockfile中每一个指令都会建立一层，有些一样目的的操作是没有必要分别都写一层的。

### 8，操作容器

启动、终止、进入

#### 查看

```
docker container ls
#正在运行的容器，或者 docker ps

```

![1563177614883](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563177614883.png)

```
docker container ls -a
#查询运行过的容器，或者 docker ps -a

```

![1563177654657](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563177654657.png)

#### 启动

方式有两种：

1. 基于镜像新建一个容器并启动

   ```
   docker run ubuntu:18.04 /bin/echo 'hello world'
   
   ```

2. 将在终止状态的容器重新启动

   docker ps -a 可以查看执行过的容器

   docker ps 正在执行的容器

   docker container start 容器id

#### 终止

```
docker container stop 容器ID

```

#### 进入

1. 进入后台 -d

   ```
    docker run -d ubuntu:18.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
   
   ```

   加入-d参数后，程序转入后台运行，可以通过以下方式查看：

   ```
   docker container logs 容器ID
   
   ```

2. attach

   ```
   docker run -dit ubuntu:18.04
   docker attach 容器ID
   #exit退出，这样会导致容器停止
   
   ```

3. exec

   ```
   docker run -dit ubuntu:18.04
   docker exec -it 容器ID bash
   #exit退出，不会导致容器停止
   
   ```

总结：一般使用exec，因为这个在exit退出编辑时，容器的状态不会受影响而停止。

![1563177510058](C:\Users\q50004926\AppData\Roaming\Typora\typora-user-images\1563177510058.png)

这里，上面一条使用的exec，exit之后容器还在；

下面一条使用的attach，exit之后容器也退出啦。























































