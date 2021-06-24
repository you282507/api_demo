#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from logging import getLogger
from time import sleep

from check_content.check_text import CheckText
from log_logger import define_logger
from serial_connect import SerialContent
from wifi_control.wifi_connect import WifiConnect
from power_control.power import PowerControl
from P600_API.p600_api import ApiControl
from readconfig import ReadConfig


RELATIVE_PATH = __file__.rsplit("\\", 1)[0]


class DevicesInfo:
    def __init__(self):
        config = ReadConfig(cfg=os.path.join(RELATIVE_PATH, 'config\\devices.config'))
        self.devices_info = config.get_value('Info')
        self.devices_serial = config.get_value('serial')


class PackagesInfo:
    def __init__(self):
        config = ReadConfig(cfg=os.path.join(RELATIVE_PATH, 'config\\upgrade.config'))
        self.package_info = config.get_value('packages')


class UpgradeTest:
    def __init__(self):
        self._logger = getLogger('upgrade.test')
        self.cfg = DevicesInfo()
        self.power_obj = PowerControl(self.cfg.devices_info.local_address, self.cfg.devices_info.port)
        self.wifi_obj = WifiConnect(self.cfg.devices_info.wifi_ssid, self.cfg.devices_info.wifi_pwd)
        self.api_obj = ApiControl(self.cfg.devices_info.device_address)
        self.check = CheckText()
        self.serial_obj = SerialContent(self.cfg.devices_serial.port, self.cfg.devices_serial.baud)

    def power_control(self, out1, out2):
        if self.power_obj.switch_status(1, out1) and \
                self.power_obj.switch_status(2, out2):
            self._logger.info("网络继电器控制成功.out1:%s,out2:%s", out1, out2)
            return True
        return False

    def check_current_state(self, expected):
        # 将字符串转为列表
        if isinstance(expected, str):
            self._logger.info("预期值为字符串。")
            expected = [expected]
        self._logger.info("开始获取串口信息")
        result = self.serial_obj.judgment_content(expected)
        if result:
            self._logger.info("识别成功。")
            return result
        self._logger.warning("识别失败。")
        return False

    def check_upgrade_start(self):
        if not self.check_current_state("Uncompress Ok!"):
            self._logger.warning("升级超时...")
            return False
        return True

    def cpu_upgrade_start(self):
        if not self.check_current_state("Welcome to recovery sys"):
            self._logger.warning("升级超时...")
            return False
        return True

    def cpu_upgrade_end(self):
        if not self.check_current_state("updatesucess"):
            self._logger.warning("升级超时...")
            return False
        return True

    def wait_to_start(self, timeout=30):
        if self.check_current_state("Welcome to HiLinux"):
            self._logger.info("设备系统启动成功。")
        if self.check_current_state("change to AP"):
            self._logger.info("设备热点启动成功。")
        if not self.check_devices_wifi(timeout):
            self._logger.warning("设备开机失败")
            return False
        self._logger.info("设备开机成功")
        return True

    def check_devices_wifi(self, timeout=30):
        while timeout > 0:
            if self.wifi_obj.scan_wifi():
                self._logger.info("检测到设备热点，设备开机成功")
                return True
            self._logger.info("休眠10s，继续搜索设备热点")
            sleep(10)
            timeout -= 1
        self._logger.warning("未检测到设备热点")
        return False

    def upload_ota_file(self, package_file):
        if not self.wifi_obj.connect_wifi():
            self._logger.warning("连接设备热点失败")
            return False
        if not self.api_obj.upgrade(package_file):
            return False
        self._logger.info("升级文件上传成功！")
        return True

    def get_current_version(self, timeout=30):
        self._logger.info("开始连接设备WiFi")
        if not self.wifi_obj.connect_wifi():
            return False
        while timeout > 0:
            current_version = self.api_obj.get_base_status()
            if current_version:
                return current_version
            sleep(10)
            timeout -= 1
        return False

    def check_all_version(self, expected, firmware_name_list):
        geshu = len(firmware_name_list)
        actual = self.get_current_version()
        for firmware_name in firmware_name_list:
            if not self.check.check_version(actual, expected, firmware_name):
                geshu -= 1
        if geshu == len(firmware_name_list):
            return True
        return False

    def write_content(self, file_path, content):
        self._logger.info(content)
        with open(file_path, 'a') as file_obj:
            file_obj.write(content)
            file_obj.write('\r')

    def wait_sleep(self, sleep_1, sleep_2):
        sleep(sleep_1)
        self.power_control(0, 0)
        sleep(15)
        sleep(sleep_2)


