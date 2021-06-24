# -*- coding: utf-8 -*-
# @Time    : 2020/4/7 16:23
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : selenium_helper.py

import time

from selenium import webdriver
from airtest_selenium.proxy import WebChrome

import config


class SeleniumHelper():

    def __init__(self, is_proxy=False, is_headless=False):
        """
        :param is_proxy: 默认不使用代理，如果使用代理则，需要先配置config.mitmproxy_server_port
        :param is_headless: 是否为无头模式
        """
        options = webdriver.ChromeOptions()

        # 在无界面模式下, 可以保证元素是可点击的, 否认会抛出异常:MoveTargetOutOfBoundsException
        # 指定浏览器的分辨率
        options.add_argument('--window-size=1920,1080')

        # # 自动允许浏览器左上角的通知提示
        # prefs = {
        #     # "profile.default_content_setting_values.notifications": 1,
        # }
        # options.add_experimental_option("prefs", prefs)
        # options.add_argument('--disable-features=EnableEphemeralFlashPermission')

        # 关闭提示: Chrome正受到自动测试软件的控制
        options.add_argument('--disable-infobars')

        # options.add_argument('--disable-extensions')
        options.add_argument('--enable-notifications')

        # 无界面模式
        if is_headless:
            options.add_argument('--headless')

        # 是否使用代理
        if is_proxy:
            options.add_argument(f"--proxy-server=http://127.0.0.1:{config.mitmproxy_server_port}")

        self.driver = WebChrome(executable_path=config.chrome_driver_path, chrome_options=options)
        self.driver.maximize_window()

    def visit_web(self, url):
        self.driver.get(url)
        return self.driver

    def click(self, css_selector):
        self.driver.find_element_by_css_selector(css_selector).click()

    def send(self, css_selector: str, input_content: str):
        self.driver.find_element_by_css_selector(css_selector).send_keys(input_content)

    def close_web(self):
        time.sleep(5)
        self.driver.close()
