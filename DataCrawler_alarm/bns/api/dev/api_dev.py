# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:49
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : operate_device.py

from bns.api.dev import call_api
from base.json_helper import JsonHelper


def set_vehicle_speed(speed, speedMode=0):
    req_data = {
        "speed": speed,
        "speedMode": speedMode
    }

    res_json = call_api(
        api_desc="设备端操作_设置车辆速度",
        api_addr="/setSpeed.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def set_car_info(carNum="豫D55555", terminalModel="RN-RD-P600", terminalID="0460432", carNumColor=1, vehicleTypeIndex=5,
                 provinceId="21", cityId="0020", height=0,
                 carCode="10101010107777777", pulse=3600, instDate=1585699200000, initMile=10, loadState=0,
                 manufacturerID="44030072604"):
    req_data = {
        "carNum": carNum,
        "carNumColor": carNumColor,
        "vehicleTypeIndex": vehicleTypeIndex,
        "provinceId": provinceId,
        "cityId": cityId,
        "height": height,
        "carCode": carCode,
        "pulse": pulse,
        "instDate": instDate,
        "initMile": initMile,
        "loadState": loadState,
        "manufacturerID": manufacturerID,
        "terminalModel": terminalModel,
        "terminalID": terminalID
    }

    res_json = call_api(
        api_desc="设备端操作_设置车辆信息",
        api_addr="/setCarInfo.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def set_alarm_switch(switch):
    """
    设置开启关闭模拟警报的开关
    :param switch: 0为关，1为开
    :return:
    """
    req_data = {
        "switch": switch
    }
    res_json = call_api(
        api_desc="设备端操作_设置模拟警报开关",
        api_addr="/setSimulateAlarm.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )
    return res_json


def set_simulate_alarm(alarm_type, rate):
    data_list = get_simulate_alarm()["response_data"]['alarmInfo']
    for data in data_list:
        if alarm_type == data['alarmType']:
            data['rate'] = rate
            alarm = data
    req_data = {
        "switch": -1,
        "alarmInfo": [alarm]
    }
    set_alarm_switch(1)
    res_json = call_api(
        api_desc="设备端操作_设置模拟警报",
        api_addr="/setSimulateAlarm.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )
    set_alarm_switch(0)
    return res_json


addr5 = "47.107.251.235"
port5 = 6608
addr4 = "lt1.gghypt.net"
port4 = 7008


# addr5 = "47.113.63.66"
# port5 = 2081


def set_net_info():
    req_data = {
        "phone": "17726149122",
        "apn": "CMNET",
        "user": "ctnet@mycdma.cn",
        "passwd": "vnet.mobi",
        "server": [
            {
                "id": 2,
                "enable": 1,
                "feature": 0,
                "jttVer": 0,
                "addr": '',
                "port": 0,
                "backupAddr": "",
                "backupPort": 0
            },
            {
                "id": 3,
                "enable": 1,
                "feature": 1,
                "jttVer": 0,
                "addr": '',
                "port": 0,
                "backupAddr": "",
                "backupPort": 0
            },
            {
                "id": 1,
                "enable": 1,
                "feature": 1,
                "jttVer": 1,
                "addr": '',
                "port": 0,
                "backupAddr": "",
                "backupPort": 0
            },
            {
                "id": 4,
                "enable": 1,
                "feature": 1,
                "jttVer": 1,
                "addr": addr4,
                "port": port4,
                "backupAddr": "",
                "backupPort": 0
            },
            {
                "id": 5,
                "enable": 1,
                "feature": 1,
                "jttVer": 0,
                "addr": addr5,
                "port": port5,
                "backupAddr": "",
                "backupPort": 0
            },
            {
                "id": 6,
                "enable": 0,
                "feature": 1,
                "jttVer": 0,
                "addr": "",
                "port": 0,
                "backupAddr": "",
                "backupPort": 0
            }
        ]
    }

    res_json = call_api(
        api_desc="设备端操作_设置网络",
        api_addr="/setNetInfo.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def get_base_status():
    res_json = call_api(
        api_desc="设备端操作_查询设备信息",
        api_addr="/baseStatus.do",
        req_method="get",
        req_type="json",
        req_data={},
    )

    return res_json


def get_car_info():
    res_json = call_api(
        api_desc="设备端操作_查询车辆信息",
        api_addr="/carInfo.do",
        req_method="get",
        req_type="json",
        req_data={},
    )

    return res_json


def get_dev_status():
    res_json = call_api(
        api_desc="设备端操作_查询设备状态",
        api_addr="/devStatus.do",
        req_method="get",
        req_type="json",
        req_data={},
    )

    return res_json


def get_driving_fatigue_param():
    res_json = call_api(
        api_desc="设备端操作_获取疲劳驾驶参数",
        api_addr="/drivingFatigueParam.do",
        req_method="get",
        req_type="json",
        req_data={},
    )
    return res_json


def set_driving_fatigue_param(req_data):
    res_json = call_api(
        api_desc="设备端操作_设置疲劳驾驶参数",
        api_addr="/setDrivingFatigueParam.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )
    return res_json


def get_over_speed_alarm_param():
    res_json = call_api(
        api_desc="设备端操作_获取超速参数",
        api_addr="/overSpeedAlarmParam.do",
        req_method="get",
        req_type="json",
        req_data={},
    )
    return res_json


def set_over_speed_alarm_param(req_data):
    res_json = call_api(
        api_desc="设备端操作_设置超速参数",
        api_addr="/setOverSpeedAlarmParam.do",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )
    return res_json


def get_simulate_alarm():
    res_json = call_api(
        api_desc="设备端操作_查询模拟警报",
        api_addr="/simulateAlarm.do",
        req_method="get",
        req_type="json",
        req_data={},
    )

    return res_json
