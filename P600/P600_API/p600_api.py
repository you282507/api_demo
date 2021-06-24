#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from logging import getLogger
import requests
from readconfig import ReadConfig


class ApiControl:
    def __init__(self, device_address):
        self.dev_address = device_address
        self.logger = getLogger('upgrade.api')

    def get_base_status(self):
        url = self.dev_address + '/baseStatus.do'
        self.logger.info("URL:%s", url)
        r = requests.get(url=url)
        r_code = r.status_code
        if r_code != 200:
            self.logger.warning("获取失败，错误码为：%s", r_code)
            return False
        self.logger.debug("获取成功，返回码为：%s", r_code)
        return r.json()

    def upgrade(self, upload_packages_path):
        url = self.dev_address + '/upload.do'
        self.logger.debug("URL:%s", url)
        files = {'file': open(upload_packages_path, 'rb')}
        self.logger.debug("files:%s", files)
        self.logger.info("开始上传文件！")
        upload_res = requests.post(url=url, files=files)
        self.logger.info(upload_res.text.strip("\r\n"))
        if upload_res:
            return True
        return False

    def get_dev_status(self):
        url = self.dev_address + '/devStatus.do'
        self.logger.info("URL:%s", url)
        r = requests.get(url=url)
        r_code = r.status_code
        if r_code != 200:
            self.logger.warning("获取失败，错误码为：%s", r_code)
            return False
        self.logger.debug("获取成功，返回码为：%s", r_code)
        return r.json()

    def get_ic_card_info(self):
        url = self.dev_address + '/ICCardInfo.do'
        self.logger.info("URL:%s", url)
        r = requests.get(url=url)
        r_code = r.status_code
        if r_code != 200:
            self.logger.warning("获取失败，错误码为：%s", r_code)
            return False
        self.logger.debug("获取成功，返回码为：%s", r_code)
        return r.json()


class PackagesInfo:
    def __init__(self):
        RELATIVE_PATH = __file__.rsplit("\\", 1)[0]
        config = ReadConfig(cfg=os.path.join(RELATIVE_PATH, '../config/upgrade.config'))
        self.package_info = config.get_value('packages')


if __name__ == '__main__':
    A = ApiControl("http://192.168.1.1:8080")
    a = A.get_base_status()
    firmware_name_list = ['mcuVer', 'pwrMcuVer', 'firmwareVer', 'oemSfVer']
    for firmware_name in firmware_name_list:
        print("%s:%s" % (firmware_name, a[firmware_name]))
    # down_path = PackagesInfo().package_info.file_2
    # down_info = PackagesInfo().package_info.file_2_info
    # b = A.upgrade(r"D:\我的下载\RD_C020_01_V03R001B020_part_20201223034917.tar.gz")
    # print(b)


