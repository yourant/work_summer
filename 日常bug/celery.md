# 解决celery中的同一个task 被重复执行

celery 的定时任务功能 bug

在celery 分布式消息队列中, 某个task被worker拿到并且执行时, 没有及时更新task 状态,导致其他worker 也
拿到了该task, 导致了 同一个任务多次执行

在异步任务中加锁，可以借助redis添加锁，在执行实际的业务逻辑前先看看有没有加锁，如果有锁， 则跳过， 如果没有
则先加锁，然后执行， 完成后释放锁，通过锁, 

# 实现任务延迟执行

apply_async 方法 支持 countdown参数, 指定多少秒之后执行


# 队列堵了

发现报错 celery couldn't apply scheduled xxxx connection reset by peer

重启服务后 未执行的 task 会被执行, 可能会累积很多历史待执行定时任务, 在重启时被批量执行

所以在重启时, 一定要先清理broker, 可以使用 redis flushdb, flushall等命令来清理broker

也可以使用 celery purey 来清理任务

<!-- 1. 所以应该先停止服务, 
2. 然后清理brokers, 
3. 然后启动

也可, 可以先使用
celery purey 清理当前 celery 任务, 然后重启系统

重启后清理, 可能会导致 -->
需求问题:


在消息订阅功能中, 需要设置请求超时时间, 由于可能会产生大量的外部请求, 而每一个外部请求都可能会超时, 就会导致任务阻塞, 所以需要给请求设置timeout

否则可能会导致队列堵塞







