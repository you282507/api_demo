# -*- coding: utf-8 -*-
# @Time    : 2020/4/8 10:25
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : image_helper.py

import base64

class PictureHelper():

    @staticmethod
    def pic_to_base64(pic_path):
        """
        功能：将1张图片转base64码
        :param pic_path: 图片的绝对路径
        :return: 图片的base64码
        """
        with open(pic_path, 'rb') as fp:
            return base64.b64encode(fp.read()).decode("utf-8")

    @staticmethod
    def pic_to_bytes(pic_path):
        """
        功能：将1张图片转字节码
        :param pic_path: 图片的绝对路径
        :return: 图片的字节码
        """
        with open(pic_path, 'rb') as fp:
            return fp.read()

    @staticmethod
    def base64_to_pic(base64_str, pic_name):
        """
        功能：将base64码转图片
        :param base64_str: 图片的base64编码
        :param pic_name: 图片的名称
        :return:
        """
        with open(pic_name, "wb") as f:
            f.write(base64.b64decode(base64_str))