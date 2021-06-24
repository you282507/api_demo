# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:49
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : operate_device.py

from bns.api.web_dipper import call_api
from base.exceptions import ObjectpathExtractNullException


def get_vehicle_list():
    req_data = {
        "json": {}
    }

    res_json = call_api(
        is_login=True,
        api_desc="车辆列表",
        api_addr="/808gps/StandardLoginAction_loadIndexCommData.action",
        req_method="post",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


def get_device_online_status(devId):
    req_data = {
        "devIdno": devId
    }

    res_json = call_api(
        is_login=True,
        api_desc="查询在线状态",
        api_addr="/StandardApiAction_getDeviceOlStatus.action",
        req_method="post",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


def get_vehicleAlarm(devId):

    req_data = {
        "devIdno": devId,
        "toMap": 2
    }

    res_json = call_api(
        is_login=True,
        api_desc="查询告警信息",
        api_addr=f"/StandardApiAction_vehicleAlarm.action",
        req_method="get",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


if __name__ == '__main__':
    from bns.utils import mitmproxy_server

    mitmproxy_server()

    from base.json_helper import JsonHelper
    res = get_vehicleAlarm("018800190012")

