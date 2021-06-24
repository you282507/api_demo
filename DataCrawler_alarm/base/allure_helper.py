# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 12:30
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : allure_helper.py

import os
import json

from requests import Response


class MyEncoder(json.JSONEncoder):
    '''
        # 对于不能序列化的数据, 确定处理方案
    '''

    def default(self, obj):
        if isinstance(obj, Response):
            return obj.__str__()

        return json.JSONEncoder.default(self, obj)


class AllureHelper():

    @staticmethod
    def attachText(title: str, body: (str, dict)) -> None:
        """
        :param title: 文本标题
        :param body: 文本内容
        :return: None
        """

        if isinstance(body, dict):
            body = str(body)

        if not isinstance(body, str):
            raise Exception(f"文本内容的类型必须为str,当前为:{type(body)}")

    @staticmethod
    def attachJson(title: str, dict_data: dict):
        """
        :param title: 文本标题
        :param dict_data: 字典数据(通过json.dumps方法转为格式化的json字符串数据)
        :return:
        """

        try:
            body = json.dumps(dict_data, cls=MyEncoder, sort_keys=True, indent=4, ensure_ascii=False)
        except Exception as e:
            AllureHelper.attachText(title, dict_data)

