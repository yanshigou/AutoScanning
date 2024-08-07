# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2023/6/26"
__title__ = "设备在线监测器v2.5_20240807"

# from platform import system as system_name
# import subprocess
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from datetime import datetime
from time import sleep
import configparser
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor
from ping3 import ping


log_limit = 0
wait_time = 10
del_nums = 50
max_workers = 8


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

        global log_limit
        global wait_time
        global max_workers
        global del_nums
        wait_time = float(cf.get("WTConfig", "wait_time"))  # 获取[BasicConfig]中ip_val对应的值
        log_limit = int(cf.get("WTConfig", "log_limit"))  # 获取[BasicConfig]中ip_val对应的值
        max_workers = int(cf.get("WTConfig", "max_workers"))  # 获取[BasicConfig]中ip_val对应的值
        del_nums = float(cf.get("WTConfig", "del_nums"))  # 获取[BasicConfig]中ip_val对应的值
        return ip_val

    except Exception as e:
        return False


def insert_log(message):
    if log_limit == 0:
        return
    else:
        text.insert(tk.END, message)
        # 限制显示的日志条数，例如只保留最后1000行
        if log_limit == 1:
            return
        a = int(text.index('end-1c').split('.')[0])
        if a > log_limit:
            text.delete(1.0, del_nums)


# def ping_device(ip_address):
#     parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
#
#     if system_name().lower() == "windows":
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#         process = subprocess.Popen(
#             ("ping " + parameters + " " + ip_address),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             startupinfo=startupinfo
#         )
#     else:
#         process = subprocess.Popen(
#             ("ping " + parameters + " " + ip_address),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
#
#     stdout, stderr = process.communicate()  # 必须使用这个等待子进程结束才能正确检测
#     process.stdout.close()
#     process.stderr.close()
#     return process.returncode == 0

def ping_device(ip_address):
    delay = ping(ip_address, timeout=1)
    return delay is not None


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

        insert_log("%s 自动运行出错 %s\n" % (datetime.now(), str(e)))


def check_device_online(ip_val):
    insert_log("开始检测设备状态\n")

    ping_bt.config(state="disabled", text='开始监测设备状态')

    with ThreadPoolExecutor(max_workers=int(max_workers)) as executor:
        with requests.Session() as session:
            session.mount('http://', HTTPAdapter(max_retries=2))
            while True:
                try:
                    res = session.get(f'http://{ip_val}/devices/allDevices/')
                    ip_list = res.json().get('devices')
                    res.close()

                    future_to_ip = {executor.submit(ping_device, ip): ip for ip in ip_list}

                    for future in future_to_ip:
                        ip = future_to_ip[future]
                        is_online = future.result()
                        insert_log('\n设备%s %s ' % (ip, is_online))
                        session.get(f'http://{ip_val}/devices/statusModify/?is_online={int(is_online)}&ip={ip}', headers={'Cache-Control': 'no-cache'}).close()
                    session.cookies.clear()
                    sleep(60 * float(wait_time))
                except Exception as e:
                    insert_log("%s 监测设备在线状态出错 %s\n" % (datetime.now(), str(e)))
                    sleep(60 * float(wait_time))


def close_b(root):
    root.quit()


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
        q = tk.Button(lf, text='退  出', command=lambda: close_b(root), padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()
