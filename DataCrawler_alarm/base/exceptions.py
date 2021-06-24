# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 20:48
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : exceptions.py


class ObjectpathParseInputException(Exception):
    """
    如果入参为字符串,且无法转为字典数据时, 则抛出此异常
    """
    pass


class ObjectpathExtractNullException(Exception):
    """
    如果提取结果为空值, 则抛出此异常
    """
    pass


class ObjectpathPatternException(Exception):
    """
    如果objectpath的提取表达式(pattern)写错了, 则抛出此异常
    """
    pass
