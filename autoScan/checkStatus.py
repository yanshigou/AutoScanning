# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2023/6/26"
__title__ = "设备在线监测器v1.2_20230627"

from platform import system as system_name
import subprocess
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from datetime import datetime
from time import sleep
import configparser


def basic_info():
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块


        # options = cf.options("DJConfig")  # 获取某个section名为BasicConfig所对应的键
        # print(options)
        #
        # items = cf.items("DJConfig")  # 获取section名为BasicConfig所对应的全部键值对
        # print(items)

        ip_val = cf.get("WTConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值
        return ip_val

    except Exception as e:
        return False


def ping_device(ip_address):

    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
    return subprocess.call(["ping", parameters, ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def thread_it(func, *args):
    """
    将函数打包进线程
    :param func:
    :param args:
    :return:
    """
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞--卡死界面！
    # t.join()


def auto_run(ip_val):
    try:

        thread_it(check_device_online, ip_val)

    except Exception as e:
        # strexc = traceback.format_exc()
        # f.write("%s 自动运行出错 %s\n" % (datetime.now(), strexc))
        text.insert(tk.END, "%s 自动运行出错 %s\n" % (datetime.now(), str(e)))


def check_device_online(ip_val):

    text.insert(tk.END, "开始检测设备状态")

    ping_bt.config(state="disabled", text='开始监测设备状态')
    while True:
        try:
            res = requests.get('http://%s/devices/allDevices/' % ip_val)
            ip_list = res.json().get('devices')
            for ip in ip_list:
                now_time = datetime.now()
                is_online = ping_device(ip)
                if is_online:
                    text.insert(tk.END, '\n%s 设备 %s 在线' % (now_time, ip))

                    requests.get('http://%s/devices/statusModify/?is_online=1&ip=%s' % (ip_val, ip))
                else:
                    text.insert(tk.END, '\n%s 设备 %s 离线' % (now_time, ip))

                    requests.get('http://%s/devices/statusModify/?is_online=0&ip=%s' % (ip_val, ip))

            sleep(60 * 5)
        except Exception as e:
            text.insert(tk.END, "%s 监测设备在线状态出错 %s\n" % (datetime.now(), str(e)))


if __name__ == '__main__':

    if basic_info():
        ip_val = basic_info()

        root = tk.Tk()

        root.title(__title__)

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        text.insert(tk.END, "配置信息如下：\n")
        text.insert(tk.END, "服务器及端口：%s\n" % ip_val)

        text.grid(row=0, column=0)
        root.geometry('1000x800+600+50')
        lf = tk.LabelFrame(root, text='')
        lf.grid(row=0, column=1)

        ping_bt = tk.Button(lf, text='开始检测设备状态', fg='red',
                            command=lambda: thread_it(check_device_online, ip_val))
        ping_bt.grid(padx=5, pady=20)

        thread_it(auto_run, ip_val)

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()
