看foundation中的代码
主体是一个baseModel方法
里面集成了许多基础方法

inner_json(self, fields=None):
将fields转换为字典返回


json(self, fields): 和
inner_json一样

get_datetime_field_str

get_date_field_str


表之间没有直接关联关系（没有使用外键关联）， 避免删除时出现问题
在代码层面实现关联查询。


任务项：
学习视频

1. json 视频
```

list元数据配置
元数据配置， is_blur 是否支持模糊搜索， 可以配置多个字段支持模糊搜索
例如姓名， 和编号可以都支持模糊搜索， 那在搜索框就可以使用这两个字段来模糊搜索
sequence 配置，就是在列表中的排序
width： 设置长度
field： ["gander"]
name:
key
meta_disabled: 
hide

info 元数据配置

groups 创建时展示的是info元数据配置 可以实现分组，把字段分块


employee人员

salary
```


2. 弹性模型

```
创建弹性模型 系统设置-》扩展管理 -》 对象管理 -》 新增


给弹性模型创建弹性字段， 在指定mask 时， mask的数据结构为列表
[
    {"key": 0,
    "name": "优秀"}
]

groups:  [
        {
            "field_list": [
                "name",
                "nationality",
                "mobile",
                "id_type",
                "identity_card"
            ],
            "key": "main",
            "label": "基本信息"
        },
        {
            "field_list": [
                "action_id",
                "action_reason_id",
                "begin_date",
                "position_id",
                "employee_category_id",
                "position_status_id",
                "gender"
            ],
```

3. 流程助理
4. 预警


在后台完成列表基本增删改查玩玩看


