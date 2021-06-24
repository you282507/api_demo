# -*- coding: utf-8 -*-
# @Time    : 2020/10/30 10:21
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : api_model.py

import re
import copy
from functools import wraps

import config
from base.http_helper import HttpHelper
from base.allure_helper import AllureHelper
from bns.exceptions import (
    RequestUrlParamsNotExistException,
    RequestDomainExtraPortException,
    RequestDomainFormatException,
    ConfigParamsMissingException,
)


class BaseApi():

    def http_request(self, req_url, req_method, req_type, req_data=None, extra_headers=None, auth_tuple=None,
                     flag=False):
        # TODO: 当参数类型出现file时, Content-Type切换为文件类型

        self.request = HttpHelper(verbose=True)

        resp = self.request.build_request(

            extra_headers=extra_headers,  # 补充请求头信息
            request_auth=auth_tuple,  # auth认证信息
            request_url=req_url,  # 请求地址
            request_method=req_method,  # 请求方法
            content_type=req_type,  # 请求内容类型
            request_data=req_data,  # 请求数据
            flag=flag
        )

        return resp

    def get_http_url(self, api_protocol, api_domain, extra_port, api_addr, request_data=None):
        """
        :param api_protocol: api协议
        :param api_domain: api域名 或 api的ip加端口
        :param extra_port: 额外指定的api端口
        :param api_addr: api地址
        :param request_data: 请求数据(意在解决api url带参数的问题)
        :return:
        """

        # 如果请求地址中带有参数, 应先转换参数
        sub_list = re.findall(r"\{(.*?)\}", api_addr)
        if sub_list:
            ### 校验花括号中的变量是否存在于请求参数中，并进行简单的字符串的替换
            for sub_var in sub_list:
                tmp_var = request_data.get(sub_var)
                if not tmp_var:
                    raise RequestUrlParamsNotExistException(f"请求函数的参数中未传入请求地址需要的动态参数：{sub_var}")
                api_addr = api_addr.replace(f"{{{sub_var}}}", str(tmp_var))

        # 如果已额外指定了端口
        if extra_port:
            tmp_list = api_domain.split(":")
            if len(tmp_list) == 1:
                raise RequestDomainExtraPortException("请求域名后不能额外再指定请求端口")
            elif len(tmp_list) == 2:
                tmp_list.pop()
                tmp_list.append(extra_port)
                api_domain = ":".join(tmp_list)
            else:
                raise RequestDomainFormatException("当前的域名格式错误: 格式应形如 www.qq.com 或 127.0.0.1:8080")

        url = f"{api_protocol}://{api_domain}{api_addr}"

        return url

    def function_params_preprocess(self, kwargs: dict, cfg_section: str = ""):
        '''
        预处理操作: 从函数的kwargs中取参数并处理
        :param kwargs:
        :return:
        '''
        if len(kwargs.keys()) != 4:
            if not cfg_section:
                raise ConfigParamsMissingException("请在config.ini中配置参数: [cfg_session]")

        api_protocol = kwargs.get("api_protocol")
        if not api_protocol:
            api_protocol = config.get_api_protocol(cfg_section)

            if not api_protocol:
                raise ConfigParamsMissingException("请在config.ini中配置参数: api_protocol")

        api_domain = kwargs.get("api_domain")
        if not api_domain:
            api_domain = config.get_api_domain(cfg_section)
            if not api_domain:
                raise ConfigParamsMissingException("请在config.ini中配置参数: api_domain")

        api_login_u = kwargs.get("api_login_u")
        if not api_login_u:
            api_login_u = config.get_api_login_u(cfg_section)
            if not api_login_u:
                raise ConfigParamsMissingException("请在config.ini中配置参数: api_login_u")

        api_login_p = kwargs.get("api_login_p")
        if not api_login_p:
            api_login_p = config.get_api_login_p(cfg_section)
            if not api_login_p:
                raise ConfigParamsMissingException("请在config.ini中配置参数: api_login_p")

        return api_protocol, api_domain, api_login_u, api_login_p

    def handle_request_data(self, data: dict):
        """
        处理http的请求参数:
            1. 移除data字典中value是None的key
            2. 如果value也是个字典，其中的None也会被移除。
        :return:
        """
        keys = data.keys()
        keys_to_remove = []
        for k in keys:
            v = data[k]
            if v is None:
                keys_to_remove.append(k)

            if isinstance(data[k], dict):
                self.handle_request_data(data[k])

        for k in keys_to_remove:
            data.pop(k)

        return data

    @staticmethod
    def allure_attach(interface_desc):
        '''
        功能说明：将函数的返回结果添加到allure的attach中。如base层中的方法需要此装饰器
        :param interface_desc: 接口功能描述
        '''

        # allure报告中不显示过长的字符串, 如图片的base64字符串
        def show_req_data(res_json_for_allure):
            if isinstance(res_json_for_allure, dict):
                for k, v in res_json_for_allure.items():
                    if isinstance(v, dict):
                        show_req_data(v)
                    if isinstance(v, str):
                        if len(v) > 1000:
                            res_json_for_allure[k] = v[:20]
                return res_json_for_allure

        def warp_func(func):

            @wraps(func)
            def fild_retry(*args, **kwargs):
                res_json = func(*args, **kwargs)
                res_json_for_allure = show_req_data(copy.copy(res_json))
                AllureHelper.attachJson("接口信息:{}".format(interface_desc), res_json_for_allure)
                return res_json

            return fild_retry

        return warp_func
