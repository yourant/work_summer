# 数据导入

mysql -uroot -p

create database lmz;

use lmz;

source abc.sql


# 数据导出
mysqldump -h主机名 -P端口 -u用户名 -p密码 --database 数据库名 > 文件名.sql



数据导入 

-f 解决sql执行中报错, 

mysql -h localhost -u root  -f database < D:/filename.sql


# mysql定位慢sql查询
```
1.开启慢查询日志功能很简单，在my.cnf 配置文件中，加入以下参数：

slow_query_log=1  #启用慢查询

slow_query_log_file=mysql.slow  #慢查询的存储位置

long_query_time=2  #指定慢查询的记录时间比如这里大于2s sql 会记录下来

2.当数据库的连接数很高时，此时注意，可通过监控软件观察时间点，然后把这一时间点的日志截取出来分析

sed -n '/#Time:130227 14:26:45/,/end/p' mysql.slow >slow.log

3.通过mysqldumpslow 命令取出耗时最长的前10条慢sql 进行分析

#mysqldumpslow -s t -t 10 slow.log

```