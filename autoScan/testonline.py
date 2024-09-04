# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2023/6/26"
__title__ = "设备在线监测器v1.3_20240720"

from platform import system as system_name
import subprocess
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from datetime import datetime
from time import sleep
import configparser
from requests.adapters import HTTPAdapter

maxrequests = requests.Session()
maxrequests.mount('http://', HTTPAdapter(max_retries=2))  # 设置重试次数为3次
log_limit = 1000


def basic_info():
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

        ip_val = cf.get("WTConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值

        global log_limit
        log_limit = cf.get("WTConfig", "log_limit")  # 获取[BasicConfig]中ip_val对应的值

        return ip_val

    except Exception as e:
        return False


def ping_device(ip_address):
    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

    if system_name().lower() == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            ("ping " + parameters + " " + ip_address),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo
        )
    else:
        process = subprocess.Popen(
            ("ping " + parameters + " " + ip_address),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    stdout, stderr = process.communicate()  # 必须使用这个等待子进程结束才能正确检测
    return process.returncode == 0


class WorkerThread(QThread):
    update_signal = pyqtSignal(str)
    update_button_signal = pyqtSignal(bool, str)

    def __init__(self, ip_val):
        super().__init__()
        self.ip_val = ip_val
        self.paused = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def run(self):
        self.update_signal.emit("开始检测设备状态")
        self.update_button_signal.emit(False, '监测设备状态中')
        while True:
            self.mutex.lock()
            while self.paused:
                self.condition.wait(self.mutex)
            self.mutex.unlock()

            try:
                res = maxrequests.get(f'http://{self.ip_val}/devices/allDevices/')
                ip_list = res.json().get('devices')
                for ip in ip_list:
                    now_time = datetime.now()
                    is_online = ping_device(ip)
                    if is_online:
                        self.update_signal.emit(f'{now_time} 设备 {ip} 在线')
                        requests.get(f'http://{self.ip_val}/devices/statusModify/?is_online=1&ip={ip}')
                    else:
                        self.update_signal.emit(f'{now_time} 设备 {ip} 离线')
                        requests.get(f'http://{self.ip_val}/devices/statusModify/?is_online=0&ip={ip}')
                sleep(60*5)
            except Exception as e:
                self.update_signal.emit(f"{datetime.now()} 监测设备在线状态出错 {str(e)}")

    def toggle_pause(self):
        self.mutex.lock()
        self.paused = not self.paused
        if not self.paused:
            self.condition.wakeAll()
        self.mutex.unlock()


class MyWindow(QWidget):
    def __init__(self, ip_val):
        super().__init__()
        self.ip_val = ip_val

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(__title__)
        self.setGeometry(100, 100, 1000, 800)

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.main_layout.addWidget(self.text_edit)

        self.button_layout = QVBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.start_button = QPushButton('开始检测设备状态')
        self.start_button.clicked.connect(self.start_thread)
        self.button_layout.addWidget(self.start_button)

        self.pause_button = QPushButton('暂停检测')
        self.pause_button.clicked.connect(self.toggle_pause)
        self.button_layout.addWidget(self.pause_button)

        self.quit_button = QPushButton('退出')
        self.quit_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.quit_button)

        self.worker_thread = WorkerThread(self.ip_val)
        self.worker_thread.update_signal.connect(self.update_text)
        self.worker_thread.update_button_signal.connect(self.update_button)

        self.start_thread()  # 自动启动

    def start_thread(self):
        if not self.worker_thread.isRunning():
            self.update_text("后台处理启动中...")
            self.worker_thread.start()

    def update_text(self, message):
        if self.text_edit.document().blockCount() > int(log_limit):
            self.text_edit.clear()
        self.text_edit.append(message)
        self.text_edit.ensureCursorVisible()

    def update_button(self, state, text):
        self.start_button.setEnabled(state)
        self.start_button.setText(text)

    def toggle_pause(self):
        self.worker_thread.toggle_pause()
        new_text = '继续检测' if self.worker_thread.paused else '暂停检测'
        self.pause_button.setText(new_text)


if __name__ == '__main__':
    if basic_info():
        ip_val = basic_info()

        app = QApplication([])
        window = MyWindow(ip_val)
        window.show()
        app.exec_()
