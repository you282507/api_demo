# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:49
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : operate_device.py

from bns.api.web_rw import call_api


def get_realtime_location(devId: int):
    req_data = {
        "vehicleIdList": [int(devId)]
    }

    res_json = call_api(
        is_login=True,
        api_desc="获取车辆实时信息",
        api_addr="/vmp/real-time/realtime-location",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def get_alarm_detail(alarmId):
    req_data = {
        "alarmId": alarmId,
    }

    res_json = call_api(
        is_login=True,
        api_desc="获取告警详情",
        api_addr="/vmp/alarm/testimony/detail",
        req_method="get",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


def get_video_list(devId):
    req_data = {
        "vehicleId": devId,
        "channelId": 1,
        "mediaType": "AUDIOVIDEO",
        "codeStreamType": 0,
        "storageType": 0,
        "startTime": "2020-12-15 00:00:00",
        "endTime": "2020-12-15 23:59:59",
    }

    res_json = call_api(
        is_login=True,
        api_desc="获取录像列表",
        api_addr="/vmp/replay",
        req_method="get",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


def send_tts_msg(devId):
    req_data = {
        "context": "现在测试TTS语音播报",
        "messageTypeEnumList": [
            "TTS"
            ],
        "ttsMessageTypeEnum": "CENTER_NAVIGATION",
        "vehicleIdList": [
            devId
            ]
        }

    res_json = call_api(
        is_login=True,
        api_desc="下发tts消息",
        api_addr="/vmp/text",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def take_picture(devId, channelId="ADAS_SHOOT", dpi="DPI_1024_768", shootCmd=1, time=0):
    req_data = {
        "channelId": channelId,
        "chroma": 128,
        "contrast": 64,
        "dpi": dpi,
        "luminance": 125,
        "quality": 5,
        "saturation": 64,
        "saveFlag": "UPLOAD",
        "shootCmd": shootCmd,
        "shootType": "TAKE_PHOTOS",
        "time": time,
        "vehicleId": devId
        }

    res_json = call_api(
        is_login=True,
        api_desc="拍照功能",
        api_addr="/vmp/terminal/shoot",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def get_alarm_info(vehicleNo, data_time, current, size=20):
    vehicleId = get_vehicle_id(vehicleNo)
    req_data = {
        "current":current,
        "size":size,
        "startTime": data_time + r" 00:00:00",
        "endTime": data_time + r" 23:59:59",
        "vehicleId":vehicleId
    }
    res_json = call_api(
        is_login=True,
        api_desc="获取主动安全报警",
        api_addr="/vmp/alarm/testimony/list",
        req_method="get",
        req_type="json",
        req_data=req_data,
    )

    return res_json


def get_vehicle_id(vehicleNo):
    req_data = {
        "vehicleNo": vehicleNo
    }

    res_json = call_api(
        is_login=True,
        api_desc="获取设备ID",
        api_addr="/vmp/vehicles/pop-up",
        req_method="post",
        req_type="json",
        req_data=req_data,
    )
    vehicle_id = res_json["response_data"]["data"][0]["id"]
    return vehicle_id
