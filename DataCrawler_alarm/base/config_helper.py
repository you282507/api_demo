# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 12:30
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : allure_helper.py

import os

import configparser


class ConfigHelper():

    def __init__(self, file_path):

        self.file_path = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFoundError("请确保配置文件存在！")

        self.cfg = self._read_cfg()

    def _read_cfg(self):
        read_cfg = configparser.ConfigParser()
        read_cfg.read(self.file_path, encoding="utf-8")
        return read_cfg

    def get_value(self, title, key):
        try:
            value = self.cfg.get(title, key)
        except:
            value = None
        return value

    def set_value(self, title, key, value):
        if isinstance(value, dict):
            import json
            value = json.dumps(value)

        self.cfg.set(title, key, value)
        with open(self.file_path, "w+") as f:
            return self.cfg.write(f)
