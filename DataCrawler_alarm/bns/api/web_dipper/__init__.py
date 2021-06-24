# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:50
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : __init__.py

"""
    解决api接口的登录和加密逻辑
"""

import copy
import json

from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed
from tenacity import retry_if_exception_type

import config
from base.character_recognition_helper import CharacterRecognitionHelper
from base.selenium_helper import SeleniumHelper
from bns.api.utils import BaseApi
from base.allure_helper import AllureHelper
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper
from bns.exceptions import WebLoginFailedException, ApiCertificationExpireException
from config import queue_web_dipper

base_api = BaseApi()
cfg = ConfigHelper(config.cfgFile)


@retry(
    retry=retry_if_exception_type(ApiCertificationExpireException),  # 重试条件
    wait=wait_fixed(2),  # 重试间隔
    stop=stop_after_attempt(2) | stop_after_delay(120),  # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
)
def call_api(api_desc: str, api_addr: str, req_method: str, req_type: str, req_data: dict, extra_port: str = None,
             extra_headers: dict = None, auth_tuple: tuple = None, is_login=True, is_capture=True, **kwargs):
    """
    :param kwargs: api_protocol, api_domain, api_login_u, api_login_p
    :return:
    """

    if not extra_headers:
        extra_headers = dict()

    # 如果配置信息中存在值, 则优先使用此headers
    if is_login:

        login_headers = cfg.get_value("api_web_dipper", "api_headers")

        if login_headers:
            if isinstance(login_headers, str):
                login_headers = json.loads(login_headers)
                extra_headers.update(login_headers)
                req_data.update(login_headers)
            else:
                extra_headers.update(login_headers)
                req_data.update(login_headers)
        else:
            pass
            # 重新登录(接口端登录, 2UI端登录,并结合抓包工具)  # 运行有多次登录的容错机会
            # login_by_web()
            get_headers_web()
            # # 并将登录信息更新到config.ini文件中
            cfg_new = ConfigHelper(config.cfgFile)
            login_headers = cfg_new.get_value("api_web_dipper", "api_headers")
            login_headers = json.loads(login_headers)
            extra_headers.update(login_headers)
            req_data.update(login_headers)

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
        base_api.function_params_preprocess(kwargs, cfg_section="api_web_dipper")

    res_info = base_api.http_request(
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
        res_json_for_allure = show_req_data(copy.copy(res_info))
        AllureHelper.attachJson("接口信息:{}".format(api_desc), res_json_for_allure)

    # 如果权限错误, 返回的字典信息只有一个元素, 且包含关键信息result
    response_data = res_info.get("response_data")
    # if response_data['result'] != 0 or response_data.get('result') == None:
    if response_data['result'] == 5:
        # 更新token
        # login_by_web()
        get_headers_web()
        # 抛出cookie过期的异常
        raise ApiCertificationExpireException

    return res_info


# # login_by_api
# @retry(
#     retry=retry_if_exception_type(WebLoginFailedException),  # 重试条件
#     wait=wait_fixed(2),  # 重试间隔
#     stop=stop_after_attempt(5) | stop_after_delay(120),  # 停止重试条件
#     reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
# )
# def login_by_web():
#     selenium = SeleniumHelper(is_proxy=True, is_headless=True)
#
#     # 打开网站
#     api_protocol = cfg.get_value("api_web_dipper", "api_protocol")
#     api_domain = cfg.get_value("api_web_dipper", "api_domain")
#     driver = selenium.visit_web(rf"{api_protocol}://{api_domain}/")
#
#     # 解析登录中的验证码图片
#     checkcode_image_path = f"{config.captcha_dir}/checkcode_dipper.png"
#     input_checkcode = CharacterRecognitionHelper.recognition_simply_number_by_baidu(image_path=checkcode_image_path)
#     # input_checkcode = "123"
#
#     # 模拟页面登录操作
#     api_login_u = cfg.get_value("api_web_dipper", "api_login_u")
#     selenium.send(".login-wrap input[name=loginAccount]", api_login_u)
#
#     api_login_p = cfg.get_value("api_web_dipper", "api_login_p")
#     selenium.send(".login-wrap input[name=loginPassword]", api_login_p)
#
#     selenium.send(".login-wrap input[name=phrase]", input_checkcode)
#
#     selenium.click(".login-wrap input[id=loginSubmit]")
#
#     # 解决alert框问题
#     try:
#         driver.switch_to.alert.accept()
#     except:
#         pass
#
#     # 关闭网站
#     selenium.close_web()
#     # 从队列中读取cookie信息, 如果报错, 则重新执行
#     try:
#         cookies = queue_web_dipper.get(block=False)
#         cfg.set_value("api_web_dipper", "api_headers", f'{{"jsession": "{cookies[:-1]}"}}')
#     except:
#         raise WebLoginFailedException()

def login():
    res_json = call_api(
        api_desc="用户登录",
        api_addr="/StandardApiAction_login.action?",
        req_method="get",
        req_type="json",
        req_data={
            "account": "admin123",
            "password": "000000",
        },
        is_capture=False,

    )

    return res_json


def get_headers_web():
    extra_headers = dict()
    res_json = login()

    cookies_content = JsonHelper.parseJson_by_objectpath(res_json, "$.response_data.jsession")
    if cookies_content:
        extra_headers["jsession"] = cookies_content
    else:
        raise Exception(f"登录失败,无法从登录的返回信息中获取cookie信息. {res_json}")


    # 将登录信息写入到配置文件中
    cfg.set_value("api_web_dipper", "api_headers", extra_headers)

    import time
    # 给写入信息留一点时间
    time.sleep(1)


if __name__ == '__main__':
    import time
    import config

    from bns.utils import mitmproxy_server

    mitmproxy_server()

    time.sleep(3)
    get_headers_web()
