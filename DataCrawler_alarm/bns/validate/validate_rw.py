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
from bns.api.web_rw import api_web_rw

log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fomat)
logger = logging.getLogger(__name__)

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)


def is_onlineStatus(value):
    onlineStatusValue = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.onlineStatusValue", res_firstOne=True
    )
    if onlineStatusValue == "离线":
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
    return api_web_rw.get_realtime_location(devId=device_id)


def is_offlineStatus(value):
    onlineStatusValue = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.onlineStatusValue", res_firstOne=True
    )
    if onlineStatusValue != "离线":
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
    return api_web_rw.get_realtime_location(devId=device_id)



def is_accOff(value):
    status = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.status", res_firstOne=True
    )
    if status:
        if 'ACC关' in status:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_accOff),
    wait=wait_fixed(int(cfgObj.get_value("validate_common", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_common", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_common", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_acc_off(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_powerOff_alarm(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '终端主电源掉电' in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_powerOff_alarm),
    wait=wait_fixed(int(cfgObj.get_value("validate_common", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_common", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_common", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_power_off_alarm(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_locationed(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '位置讯号丢失' in alarm_type:
            return 1
        else:
            return None
    else:
        return 1


@retry(
    retry=retry_if_result(is_locationed),
    wait=wait_fixed(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_locationAndonlineAndoffline", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_locationed(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_io_on(value):
    status = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.status", res_firstOne=True
    )
    if status:
        if '门4开' in status and '门5开' in status:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_io_on),
    wait=wait_fixed(int(cfgObj.get_value("validate_common", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_common", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_common", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_io_on(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_io_off(value):
    status = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.status", res_firstOne=True
    )
    if status:
        if '门4关' in status and '门5关' in status:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_io_off),
    wait=wait_fixed(int(cfgObj.get_value("validate_common", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("validate_common", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("validate_common", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_io_off(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_fatigue_alarm(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '疲劳驾驶报警' in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_fatigue_alarm),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_fatigue_alarm(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_fatigue_alarm_pre(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '疲劳驾驶预警' in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_fatigue_alarm_pre),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_fatigue_alarm_pre(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_fatigue_alarm_clear(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '疲劳驾驶报警' not in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_fatigue_alarm_clear),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_fatigue_alarm_clear(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_overspeed_alarm(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '超速报警' in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_overspeed_alarm),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_overspeed_alarm(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_overspeed_alarm_pre(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '超速预警' in alarm_type:
            return None
        else:
            return 1
    else:
        return 1


@retry(
    retry=retry_if_result(is_overspeed_alarm_pre),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_overspeed_alarm_pre(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_overspeed_alarm_clear(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '超速报警' not in alarm_type:
            return None
        else:
            return 1
    else:
        return None


@retry(
    retry=retry_if_result(is_overspeed_alarm_clear),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_overspeed_alarm_clear(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)


def is_overspeed_alarm_pre_clear(value):
    alarm_type = JsonHelper.parseJson_by_objectpath(
        value, "$.response_data.data.alarmTypeValue", res_firstOne=True
    )
    if alarm_type:
        if '超速预警' in alarm_type:
            return None
        else:
            return 1
    else:
        return None


@retry(
    retry=retry_if_result(is_overspeed_alarm_pre_clear),
    wait=wait_fixed(int(cfgObj.get_value("fatigue_alarm", "retry_interval"))),  # 重试间隔
    stop=stop_after_attempt(int(cfgObj.get_value("fatigue_alarm", "retry_counts"))) | stop_after_delay(
        int(cfgObj.get_value("fatigue_alarm", "retry_timeout"))),
    # 停止重试条件
    reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def validate_overspeed_alarm_pre_clear(device_id):
    return api_web_rw.get_realtime_location(devId=device_id)