import datetime
import json
import logging

import jpype
import xmltodict

import errors
from core.extend.dynamic_plugin.customer_util import CustomerUtil
from core.extend.third.base.service_sso import SSOService


class CustomerSSOService(SSOService):
    __third_type__ = "customer_sso"
    __authorize_type__ = "customer_sso"
    __description__ = "个性化单点登录"

    # 自定义
    __client_id__ = 'portalsystem'

    def get_authorize_redirect(self, redirect_uri, handler):
        """
        拼装重定向地址
        :param redirect_uri:
        :param handler:
        :return:
        """
        # http://rlzy01.rlzy.dev.hxmis.com/login/redirect_sso?sso=customer_sso&next=/index
        logging.info(
            "---------------------------------------------------------------------------------------------------AAaaaaaaaa")
        return ""

    def get_sso_user(self, handler):
        """
        获取第三方用户信息
        必要，第一个执行
        :param handler:
        :return:
        """
        _cached_sso_user = self.get_cached_sso_user(handler, self.__third_type__)
        logging.info(handler)
        logging.info(
            "获取第三方用户信息----------------------------------------------------------------------------------------------")
        self.record("_cached_sso_user|{}".format(_cached_sso_user))

        # 如果有缓存，直接返回
        if _cached_sso_user is not None:
            if _cached_sso_user.get('openid'):
                login_name = _cached_sso_user.get('openid')
                self.record("get_sso_user|{}".format(login_name))
                _emp_list = CustomerUtil.call_open_api(
                    name='hcm.model.list',
                    param={
                        "model": "Employee",
                        "filter_dict": {
                            "oa_account": login_name
                        },
                        "extra_property": {
                            "only_list": True,
                            "fields": [{"key": "name", "field": ["name"]}, {"key": "mobile", "field": ["mobile"]}]
                        }
                    })['list']
                self.record("get_sso_user|{}".format(_emp_list))
                if len(_emp_list) == 1:
                    self.record("get_sso_user|{}".format(login_name))
                    return _cached_sso_user
                elif len(_emp_list) > 1:
                    self.record("get_sso_user|{}".format(_cached_sso_user))
                else:
                    self.record("get_sso_user|{}".format(_cached_sso_user))
            else:
                self.record("get_sso_user|{}".format(_cached_sso_user))

        # 没有缓存，获取sso用户信息
        key_info = self.request.cookies['key'].value
        self.record(key_info)
        key_info = key_info.split('|')
        key, server_url = key_info[0], key_info[1]

        _jar_base = '/var/data/hcm_core_document/sso.jar'

        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
                           "-Djava.class.path=%s" % (_jar_base))

        SignOnClient = jpype.JClass('com.credinet.portal.sso.client.SignOnClient')

        result = SignOnClient.authenticate(key, server_url, 'hr')
        self.record(result)
        result = xmltodict.parse(result)
        logging.info(result)

        _sso_user = {}
        if not result['root']['result']:
            raise errors.SERVICE_NOT_AVAILABLE.description("getuserinfo|登录失败")
        _sso_user['openid'] = result['root']['user']
        _sso_user['id'] = _sso_user['openid']
        _sso_user['app_id'] = self.__client_id__
        self.record_third_user_info(_sso_user)

        _binds = CustomerUtil.call_open_api(
            name='hcm.model.list',
            param={
                "model": "CompanyThirdUserBind",
                "filter_dict": {
                    "third_type": self.__third_type__,
                    "open_id": _sso_user['id']
                }
            })['list']
        for _bind in _binds:
            CustomerUtil.call_open_api('hcm.model.edit', {
                "model": "CompanyThirdUserBind",
                "id_": _bind['id'],
                "info": {"user_info": json.dumps(_sso_user)}
            })
        self.record("get_sso_user|设置缓存|{}".format(_sso_user))
        self.set_cached_sso_user(handler, self.__third_type__, _sso_user, 3600 * 24 * 10)
        self.record("{}".format("get_sso_user|设置缓存成功"))
        return _sso_user

    def bind_sso_user(self, sso_user, cloud_user_id):
        """
        第三方用户信息绑定CLOUD用户
        :param sso_user:
        :param cloud_user_id:
        :return:
        """
        return {}

    def get_cloud_user(self, sso_user):
        """
        根据第三方用户信息获取CLOUD用户信息
        必要
        :param sso_user:
        :return:
        """

        if not sso_user.get("app_id"):
            sso_user["app_id"] = self.__client_id__
        self.record("get_cloud_user|{}".format(sso_user))
        self.record("get_cloud_user|{}".format(sso_user["openid"]))
        employee = CustomerUtil.call_open_api('hcm.model.list', {
            "model": "Employee",
            "filter_dict": {
                "oa_account": sso_user["openid"]
            },
            "extra_property": {
                "only_list": True,
                "fields": [{"key": "name", "field": ["name"]}, {"key": "mobile", "field": ["mobile"]}]
            }
        })['list']
        # employee=[{"mobile":"18615221104","id":1506566,"name":"李晓吉"}]
        # self.record("get_cloud_user|employee|{}".format(employee))
        mobile = ""
        if employee:
            mobile = employee[0]['mobile']
        else:
            raise errors.SERVICE_NOT_AVAILABLE.description("人员空")
        self.record("get_cloud_user|mobile|{}".format(mobile))
        self.record("get_cloud_user|open_id|{}".format(sso_user["openid"]))
        binds = CustomerUtil.call_open_api('hcm.model.list', {
            "model": "CompanyThirdUserBind",
            "filter_dict": {
                "third_type": self.__third_type__,
                "open_id": sso_user["openid"]
            }
        })['list']
        # self.record("get_cloud_user|binds|{}".format(binds))
        if binds:
            user = CustomerUtil.call_open_api('hcm.model.list', {
                "model": "User",
                "filter_dict": {"id": binds[0].get('user_id')}
            })['list']
            # self.record("get_cloud_user|user|{}".format(user))
            if user and user[0].get('cell_phone') and user[0].get('cell_phone') == mobile:
                # self.record("get_cloud_user|user|{}".format(user[0]))
                return user[0]

        _user = CustomerUtil.call_open_api('hcm.model.list', {
            "model": "User",
            "filter_dict": {
                "cell_phone": mobile
            }
        })['list']
        # self.record("|_user|{}".format(_user))
        if _user:
            if not binds:
                CustomerUtil.call_open_api('hcm.model.create', {
                    "model": "CompanyThirdUserBind",
                    "info": {"user_id": _user[0]['id'],
                             "open_id": sso_user["openid"],
                             "third_type": self.__third_type__,
                             "app_id": self.__client_id__
                             }
                })
            self.bind_sso_user(sso_user, _user[0]['id'])
        else:
            if len(mobile) == 11:
                CustomerUtil.call_open_api('hcm.model.create', {
                    "model": "User",
                    "info": {"cell_phone": mobile,
                             "name": employee[0].get("name"),
                             "bounded_employee_id": employee[0].get("id")
                             }
                })
        self.record("返回user{}".format(_user))
        return None if _user is None else _user[0]

    def customer_logout(self, handler):
        """
        根据第三方注销规则拼装注销地址
        :param handler:
        :return:
        """
        return ""

    def record(self, content, type=3):
        """
        :return:
        """
        # employee_id=CustomerUtil.get_current_context().employee.id
        company_id = 768
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
                    "content": {"msg": "{}".format(content)},
                    "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )
