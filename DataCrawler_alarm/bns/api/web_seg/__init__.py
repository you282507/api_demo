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
from base.selenium_helper import SeleniumHelper
from bns.api.utils import BaseApi
from base.allure_helper import AllureHelper
from base.config_helper import ConfigHelper
from bns.exceptions import WebLoginFailedException, ApiCertificationExpireException
from config import queue_web_seg

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

        login_headers = cfg.get_value("api_web_seg", "api_headers")

        if login_headers:
            if isinstance(login_headers, str):
                login_headers = json.loads(login_headers)
                extra_headers.update(login_headers)
            else:
                extra_headers.update(login_headers)
        else:
            pass
            # 重新登录(接口端登录, 2UI端登录,并结合抓包工具)  # 运行有多次登录的容错机会
            login_by_web()
            # # 并将登录信息更新到config.ini文件中
            cfg_new = ConfigHelper(config.cfgFile)
            login_headers = cfg_new.get_value("api_web_seg", "api_headers")
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
        base_api.function_params_preprocess(kwargs, cfg_section="api_web_seg")

    res_info = base_api.http_request(
        req_url=base_api.get_http_url(api_protocol, api_domain, extra_port, api_addr),
        req_method=req_method,
        req_type=req_type,
        req_data=req_data,
        extra_headers=extra_headers,
        auth_tuple=auth_tuple,
        flag=False
    )

    # 将抓包信息做allure呈现
    if is_capture:
        res_json_for_allure = show_req_data(copy.copy(res_info))
        AllureHelper.attachJson("接口信息:{}".format(api_desc), res_json_for_allure)

    # 如果是因为认证过期导致无法登录, 应运行重新执行api
    response_data = res_info.get("response_data")
    if "会话超时" in str(response_data):
        # 更新token
        login_by_web()
        # 抛出cookie过期的异常
        raise ApiCertificationExpireException

    return res_info


# login_by_api
@retry(
    retry=retry_if_exception_type(WebLoginFailedException),  # 重试条件
    wait=wait_fixed(2),  # 重试间隔
    stop=stop_after_attempt(5) | stop_after_delay(120),  # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
)
def login_by_web():
    selenium = SeleniumHelper(is_proxy=True, is_headless=True)

    # 打开网站
    api_protocol = cfg.get_value("api_web_seg", "api_protocol")
    api_domain = cfg.get_value("api_web_seg", "api_domain")
    driver = selenium.visit_web(rf"{api_protocol}://{api_domain}/")

    # 模拟页面登录操作
    iframe = driver.find_element_by_tag_name("iframe")
    driver.switch_to.frame(iframe)  # id, name, obj

    api_login_u = cfg.get_value("api_web_seg", "api_login_u")
    selenium.send("#main_form input[type=text]", api_login_u)

    api_login_p = cfg.get_value("api_web_seg", "api_login_p")
    selenium.send("#main_form input[type=password]", api_login_p)

    from selenium.webdriver import ActionChains
    action_chains = ActionChains(driver)

    # 滑动方案1:
    # d1 = driver.find_element_by_class_name("el-icon-d-arrow-right")
    # d2 = driver.find_element_by_class_name("drag_text")
    # action_chains.drag_and_drop_by_offset(d1, d2.size["width"], d1.size["height"]).perform()

    # 滑动方案2:
    d1 = driver.find_element_by_class_name("el-icon-d-arrow-right")
    action_chains.click_and_hold(d1).perform()
    action_chains.reset_actions()
    action_chains.move_by_offset(300, 0).perform()

    # 关闭网站
    selenium.close_web()

    # 从队列中读取cookie信息, 如果报错, 则重新执行
    try:
        cookies = queue_web_seg.get(block=False)
        cfg.set_value("api_web_seg", "api_headers", cookies)
    except:
        raise WebLoginFailedException()


if __name__ == '__main__':
    import subprocess
    import os, time
    import config

    from bns.utils import mitmproxy_server
    mitmproxy_server()
    time.sleep(3)

    login_by_web()
