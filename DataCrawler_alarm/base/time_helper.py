# -*- coding: utf-8 -*-
# @Time    : 2020/3/27 23:51
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : time_helper.py

import time
import datetime

_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TimeHelper():

    @staticmethod
    def get_time_from_timestamp(timestamp=None, time_format=None):
        """
        功能：将一个时间戳转为指定时间格式的时间，默认转为的时间格式为：%Y-%m-%d %H:%M:%S
            场景1：获取当前时间，时间格式为：%Y-%m-%d %H:%M:%S
                get_time_from_timestamp()
            场景2：获取当前时间，时间格式为：%H:%M:%S
                get_time_from_timestamp(time_format="%H:%M:%S")
            场景3：根据指定时间戳来获取时间，时间格式为：%Y-%m-%d %H:%M:%S
                get_time_from_timestamp(timestamp=1569850832)
        :param timestamp: 待转换为时间的时间戳，默认为当前时间戳
        :param time_format: 待转换成的时间格式，默认时间格式：%Y-%m-%d %H:%M:%S
        :return: 返回一个指定格式的时间
        """

        if time_format is None:
            time_format = _TIME_FORMAT

        if timestamp is None:
            return datetime.datetime.now().strftime(time_format)

        local_time = time.localtime(timestamp)
        time_data = time.strftime(time_format, local_time)
        return time_data

    @staticmethod
    def get_timestamp_from_time(assigned_time=None, magnitude="s"):
        """
        功能：将一个形如"2019-10-10 09:00:00"的时间转为时间戳
            场景1：获取当前秒级时间戳
                get_timestamp_from_time()
            场景2：获取当前毫秒级时间戳
                get_timestamp_from_time(magnitude="ms")
            场景3：获取指定时间(2019-10-10 09:00:00)对应的秒级时间戳
                get_timestamp_from_time(assigned_time="2019-10-10 09:00:00")
        :param assigned_time: 需要转为时间戳的时间，时间格式要求：2019-10-10 09:00:00
        :param magnitude: 时间戳数量级：秒(s)、毫秒(ms)、微妙(us)
        :return: 返回一个时间戳
        """

        if magnitude == "s":
            factor = 1
        elif magnitude == "ms":
            factor = 1000
        elif magnitude == "us":
            factor = 1000000
        else:
            raise Exception("不期望的magnitude值：{}".format(magnitude))

        if assigned_time is None:
            return int(time.time() * factor)

        t = time.strptime(assigned_time, _TIME_FORMAT)
        return int(time.mktime(t) * factor)

    @staticmethod
    def get_custom_time(timestamp_offset, assigned_time=None):
        """
        功能：获取一个相对时间(相对于某个时间超前或滞后)
            场景1：获取超前于当前时间10s的时间
                get_custom_time(timestamp_offset=10)
            场景2：获取滞后于当前时间10s的时间
                get_custom_time(timestamp_offset=-10)
            场景2：获取超前于"2019-10-01 09:09:09"时间20s的时间
                get_custom_time(timestamp_offset=20, assigned_time="2019-10-01 09:09:09")
        :param assigned_time: 参数时间点，默认为当前时间(格式：%Y-%m-%d %H:%M:%S)
        :param timestamp_offset: 秒级时间戳偏移量(正整数表示超前m秒，负整数表示滞后m秒)
        :return: 返回一个时间，时间格式为：%Y-%m-%d %H:%M:%S
        """

        if assigned_time is None:
            assigned_time = TimeHelper.get_time_from_timestamp()

        # TODO: 通过正则来校验参数格式为：%Y-%m-%d %H:%M:%S
        timestamp = TimeHelper.get_timestamp_from_time(assigned_time)
        new_timestamp = timestamp + timestamp_offset
        return TimeHelper.get_time_from_timestamp(timestamp=new_timestamp)
