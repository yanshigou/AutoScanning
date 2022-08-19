# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2022/8/10"
__title__ = "推送器v1.0_20220812"


import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from datetime import datetime
from time import sleep
import configparser
import os
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 建立连接 获取csrftoken
client = requests.session()


is_push = "0"


def basic_info():
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

        ip_val = cf.get("PUSHConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值

        push_time = cf.get("PUSHConfig", "push_time")  # 获取[BasicConfig]中push_time对应的值

        push_model = cf.get("PUSHConfig", "push_model")  # 获取[BasicConfig]中push_time对应的值

        global is_push
        is_push = cf.get("PUSHConfig", "is_push")  # 获取[BasicConfig]中is_push对应的值

        return ip_val, push_time, is_push, push_model
    except Exception as e:
        print(e)
        return False


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


def push(url, push_time, modelName):
    log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '推送日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')

    text.insert(tk.END, "\n" + modelName + "开始推送\n")
    f.write("\n%s " % datetime.now() + modelName + "开始推送\n")
    f.close()

    while True:
        f = open(log_file, 'a+', encoding='utf-8')
        try:
            r = requests.get('%s' % url).json()
            status = r.get('status')
            car_id = r.get('car_id')
            push_result = r.get('push_result')
            if status == "success":
                push_result = "成功"
                text.insert(tk.END, '\n%s 【%s】推送【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
                f.write('\n%s 【%s】推送成功，【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
            elif status == "fail":
                text.insert(tk.END, '\n%s 【%s】数据推送已完成' % (datetime.now(), modelName))
                f.write('\n%s 【%s】数据推送已完成' % (datetime.now(), modelName))
            elif status == "deviceIdError":
                text.insert(tk.END, '\n%s 【%s】推送【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
                f.write('\n%s 【%s】推送【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
            elif status == "error":
                text.insert(tk.END, '\n%s 【%s】推送【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
                f.write('\n%s 【%s】推送【%s】,【%s】' % (datetime.now(), modelName, push_result, car_id))
            sleep(float(push_time))
        except Exception as e:
            strexc = traceback.format_exc()
            f.write("%s 【%s】程序出错 %s\n" % (datetime.now(), modelName, strexc))
            text.insert(tk.END, "%s 【%s】程序出错 %s\n" % (datetime.now(), modelName, strexc))
        finally:
            f.close()


def auto_run(urlList, push_time, modelNameList):
    log_file = "logs/" + datetime.now().strftime('%Y-%m-%d') + '推送日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    try:
        for index, url in enumerate(urlList):
            modelName = modelNameList[index]
            thread_it(push, url, push_time, modelName)
            sleep(1)
    except Exception as e:
        strexc = traceback.format_exc()
        f.write("%s 自动运行出错 %s\n" % (datetime.now(), strexc))
        text.insert(tk.END, "%s 自动运行出错 %s\n" % (datetime.now(), strexc))
    finally:
        f.close()


if __name__ == '__main__':

    log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '推送日志.txt'

    if basic_info():
        ip_val, push_time, is_push, push_model = basic_info()

        root = tk.Tk()

        root.title(__title__)

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        if is_push == "1":
            text.insert(tk.END, "配置信息如下：\n")
            text.insert(tk.END, "服务器及端口：%s\n" % ip_val)
            text.insert(tk.END, "推送模块：%s\n" % push_model)
            text.insert(tk.END, "推送间隔(秒)：%s\n" % push_time)

            text.grid(row=0, column=0)
            root.geometry('1000x800+600+50')
            lf = tk.LabelFrame(root, text='')
            lf.grid(row=0, column=1)

            model_lb = tk.Label(lf, text="已开启推送模块：\n")
            model_lb.grid()

            model_name = ''  # dataInfo,djDataInfo,csDataInfo,wjlDataInfo,hcxxDataInfo,kcxxDataInfo,wfmdDataInfo

            pushModelList = push_model.split(',')
            urlList = []
            modelNameList = []

            for i in pushModelList:
                url = 'http://%s/%s/push/' % (ip_val, i)
                urlList.append(url)

                if i == "dataInfo":
                    model_name += "【违停推送】\n"
                    modelNameList.append("违停")
                elif i == "djDataInfo":
                    model_name += "【电警推送】\n"
                    modelNameList.append("电警")
                elif i == "csDataInfo":
                    model_name += "【超速推送】\n"
                    modelNameList.append("超速")
                elif i == "wjlDataInfo":
                    model_name += "【违禁令推送】\n"
                    modelNameList.append("违禁令")
                elif i == "hcxxDataInfo":
                    model_name += "【货车限行推送】\n"
                    modelNameList.append("货车限行")
                elif i == "kcxxDataInfo":
                    model_name += "【客车限行推送】\n"
                    modelNameList.append("客车限行")
                elif i == "wfmdDataInfo":
                    model_name += "【违法鸣笛推送】\n"
                    modelNameList.append("违法鸣笛")

            model_lb = tk.Label(lf, text=model_name + "\n")
            model_lb.grid()

            thread_it(auto_run, urlList, push_time, modelNameList)

            q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
            q.grid(padx=5, pady=10)

            root.mainloop()
        else:
            text.insert(tk.END, "配置信息如下：\n")
            text.insert(tk.END, "推送未开启，请配置参数【is_push】为【1】\n")
            text.insert(tk.END, "推送未开启，请配置参数【is_push】为【1】\n")
            text.insert(tk.END, "推送未开启，请配置参数【is_push】为【1】\n")

            text.grid(row=0, column=0)
            root.geometry('1000x800+600+50')
            lf = tk.LabelFrame(root, text='')
            lf.grid(row=0, column=1)

            count_thread_lb = tk.Label(lf, text="\n未开启推送\n")
            count_thread_lb.grid()

            q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
            q.grid(padx=5, pady=10)

            root.mainloop()
