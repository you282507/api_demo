# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:49
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : operate_device.py

from bns.api.web_nanjing import call_api


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


if __name__ == '__main__':
    from bns.utils import mitmproxy_server

    mitmproxy_server()

    res = get_vehicle_list()
    print(res)
