from logging import getLogger

from serial import Serial

from check_content.check_text import CheckText
from log_logger import define_logger


class SerialContent:
    def __init__(self, port, baud):
        self._logger = getLogger('upgrade.serial')
        self._logger.info("连接设备->端口:%s,波特率：%s", port, baud)
        self.serial = Serial(port, int(baud), timeout=1)
        self.check = CheckText()

    # def __del__(self):
    #     self._logger.info("断开串口。")
    #     self.serial.close()

    def read_line(self):
        data = ""
        try:
            data = str(self.serial.readline(), encoding="utf-8").strip()
            self._logger.debug("读取的串口信息：%s", data)
        except UnicodeDecodeError:
            self._logger.warning("UnicodeDecodeError")
        finally:
            return data

    def judgment_content(self, expected):
        if not self.serial.is_open:
            return False
        self._logger.info("端口连接成功")
        while True:
            data = self.read_line()
            if data or len(data) > 0:
                with open("serial.log", 'a') as file_obj:
                    file_obj.write(data)
                    file_obj.write('\r')
                result = self.check.check_content(expected, data)
                if result:
                    self._logger.info("获取到预期的信息行：%s", result)
                    return True


if __name__ == '__main__':
    define_logger()
    S = SerialContent("COM7", 115200)
    start_ap = "change to AP"
    Un_zip = "Uncompress Ok!"
    cpu_start = "Welcome to recovery sys"
    cpu_end = "updatesucess"
    start = "Welcome to HiLinux."
    oem = "oem mcu upgrade success"
    S.judgment_content("123")
