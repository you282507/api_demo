# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:40
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : validate_rw.py

import os
import logging

from tenacity import retry, retry_if_exception, wait_fixed, stop_after_attempt, stop_after_delay, before_sleep_log
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper

import config
from bns.api.dev import api_dev

log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fomat)
logger = logging.getLogger(__name__)

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)


@retry(
    retry=retry_if_exception(TimeoutError),
    wait=wait_fixed(int(cfgObj.get_value("set_dev_params", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("set_dev_params", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("set_dev_params", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_set_car_info():
    try:
        res_info = api_dev.set_car_info()
    except TimeoutError:
        raise TimeoutError
    return res_info


@retry(
    retry=retry_if_exception(TimeoutError),
    wait=wait_fixed(int(cfgObj.get_value("set_dev_params", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("set_dev_params", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("set_dev_params", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_set_net_info():
    try:
        res_info = api_dev.set_net_info()
    except TimeoutError:
        raise TimeoutError
    return res_info
