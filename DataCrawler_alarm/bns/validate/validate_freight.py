# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:40
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : validate_rw.py

import os
import logging

from tenacity import retry, retry_if_result, wait_fixed, stop_after_attempt, stop_after_delay, before_sleep_log
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper

import config
from bns.api.web_freight import api_web_freight

log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fomat)
logger = logging.getLogger(__name__)

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)


def is_onlineStatus(value):
    onlineStatusValue = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.isonline", res_firstOne=True
    )
    if onlineStatusValue == 0:
        return 1
    else:
        return None


@retry(
    retry=retry_if_result(is_onlineStatus),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_device_online(device_id):
    return api_web_freight.get_online_status(dev_id=device_id)


def is_offlineStatus(value):
    onlineStatusValue = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.isonline", res_firstOne=True
    )
    if onlineStatusValue == 1:
        return 1
    else:
        return None


@retry(
    retry=retry_if_result(is_offlineStatus),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_device_offline(device_id):
    return api_web_freight.get_online_status(dev_id=device_id)