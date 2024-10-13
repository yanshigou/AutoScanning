# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/09/02"
__title__ = "自动扫描器v1.0_20240902"


from wt_file_manager import FileObjectManager, FileObject
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from wt_upload_image import event
from wt.loggmodel import Logger
from datetime import datetime
from time import sleep
import configparser
import traceback
import codecs
import os


# 建立连接 获取csrftoken
client = requests.session()
event_thread_count = 0
qz_thread_count = 0


def basic_info():
    white_list = ['渝D71P00']
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

        wt_qz_path = cf.get("WTConfig", "qz_path")  # 获取[BasicConfig]中qz_path对应的值
        wt_event_path = cf.get("WTConfig", "event_path")  # 获取[BasicConfig]中qz_path对应的值
        ip_val = cf.get("WTConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值
        wt_sleep_time = cf.get("WTConfig", "sleep_time")  # 获取[BasicConfig]中sleep_time对应的值
        wt_qz_time = cf.get("WTConfig", "qz_time")  # 获取[BasicConfig]中qz_time对应的值
        wt_thread_nums = cf.get("WTConfig", "thread_nums")  # 获取[BasicConfig]中qz_time对应的值
        wt_wf_list_str = cf.get("WTConfig", "wf_list")  # 获取[BasicConfig]中wf_list对应的值
        wt_wf_list = wt_wf_list_str.split(',')

        return wt_qz_path, wt_event_path, ip_val, white_list, wt_sleep_time, wt_qz_time, wt_thread_nums, wt_wf_list
    except Exception as e:
        # print(e)
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


def event_run(event_path, ip_val, white_list, sleep_time, qz_time):
    file_folder = os.path.join(current_file_folder, "logs")
    log_file = os.path.join(file_folder, '违停日志事件.log')
    # f = open(log_file, 'a+', encoding='utf-8', errors='ignore')
    text.insert(tk.END, "开始扫描事件文件夹：%s\n" % event_path)
    # f.write(codecs.BOM_UTF8.decode("utf-8"))
    # f.write("\n%s 开始扫描事件文件夹：%s\n" % (datetime.now(), event_path))
    # f.close()
    logg = Logger(log_file, level="info")
    logg.logger.info("开始扫描事件文件夹：%s" % event_path)
    global event_thread_count
    event_thread_count += 1
    # event_bt.config(state="disabled", text='正在扫描事件文件夹')
    count_event_thread_lb.config(text="\n已开启事件扫描器数：%s\n" % str(event_thread_count))
    while True:
        logg = Logger(log_file, level="info")
        try:
            # f = open(log_file, 'a+', encoding='utf-8', errors='ignore')
            # f.write(codecs.BOM_UTF8.decode("utf-8"))
            now_time = datetime.now()
            res = event(FileObjectManager(FileObject(event_path)).scan_with_depth(10).all_file_objects(),
                        ip_val, event_path, now_time, white_list, file_folder)
            # print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            e = res.get('e')
            file_path = res.get('file_path')

            zpname = res.get('zpname')
            zp = res.get('zp')

            now_time = datetime.now()
            # if zpname:
            #     text.insert(tk.END, '\n%s 短信发送成功，已收到短信图片%s，等待扫描上传' % (now_time, zpname))
            #     # f.write('\n%s 短信发送成功，已收到短信图片%s，等待扫描上传' % (now_time, zpname))
            #     logg.logger.info('短信发送成功，已收到短信图片%s，等待扫描上传' % zpname)
            if status == "success" and zp != 'success':
                if res_status == "success":
                    res_status = '成功'
                    # text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    # f.write("\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    logg.logger.info("【事件】【扫描到文件】%s，服务器【%s】，%s" % (file_path, res_status, e))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    # f.write("\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    text.see(tk.END)
                    logg.logger.error("【事件】【扫描到文件】%s，服务器【%s】，%s" % (file_path, res_status, e))
                elif res_status == "dateError":
                    res_status = '失败'
                    # text.insert(tk.END, "\n%s【事件】【扫描到文件】%s，上传文件【%s】, 晚上不发短信\n" % (now_time, file_path, res_status))
                    # f.write("\n%s 【事件】【扫描到文件】%s，上传文件【%s】, 晚上不发短信\n" % (now_time, file_path, res_status))
                    logg.logger.warning("【事件】【扫描到文件】%s，上传文件【%s】, 晚上不发短信" % (file_path, res_status))
                elif res_status == "fail":
                    """fail"""
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【事件】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    # f.write("\n%s 【事件】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    text.see(tk.END)
                    logg.logger.warning("【事件】【扫描到文件】%s，上传文件【%s】, 该设备未启用" % (file_path, res_status))
                else:
                    text.insert(tk.END, "%s【事件】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    # f.write("\n%s 【事件】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    text.see(tk.END)
                    logg.logger.warning("【事件】【扫描到文件】%s，上传文件【%s】" % (file_path, res_status))
            elif status == "success" and zp == 'success':
                if res_status == "success":
                    res_status = '成功'
                    # text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    # f.write("\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    logg.logger.info("【事件】【扫描到文件】%s，服务器【%s】，%s" % (file_path, res_status, e))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    # f.write("\n%s 【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    text.see(tk.END)
                    logg.logger.error("【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (file_path, res_status, e))
                elif res_status == "fail":
                    """fail"""
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【事件-短信】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    # f.write("\n%s 【事件-短信】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    text.see(tk.END)
                    logg.logger.warning("【事件-短信】【扫描到文件】%s，上传文件【%s】, 该设备未启用" % (file_path, res_status))
                else:
                    text.insert(tk.END, "\n%s【事件-短信】【扫描到文件】%s，上传文件【%s】 \n" % (now_time, file_path, res_status))
                    # f.write("\n%s 【事件-短信】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    text.see(tk.END)
                    logg.logger.warning("【事件-短信】【扫描到文件】%s，上传文件【%s】" % (file_path, res_status))
            # elif status == "fail":
            #     text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, file_path))
            #     # f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】" % (now_time, file_path))
            #     logg.logger.info("【事件】【扫描到文件夹】 %s，【未发现图片】" % file_path)
            elif status == "error":
                text.insert(tk.END, "\n%s 【事件】【上传图片出错，请查看日志】：%s\n" % (now_time, e))
                # f.write("\n%s 【事件】【上传图片出错，请检查日志】：%s %s\n" % (now_time, e, file_path))
                text.see(tk.END)
                logg.logger.error("【事件】【上传图片出错，请检查日志】：%s %s" % (e, file_path))
            elif status == "over":
                # text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, event_path, sleep_time.strip()))
                # f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, event_path, sleep_time.strip()))
                # logg.logger.info("【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】" % (event_path, sleep_time.strip()))
                # text.see(tk.END)
                sleep(float(sleep_time))
            elif status == "scanError":
                text.insert(tk.END, "\n%s【事件】【扫描出错】：%s\n" % (now_time, e))
                # f.write("\n%s【事件】【扫描出错】：%s\n" % (now_time, e))
                logg.logger.error("【事件】【扫描出错】：%s" % e)
                text.see(tk.END)
            if qz_time != '0':
                sleep(float(qz_time))
        except Exception as ee:
            strexc = traceback.format_exc()
            text.insert(tk.END, "\n%s 【事件】程序出错：%s\n" % (datetime.now(), str(ee)))
            text.see(tk.END)
            # f.write("\n%s 【事件】程序出错：%s" % (datetime.now(), strexc))
            logg.logger.error("【事件】程序出错：%s" % strexc)
        # finally:
        #     logg.logger.info("")


if __name__ == '__main__':


    root = tk.Tk()

    root.title(__title__)

    # 滚动条
    scroll = tk.Scrollbar()

    text = scrolledtext.ScrolledText(root, width=90, height=60)

    text.grid(row=0, column=0)
    root.geometry('1000x800+600+50')
    lf = tk.LabelFrame(root, text='功能列表')
    lf.grid(row=0, column=1)
    if basic_info():
        current_file_folder = os.path.dirname(os.path.abspath(__file__))
        # 上一层文件夹
        # parent_folder = os.path.dirname(current_file_folder)
        # print(current_file_folder)
        # print(parent_folder)
        wt_qz_path, wt_event_path, ip_val, white_list, wt_sleep_time, wt_qz_time, wt_thread_nums, wt_wf_list = basic_info()
        count_event_thread_lb = tk.Label(lf, text="\n已开启事件扫描器数：0\n")
        count_event_thread_lb.grid()

        count_qz_thread_lb = tk.Label(lf, text="\n已开启取证扫描器数：0\n")
        count_qz_thread_lb.grid()

        event_bt = tk.Button(lf, text='开始扫描事件文件夹', fg='red',
                             command=lambda: thread_it(event_run, wt_event_path, ip_val, white_list,
                                                       wt_sleep_time, wt_qz_time))
        # qz_bt = tk.Button(lf, text='开始扫描取证文件夹', fg='red',
        #                   command=lambda: thread_it(QZ_run, qz_path, ip_val, white_list, sleep_time,
        #                                             qz_time, wf_list))
        event_bt.grid(padx=5, pady=20)
        # qz_bt.grid(padx=5, pady=20)
        #
        # thread_it(auto_run, event_path, ip_val, white_list, sleep_time, qz_time, thread_nums)
        #
        # q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        # q.grid(padx=5, pady=10)
    else:
        text.insert(tk.END, "配置文件出错\n")

    root.mainloop()
