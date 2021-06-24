import os
from logging import getLogger
from time import sleep

from power_control.power import PowerControl
from readconfig import ReadConfig
from wifi_control.wifi_connect import WifiConnect
from P600_API.p600_api import ApiControl
from audio_to_text.audio_to_text import AudioRecognition
from check_content.check_text import CheckText


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
        self._logger = getLogger('upgrade.test')
        self.cfg = DevicesInfo().devices_info
        self.power_obj = PowerControl(self.cfg.local_address, self.cfg.port)
        self.wifi_obj = WifiConnect(self.cfg.wifi_ssid, self.cfg.wifi_pwd)
        self.api_obj = ApiControl(self.cfg.device_address)
        self.recognition_obj = AudioRecognition()
        self.check = CheckText()

    def power_control(self, out1, out2):
        if self.power_obj.switch_status(1, out1) and \
                self.power_obj.switch_status(2, out2):
            self._logger.info("网络继电器控制成功")
            return True
        return False

    def check_current_state(self, expected, timeout=100):
        # 将字符串转为列表
        if isinstance(expected, str):
            self._logger.info("预期值为字符串。")
            expected = [expected]
        while timeout > 0:
            self._logger.info("核对次数：%d", timeout)
            audio_content = self.recognition_obj.audio_to_text()
            self._logger.info("音频识别内容：%s", audio_content)
            result = self.check.check_content(expected, audio_content)
            self._logger.info("与预期一致的结果：%s", result)
            if result:
                self._logger.info("识别成功。")
                return result
            self._logger.warning("识别失败。")
            timeout -= 1
        return False

    def check_upgrade_status(self, sleep_time):
        # if not self.check_current_state("升级开始"):
        #     self._logger.warning("开始升级超时...")
        #     return False
        self._logger.info("固件升级开始...,休眠%s秒", sleep_time)
        sleep(sleep_time)
        upgrade_status = self.check_current_state(["成功", "失败"])
        if not upgrade_status:
            self._logger.warning("升级超时...")
            return False
        if upgrade_status == "成功":
            self._logger.info("固件升级成功！！！")
            return True
        elif upgrade_status == "失败":
            self._logger.warning("固件升级失败！")
            return True
        else:
            self._logger.warning("升级错误！")
            return False

    def wait_to_start(self, timeout=30):
        if not self.check_current_state("一路平安"):
            self._logger.warning("等待播放开机语音超时。")
        else:
            self._logger.info("设备启动语音播报完成")
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

