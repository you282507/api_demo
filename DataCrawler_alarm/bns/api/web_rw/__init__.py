# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:50
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : __init__.py

"""
    解决api接口的登录和加密逻辑
"""

import copy

from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed
from tenacity import retry_if_exception_type

import config
from bns.api.utils import BaseApi
from base.allure_helper import AllureHelper
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper
from bns.exceptions import ApiCertificationExpireException


base_api = BaseApi()
cfg = ConfigHelper(config.cfgFile)

@retry(
    retry=retry_if_exception_type(ApiCertificationExpireException),  # 重试条件
    wait=wait_fixed(2),  # 重试间隔
    stop=stop_after_attempt(2) | stop_after_delay(120),  # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
)
def call_api(api_desc: str, api_addr: str, req_method: str, req_type: str, req_data: dict, extra_port: str = None,
             extra_headers: dict = None, auth_tuple: tuple = None, is_login=False, is_capture=True, **kwargs):
    """
    :param kwargs: api_protocol, api_domain, api_login_u, api_login_p
    :return:
    """

    if not extra_headers:
        extra_headers = dict()

    # 如果配置信息中存在值, 则优先使用此headers
    if is_login:
        login_headers = cfg.get_value("api_web_rw", "api_headers")
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
        base_api.function_params_preprocess(kwargs, cfg_section="api_web_rw")

    res_json = base_api.http_request(
        req_url=base_api.get_http_url(api_protocol, api_domain, extra_port, api_addr),
        req_method=req_method,
        req_type=req_type,
        req_data=req_data,
        extra_headers=extra_headers,
        auth_tuple=auth_tuple,
        flag=False
    )

    if is_capture:
        # 将抓包信息做allure呈现
        res_json_for_allure = show_req_data(copy.copy(res_json))
        AllureHelper.attachJson("接口信息:{}".format(api_desc), res_json_for_allure)

    # 权限错误码401
    response_data = res_json.get("response_data")
    if response_data['code'] == 401:
        # 更新token
        get_headers_web()
        # 抛出cookie过期的异常
        raise ApiCertificationExpireException

    return res_json


def web_login_verifyCode():
    res_json = call_api(
        api_desc="登录模块_登录验证码",
        api_addr="/vmp/common/captcha/string",
        req_method="get",
        req_type="urlencoded",
        req_data={},
        is_capture=False,
    )
    return res_json


def web_login_login(verifyCode, extra_headers=None):
    res_json = call_api(
        api_desc="登录模块_用户登录",
        api_addr="/vmp/auth/login",
        req_method="post",
        req_type="json",
        req_data={
            "companyNo": "hnzjtxkj",
            "username": "yueyue",
            "password": "yueyue123456",
            "customerGraphCode": verifyCode,
        },
        extra_headers=extra_headers,
        is_capture=False,

    )

    return res_json


def get_headers_web():
    extra_headers = dict()

    # 访问验证码接口, 获取验证码和cookie
    res_json = web_login_verifyCode()
    verifyCode = JsonHelper.parseJson_by_objectpath(res_json, "$.response_data.data.captcha")

    from requests import Response
    response_obj: Response = JsonHelper.parseJson_by_objectpath(res_json, "$.response_obj")
    cookies_content = response_obj.headers.get("Set-Cookie")
    if cookies_content:
        cookie_value = cookies_content.split(";")[0]
        extra_headers["Cookie"] = cookie_value
    else:
        raise Exception(f"登录失败,无法从登录的返回信息中获取cookie信息. {res_json}")

    tmp_extra_headers = dict()

    res_json = web_login_login(verifyCode, extra_headers=extra_headers)

    # set token info
    token = JsonHelper.parseJson_by_objectpath(res_json, "$..*['token']", res_firstOne=True)
    tmp_extra_headers["Authorization"] = token

    # 将登录信息写入到配置文件中
    cfg.set_value("api_web_rw", "api_headers", tmp_extra_headers)

    import time
    # 给写入信息留一点时间
    time.sleep(1)


if __name__ == '__main__':
    get_headers_web()
