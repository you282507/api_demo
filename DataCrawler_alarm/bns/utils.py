# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 16:40
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : utils.py

"""
    一些业务辅助工具
"""

import os
import time
import logging
import socket
import asyncio
import threading

from mitmproxy import proxy, options
from mitmproxy.http import HTTPFlow
from mitmproxy.tools.dump import DumpMaster

# 操作wifi
import pywifi
from pywifi import const
# 装饰器方式的重试
from tenacity import retry
# 命令行方式的重试
from tenacity import Retrying, stop_after_attempt, stop_after_delay, wait_fixed
from tenacity import retry_if_exception_type, before_sleep_log
# 操作视频文件
import cv2
# 超时检测
import func_timeout
# allure报告中的步骤呈现
import allure

# 导入配置文件
import config
from base.allure_helper import AllureHelper
from base.selenium_helper import SeleniumHelper
from base.picture_helper import PictureHelper
from base.json_helper import JsonHelper
from bns.exceptions import (
    WifiNotFoundException,
    WifiConnectException,
    VideoParamsException,
    VideoFileException,
)
from base.log_helper import LogHelper
from base.character_recognition_helper import CharacterRecognitionHelper
from config import queue_web_freight, queue_web_dipper, queue_web_seg

log_fomat = '%(asctime)s(pid:%(process)d,tid:%(thread)d)--%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fomat)
logger = logging.getLogger(__name__)

import config
from base.config_helper import ConfigHelper

cfgFile = config.project_root + os.sep + "config" + os.sep + "retry.ini"
cfgObj = ConfigHelper(cfgFile)


def my_before_sleep(retry_state):
    logger.error(f"执行函数: {retry_state.fn}, 重试次数: {retry_state.attempt_number}, 重试结果: {retry_state.outcome}")


class WifiHelper():
    """
        连接wifi
    """

    def __init__(self, wifi_name, wifi_passwd):
        self.wifi_name = wifi_name
        self.wifi_passwd = wifi_passwd
        # 创建一个wifi对象
        self.wifi = pywifi.PyWiFi()
        # 获取无线网卡
        self.itf = self.wifi.interfaces()[0]

    @retry(
        retry=retry_if_exception_type(WifiNotFoundException),  # 重试条件
        wait=wait_fixed(int(cfgObj.get_value("search_wifi", "retry_interval"))),  # 重试间隔
        stop=stop_after_attempt(int(cfgObj.get_value("search_wifi", "retry_counts"))) | stop_after_delay(int(cfgObj.get_value("search_wifi", "retry_timeout"))),  # 停止重试条件
        reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def search_wifi(self) -> bool:
        """
        搜索wifi名字是否存在
        :return:
        """
        # 扫描wifi,并获取[wifi列表]
        self.itf.scan()
        wifi_list = self.itf.scan_results()
        # 判断[wifi名字]是否在[wifi列表]中
        if self.wifi_name in [wifi.ssid for wifi in wifi_list]:
            return True
        else:
            raise WifiNotFoundException()

    def is_connect_success(self) -> bool:
        """
        判断wifi是否已连接成功
        :return: 
        """
        if self.itf.status() == const.IFACE_CONNECTED:
            logger.info("wifi连接成功")
            return True
        else:
            raise WifiConnectException()

    def conn_wifi(self, retry_interval=3, retry_counts=5, timeout=15) -> None:
        """
        填写配置信息, 并连接wifi
        :param retry_interval: 重试间隔
        :param retry_counts:  重试次数
        :param timeout:  超时时间
        :return:
        """

        if self.search_wifi():
            # 端口网卡连接
            self.itf.disconnect()

            # 删除配置文件
            self.itf.remove_all_network_profiles()

            # 加载配置文件
            profile = pywifi.Profile()  # 配置文件
            profile.auth = const.AUTH_ALG_OPEN  # 需要密码
            profile.akm.append(const.AKM_TYPE_WPA2PSK)  # 加密类型
            profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
            profile.ssid = self.wifi_name  # wifi名称
            profile.key = self.wifi_passwd  # wifi密码
            tmp_profile = self.itf.add_network_profile(profile)

            # 连接wifi
            self.itf.connect(tmp_profile)

            r = Retrying(
                retry=retry_if_exception_type(WifiConnectException),  # 重试条件
                wait=wait_fixed(retry_interval),  # 重试间隔
                stop=stop_after_attempt(retry_counts) | stop_after_delay(timeout),  # 停止重试条件
                reraise=True,  # 重试后如果再抛异常, 抛出的是原生异常
                before_sleep=before_sleep_log(logger, logging.WARNING)
            )
            try:
                r(r, self.is_connect_success)
            except Exception as e:
                raise Exception(f"wifi连接失败, wifi名称: {self.wifi_name}, wifi密码: {self.wifi_passwd}, 异常信息: {e}")
            finally:
                pass


class PowerHelper():
    """
        控制继电器的开关
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(1)
        logging.info(f"[继电器服务端]已启动, ip: {ip}, port:{port}")
        self.conn, self.addr = sock.accept()

    def __set_switch(self, desc: str, channel: int, status: int):
        """
        :param desc: 命令操作描述
        :param channel: 继电器通道
        :param status: 继电器状态
        :return:
        """
        with allure.step(desc):
            # 发数据
            content = f'AT+STACH{channel}={status}\r\n'
            logging.info(f"向[继电器]发送的数据: {content}")
            AllureHelper.attachText("向[继电器]发送的数据", content)
            # TODO: 发送和接收数据需要捕获异常
            self.conn.sendall(content.encode('utf-8'))
            # 收数据
            data = self.conn.recv(1024)
            logging.info(f"从[继电器]接收的数据: {data}")
            AllureHelper.attachText("从[继电器]接收的数据", data.decode("utf-8"))

    def open_acc(self):
        self.__set_switch("打开ACC", 1, 1)

    def open_power(self):
        self.__set_switch("打开主电", 2, 1)

    def open_accAndPower(self):
        self.__set_switch("打开ACC", 1, 1)
        self.__set_switch("打开主电", 2, 1)

    def close_accAndPower(self):
        self.__set_switch("关闭ACC", 1, 0)
        self.__set_switch("关闭主电", 2, 0)

    def close_acc(self):
        self.__set_switch("关闭ACC", 1, 0)

    def close_power(self):
        self.__set_switch("关闭主电", 2, 0)


@func_timeout.func_set_timeout(60)
def play_video(video_path: str, speed: int = 1, window_name: str = "demo") -> None:
    """
    视频播放
    :param video_path: 待播放的文件路径
    :param speed: 播放速度
    :param window_name: windows句柄名称
    :return:
    """
    # 校验是否为字符串
    if not isinstance(video_path, str):
        raise VideoParamsException(f"video_path参数类型必须为str, 当前类型为{type(video_path)}, 当前值为:{video_path}")

    # 校验是否为文件路径
    if not os.path.isfile(video_path):
        raise VideoFileException(f"请检查参数video_path, 此路径不存在: f{video_path}")

    # Todo: 校验是否为视频类型的文件

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise VideoFileException(f"此视频无法打开, 当前视频路径为: {video_path}")

    # 获取视频的每秒传输帧数
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 每读取一帧后的等待时间
    interval_time = 1 / fps

    # 视频最大化
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:

        # 读取视频的一帧
        ret, frame = cap.read()
        # 读取间隔
        time.sleep(round(interval_time / speed, 10))
        # 读取结束条件
        if cv2.waitKey(1) & 0xFF == ord('q') or ret == False:
            break
        # 显示帧画面
        cv2.imshow(window_name, frame)

    # 释放资源
    cv2.destroyAllWindows()
    cap.release()


class MitmproxyHandler:
    """
    数据抓包后，对抓取到的数据进行的处理操作
    """

    def request(self, flow: HTTPFlow):
        pass

    def response(self, flow: HTTPFlow):

        # 从响应信息中获取请求url
        url = flow.request.url

        # 北斗主动安全云平台: 保存登录验证码图片
        if "/808gps/rand.action" in url:
            with open(f"{config.captcha_dir}/checkcode_dipper.png", "wb") as f:
                f.write(flow.response.content)

        # 北斗主动安全云平台：登陆成功后，保存headers
        elif "/808gps/StandardLoginAction_login.action" in url:

            res = flow.response.get_text()

            res_code = JsonHelper.parseJson_by_objectpath(res, "$.result")

            if res_code == 0 and "enableLoginDetailTip" in res:
                print("dipper平台登录成功")

                JSESSIONID = flow.request.cookies.get("JSESSIONID")
                if JSESSIONID:
                    headers_cookie = f"{JSESSIONID};"
                    queue_web_dipper.put(headers_cookie)

            else:
                print("抛出异常,重新登录")

        # 货车平台：保存登录验证码图片
        elif "/sysbasic/rondamImage.action" in url:
            with open(f"{config.captcha_dir}/checkcode_freight.png", "wb") as f:
                f.write(flow.response.content)

        # 货车平台：登陆成功后，保存headers
        elif "/sysbasic/loginPub.action" in url:
            # 如果登录成功, 则保存cookie
            # 如果登录失败, 则需要重新尝试

            res = flow.response.get_text()

            # 如果是验证码的错误, 则重新尝试
            try:
                res_code = JsonHelper.parseJson_by_objectpath(res, "$..errorLevel[0]")
            except:
                res_code = JsonHelper.parseJson_by_objectpath(res, "$.result")

            if res_code == "0":
                print("freight平台登录成功")

                COOKIE_USERID_CAR = flow.response.cookies.get("COOKIE_USERID_CAR")
                if COOKIE_USERID_CAR:
                    headers_cookie = f"COOKIE_USERID_CAR={COOKIE_USERID_CAR[0]};"
                    print(headers_cookie)

                    queue_web_freight.put(headers_cookie)

            else:
                print("货运平台抛出异常,重新登录")

        # 赛格平台: 保存Authorization信息 (此接口只有在登录成功后才会被抓取到)
        elif "/gps-web/h5/mgr/connectItem?getBbCheckPostList" in url:
            Authorization = flow.request.headers.get("Authorization")
            headers_cookie = f'{{"Authorization": "{Authorization}"}}'
            queue_web_seg.put(headers_cookie)


# see source mitmproxy/master.py for details
def loop_in_thread(loop, m):
    asyncio.set_event_loop(loop)  # This is the key.
    m.run_loop(loop.run_forever)


def mitmproxy_server():
    # 配置代理地址和端口
    opts = options.Options(listen_host="127.0.0.1", listen_port=int(config.mitmproxy_server_port))
    m = DumpMaster(opts, with_termlog=False, with_dumper=False)
    pconf = proxy.config.ProxyConfig(opts)
    m.server = proxy.server.ProxyServer(pconf)
    # 插件功能
    m.addons.add(MitmproxyHandler())

    # 后台运行mitmproxy
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=loop_in_thread, args=(loop, m))
    print(f"Proxy server listening at http://127.0.0.1:{config.mitmproxy_server_port}")
    t.daemon = True
    t.start()

    # print(f"Proxy server listening at http://127.0.0.1:{config.mitmproxy_server_port}")
    # logger.info(f"Proxy server listening at http://127.0.0.1:{config.mitmproxy_server_port}")
    # m.run()

    # # Other servers might be started too.
    # time.sleep(200000)
    # # print('going to shutdown mitmproxy')
    # m.shutdown()


def web_login_sky():
    selenium = SeleniumHelper(is_proxy=True)
    driver = selenium.visit_web(r"http://www.g-sky.cn/list-70-1.html")

    # 页面操作: 进入登录页面
    driver.find_element_by_partial_link_text("登录").click()

    # 页面操作: 输入登录信息
    driver.find_element_by_css_selector("#loginForm input[name=username]").send_keys("admin")
    driver.find_element_by_css_selector("#loginForm input[name=password]").send_keys("reconovA2019")

    # 解析验证码图片
    input_checkcode = CharacterRecognitionHelper.recognition_by_ttshitu(
        image_path=f"{config.captcha_dir}/checkcode_ttshitu.png")

    # 页面操作: 输入验证码信息
    driver.find_element_by_css_selector("#loginForm input[name=code]").send_keys(input_checkcode)

    # 页面操作：点击确定按钮
    driver.find_element_by_css_selector("#loginForm input[name=dosubmit]").click()

    selenium.close_web()


def web_login_freight():
    selenium = SeleniumHelper(is_proxy=True)
    driver = selenium.visit_web(r"http://1.203.80.3:8094/")

    # 页面操作: 输入登录信息
    driver.find_element_by_css_selector().send_keys("zhongjiaotongxin@foxmail.com")
    driver.find_element_by_css_selector().send_keys("hnzjtx55222528")

    # 解析验证码图片
    input_checkcode = CharacterRecognitionHelper.recognition_by_ttshitu(
        image_path=f"{config.captcha_dir}/checkcode_freight.png")

    # 页面操作: 输入验证码信息
    driver.find_element_by_css_selector("#login_main input[name=imgCode]").send_keys(input_checkcode)

    # 页面操作：点击确定按钮
    driver.find_element_by_css_selector("#login_main input[id=loginSubmit]").click()

    selenium.close_web()


if __name__ == '__main__':
    mitmproxy_server()
    import time

    time.sleep(10000)
    # p = start_httpproxy()
    # try:
    #     while True:
    #         # 从req_queue获取请求，进行处理
    #         time.sleep(300)
    # except KeyboardInterrupt:
    #     p.terminate()
    #     p.join()
