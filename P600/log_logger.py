#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import os


def define_logger():
    """
    LOG define logger
    :return: None
    """
    logger = logging.getLogger("upgrade")
    logger.setLevel(logging.INFO)
    log_format = '%(asctime)s - %(name)s - %(filename)s[line:%(lineno)d]-' \
                 '%(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    log_name = time.strftime('%Y%m%d_%H%M%S')
    dir_name = 'log'
    result = os.path.exists(dir_name)
    if not result:
        os.makedirs(dir_name)
    file_handler = logging.FileHandler(".\\log\\log_%s.log" % log_name)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(stream=None)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
