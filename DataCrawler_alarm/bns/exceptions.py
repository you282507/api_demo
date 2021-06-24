# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 20:48
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : exceptions.py


class WifiNotFoundException(Exception):
    """
    如果wifi名称搜索不到, 则抛出此异常
    """
    pass


class WifiConnectException(Exception):
    """
    如果wifi无法连接成功, 则抛出此异常
    """
    pass


class RequestUrlParamsNotExistException(Exception):
    """
    在请求地址带有参数的情况下
    如果此参数不存在于输入数据中, 则抛出此异常
    """
    pass


class RequestDomainExtraPortException(Exception):
    """
    请求域名后如果添加了端口, 则抛出此异常
    """
    pass


class RequestDomainFormatException(Exception):
    """
    请求域名或请求IP端口格式错误, 则抛出此异常
    """
    pass


class ConfigParamsMissingException(Exception):
    """
    如果配置参数缺失, 则抛出此异常
    """
    pass


class VideoParamsException(Exception):
    """
    播放视频场景下, 入参出现异常时, 则抛出此异常
    """
    pass


class VideoFileException(Exception):
    """
    播放视频场景下, 视频文件出现异常时, 则抛出此异常
    """
    pass


class WebLoginFailedException(Exception):
    """
    如果模拟web登录失败了, 则抛出此异常
    """
    pass

class ApiCertificationExpireException(Exception):
    """
    如果调用业务api时认证信息过期了, 则抛出此异常
    """
    pass
