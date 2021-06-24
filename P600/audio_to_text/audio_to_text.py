# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import time

import requests
import json
import base64
import os
from logging import getLogger
import speech_recognition as sr
from readconfig import ReadConfig


class KeyInfo:
    def __init__(self):
        relative_path = __file__.rsplit("\\", 1)[0]
        project_path = relative_path.rsplit("\\", 1)[0]
        config = ReadConfig(cfg=os.path.join(project_path, 'config\\key.config'))
        self.baidu_key_info = config.get_value('baidu')


class AudioRecognition:
    def __init__(self):
        self._logger = getLogger('upgrade.audio')
        self._key = KeyInfo().baidu_key_info
        self._token = self.get_token()
        self.dir_name = r'.\wav_file'

    def __del__(self):
        if os.path.exists(self.dir_name):
            shutil.rmtree(self.dir_name)

    def get_token(self):
        self._logger.info('开始获取token...')
        # 请求接口url
        baidu_server = self._key.url
        # 授权类型
        grant_type = self._key.type
        # Api Key
        client_id = self._key.api_key
        # 密钥 Key
        client_secret = self._key.secret_key
        self._logger.info('开始获取token...')
        # 拼url
        url = f"{baidu_server}grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}"
        self._logger.info('请求的URL:%s', url)
        res = requests.post(url)
        res_code = res.status_code
        if res_code == 200:
            token = json.loads(res.text)["access_token"]
            self._logger.info('获取到token:%s', token)
            return token
        self._logger.warning("请求失败，状态码为：%s", res_code)
        return False

    def baidu_audio_api(self, filename):
        self._logger.debug('开始识别语音文件...')
        with open(filename, "rb") as f:
            speech = base64.b64encode(f.read()).decode('utf-8')
        size = os.path.getsize(filename)
        headers = {'Content-Type': 'application/json'}
        url = "https://vop.baidu.com/server_api"
        data = {
            "format": "wav",
            "rate": "16000",
            "dev_pid": "1536",
            "speech": speech,
            "cuid": "TEDxPY",
            "len": size,
            "channel": 1,
            "token": self._token,
        }
        # Post请求
        req = requests.post(url, json.dumps(data), headers)
        # 获取访问的状态码
        req_code = req.status_code
        if req_code != 200:
            self._logger.warning("获取的状态码：%s:", req_code)
            return False
        result = req.json()
        self._logger.debug("返回结果:", result)
        msg = result["err_msg"]
        if msg == "success.":
            audio_content = result['result'][0]
            if not audio_content:
                self._logger.warning("语音识别得文本内容为空")
                return False
            self._logger.debug("语音识别得文本内容：%s", audio_content)
            return audio_content
        else:
            err_no = result["err_no"]
            self._logger.warning("内容获取失败,错误码为：%s", err_no)
            return False

    def record_sound(self):
        wav_name = time.strftime('%Y%m%d_%H%M%S') + ".wav"
        # 判断文件是否存在，存在忽略，不存在创建
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
        file = r"%s\%s" % (self.dir_name, wav_name)
        r = sr.Recognizer()
        # 启用麦克风
        mic = sr.Microphone()
        self._logger.info('录音中...')
        with mic as source:
            # 降噪
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        with open(file, "wb") as f:
            # 将麦克风录到的声音保存为wav文件
            f.write(audio.get_wav_data(convert_rate=16000))
        self._logger.info('文件：%s。录制成功...', file)
        return file

    def audio_to_text(self):
        file_path = self.record_sound()
        text_content = self.baidu_audio_api(file_path)
        self._logger.info('识别完成...')
        if text_content:
            return text_content
        return False


if __name__ == '__main__':
    A = AudioRecognition()
    a = A.audio_to_text()
    print(a)