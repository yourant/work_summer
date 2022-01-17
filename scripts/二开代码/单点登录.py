# -*- coding:utf-8 -*-
# @CreateTime : 2019/10/30 9:31
# @Author: 郑辰龙
# @File : customer_sso.py
import datetime
import json
import logging
import urllib

import requests
from oauthlib.common import to_unicode

import errors
from core.extend.dynamic_plugin.customer_util import CustomerUtil
from core.extend.sync_outer.services_base import BaseSyncOuterService
from core.extend.third.base.service_sso import SSOService



class customer_sso(SSOService):
    """
    三方单点登录集成 竹云系统 【人员编码】唯一识别标志
    """
    __third_type__ = "customer_sso"
    __server_url__ = "https://bam.scg.cn"
    __client_id__ = "hrsystem"
    __client_secret__ = "ea8547dd6be342e6aa157aab7cc657b8"
    __hcm_server_url = "https://ehr.scg.cn"
    __redirect_uri__ = "{}/api/auth/login_by_sso?sso_platform_config_id=1&sso=customer_sso&next=/index".format(__hcm_server_url)
    __state__ = "hcmcloud"
    __response_type__ = "code"

    def get_authorize_redirect(self, redirect_uri, handler):
        """
        地址重定向
        :param redirect_uri:
        :param handler:
        :return:
        """
        self.__redirect_uri__ = redirect_uri
        url = "{}/idp/oauth2/authorize?redirect_uri={}&state={}&client_id={}&response_type={}".format(
            "https://bam.scg.cn", urllib.parse.quote(self.__redirect_uri__), self.__state__, self.__client_id__,
            self.__response_type__)
        logging.info("customer_sso|get_code_url|{}".format(url))
        return url

    def get_sso_user(self, handler):
        """
        获取登录信息
        :param handler:
        :return:
        """
        _cached_sso_user = self.get_cached_sso_user(handler, self.__third_type__)

        if _cached_sso_user:
            employee_number = _cached_sso_user.get("spRoleList")
            if not employee_number:
                logging.info("customer_sso|spRoleList为空:{}".format(_cached_sso_user))
                employee_number = _cached_sso_user.get("loginName")
                logging.info("customer_sso|loginName:{}".format(employee_number))
            if employee_number:
                logging.info("customer_sso|spRoleList:{}".format(_cached_sso_user.get("spRoleList")))
                logging.info("customer_sso|number:{}".format(employee_number))
                _emp_list = CustomerUtil.call_open_api("hcm.model.list", {
                    "model": "Employee",
                    "filter_dict": {
                        "number": employee_number  # du855
                    }
                })["list"]
                if len(_emp_list) == 1:
                    return _cached_sso_user
                elif len(_emp_list) > 1:
                    logging.info("customer_sso|员工编号不唯一！|{}".format(_cached_sso_user))
                else:
                    logging.info("customer_sso|未找到员工！|{}".format(_cached_sso_user))
            else:
                logging.info("customer_sso|未找到员工！编号为空|{}".format(_cached_sso_user))
        logging.info("customer_sso|handler.request.arguments:{}".format(handler.request.arguments))
        if "code" not in handler.request.arguments:
            logging.info("customer_sso|code not find|{}".format(handler.request.arguments))
            return None
        code = to_unicode(handler.request.arguments.get("code")[0])
        logging.info("customer_sso|code_found|{}".format(code))
        _sso_user = self.get_user_info_by_code(code)
        _sso_user["id"] = _sso_user["openid"]
        _sso_user["app_id"] = self.__client_id__
        logging.info("customer_sso|记录登录用户信息开始|{}".format(_sso_user))
        self.record_third_user_info(_sso_user)  # 记录登录用户信息
        logging.info("customer_sso|记录登录用户信息结束|")
        _binds = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "CompanyThirdUserBind",
            "filter_dict": {
                "third_type": self.__third_type__,
                "open_id": _sso_user["openid"]
            }
        })["list"]
        if not _binds:
            logging.info("customer_sso|CompanyThirdUserBind数据为空|{}|{}".format(self.__third_type__, _sso_user["openid"]))
        for _bind in _binds:
            CustomerUtil.call_open_api("hcm.model.edit", {
                "model": "CompanyThirdUserBind",
                "id_": _bind["id"],
                "info": {"user_info": json.dumps(_sso_user)}
            })
        # 设置缓存
        logging.info("customer_sso|设置缓存开始|{}".format(_sso_user))
        self.set_cached_sso_user(handler, self.__third_type__, _sso_user, 3600 * 24 * 10)
        logging.info("customer_sso|设置缓存成功|{}".format(_sso_user))
        return _sso_user

    def get_user_info_by_code(self, _code):
        token = self.fetch_user_access_token(_code)
        user_info = self.get_user_info(token["openid"], token["access_token"])
        return user_info

    # 获取TOKEN
    def fetch_user_access_token(self, code):
        _url = "{}/idp/oauth2/getToken?client_id={}&grant_type=authorization_code&code={}&client_secret={}".format(
            self.__server_url__, self.__client_id__, code, self.__client_secret__)
        logging.info("customer_sso|TOKEN_URL|{}".format(_url))
        try:
            result = requests.request("POST", url=_url, verify=False)
            if result.status_code == 200:
                result = json.loads(result.content)
            else:
                logging.info("customer_sso|TOKEN_ERROR|{}|{}".format(result.status_code, result.content))
                raise errors.SERVICE_NOT_AVAILABLE.description(result.content)
        except Exception as e:
            logging.info("customer_sso|TOKEN_ERROR|{}".format(e.message))
            raise errors.SERVICE_NOT_AVAILABLE.description("{}".format(e.message))
        if "access_token" not in result:
            logging.info("customer_sso|TOKEN_ERROR|返回信息不包含TOKEN|{}".format(result))
            raise errors.SERVICE_NOT_AVAILABLE.description("返回信息不包含TOKEN")
        # if "refresh_token" not in result:
        #     logging.info("not find refresh_token")
        #     raise errors.SERVICE_NOT_AVAILABLE.description(result)
        if "openid" not in result:
            result["openid"] = result.get("uid")
        _token_key = "{}_access_token:{}".format(self.__third_type__, result["openid"])
        self.set_cached_token(result, 7000)
        logging.info("customer_sso|TOKEN_SUCCESS|{}".format(result))
        return result

    # 获取用用户信息
    def get_user_info(self, openid, access_token):
        """
        请求竹云系统获取用户信息
        :param openid:
        :param access_token:
        :return:
        """
        url = "{}/idp/oauth2/getUserInfo?access_token={}&client_id={}".format(self.__server_url__, access_token,
                                                                              self.__client_id__)
        logging.info("customer_sso|USER_INFO|URL|{}".format(url))
        try:
            result = requests.request("GET", url=url, verify=False)
            result = json.loads(result.content)
        except Exception as e:
            logging.info("customer_sso|USER_INFO_ERROR|{}".format(e.message))
            raise errors.SERVICE_NOT_AVAILABLE.description(e.message)
        logging.info("customer_sso|USER_INFO|SUCCESS|{}".format(result))
        result["openid"] = openid
        return result

    def get_cloud_user(self, sso_user):
        logging.info("customer_sso|CLOUD_USER|SSO_USER|{}".format(sso_user))
        _binds = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "CompanyThirdUserBind",
            "filter_dict": {
                "third_type": self.__third_type__,
                "open_id": sso_user["openid"]
            }
        })["list"]
        if not _binds:
            logging.info("customer_sso|get_cloud_user|CompanyThirdUserBind数据为空|{}|{}".format(self.__third_type__,
                                                                                             sso_user["openid"]))
        logging.info("customer_sso|get_cloud_user|查询人员|{}".format(sso_user["loginName"]))
        _employee = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "Employee",
            "filter_dict": {
                "number": sso_user["loginName"]  # du855 人员编号为登录账号 sso_user["loginName"]
            }
        })["list"]
        logging.info("customer_sso|get_cloud_user|查询人员结束|{}".format(_employee))
        if _employee:
            sso_user["mobile"] = _employee[0]["mobile"]
        else:
            logging.info("customer_sso|CLOUD_USER|系统中不存在员工编码为{}的人员".format(sso_user["loginName"]))
            raise errors.SERVICE_NOT_AVAILABLE.description("系统中不存在员工编码为{}的人员".format(sso_user["loginName"]))
        if _binds:
            _user = CustomerUtil.call_open_api("hcm.model.get", {
                "model": "User",
                "id_": _binds[0]["user_id"]
            })
            if _user and _user.get("cell_phone") and sso_user.get("mobile") and _user.get("cell_phone") == sso_user.get(
                    "mobile"):
                return _user
        # 启动默认绑定信息，当做自动绑定器使用，正常流程应当在 bind_sso_user
        logging.info("customer_sso|get_cloud_user|获取USER|{}".format(sso_user["mobile"]))
        _user = CustomerUtil.call_open_api("hcm.model.list", {
            "model": "User",
            "filter_dict": {
                "cell_phone": sso_user["mobile"]
            }
        })["list"]
        logging.info("customer_sso|get_cloud_user|_user|{}".format(_user))
        if _user:  # 存在绑定单点用户
            self.bind_sso_user(sso_user, _user[0]["id"])
        else:  # 不存在新建User
            logging.info("customer_sso|get_cloud_user|新建User|{}".format(sso_user))
            # if sso_user["phone"] and len(sso_user["mobile"]) == 11:
            if len(sso_user["mobile"]) == 11:
                CustomerUtil.call_open_api("hcm.model.create", {
                    "model": "User",
                    "info": {"cell_phone": sso_user["mobile"]}
                })
        return None if _user is None else _user[0]

    def customer_logout(self, handler):
        """
        退出登录
        :param handler:
        :return:
        """
        _cache_key = handler.get_secure_cookie("customer_sso_sso")
        self.clear_cached("customer_sso_{}".format(_cache_key))
        return "{}/idp/profile/OAUTH2/Redirect/GLO?redirctToUrl={}&redirectToLogin=true&entityId={}".format(
            self.__server_url__, urllib.parse.quote(self.__hcm_server_url), self.__client_id__)

    def record(self, content, type=3):
        """
        日志记录
        :param content: 内容
        :param type: 2 异常 3 其他
        :return:
        """
        # employee_id=CustomerUtil.get_current_context().employee.id
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
                    "content": {"msg": content},
                    "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )