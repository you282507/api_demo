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
from base.exceptions import ObjectpathExtractNullException

import config
from bns.api.web_dipper import api_web_dipper


log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fomat)
logger = logging.getLogger(__name__)

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)

def is_online_status(value):
    result = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.onlines.online", res_firstOne=True
    )
    return not result


@retry(
    retry=retry_if_result(is_online_status),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_is_online_status(device_id):
    return api_web_dipper.get_device_online_status(devId=device_id)

def is_offline_status(value):
    result = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.onlines.online", res_firstOne=True
    )
    return result


@retry(
    retry=retry_if_result(is_offline_status),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_offline_status(device_id):
    return api_web_dipper.get_device_online_status(devId=device_id)


def is_login(value):
    result = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.result", res_firstOne=True
    )
    return result


@retry(
    retry=retry_if_result(is_login),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_get_login_status(device_id):
    return api_web_dipper.get_vehicleAlarm(devId=device_id)


def is_powerOff_alarm(value):
    try:
        alarm_type = JsonHelper.parseJson_by_objectpath(
            value, "$..*[@.DevIDNO is '018800190012'].stType", res_firstOne=False
        )
    except Exception:
        return 1

    if alarm_type:
        if 206 in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_powerOff_alarm),
    wait=wait_fixed(int(cfgObj.get_value("validate_power_off", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_power_off", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_power_off", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_power_off_alarm(device_id):
    return api_web_dipper.get_vehicleAlarm(devId=device_id)


def is_locationed(value):
    try:
        alarm_type = JsonHelper.parseJson_by_objectpath(
            value, "$..*[@.DevIDNO is '018800190012'].stType", res_firstOne=False
        )
    except Exception:
        return 1

    if alarm_type:
        if 206 in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_powerOff_alarm),
    wait=wait_fixed(int(cfgObj.get_value("validate_power_off", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_power_off", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_power_off", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_power_off_alarm(device_id):
    return api_web_dipper.get_vehicleAlarm(devId=device_id)