import unittest
from logging import getLogger
from time import sleep

from log_logger import define_logger
from upgrade_test import UpgradeTest, PackagesInfo


class MyTestCase(unittest.TestCase):
    up_path = PackagesInfo().package_info.file_1
    up_info = PackagesInfo().package_info.file_1_info
    down_path = PackagesInfo().package_info.file_2
    down_info = PackagesInfo().package_info.file_2_info
    firmware_name = PackagesInfo().package_info.firmware_name_list.split(',')
    cycles = 99
    file_name = "升级结果.txt"

    @classmethod
    def setUpClass(cls):
        cls._logger = getLogger('upgrade.unittest')
        define_logger()
        cls.upgrade_obj = UpgradeTest()
        cls._logger.info("设备断电")
        cls.upgrade_obj.power_control(0, 0)
        cls._logger.info("休眠15s")0
        sleep(15)

    def setUp(self):
        self._logger.info("设备上电")
        self.upgrade_obj.power_control(1, 1)

    def test_promote_and_demote(self):
        upgrade_success = 0
        downgrade_success = 0
        self._logger.info("等待设备启动完成")
        self.upgrade_obj.wait_to_start()
        for i in range(self.cycles):
            msg0 = "第%s次测试：" % upgrade_success
            self._logger.info(msg0)
            self.upgrade_obj.write_content(self.file_name, msg0)
            self._logger.info("准备上传升级包")
            self.upgrade_obj.upload_ota_file(self.up_path)
            self._logger.info("等待解压完成")
            self.upgrade_obj.check_upgrade_start()
            self._logger.info("等待CPU升级开始")
            self.upgrade_obj.cpu_upgrade_start()
            self._logger.info("等待CPU升级完成")
            self.upgrade_obj.cpu_upgrade_end()
            self._logger.info("等待设备启动完成")
            self.upgrade_obj.wait_to_start()
            self._logger.info("休眠300s")
            sleep(300)
            if self.upgrade_obj.check_all_version(self.up_info, self.firmware_name):
                upgrade_success += 1
                msg1 = "升级成功次数：" + str(upgrade_success)
                self._logger.info(msg1)
                self.upgrade_obj.write_content(self.file_name, msg1)

            self._logger.info("准备上传升级包")
            self.upgrade_obj.upload_ota_file(self.down_path)
            self._logger.info("等待解压完成")
            self.upgrade_obj.check_upgrade_start()
            self._logger.info("等待CPU升级开始")
            self.upgrade_obj.cpu_upgrade_start()
            self._logger.info("等待CPU升级完成")
            self.upgrade_obj.cpu_upgrade_end()
            self._logger.info("等待设备启动完成")
            self.upgrade_obj.wait_to_start()
            self._logger.info("休眠300s")
            sleep(300)
            self._logger.info("休眠300s")
            sleep(300)
            if self.upgrade_obj.check_all_version(self.down_info, self.firmware_name):
                downgrade_success += 1
                msg2 = "降级成功次数：" + str(downgrade_success)
                self._logger.info(msg2)
                self.upgrade_obj.write_content(self.file_name, msg2)

    # def test_promote_and_demote_duandian(self):
    #     upgrade_success = 0
    #     downgrade_success = 0
    #     for i in range(self.cycles):
    #         msg0 = "升降级第%s次：" % upgrade_success
    #         self.upgrade_obj.xieru(self.file_name, msg0)
    #         self.upgrade_obj.wait_to_start()
    #         self.upgrade_obj.upload_ota_file(self.up_path)
    #         self.upgrade_obj.check_upgrade_start()
    #         self.upgrade_obj.cpu_upgrade_start()
    #         self.upgrade_obj.cpu_upgrade_end()
    #         self.upgrade_obj.wait_to_start()
    #         sleep(300)
    #         if self.upgrade_obj.check_all_version(self.up_info, self.firmware_name):
    #             upgrade_success += 1
    #             msg1 = "升级成功次数：" + str(upgrade_success)
    #             self.upgrade_obj.xieru(self.file_name, msg1)
    #
    #         self.upgrade_obj.wait_to_start()
    #         self.upgrade_obj.upload_ota_file(self.up_path)
    #         self.upgrade_obj.check_upgrade_start()
    #         self.upgrade_obj.cpu_upgrade_start()
    #         self.upgrade_obj.cpu_upgrade_end()
    #         self.upgrade_obj.wait_to_start()
    #         sleep(300)
    #         if self.upgrade_obj.check_all_version(self.up_info, self.firmware_name):
    #             downgrade_success += 1
    #             msg2 = "降级成功次数：" + str(upgrade_success)
    #             self.upgrade_obj.xieru(self.file_name, msg2)


if __name__ == '__main__':
    unittest.main()
