# 环境安装

安装 mysqlclient 的时候
依赖
libmysqlclient-dev
libssl-dev

安装libssl-dev 时报错，  依赖libssl

安装libssl 报错 已存在其他版本的libssl

将其他版本libssl 卸载
sudo apt remove libssl

此时可能会有卸载不全的情况

sudo apt autoremove

sudo rm -rf /etc/apt/apt.conf.d/20snapd.conf

我刚电脑死机，重启之后docker镜像全被删了, 其实没有被删除， 只是重启时， 可能选择了修改引擎，然后修改了镜像文件的读取地址， 

搜索DockerDesktop.vhdx

# 后端部署
```
后端环境安装，代码运行
配置好本地config

初始化表和数据
执行 python adjusttablestructure.py

执行 python application.py

执行 python applicatio.py  worker 启动celery
```
# 前端部署
```
安装依赖，和包
nodejs
npm
yarn
node-sass

执行 yarn install
执行 yarn run init
执行 yarn run dev-hot
```










