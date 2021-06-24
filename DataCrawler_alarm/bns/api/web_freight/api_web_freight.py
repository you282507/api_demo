# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:49
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : operate_device.py

from bns.api.web_freight import call_api


def get_vehicle_list():
    req_data = {
        "entId": "2299090585103529875",
        "requestParam.equal.allShowStatus": "-1",
        "requestParam.equal.lt12Ton": "0",
        "requestParam.page": "1",
        "requestParam.rows": "30",
        "sortname": "createTime",
        "sortorder": "asc",
    }

    res_json = call_api(
        is_login=True,
        api_desc="车辆列表",
        api_addr="/carApp/operationSupport/findForListPage.action",
        req_method="post",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


def get_online_status(dev_id):
    req_data = {
        "idArrayStr": dev_id
    }

    res_json = call_api(
        is_login=True,
        api_desc="在线状态",
        api_addr="/carApp/operationSupport/findMarkers.action",
        req_method="post",
        req_type="urlencoded",
        req_data=req_data,
    )

    return res_json


if __name__ == '__main__':
    from base.json_helper import JsonHelper

    from bns.utils import mitmproxy_server

    mitmproxy_server()

    res = get_vehicle_list()
    print(res.get("response_data"))
