# -*- coding: utf-8 -*-
# @Time    : 2020/3/27 16:42
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : http_helper.py

import re
import ssl
import uuid
import urllib3
import json

import requests
from requests import Response
from requests import exceptions
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart.encoder import MultipartEncoder

from base.allure_helper import AllureHelper
from base.time_helper import TimeHelper
from base.log_helper import LogHelper

http_request_timeout = 20

from base.time_helper import TimeHelper


def str_to_dict(query_str):
    a_list = query_str.split('&')
    a_list_of_lists = [v.split('=', 1) for v in a_list]
    return dict(a_list_of_lists)


class HttpHelper(object):

    def __init__(self, verbose=False):

        # 解决控制台输出 InsecureRequestWarning 的问题
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 初始化日志句柄
        self.log = LogHelper()
        # 日志开关
        self.verbose = verbose
        # 信息收集
        self.info = dict()
        # 初始化信息头
        self.headers = {}

    def log_print(self, resp: Response, *args, **kwargs):

        if resp.status_code != 500:
            self.log.log_info(f"请求url: ({resp.request.method}) {resp.request.url}")
            self.log.log_info(f"请求header: {resp.request.headers}")
            self.log.log_info(f"请求数据: {resp.request.body}")
            self.log.log_info(f"响应数据: {resp.text[:200] }")  # 只显示前200个内容
        else:
            self.log.log_error("请求服务器端异常")

    def handle_request_exception(self):

        self.log.log_error(f"请求头信息: {self.headers}")
        self.log.log_error(f"请求url: ({self.request_method}){self.request_url}")
        self.log.log_error(f"请求数据: {self.request_data}")

        self.info["request_contentType"] = self.content_type
        self.info["request_url"] = self.request_url
        self.info["request_method"] = self.request_method
        self.info["request_data"] = self.request_data

        return self.info

    def build_request(self, request_method, content_type, request_url, request_data=None, extra_headers=None,
                      request_auth=None, flag=False):
        """
        构建请求
        :param request_headers:
        :param request_method:
        :param request_url:
        :param request_data:
        :param flag:True表示get请求、content_type为json使用params传参
        :return:
        """

        """
        发送请求: get, post, put, delete等
        :return:
        """
        self.request_method = request_method
        self.content_type = content_type
        self.request_url = request_url
        self.request_data = request_data
        self.extra_headers = extra_headers

        ssl._create_default_https_context = ssl._create_unverified_context

        self.info["time"] = TimeHelper.get_time_from_timestamp()

        if request_auth:
            if not isinstance(request_auth, tuple):

                # auth如果是requests.auth.HTTPDigestAuth, 支持, 否则报错
                if isinstance(request_auth, HTTPDigestAuth):
                    pass
                else:
                    raise Exception(f"request_auth必须是tuple类型, 当前类型: {type(request_auth)}, 当前内容: {request_auth}")
        else:
            request_auth = tuple()

        # extra_headers: 追加或覆盖self.headers
        if extra_headers:
            self.log.log_info(f"当前请求有额外的headers信息: {extra_headers}")
            if isinstance(extra_headers, dict):
                self.headers.update(extra_headers)

        try:

            if (request_method == "get" or request_method == "delete") and (
                    content_type == "urlencoded" or content_type == "json") and not flag:
                self.headers["Content-Type"] = "application/json;charset=UTF-8"
                if content_type == "urlencoded":
                    self.headers["Content-Type"] = "application/x-www-form-urlencoded"

                response = getattr(requests, request_method)(url=request_url, params=request_data, headers=self.headers,
                                                             auth=request_auth, verify=False,
                                                             timeout=http_request_timeout,
                                                             hooks={'response': [self.log_print, ]})

            elif request_method == "get" and content_type == "json" and flag:

                self.headers["Content-Type"] = "application/json;charset=UTF-8"
                response = requests.get(url=request_url, params=request_data, headers=self.headers,
                                        auth=request_auth, verify=False, timeout=http_request_timeout,
                                        hooks={'response': [self.log_print, ]})

            elif request_method in ["post", "delete", "put"] and content_type == "urlencoded":

                self.headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = getattr(requests, request_method)(url=request_url, data=request_data, headers=self.headers,
                                                             auth=request_auth, verify=False,
                                                             timeout=http_request_timeout,
                                                             hooks={'response': [self.log_print, ]})

            elif request_method in ["get", "post", "delete", "put"] and content_type == "json":

                self.headers["Content-Type"] = "application/json;charset=UTF-8"
                response = getattr(requests, request_method)(url=request_url, json=request_data, headers=self.headers,
                                                             auth=request_auth, verify=False,
                                                             timeout=http_request_timeout,
                                                             hooks={'response': [self.log_print, ]})

            elif request_method == "post" and content_type == "file_boundary":

                '''
                    # request_data的格式说明, 支持多文件参数和多文本参数
                    request_data={
                        'file': ('文件名字', 文件二进制数据, "文件类型"),   # 文件参数
                        'file': (os.path.basename(file_path), open(file_path, 'rb'), "application/x-zip-compressed"),   # 文件参数
                        'content': content,   # 文本参数
                    },
                '''
                advanced_data = MultipartEncoder(
                    fields=request_data,
                    boundary="----%s" % uuid.uuid4()
                )

                self.headers["Content-Type"] = advanced_data.content_type
                response = requests.post(url=request_url, data=advanced_data, headers=self.headers,
                                         auth=request_auth, verify=False, timeout=http_request_timeout,
                                         hooks={'response': [self.log_print, ]})

            else:
                raise Exception("当前http请求没封装,请求方法：{}，请求类型：{}".format(request_method, content_type))

        except exceptions.Timeout as e:
            info_dict = self.handle_request_exception()
            AllureHelper.attachJson("接口请求失败:{}".format(e), info_dict)
            raise Exception(f"http请求超时:{e}")

        except exceptions.InvalidURL as e:
            info_dict = self.handle_request_exception()
            AllureHelper.attachJson("接口请求失败:{}".format(e), info_dict)
            raise Exception(f"http非法url:{e}")

        except exceptions.HTTPError as e:
            info_dict = self.handle_request_exception()
            AllureHelper.attachJson("接口请求失败:{}".format(e), info_dict)
            raise Exception(f"http请求错误:{e}")

        except Exception as e:
            info_dict = self.handle_request_exception()
            AllureHelper.attachJson("接口请求失败:{}".format(e), info_dict)
            raise Exception(f"http请求未知异常:{e}")

        return self.parse_response(response)

    def parse_response(self, response: Response, *args, **kwargs):
        """
        回调函数
        :param response: requests.Response对象
        :return:
        说明:
            1. 返回响应对象
            2. 将响应对象中常用的内容返回
        """

        # 将响应对象返回
        self.info["response_obj"] = response

        self.info["request_contentType"] = response.request.headers.get("Content-Type")
        self.info["request_url"] = response.request.url
        self.info["request_method"] = response.request.method

        # 如果请求体是bytes类型, 就转为字符串
        request_data = response.request.body  # TODO: 字符串转字典

        if request_data:
            if isinstance(request_data, bytes):
                self.info["request_data"] = json.loads(request_data.decode())
            elif isinstance(request_data, MultipartEncoder):
                pattern = r"<MultipartEncoder: (.*?)>"
                request_data = re.search(pattern, str(request_data)).group(1).replace('\'', '\"')
                try:
                    self.info["request_data"] = json.loads(request_data)
                except Exception as e:
                    self.info["request_data"] = request_data
            else:  # 包含空值和不需要特殊处理的
                self.info["request_data"] = str_to_dict(request_data)
        else:
            self.info["request_data"] = None

        self.info["response_time"] = response.elapsed.total_seconds()

        response_status_code = response.status_code
        self.info["response_code"] = response_status_code
        # self.info["response_headers"] = response.headers

        # TODO: 如果请求的返回信息有异常,导致必须有的信息没有. 怎么处理?
        if response_status_code in [200, ]:
            # 获取响应数据格式
            response_contentType = response.headers.get("Content-Type")
            self.info['response_contentType'] = response_contentType

            if response_contentType:
                # response_data 根据 response_contentType 做相应的处理
                if response_contentType in ["application/json;charset=UTF-8", "application/json",
                                            "text/json; charset=utf-8"]:

                    try:
                        self.info['response_data'] = response.json()
                    except Exception:
                        self.log.log_error(self.info)
                        self.info['response_data'] = response.text
                        # raise Exception("响应数据类型是json，但响应数据无法转为json格式: {}".format(self.info))

                elif response_contentType in ["image/jpeg", ]:
                    self.info['response_data'] = response.content

                else:

                    # 如果response_contentType类型不是期望的，优先尝试强转json
                    try:
                        self.info['response_data'] = response.json()
                    except Exception:
                        self.info['response_data'] = response.text
                        # raise Exception("响应数据没有收集,当前响应数据类型为:{}, 请联系管理员.".format(response_contentType))
            else:
                try:
                    self.info['response_data'] = response.json()
                except Exception:
                    raise Exception("无法获取当前的响应数据类型, 请联系管理员")

            return self.info

        return self.info


if __name__ == '__main__':
    pass
