```
完成 给自定义的模型 设置按钮的功能， 查看foundation.py  中的 get_data_list, 

get_data_count, create_data, 

前端 dataservice.JS 文件中定义了详细的取数方法， 例如callHcmOpenWebSocket

base_crud_service.js  也定义了通用的 api 调取方法， 在自定义controller时，需要先初始化
let CRUDService = BaseCRUDService.getModelService('Announce');

指定model， 然后就可以直接使用
editItem等方法 

如果是自定义的api， 则前端的传参和后端的函数形参是一致的， 只是后端会多一个notify参数


其他默认操作orm的方法在foundation 中查看， 也可以在对应models中自定义操作方式


select
将socket 放到队列里， 当有对应的事件被调用， 会遍历队列逐一去匹配

由于遍历的开销大， 所以规定了select 的最大监听数量， 默认是1024


poll 和 select 没有本质区别， 只是将存放socket 的地方由 队列变成了 链表，
而链表没有长度限制， 


poll

epoll的区别

```