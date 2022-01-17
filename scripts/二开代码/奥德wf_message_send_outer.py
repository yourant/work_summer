class WfMessageSendOuter(BasePrivateApiService):
    """
    HCM与泛微系统待办集成
    云函数名称 wf_message_send_outer
    云函数类型 动态openapi 便于重传
    事件定义: 
    {
        "add":"新增", # assign里面有一个参数category 当 5为抄送待办 一般不同步
        "finish":"同意",
        "reject":"拒绝",
        "cancel":"撤销"
    }
    泛微系统对 appName,modelName,modelId有强制校验一次待办,已办的这三个参数必须一致,如果发生改变就会出错,所以对于待办(add事件)这三个参数不做考虑,
    其他事件取泛微系统的那条待办的modelName,appName参数,因此modelName最好用流程定义的名称这个基本不会发生改变,
    台账模型 WfMessageSendOuter
    """

    def __init__(self, **kwargs):
        self.__description__ = "与泛微做待办集成"
        self.record_model = "WfMessageSendOuter"  # 台账模型(重传模型)
        self.local_host = "http://192.168.11.230"  # 人力系统的域名
        outer_host = "http://192.168.10.132:8089"  # 第三方系统域名
        self.outer_url = f"{outer_host}/rest/ofs/"  # 一般情况泛微接口都是这个
        self.map_key = "UserId"  # 与泛微约定好人员映射的本地字段 此处用人员模型弹性字段
        self.appName = "hcm"  # 泛微系统注册的异构应用名称
        self.version_dict = {
            1: "bill",
            2: "workflow_bill",
            3: "workflow_bill_v3"}  # 流程各个版本对应的场景可扩展当存在v4时便于修改
        self.method_dict = {
            "add": "ReceiveRequestInfoByJson",
            "finish": "ReceiveRequestInfoByJson",
            "reject": "ReceiveRequestInfoByJson",
            "cancel": "deleteUserRequestInfoByJson"}  # 对应泛微的api
        self.remark_dict = {
            "add": "0",  # 对应泛微待办
            "finish": "2",  # 对应泛微已办
            "reject": "2"  # 对应泛微已办
        }
        self.view_dict = {
            "add": "0",  # 未读
            "finish": "1",  # 已读
            "reject": "1"  # 已读
        }

    def execute(self, event, assign):
        self.log(f"{event}------{assign}")
        if event == "add" and assign.get("category") == 5:
            return "pass"  # 抄送一般不处理
        assign_id = assign.get("id")  # 本条待办任务的id
        submit_user_id = assign.get("submit_user_id")  # 发起人id
        executor_id = assign.get("executor_id")  # 接收人id
        record_id = self.create_record({
            "event": event,
            "submit_user_id": submit_user_id,
            "executor_id": executor_id,
            "assign_id": assign_id}).get("id")  # 创建一条记录到重传模型
        try:
            submit_user = self.get_employee_info(submit_user_id)  # 发起人信息详情
            executor = self.get_employee_info(executor_id)  # 接收人信息详情
            create_time = assign.get("create_time") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 代办任务生成时间
            business_info, inst_info, redirect_url = self.get_workflow_info(assign_id)
            wf_inst_id = inst_info.get("id")  # 流程实例id
            link = self.get_link(executor.get("mobile"), redirect_url)  # 单点链接
            executor_other_username = executor.get(self.map_key)
            if not executor_other_username:
                self.update_record(record_id, {"content": "接收人账号获取失败"})
                return "接收人账号获取失败"
            if event in ["add", "finish", "reject"]:
                submit_other_username = submit_user.get(self.map_key)
                # if not submit_other_username:
                #     self.update_record(record_id, {"content": "提交人账号获取失败"})
                #     return "提交人账号获取失败"
                context = {
                    "syscode": self.appName,
                    "pcurl": link,  # 点击代办跳转的url
                    "appurl": link,  # 点击代办跳转的url
                    "flowid": str(assign_id),
                    "requestname": inst_info.get('wf_inst_title'),
                    "workflowname": business_info.get('name'),
                    "nodename": assign.get("wf_name"),
                    "isremark": self.remark_dict.get(event),
                    "viewtype": self.view_dict.get(event),
                    "creator": submit_other_username,
                    "createdatetime": create_time,
                    "receiver": executor_other_username,
                    "receivedatetime": create_time,
                    "receivets": str(int(round(time.time() * 1000)))
                }
            else:
                context = {
                    "syscode": self.appName,
                    "flowid": assign_id,
                    "userid": executor_other_username
                }
            return self.push_to_outer(event, record_id, wf_inst_id, context)
        except Exception as e:
            self.update_record(record_id, {
                "content": json.dumps({"msg": str(e), "event": event, "assign": assign}, ensure_ascii=False)})
            return str(e)

    def push_to_outer(self, event, record_id, wf_inst_id, context):
        """推送给外部系统"""
        self.update_record(record_id, {
            "wf_inst_id": wf_inst_id,
            "param": json.dumps(context, ensure_ascii=False)})  # 修改记录的参数
        url = f"{self.outer_url}{self.method_dict.get(event)}"
        for i in range(3):
            try:
                response = requests.post(url, json=context)
                result = json.loads(response.content)
                if result.get("operResult") == "1":
                    self.update_record(record_id, {"status": True, "content": ""})
                    return True
                else:
                    self.update_record(record_id, {"content": json.dumps(result, ensure_ascii=False)})
            except Exception as e:
                self.update_record(record_id, {"content": str(e)})
        return False

    def get_link(self, executor_mobile, redirect_url):
        """获取单点地址,可以用其他方式 如个性化登录"""
        return "{}/oauth2/third/auth?client_id={}&redirect_uri={}&response_type=code&state={}&name={}&password={}&flag=veri".format(
            self.local_host,
            "oa_third_login",
            urllib.parse.quote(redirect_url),
            "oa_third_login",
            base64.b64encode(executor_mobile.encode()).decode("utf-8"),  # 让这个看上去像加密一样
            "****")

    def get_employee_info(self, employee_id):
        """获取人员详细信息"""
        return CustomerUtil.call_open_api("hcm.model.get", {"id_": employee_id, "model": "Employee"})

    def get_workflow_info(self, assign_id):
        """根据任务id 返回流程定义的信息 流程实例的信息 以及场景"""
        work_flow = CustomerUtil.call_open_api("workflow.get.wf.all", {"assignment_id": assign_id}).get("data", {})
        business_id = work_flow.get("wf", {}).get("business_id")
        version = CustomerUtil.call_open_api("workflow.business.version", {"business_id": business_id}).get("version")
        state = self.version_dict.get(version)  # 根据版本得到场景
        redirect_url = '/#/{}?wf_assignment_id={}&business_id={}'.format(state, assign_id,
                                                                         business_id)  # 免登陆单点后重定向地址next参数
        return work_flow.get("business", {}), work_flow.get("inst", {}), redirect_url

    def create_record(self, info):
        """新增至重传模型,记录台账,这与重传操作是关联一起的所以 加一个查询操作"""
        param = {"model": self.record_model,
                 "filter_dict": {
                     "assign_id": info.get("assign_id"),
                     "event": info.get("event")
                 }}
        result = CustomerUtil.call_open_api("hcm.model.list", param)["list"]
        if result:
            return result[0]
        info["status"] = False
        info["create_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return CustomerUtil.call_open_api("hcm.model.create", {"model": self.record_model, "info": info})

    def update_record(self, record_id, info):
        """回写状态,记录错误日志"""
        return CustomerUtil.call_open_api("hcm.model.edit",
                                          {"model": self.record_model, "info": info, "id_": record_id})

    def log(self, content, type=3):
        """
        日志记录
        :param content: 内容
        :param type: 2 异常 3 其他
        :return:
        """
        company_id = CustomerUtil.get_current_context().company.id
        category = self.__class__.__name__
        CustomerUtil.call_open_api(
            name="hcm.model.create",
            param={
                "model": "SyncOuterRecord",
                "info": {
                    "company_id": company_id,
                    "name": category,
                    "category": category,
                    "type": type,
                    "content": str(content),
                    "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )
