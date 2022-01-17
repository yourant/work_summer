class SyncInstance(ThirdBaseUpdateObject):
    """
    基类代码路径:core.extend.third.base.service_sync.ThirdBaseSyncObject
    wiki:http://wiki.hcmcloud.cn/pages/viewpage.action?pageId=2425690
    """

    __third_type__ = "third_to_group"
    __description__ = "数据同步示例"
    __biz_model__ = dict(
        person_new="Employee",
        person_del="Employee",
        person_edit="Employee",
        person_sync="Employee",
        org_new="DepartmentHistory",
        org_sync="DepartmentHistory",
        org_edit="DepartmentHistory",
        org_del="DepartmentHistory",
        org_reverse="DepartmentHistory",
        job_information_sync="JobInformation",
        job_information_edit="JobInformation",
        job_information_new="JobInformation"
    )
    __token__ = "hcm27537b298857d472a6cda6dedd18b020bb21277d"
    __headers__ = {
        'Content-Type': "application/json",
        'OuterToken': "hcm27537b298857d472a6cda6dedd18b020bb21277d",
    }
    __server_url__ = "https://hcm.cggc.cn/api_outer_sync"

    __job_info_new_ = "{}/third_job_info_new_new?outer_token={}".format(__server_url__, __token__ )
    __job_info_edit_ = "{}/third_job_info_edit_new?outer_token={}".format(__server_url__,__token__)
    __job_info_sync_ = "{}/third_job_info_sync_new?outer_token={}".format(__server_url__,__token__)
    __job_info_reverse_ = "{}/third_job_info_reverse_new?outer_token={}".format(__server_url__,__token__)

    def __init__(self, context, is_record):
        super(SyncInstance, self).__init__(context=context, is_record=is_record)

    def job_information_new(self, filter_dict=None, extra_property=None, **kwargs):
        """
        SYNC: 新增任职
        """
        try:
            self.record.info("job_information_new", kwargs)
            info = self.get_sync_job_info_new(kwargs) or {}
            if not info.get("sync_type"):
                return
            if info.get("sync_type") == "create":
                self.call_api(self.__job_info_new_, info)
            elif info.get("sync_type") == "edit":
                self.call_api(self.__job_info_edit_, info)
        except Exception as e:
            self.record_new("job_information_new", "data:{};error:{}".format(kwargs,e))

    def job_information_edit(self, filter_dict=None, extra_property=None, **kwargs):
        """
        SYNC:修改任职
        """
        try:
            self.record.info("job_information_edit", kwargs)
            info = self.get_sync_job_info_edit(kwargs) or {}
            if not info.get("sync_type"):
                return
            if info.get("sync_type") == "edit":
                self.call_api(self.__job_info_edit_, info)
        except Exception as e:
            self.record_new("job_information_edit", "data:{};error:{}".format(kwargs,e))

    def job_information_sync(self, filter_dict=None, extra_property=None, **kwargs):
        """
        SYNC:变更任职
        """
        try:
            self.record.info("job_information_sync", kwargs)
            info = self.get_sync_job_info_sync(kwargs) or {}
            if not info.get("sync_type"):
                return
            if info.get("sync_type") == "update":
                self.call_api(self.__job_info_sync_, info)
        except Exception as e:
            self.record_new("job_information_sync", "data:{};error:{}".format(kwargs,e))

    def job_information_reverse(self, filter_dict=None, extra_property=None, **kwargs):
        """
        SYNC:任职还原
        """
        try:
            self.record.info("job_information_reverse", kwargs)
            info = self.get_sync_job_info_reverse(kwargs) or {}
            if not info.get("sync_type"):
                return
            if info.get("sync_type") == "reverse":
                self.call_api(self.__job_info_reverse_, info)
        except Exception as e:
            self.record_new("job_information_reverse", "data:{};error:{}".format(kwargs,e))

    def record_new(self, log_type, content):
        CustomerUtil.call_open_api("hcm.model.create",
                                   param={"model": "dynamic_log", "info": {
                                       "log_type": log_type,
                                       "content": "{}".format(content),
                                       "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   }})

    def call_api(self, url, info):
        try:
            data = {"param": info}
            self.record_new("call_api", "data:{};url:{}".format(data, url))
            response = requests.request(method='POST', url=url, json=data, verify=False)
            if response.status_code == 200:
                result = json.loads(response.content)
                if result.get('success'):
                    data1 = {
                        "sync_type": type,
                        "sync_status": "success",
                        "sync_guid": info.get("id"),
                        "sync_info": "{}".format(result),
                        "sync_data": "{}".format(info),
                        "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "status_code": 200,
                        "source": "1",
                        "url": url
                    }
                    # self.sync_log(data1)
                    self.record.info(name="call_api", content="data:{};url:{}".format(data1, url))
                    return result
                else:
                    data1 = {
                        "sync_type": type,
                        "sync_status": "fail",
                        "sync_guid": info.get("id"),
                        "sync_info": "{}".format(result),
                        "sync_data": "{}".format(info),
                        "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "status_code": 200,
                        "source": "1",
                        "url": url
                    }
                    # self.sync_log(data1)
                    self.record.error(name="call_api", content="data:{};url:{}".format(data1, url))
            else:
                data1 = {
                    "sync_type": type,
                    "sync_guid": info.get("id"),
                    "sync_status": "fail",
                    "sync_info": "请求接口失败,报文：{}".format(response.content),
                    "sync_data": "{}".format(info),
                    "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    "status_code": response.status_code,
                    "source": "1",
                    "url": url
                }
                # self.sync_log(data1)
                self.record.error(name="call_api", content="data:{};url:{}".format(data1, url))
            return None
        except Exception as e:
            self.record_new("call_api", "data:{};error:{}".format(info, e))
            return None

    def sync_log(self, info):
        if info["sync_status"] == "success":
            result = CustomerUtil.call_open_api(
                name='hcm.model.list',
                param={
                    'model': 'third_sync_log',
                    "page_index": 1, "page_size": 2000,
                    'filter_dict': {
                        'sync_guid': info["sync_guid"],
                        'sync_status': "fail"
                    }, "extra_property": {"only_list": True}
                })["list"]
            if len(result) > 0:
                ids = [a.get("id") for a in result]
                CustomerUtil.call_open_api(
                    name='hcm.model.remove.batch',
                    param={
                        'model': 'third_sync_log',
                        "ids": ids
                    }
                )
        CustomerUtil.call_open_api("hcm.model.create", param={
            "model": "third_sync_log",
            "info": info
        })

    def get_sync_job_info_new(self, kwargs):
        try:
            record_str = "job_information_new"
            data = kwargs.get("data")
            id = data.get("id")
            employee_id = data.get("employee_id")
            sync_fields_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "sync_filed_setting",
                                                                                   "filter_dict": {
                                                                                       "s_model": "JobInformationMaster",
                                                                                       "s_help_type": {
                                                                                           "notin": ["attach"]},
                                                                                   },
                                                                                   "page_index": 1,
                                                                                   "page_size": 1000,
                                                                                   "extra_property": {"sorts": [],
                                                                                                      "only_list": True},
                                                                                   "biz_type": "list"})
            emp_sync_fields_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "sync_filed_setting",
                                                                                   "filter_dict": {
                                                                                       "s_model": "Employee",
                                                                                       "s_help_type": {
                                                                                           "notin": ["attach"]},
                                                                                   },
                                                                                   "page_index": 1,
                                                                                   "page_size": 1000,
                                                                                   "extra_property": {"sorts": [],
                                                                                                      "only_list": True},
                                                                                   "biz_type": "list"})
            if len(sync_fields_list["list"]) <= 0:
                self.record.other(name=record_str, content=f"未获取到同步配置字段，同步取消")
                return
            self.record.other(name=record_str, content=f"获取到同步配置字段完毕")
            _check_model = list(set([x["d_model"] for x in sync_fields_list["list"]]))
            if len(_check_model) != 1:
                self.record.other(name=record_str,
                                  content=f"同步子集JobInformationMaster对应的目的子集不唯一：[{','.join(_check_model)}],同步取消")
                return
            # self.d_subset = _check_model[0]
            extra_fields = [{"field": [x['s_field']], "key": x['s_field']} for x in sync_fields_list["list"]]
            extra_fields.append({"field": ["employee_id"], "key": "employee_id"})
            extra_fields.append({"field": ["employee.identity_card"], "key": "employee.identity_card"})
            extra_fields.append({"field": ["action.number"], "key": "action_number"})

            data_list = CustomerUtil.call_open_api("hcm.model.list", {
                "model": "JobInformationMaster",
                "filter_dict": {"id": id},
                "page_index": 1,
                "page_size": 1,
                "extra_property": {
                    "state": "inside",
                    "fields": extra_fields,
                    "sorts": [
                        {"key": "employee_id", "type": "asc"},
                        {"key": "position_type", "type": "asc"}
                    ],
                    "only_list": True
                }
            })["list"]
            if len(data_list) == 0:
                self.record.error(name=record_str, content="data:{};error:{}".format(data, "查询不到任职信息"))
                return {}
            job_info = data_list[0]
            data_info = self.handle_data_info(record_str, job_info, sync_fields_list)
            emp_info = self.handle_emp_info(employee_id,emp_sync_fields_list)
            if not data_info:
                return {}
            data_info["emp"] = emp_info
            action_number = job_info.get("action").get("number")
            action_list = CustomerUtil.call_open_api("hcm.model.list", {
                "model": "EmployeeAction_mapping", "filter_dict": {},
                "page_index": 1, "page_size": 100,
                "extra_property": {"sorts": [],
                                   "only_list": True}})["list"]
            action_info = {x.get("number"): x.get("group_id") for x in action_list}
            action_id = action_info.get(action_number)
            # 若变动事务是集团调入，则推送集团为修订事务(sync_type标识为修订)
            if str(action_number) == "HCMA32":
                data_info["sync_type"] = "edit"
                data_info["is_special"] = True
                data_info["data"]["action_id"] = action_id
            else:
                data_info["sync_type"] = "create"
                data_info["is_special"] = False
                data_info["data"]["action_id"] = action_id
            if not action_id:
                self.record.error(name=record_str, content="data:{};error:{}".format(data, "没有找到对应的变动事务"))
                return {}
            return data_info
        except Exception as e:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, e))
            return {}

    def get_sync_job_info_edit(self, kwargs):
        record_str = "job_information_edit"
        data = kwargs.get("data")
        id = data.get("id")
        employee_id = data.get("employee_id")
        sync_fields_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "sync_filed_setting",
                                                                               "filter_dict": {
                                                                                   "s_model": "JobInformationMaster",
                                                                                   "s_help_type": {
                                                                                       "notin": ["attach"]},
                                                                               },
                                                                               "page_index": 1,
                                                                               "page_size": 1000,
                                                                               "extra_property": {"sorts": [],
                                                                                                  "only_list": True},
                                                                               "biz_type": "list"})
        if len(sync_fields_list["list"]) <= 0:
            self.record.other(name=record_str, content=f"未获取到同步配置字段，同步取消")
            return
        self.record.other(name=record_str, content=f"获取到同步配置字段完毕")
        _check_model = list(set([x["d_model"] for x in sync_fields_list["list"]]))
        if len(_check_model) != 1:
            self.record.other(name=record_str,
                              content=f"同步子集JobInformationMaster对应的目的子集不唯一：[{','.join(_check_model)}],同步取消")
            return
        # self.d_subset = _check_model[0]
        extra_fields = [{"field": [x['s_field']], "key": x['s_field']} for x in sync_fields_list["list"]]
        extra_fields.append({"field": ["employee_id"], "key": "employee_id"})
        extra_fields.append({"field": ["employee.identity_card"], "key": "employee.identity_card"})
        extra_fields.append({"field": ["action.number"], "key": "action_number"})

        data_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "JobInformationMaster",
            "filter_dict": {"id": id},
            "page_index": 1,
            "page_size": 1,
            "extra_property": {
                "state": "inside",
                "fields": extra_fields,
                "sorts": [
                    {"key": "employee_id", "type": "asc"},
                    {"key": "position_type", "type": "asc"}
                ],
                "only_list": True
            }
        })["list"]
        if len(data_list) == 0:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, "查询不到任职信息"))
            return {}
        job_info = data_list[0]
        data_info = self.handle_data_info(record_str, job_info, sync_fields_list)

        action_number = job_info.get("action").get("number")
        action_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "EmployeeAction_mapping", "filter_dict": {},
            "page_index": 1, "page_size": 100,
            "extra_property": {"sorts": [],
                               "only_list": True}})["list"]
        action_info = {x.get("number"): x.get("group_id") for x in action_list}
        action_id  = action_info.get(action_number)
        if not action_id:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, "没有找到对应的变动事务"))
            return {}
        data_info["sync_type"] = "edit"
        data_info["data"]["action_id"] = action_id
        # 若变动事务是调出，则不进行推送
        if str(action_number) == "HCMA07":
            data_info["sync_type"] = None
        else:
            data_info["is_special"] = False
        return data_info

    def get_sync_job_info_sync(self, kwargs):
        record_str = "job_information_sync"
        data = kwargs.get("data")
        id = data.get("id")
        employee_id = data.get("employee_id")
        sync_fields_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "sync_filed_setting",
                                                                               "filter_dict": {
                                                                                   "s_model": "JobInformationMaster",
                                                                                   "s_help_type": {
                                                                                       "notin": ["attach"]},
                                                                               },
                                                                               "page_index": 1,
                                                                               "page_size": 1000,
                                                                               "extra_property": {"sorts": [],
                                                                                                  "only_list": True},
                                                                               "biz_type": "list"})
        if len(sync_fields_list["list"]) <= 0:
            self.record.other(name=record_str, content=f"未获取到同步配置字段，同步取消")
            return
        self.record.other(name=record_str, content=f"获取到同步配置字段完毕")
        _check_model = list(set([x["d_model"] for x in sync_fields_list["list"]]))
        if len(_check_model) != 1:
            self.record.other(name=record_str,
                              content=f"同步子集JobInformationMaster对应的目的子集不唯一：[{','.join(_check_model)}],同步取消")
            return
        # self.d_subset = _check_model[0]
        extra_fields = [{"field": [x['s_field']], "key": x['s_field']} for x in sync_fields_list["list"]]
        extra_fields.append({"field": ["employee_id"], "key": "employee_id"})
        extra_fields.append({"field": ["employee.identity_card"], "key": "employee.identity_card"})
        extra_fields.append({"field": ["action.number"], "key": "action_number"})

        data_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "JobInformationMaster",
            "filter_dict": {"id": id},
            "page_index": 1,
            "page_size": 1,
            "extra_property": {
                "state": "inside",
                "fields": extra_fields,
                "sorts": [
                    {"key": "employee_id", "type": "asc"},
                    {"key": "position_type", "type": "asc"}
                ],
                "only_list": True
            }
        })["list"]
        if len(data_list) == 0:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, "查询不到任职信息"))
            return {}
        job_info = data_list[0]
        data_info = self.handle_data_info(record_str, job_info, sync_fields_list)

        action_number = job_info.get("action").get("number")
        action_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "EmployeeAction_mapping", "filter_dict": {},
            "page_index": 1, "page_size": 100,
            "extra_property": {"sorts": [],
                               "only_list": True}})["list"]
        action_info = {x.get("number"): x.get("group_id") for x in action_list}
        action_id = action_info.get(action_number)
        if not action_id:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, "没有找到对应的变动事务"))
            return {}

        data_info["sync_type"] = "update"
        data_info["data"]["action_id"] = action_id
        return data_info

    def get_sync_job_info_reverse(self, kwargs):
        record_str = "job_information_reverse"
        data = kwargs.get("data")
        id = data.get("id")
        employee_id = data.get("employee_id")
        sync_fields_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "sync_filed_setting",
                                                                               "filter_dict": {
                                                                                   "s_model": "JobInformationMaster",
                                                                                   "s_help_type": {
                                                                                       "notin": ["attach"]},
                                                                               },
                                                                               "page_index": 1,
                                                                               "page_size": 1000,
                                                                               "extra_property": {"sorts": [],
                                                                                                  "only_list": True},
                                                                               "biz_type": "list"})
        if len(sync_fields_list["list"]) <= 0:
            self.record.other(name=record_str, content=f"未获取到同步配置字段，同步取消")
            return
        self.record.other(name=record_str, content=f"获取到同步配置字段完毕")
        _check_model = list(set([x["d_model"] for x in sync_fields_list["list"]]))
        if len(_check_model) != 1:
            self.record.other(name=record_str,
                              content=f"同步子集JobInformationMaster对应的目的子集不唯一：[{','.join(_check_model)}],同步取消")
            return
        # self.d_subset = _check_model[0]
        extra_fields = [{"field": [x['s_field']], "key": x['s_field']} for x in sync_fields_list["list"]]
        extra_fields.append({"field": ["employee_id"], "key": "employee_id"})
        extra_fields.append({"field": ["employee.identity_card"], "key": "employee.identity_card"})
        extra_fields.append({"field": ["action.number"], "key": "action_number"})

        data_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "JobInformation",
            "filter_dict": {"id": id},
            "page_index": 1,
            "page_size": 1,
            "extra_property": {
                "state": "inside",
                "fields": extra_fields,
                "sorts": [
                    {"key": "employee_id", "type": "asc"},
                    {"key": "position_type", "type": "asc"}
                ],
                "only_list": True
            }
        })["list"]
        if len(data_list) == 0:
            self.record.error(name=record_str, content="data:{};error:{}".format(data, "查询不到任职信息"))
            return {}
        job_info = data_list[0]
        data_info = self.handle_data_info(record_str, job_info, sync_fields_list)

        action_number = job_info.get("action").get("number")
        action_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "EmployeeAction_mapping", "filter_dict": {},
            "page_index": 1, "page_size": 100,
            "extra_property": {"sorts": [],
                               "only_list": True}})["list"]
        action_info = {x.get("number"): x.get("group_id") for x in action_list}
        action_id = action_info.get(action_number)

        data_info["sync_type"] = "reverse"
        data_info["data"]["action_id"] = action_id
        return job_info

    def handle_data_info(self, record_str, data, sync_fields_list):
        try:
            # result = []
            person_dict = {}
            basic_help_dict = {}
            identity_card = data["employee"]["identity_card"]
            data_info = {}
            data_info["outer_identity_card"] = identity_card
            data_info["outer_id"] = data["id"]
            data_info["field_config"] = sync_fields_list["list"]
            info ={}
            for field in sync_fields_list["list"]:
                s_field = field["s_field"]
                d_field = field["d_field"]
                if s_field in ["employee_id", "employee.identity_card", "action.number"]:
                    continue
                value = data[s_field]
                info[d_field] = value
                if not value:
                    continue
                s_help_type = field["s_help_type"]  # 三公司帮助类型
                d_help_type = field["d_help_type"]  # 集团帮助类型
                help_field = field["help_field"]  # 总部关联帮助定位字段
                s_object = field["s_object"]  # 三公司帮助码表
                d_object = field["d_object"]  # 总部帮助码表
                if d_help_type == "id":  # 关联
                    if not d_object:
                        self.record.error(name=record_str, content=f"目标关联字段:[{d_field}]对应码表帮助为空，该字段不同步")
                        info[d_field] = None
                        continue
                # 需要特殊转化的就两种 #1：
                # 1.码表/人员 关联-d帮助定位字段-d帮助定位字段-关联【因为默认 码表对应关系为name,人员为身份证号，需要两边都转化，配置即可】
                # 2.参照-d帮助定位字段-关联
                # 3.无帮助-d帮助定位字段-关联
                # 4.人员/码表 除外 关联-d帮助定位字段-关联【认为帮助字段放在目的帮助模型即集团的帮助模型上】
                if s_help_type == "mask" or d_help_type == "mask":  # 优先处理mask
                    mask_help = field["mask_help"]
                    info[d_field] = mask_help.get(str(value), value)
                elif s_help_type == "id":
                    if not s_object:
                        self.record.error(name=record_str,
                                          content=f"源关联字段:[{s_field}:{value}]对应码表帮助为空，该字段不同步")
                        info[d_field] = None
                        continue
                    # 码表帮助
                    if "common_basic_item_data" in s_object or "common_basic_tree_item_data" in s_object or d_help_type == "name":
                        if s_object in basic_help_dict.keys():
                            filter_list = basic_help_dict[s_object]
                        else:
                            basic_help_dict[s_object] = self.get_help_dict(s_object, help_field)
                            filter_list = basic_help_dict[s_object]
                        filter_basic = [x for x in filter_list if str(x["id"]) == str(value)]
                        if len(filter_basic) > 0:
                            if "common_basic_tree_item_data" in s_object \
                                    and "common_basic_tree_item_data" in d_object \
                                    and d_help_type == "id" \
                                    and help_field == "name":
                                basic_item = filter_basic[0]
                                if basic_item["parent_id"]:
                                    parent_filter = [x for x in filter_list if
                                                     x["id"] == basic_item["parent_id"]]
                                    info[
                                        d_field] = f"{parent_filter[0][help_field]}&{filter_basic[0][help_field]}"
                            else:
                                info[d_field] = filter_basic[0][help_field]

                        else:

                            self.record.error(name=record_str,
                                              content=f"未找到关联字段:[{s_field}:{value}]对应码表[{s_object}]帮助项，该字段不同步")
                            info[d_field] = None
                            continue

                    elif s_object == "Employee":
                        if d_help_type == "id":
                            if str(value) in person_dict.keys():
                                info[d_field] = person_dict[str(value)]
                            else:
                                emp_info = CustomerUtil.call_open_api("hcm.model.get",
                                                                      param={"model": "Employee",
                                                                             "id_": value})

                                identity_card = emp_info["identity_card"]
                                person_dict[str(value)] = identity_card
                                info[d_field] = identity_card
                        else:
                            info[d_field] = getEmpCardJson(employeeId=value)["name"]

                    else:
                        if s_object in basic_help_dict.keys():
                            filter_list = basic_help_dict[s_object]
                        else:
                            basic_help_dict[s_object] = self.get_help_dict(s_object, help_field)
                            filter_list = basic_help_dict[s_object]
                        filter_basic = [x for x in filter_list if x["id"] == value]
                        if len(filter_basic) > 0:
                            info[d_field] = filter_basic[0][help_field]
                elif s_help_type == "attach":
                    continue
            data_info["data"] = info
            return data_info
        except Exception as e:
            # logging.info(f"inner:[{e}:{data}]")
            self.record.error(name=record_str, content=f"inner:[{e}]")
            return {}

    def get_help_dict(self, s_object, help_field):
        """
        获取码表跟非人员模型的帮助
        :param s_object: 三公司帮助码表
        :param help_field: 帮助定位字段
        :return:
        """
        fields = [{"field": ["name"], "key": "name"},
                  {"field": ["number"], "key": "number"},
                  {"field": ["parent_id"], "key": "parent_id"},
                  {"field": ["id"], "key": "id"}]
        if help_field not in ["id", "name", "id"]:
            fields.append({"field": [help_field], "key": help_field})
        help_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": s_object,
                                                                        "page_index": 1,
                                                                        "page_size": 99999,
                                                                        "extra_property": {"sorts": [],
                                                                                           "fields": fields,
                                                                                           "only_list": True},
                                                                        "biz_type": "list"})
        return help_list["list"]

    def handle_emp_info(self, employee_id,sync_fields_list):
        record_str = "emp_create"
        _check_model = list(set([x["d_model"] for x in sync_fields_list["list"]]))
        if len(_check_model) != 1:
            self.record.other(name=record_str,
                              content=f"同步子集JobInformationMaster-Employee对应的目的子集不唯一：[{','.join(_check_model)}],同步取消")
            return
        # self.d_subset = _check_model[0]
        extra_fields = [{"field": [x['s_field']], "key": x['s_field']} for x in sync_fields_list["list"]]

        data_list = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "Employee",
            "filter_dict": {"id": employee_id},
            "page_index": 1,
            "page_size": 1,
            "extra_property": {
                "fields": extra_fields,
                "sorts": [
                    {"key": "id", "type": "asc"}
                ],
                "only_list": True
            }
        })["list"]
        if len(data_list) == 0:
            self.record.error(name=record_str, content="data:{};error:{}".format(employee_id, "查询不到主集信息"))
            return {}
        data = data_list[0]
        try:
            person_dict = {}
            basic_help_dict = {}
            data_info = {}
            data_info["field_config"] = sync_fields_list["list"]
            info ={}
            for field in sync_fields_list["list"]:
                s_field = field["s_field"]
                d_field = field["d_field"]
                if s_field in ["employee_id", "employee.identity_card", "action.number"]:
                    continue
                value = data[s_field]
                s_help_type = field["s_help_type"]
                info[d_field] = value
                if not value:
                    continue
                s_help_type = field["s_help_type"]  # 三公司帮助类型
                d_help_type = field["d_help_type"]  # 集团帮助类型
                help_field = field["help_field"]  # 总部关联帮助定位字段
                s_object = field["s_object"]  # 三公司帮助码表
                d_object = field["d_object"]  # 总部帮助码表
                if d_help_type == "id":  # 关联
                    if not d_object:
                        self.record.error(name=record_str, content=f"目标关联字段:[{d_field}]对应码表帮助为空，该字段不同步")
                        info[d_field] = None
                        continue
                # 需要特殊转化的就两种 #1：
                # 1.码表/人员 关联-d帮助定位字段-d帮助定位字段-关联【因为默认 码表对应关系为name,人员为身份证号，需要两边都转化，配置即可】
                # 2.参照-d帮助定位字段-关联
                # 3.无帮助-d帮助定位字段-关联
                # 4.人员/码表 除外 关联-d帮助定位字段-关联【认为帮助字段放在目的帮助模型即集团的帮助模型上】
                if s_help_type == "mask" or d_help_type == "mask":  # 优先处理mask
                    mask_help = field["mask_help"]
                    info[d_field] = mask_help.get(str(value), value)
                elif s_help_type == "id":
                    if not s_object:
                        self.record.error(name=record_str,
                                          content=f"源关联字段:[{s_field}:{value}]对应码表帮助为空，该字段不同步")
                        info[d_field] = None
                        continue
                    # 码表帮助
                    if "common_basic_item_data" in s_object or "common_basic_tree_item_data" in s_object or d_help_type == "name":
                        if s_object in basic_help_dict.keys():
                            filter_list = basic_help_dict[s_object]
                        else:
                            basic_help_dict[s_object] = self.get_help_dict(s_object, help_field)
                            filter_list = basic_help_dict[s_object]
                        filter_basic = [x for x in filter_list if x["id"] == value]
                        if len(filter_basic) > 0:
                            if "common_basic_tree_item_data" in s_object \
                                    and "common_basic_tree_item_data" in d_object \
                                    and d_help_type == "id" \
                                    and help_field == "name":
                                basic_item = filter_basic[0]
                                if basic_item["parent_id"]:
                                    parent_filter = [x for x in filter_list if
                                                     x["id"] == basic_item["parent_id"]]
                                    info[
                                        d_field] = f"{parent_filter[0][help_field]}&{filter_basic[0][help_field]}"
                            else:
                                info[d_field] = filter_basic[0][help_field]

                        else:

                            self.record.error(name=record_str,
                                              content=f"未找到关联字段:[{s_field}:{value}]对应码表[{s_object}]帮助项，该字段不同步")
                            info[d_field] = None
                            continue

                    elif s_object == "Employee":
                        if d_help_type == "id":
                            if str(value) in person_dict.keys():
                                info[d_field] = person_dict[str(value)]
                            else:
                                emp_info = CustomerUtil.call_open_api("hcm.model.get",
                                                                      param={"model": "Employee",
                                                                             "id_": value})

                                identity_card = emp_info["identity_card"]
                                person_dict[str(value)] = identity_card
                                info[d_field] = identity_card
                        else:
                            info[d_field] = getEmpCardJson(employeeId=value)["name"]
                elif s_help_type == "attach":
                    continue
            data_info["data"] = info
            return data_info
        except Exception as e:
            # logging.info(f"inner:[{e}:{data}]")
            self.record.error(name=record_str, content=f"inner:[{e}]")
            return {}