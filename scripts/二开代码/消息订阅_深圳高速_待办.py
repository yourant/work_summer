class Handle(object):
    """
    测试用例
{
    "event": "add",
    "assign": {
        "id": 7080076,
        "executor_id": 2202015,
        "submit_user_id": 1908855,
        "create_time": "2020-08-14 17:38:20"
    }
}
    """

    def __init__(self):
        self.host_name = 'https://hr.sz-expressway.com'
        self.task_model_name = 'Gtasks'
        self.cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_str = None
        self.link_url = None

    def execute(self, event, assign):
        self.log("event:{}, assign:{}".format(event, assign))
        assignment_id = assign['id']
        wf_all_data = CustomerUtil.call_open_api("workflow.get.wf.all", {
            "assignment_id": assignment_id
        })

        business_id = wf_all_data["data"]["wf"]["business_id"]
        ver_info = CustomerUtil.call_open_api("workflow.business.version", {
            "business_id": business_id
        })
        if ver_info["success"]:
            # 具体流程审批页面
            # business_version = ver_info["version"]
            # state = "workflow_bill_v3" if business_version == 3 else "workflow_bill"  # 不考虑v1
            # self.add_str = '/#/{}?wf_assignment_id={}&business_id={}'.format(state, assignment_id, business_id)

            # 改为待办列表页面
            self.add_str = '/#/workflow_center/pending'
            self.handle_state(event, assign, wf_all_data)
        else:
            self.handle_state(event, assign, wf_all_data, False)

    def handle_state(self, event, assign, wf_all_data, is_need_push=True):
        if wf_all_data["success"]:
            assign_category = assign.get('category')
            # 特殊处理，当抄送时候，不发送给oa
            if assign_category and str(assign_category) == '5':
                pass
            elif event == "add":
                self.handle_add(assign, wf_all_data, is_need_push)
            elif event == "finish":
                self.handle_finish(assign, wf_all_data, is_need_push)
            elif event == "reject":
                self.handle_reject(assign, wf_all_data, is_need_push)
            elif event == "cancel":
                self.handle_cancel(assign, wf_all_data, is_need_push)
        else:
            raise errors.DATA_RULE_ERROR.description("请检查流程数据！")

    def create_task_info(self, info):
        """
        创建待办列表数据
        :param info:
        :return:
        """
        return CustomerUtil.call_open_api('hcm.model.create', {
            "model": self.task_model_name,
            "info": info
        })

    def update_task_info(self, assignment_id, update_info):
        """
        根据待办任务id来修改弹性模型数据
        :param assignment_id:
        :param update_info:
        :return:
        """
        info_list = CustomerUtil.call_open_api('hcm.model.list', {
            "model": self.task_model_name,
            "filter_dict": {
                "assignment_id": assignment_id
            },
            "extra_property": {
                "only_list": True,
                "fields": [{"field": ["id"], "key": "id"}]
            }
        })['list']
        if not len(info_list):
            return
        id_ = info_list[0]['id']
        info = CustomerUtil.call_open_api('hcm.model.get', {
            "model": self.task_model_name,
            "id_": id_
        })
        info.update(update_info)
        return CustomerUtil.call_open_api('hcm.model.edit', {
            "model": self.task_model_name,
            "id_": id_,
            "info": info
        })

    def handle_add(self, assign, wf_all_data, is_need_push=True):
        """
        新的待办任务
        :param assign:
        :param wf_all_data:
        :param is_need_push:
        :return:
        """
        assignment_id = assign['id']
        executor_id = assign["executor_id"]
        submit_user_id = assign["submit_user_id"]
        create_time = assign['create_time']
        executor = getEmpCardJson(executor_id)
        submit_user = getEmpCardJson(submit_user_id)
        inst_data = wf_all_data['data']['inst']
        wf_name = inst_data['wf_name']
        wf_inst_title = inst_data['wf_inst_title']
        if self.add_str:
            self.link_url = self.quote_url(executor.get("number"))

        # 创建待办数据到待办同步台账
        self.create_task_info({
            "assignment_id": assignment_id,
            "status": 1,
            "executor_id": executor_id,
            "submit_user_id": submit_user_id,
            "create_time": create_time,
            "wf_name": wf_name,
            "wf_inst_title": wf_inst_title,
            "link_url": self.link_url,
            "update_time": self.cur_time,
            "note": None if self.link_url else "请检查流程版本！"
        })

        if is_need_push:
            # 推送数据
            data = {
                "appName": "HR",
                "modelName": wf_name,
                "modelId": assignment_id,
                "subject": wf_inst_title,
                "link": self.link_url,
                "type": 1,  # 1：审批类待办、2：通知类待办
                "key": None,
                "param1": None,
                "param2": None,
                "targets": json.dumps({"LoginName": executor.get("number")}),
                "createTime": create_time,
                "docCreator": json.dumps({"LoginName": submit_user.get("number")}),
                "level": None,  # 1：紧急、2：急、3：一般
                "extendContent": None,
                "others": None
            }
            self.push('sendTodo', data)

    def handle_finish(self, assign, wf_all_data, is_need_push=True):
        """
        完成待办任务
        :param assign:
        :param wf_all_data:
        :param is_need_push:
        :return:
        """
        assignment_id = assign['id']
        executor_id = assign["executor_id"]
        executor = getEmpCardJson(executor_id)
        inst_data = wf_all_data['data']['inst']
        wf_name = inst_data['wf_name']

        self.update_task_info(assignment_id, {
            "status": 2,
            "update_time": self.cur_time
        })
        if is_need_push:
            data = {
                "appName": "HR",
                "modelName": wf_name,
                "modelId": assignment_id,
                "optType": 1,  # 1：表示设待办为已办操作、2：表示设置目标待办所属人为已办操作
                "key": None,
                "param1": None,
                "param2": None,
                "type": None,  # 1：待审、2：待阅、3：暂挂
                "targets": json.dumps({"LoginName": executor.get("number")})
            }
            self.push('setTodoDone', data)

    def handle_reject(self, assign, wf_all_data, is_need_push=True):
        """
        不同意待办任务处理
        :param assign:
        :param wf_all_data:
        :param is_need_push:
        :return:
        """
        self.handle_finish(assign, wf_all_data, is_need_push)

    def handle_cancel(self, assign, wf_all_data, is_need_push=True):
        """
        撤销待办任务
        :param assign:
        :param wf_all_data:
        :param is_need_push:
        :return:
        """
        self.handle_finish(assign, wf_all_data, is_need_push)

    def quote_url(self, name):
        _url = "{}/oauth2/third/auth?client_id={}&redirect_uri={}&response_type=code&state={}&name={}&flag=veri"
        url = _url.format(self.host_name, "oa_third_single_login", urllib.parse.quote(self.add_str),
                          "oa_third_single_login", name)
        return url

    def push(self, interface_name, data):
        self.log("interface_name:{}, data:{}".format(interface_name, data))
        # push_url = "http://192.168.6.61/sys/webservice/sysNotifyTodoWebService?wsdl"
        push_url = "http://ekp.sz-expressway.com/sys/webservice/sysNotifyTodoWebService?wsdl"
        client = Client(push_url)

        response = None
        if interface_name == 'sendTodo':
            response = client.service.sendTodo(data)
        elif interface_name == 'setTodoDone':
            response = client.service.setTodoDone(data)

        self.log("notifyTodoAppresponse:{}".format(response))
        if response.returnState == 1:  # 0：未操作、1：操作失败、2：操作成功
            self.log(response.message)
            raise Exception(response.message)
        else:
            return {"success": True, "msg": "操作成功！"}

    def log(self, log_content, enabled=True):
        if not enabled:
            return
        log_info = {
            "log_type": to_unicode('mc_test'),
            "create_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "content": str(log_content)
        }
        CustomerUtil.call_open_api("hcm.model.create", {"model": "dynamic_log", "info": log_info})

    def test(self, **param):
        return self.execute(**param)
