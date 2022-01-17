

import json
import requests
import logging
import inspect
from requests.adapters import HTTPAdapter
from util import decode_bytes_dict

__all__ = ["HCMRequests", "HCMSessionService"]


class HCMSessionService(object):
    def __init__(self, number="default", kwargs=None):
        self.number = number
        self.kwargs = kwargs or {}

    def session(self):
        if self.number == "retry":
            return self.retry
        else:
            return self.default

    @property
    def default(self):
        """
        默认会话
        :return:
        """

        return requests.Session()

    @property
    def retry(self):
        """
        支持重复请求的会话
        :return:
        """

        # 错误码为50x，重试时间间隔为0.3
        default_kwargs = dict(
            total=0,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        default_kwargs.update(self.kwargs)

        session = requests.Session()

        retry = requests.urllib3.util.retry.Retry(**default_kwargs)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


class HCMRequests(object):
    """
    HCM 请求通用类：
    1、可引入后创建实例，适用于发起简单请求
    2、可继承实现，适用于复杂场景发起请求
    3、响应体自动解析，自动对bytes解码，decode

    其他：
    1、查询日志技巧，如：使用'*Requests_test*'进行日志查询
    2、依赖内建请求包实现，建议查阅requests相关资料
    3、可设置日志标识、解析格式等，统一管理，便于跟踪
    """

    def __init__(self, prefix='test', rtype='content', method='POST', url=None, session_number="default",
                 session_kwargs=None, **kwargs):
        """初始化方法

        【常用参数】
        :param prefix: 日志标识，默认为test，拼装后为 Requests_test
        :param rtype: 响应数据的解析方式,默认为response.content自动解析
        :param method: 请求方式，默认为POST请求
        :param url: 请求地址
        :param session_number: 请求会话
        :param session_kwargs: 请求会话参数
        :param kwargs: 拓展参数，参照requests

        【以下为拓展参数】
        :param params: (可选) 字典格式或者JSON反序列化后的字符串，作为Request的query参数
        :param data: (可选) 字典格式，一个由元组(key, value)构成的列表, 字节流或者文件对象，作为Request的body参数
        :param json: (可选) JSON序列，作为Request的body参数
        :param headers: (可选) 字典格式，作为Request的HTTP请求头
        :param cookies: (可选) 字典格式或者CookieJar对象，作为Request的Cookies
        :param files: (可选) 字典格式，分为{'name': file-like-objects}和{'name': file-tuple}两种，用于文件上传；
            其中，file-tuple可以是二元组('filename', fileobj)，三元组('filename', fileobj, 'content_type')，
            或者四元组('filename', fileobj, 'content_type', custom_headers)
        :param auth: (可选) 身份认证
        :param timeout: (可选) 放弃请求前的服务器等待时长，FLOAT格式或者元组格式(connect timeout, read timeout)
        :param allow_redirects: (可选) 布尔值，是否允许 GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD 重定向，默认为True
        :param proxies: (可选) 字典格式，代理
        :param verify: (可选) 为布尔值时，控制是否校验服务器TLS证书，默认为True；为字符串时，指定 CA 证书路径
        :param stream: (可选) 为False时，响应内容将实时下载
        :param cert: (可选) 为字符串时，指定 ssl 客户端证书路径；若果是元组，('cert', 'key')
        :param proxy_number: (可选) 指定 HCM 公有云的某台机器作为代理
        :return:
        """

        self.prefix = prefix
        self.rtype = rtype
        self.method = method
        self.url = url
        self.session = HCMSessionService(session_number, session_kwargs).session()
        self.kwargs = kwargs

        proxy_number = kwargs.pop("proxy_number") if "proxy_number" in kwargs else None
        proxies = self._proxies_parse(proxy_number)
        if proxies:
            self.kwargs['proxies'] = proxies

    def request(self, method=None, url=None, **kwargs):
        """
        通用请求
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        proxy_number = kwargs.pop("proxy_number") if "proxy_number" in kwargs else None
        proxies = self._proxies_parse(proxy_number)
        if proxies:
            kwargs['proxies'] = proxies
        method = method or self.method
        url = url or self.url
        kwargs = dict(kwargs, **self.kwargs)
        try:
            logging.info('Requests_{}:{}:{}:{}'.format(
                self.prefix,
                method,
                url,
                json.dumps({_k: _v for _k, _v in kwargs.items() if not isinstance(_v, bytes)}))
            )
        except Exception as json_e:
            print(json_e)

        try:
            with self.session as session:
                if "verify" in kwargs and not kwargs.get("verify"):
                    requests.urllib3.disable_warnings()

                _response = session.request(method, url, **kwargs)

            _response = self._handler_response(_response)
            _data = self._parse(_response)

            # logging.info('Requests_{}_end:{}'.format(self.prefix, _response.status_code))
            logging.info('Requests_{}_end:{}:{}'.format(self.prefix, _response.status_code, _response.content))
            return _data
        except requests.exceptions.RequestException as requests_ge:
            logging.error('Requests_{}_error:{}, kwargs: {}'.format(self.prefix, getattr(requests_ge, "message") if hasattr(
                requests_ge, "message") else requests_ge, kwargs))
            raise ge.OUTER_REQUEST_FAILED.description('Requests_{}_error:{}, kwargs: {}'.format(self.prefix, getattr(
                requests_ge, "message") if hasattr(requests_ge, "message") else requests_ge, kwargs))
        except ge.AppException as requests_e:
            logging.error('Requests_{}_error:{}, kwargs: {}'.format(self.prefix, requests_e, kwargs))
            raise ge.DATA_NOT_FOUND.description('请求失败:{}'.format(requests_e))
        except Exception as e:
            logging.error('Requests_{}_error:{}, kwargs: {}'.format(self.prefix, e, kwargs))
            raise ge.DATA_NOT_FOUND.description('请求失败:{}'.format(e))

    def _proxies_parse(self, proxy_number):
        if proxy_number:
            logging.info("HCMRequests_proxy_number:{}".format(proxy_number))
            from core.extend.proxy_serivice.proxy_util import HcmProxyUtil
            _proxy_url = HcmProxyUtil.get_proxy_by_number(proxy_number)
            if _proxy_url:
                return {"http": _proxy_url, "https": _proxy_url}
            else:
                logging.info('proxy setting error')

    def _set_headers(self, _headers=None):
        """
        设置请求头，内部调用
        :param _headers:
        :return:
        """

        if isinstance(_headers, dict):
            self.kwargs['headers'] = _headers

    def _set_cookies(self, _cookies=None):
        """
        设置cookies，内部调用
        :param _cookies:
        :return:
        """

        from http.cookiejar import CookieJar
        if isinstance(_cookies, (dict, CookieJar)):
            self.kwargs['cookies'] = _cookies

    def _set_proxies(self, _proxies=None):
        """
        设置proxies，内部调用
        :param _proxies:
        :return:
        """

        if isinstance(_proxies, dict):
            self.kwargs['proxies'] = _proxies

    def _format_data(self, _data=None):
        """
        data序列化，可复写，内部调用
        :param _data:
        :return:
        """

        if isinstance(_data, dict):
            self.kwargs['data'] = json.dumps(_data)

    def _handler_response(self, _response):
        """
        响应处理，可复写，内部调用
        :param _response:
        :return:
        """

        if not _response.ok:
            print('Response_{}:{}:{}'.format(self.prefix, _response.status_code, _response.content))
            self.raise_for_status(_response)

        return _response

    @staticmethod
    def raise_for_status(_response):
        """
        异常检测,可复写
        :param _response:
        :return:
        """

        _response.raise_for_status()

    def _parse(self, _response):
        """
        响应数据解析,可复写，内部调用
        :param _response:
        :return:
        """

        if self.rtype == "self":
            return _response

        if not hasattr(_response, self.rtype):
            print('Return_{}:{}:{}'.format(self.prefix, self.rtype, _response.content))
            raise ge.DATA_RULE_ERROR.description('数据解析失败，没有该解析方式:{}'.format(self.rtype))

        _cls = getattr(_response, self.rtype)
        _r = None
        if inspect.ismethod(_cls):
            _r = _cls()
        else:
            if isinstance(_cls, str):
                try:
                    _r = json.loads(_cls)
                except Exception as e:
                    _r = _cls
                    print('NO_JSON_TYPE_TO_LOADS:{}'.format(e))
            elif isinstance(_cls, bytes):
                try:
                    _r = json.loads(_cls.decode('utf-8'))
                except Exception as e:
                    _r = _cls
                    print('NO_JSON_TYPE_TO_LOADS:{}'.format(e))
            else:
                _r = _cls

        try:
            return decode_bytes_dict(_r)
        except Exception as e:
            print('NO_BYTES_TYPE_TO_DECODE:{}'.format(e))
            return _r


if __name__ == "__main__":
    _ret = HCMRequests(
        session_number="retry",
        session_kwargs={"total": 5},
        headers={"Authorization": "123"},
        rtype="content",
        verify=False,
        method="GET"
    )
    _res = _ret.request(url="https://inspur.hcmcloud.cn/api/ping_all_alive")
    print(_res)
