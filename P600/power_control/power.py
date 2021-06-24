#!/usr/bin/env python
# -*- coding: utf-8 -*

import socket
from logging import getLogger
from time import sleep


class PowerControl:
    def __init__(self, addr, port):
        self.logger = getLogger('upgrade.power')
        self.addr = addr
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.addr, self.port))
        self.logger.debug('监听中....')
        sock.listen(1)
        self.conn = sock.accept()[0]

    def switch_status(self, channel, status):
        msg = f'AT+STACH{channel}={status}\r\n'
        self.logger.debug('消息：%s', msg.strip("\r\n"))
        self.conn.sendall(msg.encode('utf-8'))
        self.logger.debug('发送消息')
        data = self.conn.recv(1024)
        status = str(data, encoding="utf-8").strip()
        self.logger.debug('获取返回消息：%s', status)
        if status == "OK":
            return True
        return False


if __name__ == "__main__":
    pc = PowerControl('192.168.100.100', 6000)
    pc.switch_status(1, 1)
    pc.switch_status(2, 1)
    # sleep(30)
    # pc.switch_status(2, 1)
