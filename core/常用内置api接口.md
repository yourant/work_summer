## 常用接口
/server/redis

查看客户端版本
/client/version
/server/version

/login/header
查看登录的请求头 Host参数， 我们会使用Host 参数切割第一个.前的字符串作为公司的domain，然后去数据库搜索对应的公司

/kibana

查看model
/#/common_model_list?model=
查看对象
/#/hcm_model_viewer/base?id=

/api

hcm.model.list

查看定时任务状态, 直接请求即可
celery.status

执行sql 查看数据库数据
wf.db.query

执行批量删除
hcm.model.remove.batch

celery 定时任务控制器, 可以终止任务
deploy.agent.celery.control.operate
{
  "operate": "revoke",
  "任务id"
}
可以在 celery.app.control 中查看支持的方法


测试消息发送

api/message.send.message

{
  "msglist": [
    {
     "sender": 3002581,
     "to": 3002581,
     "company_id": 1375,
     "msg_type": null,
     "content": "测试消息2",
     "state": "message"
    }]
}

{
  "params": {
    "employee_other_depart_state": "abcd",  # 兼职场景
    "extra_property": {
      "state" : "bbc"  # 主场景
    }
  }
}

https%3A//work.hcmcloud.cn/authorizer_pc_auth%3Fredirect%3Dhttps%253A//inspur.hcmcloud.cn/login%253Fv%253D1629450853718%2526next%253D%25252F%252523%25252Findex%2526app_type%253Dservice%2526sso%253Dwwx_work%2526i


https://inspur.hcmcloud.cn/login?func=SSO_BIND&sso=wwx_work&sso_id=LiuMingZhe&app_id=ww6875a3f294efe834&mode=GETCODE&next=%2F%23%2Findex&app_type=service&v=1629450924261.4155


140282524136448 未成功登录的


elastic

hcmcloud_2018


https://open.weixin.qq.com/connect/oauth2/authorize?appid=wwc7e707a7f4bc9365&redirect_uri=http%3A%2F%2Fhr.whucg.cn%3A8888%2Flogin%3Fsso%3Dplatform_6f67391c0e140c25a5192c242689bc9524c0dbd2%26next_stage%3Drequest_1%26is_only_sso%3D1&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect