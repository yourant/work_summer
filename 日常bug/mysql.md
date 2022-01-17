数据导入

mysql -uroot -p

create database lmz;

use lmz;

source abc.sql


数据导出
mysqldump -h主机名 -P端口 -u用户名 -p密码 --database 数据库名 > 文件名.sql



数据导入 

-f 解决sql执行中报错, 

mysql -h localhost -u root  -f database < D:/filename.sql
