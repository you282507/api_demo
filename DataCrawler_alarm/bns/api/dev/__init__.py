# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:50
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : __init__.py

"""
    解决api接口的登录和加密逻辑
"""

import copy

import config
from bns.api.utils import BaseApi
from base.allure_helper import AllureHelper
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper

base_api = BaseApi()


def call_api(api_desc: str, api_addr: str, req_method: str, req_type: str, req_data: dict, extra_port: str = None,
             extra_headers: dict = None, auth_tuple: tuple = None, is_login=False, **kwargs):
    """
    :param kwargs: api_protocol, api_domain, api_login_u, api_login_p
    :return:
    """

    if not extra_headers:
        extra_headers = dict()

    # 如果配置信息中存在值, 则优先使用此headers
    if is_login:
        login_headers = config.get_api_headers("api_dev")
        if login_headers:
            import json
            login_headers = json.loads(login_headers)
            extra_headers.update(login_headers)

    def show_req_data(res_json_for_allure):
        if isinstance(res_json_for_allure, dict):
            for k, v in res_json_for_allure.items():
                if isinstance(v, dict):
                    show_req_data(v)
                if isinstance(v, str):
                    if len(v) > 1000:
                        res_json_for_allure[k] = v[:20]
            return res_json_for_allure

    api_protocol, api_domain, api_login_u, api_login_p = \
        base_api.function_params_preprocess(kwargs, cfg_section="api_dev")

    res_json = base_api.http_request(
        req_url=base_api.get_http_url(api_protocol, api_domain, extra_port, api_addr),
        req_method=req_method,
        req_type=req_type,
        req_data=req_data,
        extra_headers=extra_headers,
        auth_tuple=auth_tuple,
        flag=False
    )

    # 将抓包信息做allure呈现
    res_json_for_allure = show_req_data(copy.copy(res_json))
    AllureHelper.attachJson("接口信息:{}".format(api_desc), res_json_for_allure)

    return res_json


if __name__ == '__main__':
    pass
