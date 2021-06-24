#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from ast import literal_eval
from logging import getLogger
from time import sleep

from log_logger import define_logger
from wifi_control.wifi_connect import WifiConnect
from power_control.power import PowerControl
from P600_API.p600_api import ApiControl
from readconfig import ReadConfig
from audio_to_text.audio_to_text import AudioRecognition

RELATIVE_PATH = __file__.rsplit("\\", 1)[0]


class DevicesInfo:
    def __init__(self):
        config = ReadConfig(cfg=os.path.join(RELATIVE_PATH, 'config\\devices.config'))
        self.devices_info = config.get_value('Info')


class PackagesInfo:
    def __init__(self):
        config = ReadConfig(cfg=os.path.join(RELATIVE_PATH, 'config\\upgrade.config'))
        self.package_info = config.get_value('packages')


class UpgradeTest:
    def __init__(self):
        self.logger = getLogger('upgrade.test')
        self.cfg = DevicesInfo().devices_info
        self.power_obj = PowerControl(self.cfg.local_address, self.cfg.port)
        self.wifi_obj = WifiConnect(self.cfg.wifi_ssid, self.cfg.wifi_pwd)
        self.api_obj = ApiControl(self.cfg.device_address)
        self.recognition_obj = AudioRecognition()

    def power_control(self, out1, out2):
        if self.power_obj.switch_status(1, out1) and \
                self.power_obj.switch_status(2, out2):
            self.logger.info("网络继电器控制成功")
            return True
        return False

    def check_boot(self, timeout=30):
        if not self.check_status("一路平安"):
            self.logger.warning("等待播放开机语音超时。")
        else:
            self.logger.info("设备启动语音播报完成")
        while timeout > 0:
            if self.wifi_obj.scan_wifi():
                self.logger.info("检测到设备热点，设备开机成功")
                return True
            self.logger.info("休眠10s，等待搜索到设备热点")
            sleep(10)
            timeout -= 1
        self.logger.warning("设备开机失败")
        return False

    def upload_ota_file(self, package_file):
        if not self.wifi_obj.connect_wifi():
            self.logger.warning("连接设备热点失败")
            return False
        if not self.api_obj.upgrade(package_file):
            return False
        self.logger.info("升级文件上传成功！")
        return True

    def check_upgrade_status(self):
        # if not self.check_status("升级开始"):
        #     self.logger.warning("开始升级超时...")
        #     return False
        self.logger.info("固件升级开始...")
        sleep(90)
        upgrade_status = self.check_status(("成功", "失败"))
        if not upgrade_status:
            self.logger.warning("升级超时...")
            return False
        if upgrade_status == "成功":
            self.logger.info("固件升级成功！！！")
            return True
        elif upgrade_status == "失败":
            self.logger.warning("固件升级失败！")
            return False
        else:
            self.logger.warning("升级错误！")
            return False

    def check_devices_wifi(self, timeout=30):
        while timeout > 0:
            if self.wifi_obj.scan_wifi():
                self.logger.info("检测到设备热点，设备开机成功")
                return True
            self.logger.info("休眠10s，继续搜索设备热点")
            sleep(10)
            timeout -= 1
        self.logger.warning("未检测到设备热点")
        return False

    def check_version(self, expected, template, firmware_name):
        self.logger.info("预期升级完成的版本信息：\n%s", expected)
        expected = self.str_to_dict(expected)
        template = self.str_to_dict(template)
        if not (expected and template):
            return False
        if isinstance(firmware_name, list):
            ver_number = len(firmware_name)
            for name in firmware_name:
                expected_ver = expected[name]
                template_ver = template[name]
                if expected_ver != template_ver:
                    msg = name + ':预期版本：' + template_ver + ",实际版本：" + expected_ver
                    self.logger.info("该固件升级失败：%s", str(msg))
                    ver_number -= 1
                else:
                    self.logger.info("%s固件升级成功:", name)
            if ver_number == len(firmware_name):
                self.logger.info("固件版本核对成功", )
                return True
            return False
        elif isinstance(firmware_name, str):
            expected_ver = expected[firmware_name]
            template_ver = template[firmware_name]
            if expected_ver != template_ver:
                msg = firmware_name + ':预期版本：' + template_ver + ",实际版本：" + expected_ver
                self.logger.info("该固件升级失败：%s", str(msg))
                return False
            self.logger.info("%s固件升级成功:", firmware_name)
            return True

    def get_upgrade_ver(self, timeout=30):
        while timeout > 0:
            self.logger.info("开始连接设备WiFi")
            if not self.wifi_obj.connect_wifi():
                return False
            current_version = self.api_obj.get_base_status()
            if current_version:
                return current_version
            sleep(10)
            timeout -= 1
        return False

    def str_to_dict(self, value_str):
        if not isinstance(value_str, dict):
            try:
                value_str = literal_eval(value_str)
            except ValueError:
                self.logger.info("传入值的类型：%s", type(value_str))
                self.logger.warning("预期输入值得类型错误")
                return False
            return value_str
        return value_str

    def start_upgrade(self, file_path, file_ver, firmware, timeout=30):
        if self.upload_ota_file(file_path):
            upgrade_status = None
            firmware_list = ['主MCU', '电源MCU', 'CPU', '副MCU']
            for name in firmware_list:
                if not self.check_upgrade_status():
                    self.logger.warning("%s升级失败", name)
                else:
                    self.logger.info("%s升级成功", name)
            while timeout > 0:
                current_version = self.get_upgrade_ver()
                if not current_version:
                    return False
                if not upgrade_status:
                    if self.check_version(file_ver, current_version, firmware):
                        upgrade_status = True
                else:
                    result = self.check_version(file_ver, current_version, "oemSfVer")
                    self.logger.info("oemSfVer结果：%s", result)
                    if result:
                        return True
                    self.logger.info("等待30s")
                    sleep(30)
                    timeout -= 1
        self.logger.warning("该版本升级失败！！")
        return False

    def check_status(self, expected, timeout=100):
        if isinstance(expected, str):
            expected_list = [expected]
            expected = tuple(expected_list)
        while timeout > 0:
            result = self.recognition_obj.check_content(expected)
            if result:
                self.logger.info("识别成功")
                return result
        return False


LOGGER = getLogger('upgrade.run_upgrade_test')


def run_upgrade_test(count, ver1_path, ver1_info, ver2_path, ver2_info, firmware):
    upgrade_obj = UpgradeTest()
    if not upgrade_obj.power_control(1, 1):
        return False
    LOGGER.info("休眠60s，等待开机。")
    sleep(60)
    # 检查是否开机成功
    if not upgrade_obj.check_boot():
        return False
    upgrade_success = 0
    downgrade_success = 0
    for i in range(count):
        LOGGER.info("开始执行第%s次升降级测试", i+1)
        if upgrade_obj.start_upgrade(ver1_path, ver1_info, firmware):
            upgrade_success += 1
            LOGGER.info("升级次数:+1")
        if upgrade_obj.start_upgrade(ver2_path, ver2_info, firmware):
            downgrade_success += 1
            LOGGER.info("降级次数:+1")
        LOGGER.info("共执行升降级次数:%s", i+1)
        LOGGER.info("升级成功次数:%s", upgrade_success)
        LOGGER.info("降级成功次数:%s", downgrade_success)
    LOGGER.info("测试完成。")


if __name__ == '__main__':
    define_logger()
    up_path = PackagesInfo().package_info.file_1
    up_info = PackagesInfo().package_info.file_1_info
    down_path = PackagesInfo().package_info.file_2
    down_info = PackagesInfo().package_info.file_2_info
    firmware_name = PackagesInfo().package_info.firmware_name_list.split(',')
    run_upgrade_test(2, up_path, up_info, down_path, down_info, firmware_name)
    # run_upgrade_test(2, down_path, down_info, up_path, up_info, firmware_name)


