#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger
import pywifi
import time
from pywifi import const


class WifiConnect(object):
    def __init__(self, ssid, pwd):
        self.logger = getLogger('upgrade.wifi')
        self.wifi = pywifi.PyWiFi()  # 创建一个wifi对象
        self.itf = self.wifi.interfaces()[0]  # 取第一个无线网卡
        self.ssid = ssid
        self.pwd = pwd

    def scan_wifi(self):
        """
        扫描附件wifi
        """
        self.itf.scan()  # 扫描附件wifi
        time.sleep(3)
        wifi_list = self.itf.scan_results()
        for i in wifi_list:
            if i.ssid == self.ssid:
                self.logger.debug("搜索到设备wifi:%s", self.ssid)
                return True
        self.logger.error("未搜索到WiFi：%s", self.ssid)
        return False

    def connect_wifi(self, timeout=60):
        self.logger.debug("断开网卡连接")
        self.itf.disconnect()
        while not self.scan_wifi():
            if timeout < 0:
                self.logger.error("无法连接WiFi：%s", self.ssid)
                return False
            self.logger.debug("休眠10s")
            time.sleep(10)
            timeout -= 1

        profile = pywifi.Profile()  # 配置文件
        profile.ssid = self.ssid  # wifi名称
        profile.auth = const.AUTH_ALG_OPEN  # 需要密码
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # 加密类型
        profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
        profile.key = self.pwd  # wifi密码

        self.itf.remove_all_network_profiles()  # 删除其他配置文件
        tmp_profile = self.itf.add_network_profile(profile)  # 加载配置文件
        self.logger.debug("尝试连接WIFI")
        self.itf.connect(tmp_profile)  # 连接
        self.logger.debug("等待3s")
        time.sleep(3)  # 尝试3秒能否成功连接
        if self.itf.status() == const.IFACE_CONNECTED:
            self.logger.debug("成功连接")
            return True
        self.logger.error("连接失败")
        return False
