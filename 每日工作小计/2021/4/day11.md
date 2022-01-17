## 关于代码提交
- 两周作为一个迭代， 迭代第一周，需求代码可以直接合入release， 第二周，需要经过 测试同意，再合入release
- 紧急需求可以直接合入master， 需要发邮件申请

- develop分支随时都可以合入，但是需要经过自测，保证代码质量
- 直接在jira上创建分支， 


## 关于配置
1. 系统设置配置公司级模板， 可以实现自定义 后端的json 文件

2. 可以借助模板配置，实现自定义视图，通过对，对象管理的不同类型的布局进行修改
改变布局元数据的state， 可以指定页面启用不同的 元数据配置文件，从而实现自定义页面


## 手动运行任务

执行路径， 调用hcm.periodic.task.run接口， hcm.periodic.task的run 方法

调用定时任务指定的 路径， 去执行对应方法，异步执行

在对应方法中， 解析预置的传参， 
```
{
    "services": ["person_new"],
    "consumer": "work_inner",
    "company_id": 169,
    "param": {
        "filter_dict": {
            "name": "胡栋栋"
        }
    }
}
```
services， Service类中对应的func

consumer， 对应的Service  __third_type__，可以定位到Service，然后对Service进行初始化，
此时会检测公司是否有配置对应的 app_id, 也就是需要在第三方数据同步中配置一下,
获取需要同步的数据， 主要使用 query_str来查询，查询更新时间范围内的数据

获取到数据， 将数据格式化，校验配置中的必填字段， 且填充 sort_order， 如果有必填字段为空，则该条数据不同步

然后对Service进行初始化，

company_id: 过滤信息

pararm 过滤信息