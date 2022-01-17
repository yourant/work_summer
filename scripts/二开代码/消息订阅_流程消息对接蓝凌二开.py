from core.extend.dynamic_plugin.customer_util import CustomerUtil
from core.extend.sync_outer.services_base import BaseSyncOuterService
from cacheUtil import getDeptJson,getEmpCardJson
import datetime
import json
import logging
import dicttoxml
import xmltodict
from suds.client import Client
import  requests
import copy
from core.extend.hcm_requests.api import HCMRequests
from core.extend.third.base.service_sync import ThirdBaseSyncObject as ThirdBaseUpdateObject


class DynamicFlowAPI(ThirdBaseUpdateObject):
    def __init__(self):
        self.__description__ = "OA协同代办对接"  # 业务 catagory
        self.context = None
        self.method = None
        self.result = None
        self.client = None
        self.assign_id = None

        super(DynamicFlowAPI, self).__init__(context=CustomerUtil.get_current_context(), is_record=True)

    def execute(self, event, assign):
        try:
            self.log(name="event_check", content="event:{},id:{}".format(event, assign['id']))

            # 正式
            # add_str_domain = 'https://hr.hncsmtr.com'
            # add_mobileStr_domain = 'https://hr-mobile.hncsmtr.com:7443'

            # 测试
            add_str_domain = 'https://hr-sit.hncsmtr.com:8443'
            add_mobileStr_domain = 'https://hr-sit.hncsmtr.com:8443'

            # 正式
            # url = "https://office.hncsmtr.com/sys/webservice/sysNotifyTodoWebService?wsdl"

            # 测试
            url = "https://office-sit.hncsmtr.com:8443/sys/webservice/sysNotifyTodoWebService?wsdl"

            self.assign_id = str(assign['id'])
            # 当执行人为空时不做同步
            if not assign["executor"]:
                self.log(name=f"execute", content=f"{self.assign_id}:当前审批人为空，不处理")
                info = {
                    "event": event,
                    "assign": json.dumps(assign),
                    "method": self.method if self.method else None,
                    "status": "success",
                    "errormsg": f"{self.assign_id}:当前审批人为空，不处理",
                    "cloud_func": "wf_message_send_outer",
                    "wf_mark_id": self.assign_id,
                    "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                }
                self.sync_log(info=info)
                return

            # 获取流程信息并拼接跳转URL
            self.log(name=f"execute", content=f"workflow.get.wf.all")
            work_flow = CustomerUtil.call_open_api("workflow.get.wf.all", {"assignment_id": self.assign_id})
            business_id = work_flow["data"]["wf"]["business_id"]
            ver_info = CustomerUtil.call_open_api("workflow.business.version", param={"business_id": business_id})
            state = None
            if ver_info["success"]:
                business_version = ver_info["version"]
                if business_version == 3:
                    state = "workflow_bill_v3"
                elif business_version == 2:
                    state = "workflow_bill"
                elif business_version == 1:
                    state = "bill"
            else:
                raise Exception("event:{},id:{}未获取到流程版本信息".format(event, self.assign_id))

            if not state:
                raise Exception("event:{},id:{}获取state失败".format(event, self.assign_id))
            add_str = '{}/#/{}?wf_assignment_id={}&business_id={}'.format(add_str_domain, state, self.assign_id,
                                                                          business_id)
            add_mobileStr = '{}/#/{}?wf_assignment_id={}&business_id={}'.format(add_mobileStr_domain, state,
                                                                                self.assign_id, business_id)

            # 获取OA模块信息 默认组织人事
            appName = "014"
            modelName = "014001"
            mapping_list = self.get_model_mapping()
            if mapping_list:
                check_model = [x for x in mapping_list if x["business_id"] == business_id]
                if check_model:
                    modelName = check_model[0]["modelDesc"]

            self.client = Client(url)
            self.client.set_options(timeout=120)

            if event == "add":
                self.log(name=f"execute", content=event)
                wf_inst_title = work_flow["data"]["inst"]["wf_inst_title"]
                self.context = self.client.factory.create("notifyTodoSendContext")
                self.log(name=f"execute_context", content=event)
                self.method = "sendTodo"
                self.context.appName = appName
                self.context.modelName = modelName
                self.context.modelId = self.assign_id
                self.context.subject = wf_inst_title
                self.context.link = add_str
                self.context.mobileLink = add_mobileStr
                self.context.type = 1
                self.context.key = ""
                self.context.param1 = ""
                self.context.param2 = ""
                self.context.language = ""
                self.context.others = ""
                targets = {
                    "PersonNo": assign["executor"]["number"]
                }
                self.context.targets = json.dumps(targets)
                self.context.createTime = assign['create_time']
                submit_user_id = assign["submit_user_id"]
                submit_user = getEmpCardJson(employeeId=submit_user_id)
                docCreator = {
                    "PersonNo": submit_user["number"]
                }
                self.context.docCreator = json.dumps(docCreator)
                self.context.level = 3
                self.context.extendContent = ""
                self.call_webservice()
            elif event == 'cancel':
                self.log(name=f"execute", content=event)
                log_list = self.get_mesg_todo_list(modelId=self.assign_id)
                if not log_list:
                    todo_info = self.get_filter_todo_list(assign["executor"]["number"], self.assign_id)
                else:
                    try:
                        todo_str = log_list[0]["param"]
                        todo_str = todo_str.replace("\"", "").replace("'", '"')
                        todo_info = json.loads(todo_str)
                    except Exception as e:
                        self.log(name=f"execute", content=f"{event}:parse:{e}")
                        todo_info = self.get_filter_todo_list(assign["executor"]["number"], self.assign_id)

                self.context = self.client.factory.create("notifyTodoRemoveContext")
                self.log(name=f"execute_context", content=event)
                self.method = "deleteTodo"
                self.context.appName = todo_info.get("appName") if todo_info.get("appName") else appName
                self.context.modelName = todo_info["modelName"] if todo_info else modelName
                self.context.modelId = todo_info["modelId"] if todo_info else self.assign_id
                self.context.optType = 1
                self.context.type = 1
                self.context.others = ""
                self.context.key = ""
                self.context.param1 = ""
                self.context.param2 = ""
                targets = {
                    "PersonNo": assign["executor"]["number"]
                }
                self.context.targets = json.dumps(targets)
                self.call_webservice()
            elif event == 'finish' or event == 'reject':
                self.log(name=f"execute", content=event)
                log_list = self.get_mesg_todo_list(modelId=self.assign_id)
                if not log_list:
                    todo_info = self.get_filter_todo_list(assign["executor"]["number"], self.assign_id)
                else:
                    try:
                        todo_str = log_list[0]["param"]
                        todo_str = todo_str.replace("\"", "").replace("'", '"')
                        todo_info = json.loads(todo_str)
                    except Exception as e:
                        self.log(name=f"execute", content=f"{event}:parse:{e}")
                        todo_info = self.get_filter_todo_list(assign["executor"]["number"], self.assign_id)
                self.context = self.client.factory.create("notifyTodoRemoveContext")
                self.log(name=f"execute_context", content=event)
                self.method = "setTodoDone"
                self.context.appName = todo_info.get("appName") if todo_info.get("appName") else appName
                self.context.modelName = todo_info["modelName"] if todo_info else modelName
                self.context.modelId = todo_info["modelId"] if todo_info else self.assign_id
                self.context.optType = 1
                self.context.key = ""
                self.context.param1 = ""
                self.context.param2 = ""
                self.context.type = 1
                self.context.others = ""
                targets = {
                    "PersonNo": assign["executor"]["number"]
                }
                self.context.targets = json.dumps(targets)
                self.call_webservice()
            else:
                raise Exception(f"未识别的事件类型")
            self.log(name=f"execute", content=f"result {self.result}")
            if self.result is not None:
                resulr_dict = dict(self.result)
                returnState = int(resulr_dict.get("returnState"))
                message = resulr_dict.get("message")
                if returnState in [1, 0]:
                    raise Exception(
                        "返回状态{}，标识为{}的代办同步失败,返回结果【操作失败】,失败原因{}".format(returnState, self.assign_id, message))
                if returnState == 2:
                    self.log(name="wf_outer_info", content=f"{self.assign_id}:{resulr_dict}")
                    self.sync_log(info={
                        "event": event,
                        "assign": json.dumps(assign),
                        "status": "success",
                        "method": self.method if self.method else None,
                        "errormsg": "",
                        "cloud_func": "wf_message_send_outer",
                        "param": str(self.client.dict(self.context)) if self.client and self.context else None,
                        "wf_mark_id": self.assign_id,
                        "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "result": str(dict(self.result)) if self.result else None
                    })
            else:
                raise Exception(f"重推失败，返回结果仍然为{self.result}")
        except Exception as e:
            self.log(name="wf_outer_error", content=f"{self.assign_id}:{e}", log_type="error")
            info = {
                "event": event,
                "assign": json.dumps(assign),
                "method": self.method if self.method else None,
                "status": "fail",
                "errormsg": f"{e}",
                "cloud_func": "wf_message_send_outer",
                "wf_mark_id": self.assign_id,
                "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),

            }
            # 防止异常参数拼接错误，添加try
            try:
                info = {
                    "event": event,
                    "assign": json.dumps(assign),
                    "status": "fail",
                    "method": self.method if self.method else None,
                    "errormsg": f"{e}",
                    "cloud_func": "wf_message_send_outer",
                    "param": str(self.client.dict(self.context)) if self.client and self.context else None,
                    "wf_mark_id": self.assign_id,
                    "sync_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    "result": str(dict(self.result)) if self.result else None
                }
            except Exception as e2:
                info["errormsg"] = info["errormsg"] + "###" + f"{e2}"

            self.sync_log(info=info)

    def call_webservice(self):
        retry_count = 0
        while True:
            try:
                self.log(name=f"call_webservice_begin_{self.method}",
                         content=f"第{retry_count}次调用：{self.assign_id}:{self.client.dict(self.context)}")
                if self.method == "sendTodo":
                    self.result = self.client.service.sendTodo(self.context)
                if self.method == "deleteTodo":
                    self.result = self.client.service.deleteTodo(self.context)
                if self.method == "setTodoDone":
                    self.result = self.client.service.setTodoDone(self.context)
                self.log(name=f"call_webservice_end_{self.method}",
                         content=f"结束第{retry_count}次调用：{self.assign_id}:{self.result}")
                if self.result is None:
                    retry_count = retry_count + 1
                    if retry_count > 5:
                        break
                    self.log(name=f"call_webservice_end_{self.method}",
                             content=f"调用失败，将发起第{retry_count}次重试：{self.assign_id}:{self.result}")
                else:
                    break

            except Exception as e:
                self.log(name="wf_outer_call_webservice_error", content=f"{self.assign_id}:{e}", log_type="error")
                raise e

    def get_mesg_todo_list(self, modelId):
        log_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "wf_message_send_log",
                                                                       "filter_dict": {
                                                                           "cloud_func": "wf_message_send_outer",
                                                                           "status": "success",
                                                                           "method": ["sendTodo"],
                                                                           "wf_mark_id": modelId},
                                                                       "page_index": 1, "page_size": 200,
                                                                       "extra_property": {"sorts": [],
                                                                                          "only_list": True},
                                                                       "biz_type": "list"})
        return log_list.get("list") or []

    def get_filter_todo_list(self, personNo, modelId):
        return {}
        try:
            filter_context = self.client.factory.create("notifyTodoGetContext")
            targets = {
                "PersonNo": personNo
            }
            filter_context.targets = json.dumps(targets)
            filter_context.rowSize = 1000
            filter_context.pageNo = 1
            otherCond = {
                "modelId": modelId
            }
            filter_context.otherCond = json.dumps([otherCond])
            filter_result = self.client.service.getTodo(filter_context)
            result_dict = dict(filter_result)
            returnState = int(result_dict.get("returnState"))
            if returnState == 2:
                message = json.loads(result_dict['message'])
                if message.get("errorPage"):
                    return {}
                else:
                    count = message["count"]
                    if count > 0:
                        info = message["docs"][-1]
                        self.log(name="get_filter_todo_list",
                                 content={"personNo": personNo, "modelId": modelId, "info": f"{info}"})
                        return info
            return {}
        except Exception as e:
            self.log(name="get_filter_todo_list_error",
                     content={"personNo": personNo, "modelId": modelId, "error": f"{e}"})
            return {}

    def get_model_mapping(self):
        mapping_list = CustomerUtil.call_open_api("hcm.model.list", param={"model": "workflow_model_mapping",
                                                                           "filter_dict": {},
                                                                           "page_index": 1, "page_size": 99999,
                                                                           "extra_property": {"sorts": [],
                                                                                              "only_list": True,
                                                                                              "fileds": [
                                                                                                  {"key": "business_id",
                                                                                                   "field": [
                                                                                                       "business_id"]},
                                                                                                  {"key": "modelName",
                                                                                                   "field": [
                                                                                                       "modelName"]},
                                                                                                  {"key": "modelDesc",
                                                                                                   "field": [
                                                                                                       "modelDesc"]}]},
                                                                           "biz_type": "list"})
        return mapping_list["list"]

    def sync_log(self, info):
        if info["status"] == "success":
            param = {
                'model': 'wf_message_send_log',
                "page_index": 1, "page_size": 2000,
                'filter_dict': {
                    'wf_mark_id': info["wf_mark_id"],
                    'status': "fail"
                }, "extra_property": {"only_list": True}
            }
            if info.get("method"):
                param["filter_dict"]["method"] = info["method"]
            result = CustomerUtil.call_open_api(
                name='hcm.model.list',
                param=param)["list"]
            if len(result) > 0:
                ids = [a.get("id") for a in result]
                CustomerUtil.call_open_api(
                    name='hcm.model.remove.batch',
                    param={
                        'model': 'wf_message_send_log',
                        "ids": ids
                    }
                )
            CustomerUtil.call_open_api("hcm.model.create", param={
                "model": "wf_message_send_log",
                "info": info
            })
        else:
            result = CustomerUtil.call_open_api(
                name='hcm.model.list',
                param={
                    'model': 'wf_message_send_log',
                    "page_index": 1, "page_size": 2000,
                    'filter_dict': {
                        'wf_mark_id': info["wf_mark_id"]

                    }, "extra_property": {"only_list": True}
                })["list"]
            if len(result) <= 0:
                CustomerUtil.call_open_api("hcm.model.create", param={
                    "model": "wf_message_send_log",
                    "info": info
                })

    def log(self, name, content, log_type="info"):
        if log_type == "error":
            self.record.error(name=name, content=content)
        else:
            self.record.info(name=name, content=content)
        CustomerUtil.call_open_api("hcm.model.create",
                                   param={"model": "dynamic_log", "info": {
                                       "log_type": self.__description__,
                                       "content": "{}#####{}".format(name, content),
                                       "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   }})