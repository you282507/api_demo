#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


class OperationalError(Exception):
    """operation error."""


class Dictionary(dict):
    """ custom dict."""
    def __getattr__(self, key):
        return self.get(key, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ReadConfig:
    """
    Read Config
    """
    def __init__(self, file_name="config", cfg=None):
        """
        @param file_name: file name without extension.
        @param cfg: configuration file path.
        """
        config = configparser.ConfigParser()
        if cfg:
            config.read(cfg)
        else:
            config.read(
                os.path.join(CURRENT_DIR, "conf", "%s.conf" % file_name))
        for section in config.sections():
            setattr(self, section, Dictionary())
            for name, raw_value in config.items(section):
                try:
                    if config.get(section, name) in ["0", "1"]:
                        raise ValueError
                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        value = config.get(section, name)
                setattr(getattr(self, section), name, value)

    def get_value(self, section):
        """Get option.
        @param section: section to fetch.
        @return: option value.
        """
        try:
            return getattr(self, section)
        except AttributeError as error:
            raise OperationalError("Option %s is not found"
                                   " in configuration, error: %s" %
                                   (section, error))
