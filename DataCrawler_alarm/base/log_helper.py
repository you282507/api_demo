# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 13:48
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : log_helper.py

import logging


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class LogHelper(object):

    def __init__(self):
        log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fomat)

    def get_logobj(self):
        return logging.getLogger(__name__)

    def log_info(self, msg):
        logging.info(msg)

    def log_warning(self, msg):
        logging.warning(msg)

    def log_error(self, msg):
        logging.error(msg)


if __name__ == '__main__':
    mlog = LogHelper()

    mlog.log_info('i am info')
    mlog.log_warning('i am warning')
    mlog.log_error('i am error')
