celery 配置

celery 4.4
redis 作为broker 和 backend


遇到的问题 发布一个任务， 被多个worker 重复执行


解决方案 
1. 采用 rabbitmq 作为broker

2. 在执行时加锁 通过任务传参 作为 redis 的key，给key 设置过期时间， 在任务函数执行时检查 key是否存在，然后判断继续执行还是直接返回

保证了 任务不被重复执行
