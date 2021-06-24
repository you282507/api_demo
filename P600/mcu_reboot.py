import random
from time import sleep
from log_logger import define_logger
from upgrade_test import UpgradeTest


class McuRebootTest(UpgradeTest):
    def check_ic_card_info(self):
        ic_card_info = self.api_obj.get_ic_card_info()
        self._logger.info("IC卡信息：%s", ic_card_info)
        ic_card_keys = ['driverName',
                        'drivingLicenseNum',
                        'drivingLicenseValidTerm',
                        'qualificationNum',
                        'qualificationValidTerm',
                        'certifyingAuthority']
        for key in ic_card_keys:
            if not ic_card_info[key]:
                self._logger.warning("%s信息为空", key)
                return False
        return ic_card_info

    def run_mcu_reboot_test(self):
        self._logger.info("设备断电")
        if not self.power_control(0, 0):
            return False
        sleep_time = random.randint(30, 180)
        self._logger.info("等待%s", sleep_time)
        sleep(sleep_time)
        self._logger.info("设备上电")
        if not self.power_control(1, 1):
            return False
        self._logger.info("等待设备启动")
        if not self.wait_to_start():
            return False
        self._logger.info("连接设备热点")
        if not self.wifi_obj.connect_wifi():
            self._logger.warning("连接设备热点失败")
            return False
        self._logger.info("等待60s")
        sleep(60)
        self._logger.info("开始查询IC卡信息")
        if not self.check_ic_card_info():
            return False
        return True


if __name__ == '__main__':
    define_logger()
    MCU_OBJ = McuRebootTest()
    bout = 9999999
    file_name = "MCU.txt"
    for i in range(bout):
        IC_CARD_INFO = MCU_OBJ.run_mcu_reboot_test()
        if not IC_CARD_INFO:
            msg = f"第{i}次测试，测试结果：失败"
        else:
            msg = f"第{i}次测试，测试结果：成功"
        MCU_OBJ.write_content(file_name, msg)
