# insert
> insert into table (column1, column2) values (value1, value2)

# update
> update table set (column1=value1) where id = 1


# delete
> delete from table where id = 1


# select 

```
select id from user where id = 2
select id from user where name like '刘%'

select gender, count(gender) from user group by gender

```

# explain

```
可以输出sql 执行耗时
explain select id from user where id = 1
```

> 柔性事务和钢性事务, 雪花算法生成id, 
