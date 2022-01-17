
由于钉钉同步近期出现大量问题，现给出优化方案


1. 去掉数据同步的单点登录逻辑， 直接获取access_token完成认证

新增 -》 


修改后数据同步逻辑一定要清楚

修改 -》


删除的筛选逻辑一定要考虑清楚， 

{
  "default_filter_dict":{
    "job_info.is_primary": true   # 这个过滤有点疑惑， 不是主任职就删除
  },
  "query_index": [
    {
      "key": "operate_time",
      "operate_time": {
        "op": ">=",
        "value": "'{OPERATE_TIME}'"
      }
    },
    {
      "key":"job_info_operate_date",
      "job_info.begin_date": {
        "op": "=",
        "value": "'{OPERATE_DATE}'"
      }
    },
    {
      "key":"job_info_operate_time",
      "job_info.operate_time": {
        "op": ">=",
        "value": "'{OPERATE_TIME}'"
      }
    }
  ],

默认模板文件配置

删除 -》 



