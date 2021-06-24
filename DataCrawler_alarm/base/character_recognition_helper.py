# -*- coding: utf-8 -*-
# @Time    : 2020/11/15 20:44
# @Author  : chinablue
# @File    : character_recognition_helper.py

from aip import AipOcr

from base.http_helper import HttpHelper
from base.picture_helper import PictureHelper
from base.json_helper import JsonHelper


class CharacterRecognitionHelper():
    """
    文字识别
    """

    @staticmethod
    def recognition_by_ttshitu(image_path):
        """
        官网：http://www.ttshitu.com/price.html?spm=null
        :param image_path:
        :return:
        """
        request = HttpHelper(verbose=True)

        req_url = r"http://api.ttshitu.com/base64"
        extra_headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        req_method = "post"

        req_type = "json"

        req_data = {
            "username": "qq1468838728",
            "password": "Dj123456",
            "typeid": "3",
            "image": PictureHelper.pic_to_base64(image_path)
        }

        resp = request.build_request(
            extra_headers=extra_headers,  # 补充请求头信息
            request_url=req_url,  # 请求地址
            request_method=req_method,  # 请求方法
            content_type=req_type,  # 请求内容类型
            request_data=req_data,  # 请求数据
        )

        resp = JsonHelper.parseJson_by_objectpath(resp, "$.response_data.data.result")

        return resp

    @staticmethod
    def recognition_simply_number_by_baidu(image_path):
        # baidu的OCR接口: https://login.bce.baidu.com/

        app_id = "18171032"
        api_key = "Q7CiBp0IDAlZb3efRL1fAhig"
        secret_key = "7DY8yTlKKaTI3Q0s8X6HfGAEi4KW0iAr"

        client = AipOcr(app_id, api_key, secret_key)

        # 定义一些参数
        options = {
            # 默认是CHN_ENG (中英文混合)
            "language_type": "ENG"
        }

        with open(image_path, 'rb') as fp:
            results = client.numbers(fp.read(), options=options)

        resp = JsonHelper.parseJson_by_objectpath(results, "$.words_result..words", res_firstOne=True)

        return resp
