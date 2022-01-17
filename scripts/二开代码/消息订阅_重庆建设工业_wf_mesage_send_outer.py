class OtherExtendPlugin(object):
    """
    其他类别云函数
    """

    host_name = 'http://10.96.255.32'

    def test(self, event, assign):
        """
        测试执行方法
        """
        """
        {
    "event": "add",
    "assign": {
        "id": 8014795,
        "executor_id": 2176261,
        "submit_user_id": 2176261
    }
}"""
        return self.execute(event, assign)

    oa_user_name = "HCM"
    oa_password = '123456'

    def __init__(self):
        self.host_name = 'http://10.96.255.32'
        self.cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_str = None
        self.model_name = "OAMessageSync"
        self.link_url = None

    def execute(self, event, assign):

        self.get_access_token()
        assignment_id = assign['id']
        wf_all_data = CustomerUtil.call_open_api("workflow.get.wf.all", {
            "assignment_id": assignment_id
        })
        business_id = wf_all_data["data"]["wf"]["business_id"]
        ver_info = CustomerUtil.call_open_api("workflow.business.version", {
            "business_id": business_id
        })
        if ver_info["success"]:
            business_version = ver_info["version"]
            state = "workflow_bill_v3" if business_version == 3 else "workflow_bill"  # 不考虑v1
            self.add_str = '/#/{}?wf_assignment_id={}&business_id={}'.format(state, assignment_id, business_id)
            self.handle_state(event, assign, wf_all_data, True)
        else:
            self.handle_state(event, assign, wf_all_data, False)

    def handle_state(self, event, assign, wf_all_data, is_need_push=True):
        if wf_all_data["success"]:
            executor_id = assign["executor_id"]
            executor = getEmpCardJson(executor_id)
            executor_number = executor["number"]
            # executor_number = "hcm"
            inst_data = wf_all_data['data']['inst']
            wf_inst_title = inst_data['wf_inst_title']
            submit_user_id = inst_data["submit_user_id"]
            submit_user_info = getEmpCardJson(submit_user_id)
            if event == "add":
                if self.add_str:
                    self.link_url = self.quote_url(executor_id)
                try:
                    client = Client("http://10.96.200.24/seeyon/services/messageService?wsdl")
                    result = client.service.sendMessageByLoginName(token=self.token,
                                                                   loginNames=executor_number, content=wf_inst_title,
                                                                   url=self.link_url)
                    logging.info(result)
                except Exception as e:
                    logging.info(e)

        else:
            raise errors.DATA_RULE_ERROR.description("请检查流程数据！")

    def quote_url(self, executor_id):
        _url = "{}/api/auth/login_by_sso?sso=customer_sso&next={}&encrypt_p={}"
        url = _url.format(
            self.host_name,
            urllib.parse.quote(self.add_str),
            str(uuid.uuid3(uuid.NAMESPACE_DNS, str(executor_id))))
        logging.info(url)
        return url

    def log(self, log_content):
        # if not enabled:
        #     return
        log_info = {
            "log_type": to_unicode('sxy_test'),
            "create_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "content": str(log_content)
        }
        CustomerUtil.call_open_api("hcm.model.create", {"model": "dynamic_log", "info": log_info})

    def get_access_token(self):
        client = Client("http://10.96.200.24/seeyon/services/authorityService?wsdl")
        try:
            result = client.service.authenticate(userName="service-admin", password="123456")
            self.token = result.id
        except Exception as e:
            logging.info(e)

    def get_fields(self, field_list):
        result_list = []
        for item in field_list:
            if item.find(".") == -1:
                result_list.append({"field": [item], "key": item})
            else:
                f_list = item.split(".")
                result_list.append({"field": f_list, "key": item})
        return result_list
