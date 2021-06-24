# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import literal_eval
from logging import getLogger


class CheckText:
    def __init__(self):
        self._logger = getLogger('upgrade.check')

    def str_to_dict(self, value_str):
        if not isinstance(value_str, dict):
            try:
                value_str = literal_eval(value_str)
            except ValueError:
                self._logger.info("传入值的类型：%s", type(value_str))
                self._logger.warning("预期输入值得类型错误")
                return False
        return value_str

    def check_content(self, expected, actual):
        self._logger.debug("实际值结果：%s", actual)
        if not actual:
            self._logger.warning("实际值为空！")
            return False
        for exp in expected:
            msg = "预期值：" + exp + "   实际值：" + str(actual)
            self._logger.info(msg)
            if actual.find(exp) == -1:
                self._logger.warning("实际值未包含预期值！")
            else:
                return exp
        return False

    def check_version(self, actual, expected, firmware_name):
        self._logger.info("预期升级完成的版本信息：\n%s", actual)
        # 转换类型
        actual = self.str_to_dict(actual)
        expected = self.str_to_dict(expected)
        # 判断是否都转为字典
        if not (actual and expected):
            return False
        if isinstance(firmware_name, str):
            actual_ver = actual[firmware_name]
            expected_ver = expected[firmware_name]
            if actual_ver != expected_ver:
                msg = firmware_name + ':预期版本：' + expected_ver + ",实际版本：" + actual_ver
                self._logger.info("该固件升级失败：%s", str(msg))
                return False
            self._logger.info("%s固件升级成功:", firmware_name)
            return True
        return False
