# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 16:23
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : json_helper.py

import re
import json
import types
import objectpath

from requests_toolbelt.multipart.encoder import MultipartEncoder

from base.exceptions import ObjectpathParseInputException, ObjectpathExtractNullException, ObjectpathPatternException


class MyEncoder(json.JSONEncoder):
    '''
        # 对于不能序列化的数据, 确定处理方案
    '''

    def default(self, obj):

        if isinstance(obj, bytes):
            return obj.__str__()

        elif isinstance(obj, MultipartEncoder):
            obj_str = obj.__str__()
            res = re.search("<MultipartEncoder: (.*)>", obj_str)  # 使用贪婪匹配
            return res.group(1)

        return json.JSONEncoder.default(self, obj)


class JsonHelper():

    @staticmethod
    def json_format(json_dict):
        """
        功能：json字典 --> 带缩进格式的json字符串
        :param json_dict: 字典
        :return: 返回带缩进格式的json字符串
        """

        if not isinstance(json_dict, dict):
            raise Exception("json_dict数据类型必须为字典")

        return json.dumps(json_dict, cls=MyEncoder, sort_keys=True, indent=4, ensure_ascii=False)

    @staticmethod
    def parseJson_by_objectpath(json_dict: (dict, str), pattern: str, res_allowNone=False, res_firstOne=False):
        """
        功能: 输入表达式来提取json中的内容
        PS：关于表达式pattern的规则，请参考：http://objectpath.org/reference.html
        :param json_dict: 字典类型或字符串类型
        :param pattern: 提取信息表达式
        :param res_allowNone: 是否允许提取不到信息, 默认False
        :param res_firstOne:  如果返回的是一个非空列表, 是否返回列表的首个元素, 默认False
        :return: 返回提取到的内容 或 直接抛出异常
        """

        if not json_dict:
            raise ObjectpathParseInputException(f"入参校验失败：入参json_dict为空值")

        # 如果是字符串, 先转为字典数据. 即传入的字符串必须是可以转为字典的字符串
        if isinstance(json_dict, str):
            try:
                json_dict = json.loads(json_dict)
            except Exception:
                raise ObjectpathParseInputException(f"入参校验失败: 输入字符串无法转为字典数据, json_dict: {json_dict}")

        if not isinstance(json_dict, dict):
            raise ObjectpathParseInputException(f"入参校验失败：入参数据类型不是字典类型, {type(json_dict)}")

        try:
            tree = objectpath.Tree(json_dict)
            res = tree.execute(pattern)

            import itertools
            if isinstance(res, (types.GeneratorType, itertools.chain)) is True:
                res_list = list(res)
                if len(res_list) > 0:
                    if res_firstOne:
                        return res_list[0]
                    return res_list
                else:
                    if res_allowNone:
                        return False
                    raise ObjectpathExtractNullException(f"提取表达式：{pattern}，此时传入的json内容为{json_dict}")
            else:
                if res is None:
                    if res_allowNone:
                        return False
                    raise ObjectpathExtractNullException(f"提取表达式：{pattern}，此时传入的json内容为{json_dict}")
                return res

        except Exception as e:
            raise ObjectpathPatternException(f"提取表达式：{pattern}，此时传入的json内容为{json_dict}")
