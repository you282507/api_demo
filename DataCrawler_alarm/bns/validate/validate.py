# -*- coding: utf-8 -*-
# @Time    : 2020/11/23 14:54
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : validate.py

import os

import allure
import pytest
from tenacity import retry, retry_if_result, wait_fixed, stop_after_attempt, stop_after_delay, before_sleep_log

import config
from base.json_helper import JsonHelper
from base.config_helper import ConfigHelper

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)


class Assert():

    @staticmethod
    def assert_actual_equal_expect(desc_msg, actual_value, expect_value):
        """
        断言方法：expect_value等于actual_value
        :param desc_msg: 需要校验的值
        :param actual_var: 实际值
        :param expect_var: 期望值
        """

        if type(actual_value) != type(expect_value):
            actual_value = str(actual_value)
            expect_value = str(expect_value)

        with allure.step(f'断言校验：{desc_msg},  断言方式: 等于'):
            assert expect_value == actual_value

    @staticmethod
    def assert_actual_contain_expect(desc_msg, actual_value, expect_value):
        """
        断言方法：expect_value被actual_value包含
        :param desc_msg: 对expect_value的一个解释说明(描述下期望值的具体含义)
        :param actual_var: 实际值
        :param expect_var: 期望值
        """

        with allure.step(f'断言校验：{desc_msg},  断言方式: 包含'):
            assert str(expect_value) in str(actual_value)

    @staticmethod
    def assert_actual_notContain_expect(desc_msg, actual_value, expect_value):
        """
        断言方法：expect_value不被actual_value包含
        :param desc_msg: 对不期望被包含内容的一个解释说明
        :param actual_var: 实际值
        :param expect_var: 期望值
        """

        with allure.step(f'断言校验：{desc_msg},  断言方式: 不包含'):
            assert str(expect_value) not in str(actual_value)


class Validate(Assert):

    def validate_code(self, res_json, expect_http_code=200, expect_bns_code=0):
        # http状态码
        http_code = JsonHelper.parseJson_by_objectpath(res_json, "$.response_code")
        Validate.assert_actual_equal_expect("HTTP状态码", http_code, expect_http_code)
        # 业务状态码
        bns_code = JsonHelper.parseJson_by_objectpath(res_json, "$.response_data.code")
        Validate.assert_actual_equal_expect("业务状态码", bns_code, expect_bns_code)

    def extract_data(self, res_json, pattern):
        with allure.step(f"提取数据: {pattern}"):
            areaId_partner = JsonHelper.parseJson_by_objectpath(res_json, pattern, res_allowNone=True,
                                                                res_firstOne=True)
            assert areaId_partner is not False
            return areaId_partner


    # def has_accessRule_list(value):
    #     count = JsonHelper.parseJson_by_objectpath(
    #         value, "count($.response_data..*[@.id and @.name])",
    #     )
    #     if count == 0:
    #         return True
    #     else:
    #         return False
    #
    # @retry(
    #     retry=retry_if_result(has_accessRule_list),
    #     wait=wait_fixed(int(cfgObj.get_value("validate_accessRule_loaded", "retry_interval"))),
    #     stop=stop_after_attempt(
    #         int(cfgObj.get_value("validate_accessRule_loaded", "retry_counts"))) | stop_after_delay(
    #         int(cfgObj.get_value("validate_accessRule_loaded", "retry_timeout"))),
    #     reraise=True,
    # )
    # def validate_accessRule_loaded(self):
    #     """
    #     校验点: 通行时间规则已加载完成
    #     :return:
    #     """
    #     with allure.step("延迟断言校验"):
    #         return bns_api.bns_accessRule_list()



















