# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2022/8/5"
__title__ = "电警扫描器v1.5_20230203"

from dj_file_manager import FileObjectManager, FileObject
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from dj_upload_image import QZ
from datetime import datetime
from time import sleep
import configparser
import traceback


# 建立连接 获取csrftoken
client = requests.session()

thread_count = 0


def basic_info():
    white_list = ['渝D71P00']
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

        # options = cf.options("QJCSConfig")  # 获取某个section名为BasicConfig所对应的键
        # print(options)
        #
        # items = cf.items("QJCSConfig")  # 获取section名为BasicConfig所对应的全部键值对
        # print(items)

        qz_path = cf.get("DJConfig", "qz_path")  # 获取[BasicConfig]中qz_path对应的值

        ip_val = cf.get("DJConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值

        sleep_time = cf.get("DJConfig", "sleep_time")  # 获取[BasicConfig]中sleep_time对应的值

        qz_time = cf.get("DJConfig", "qz_time")  # 获取[BasicConfig]中qz_time对应的值

        wf_list_str = cf.get("DJConfig", "wf_list")  # 获取[BasicConfig]中wf_list对应的值
        wf_list = wf_list_str.split(',')

        return qz_path, ip_val, white_list, sleep_time, qz_time, wf_list
    except Exception as e:
        # print(e)
        return False


def QZ_run(qz_path, ip_val, white_list, sleep_time, qz_time, wf_list):
    log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "\n开始扫描电警文件夹：%s\n" % qz_path)
    f.write("\n%s 开始扫描电警文件夹：%s\n" % (datetime.now(), qz_path))
    f.close()
    # count = 0
    global thread_count
    thread_count += 1
    # qz_bt.config(state="disabled", text='正在扫描电警文件夹')
    count_thread_lb.config(text="\n已开启扫描器数：%s\n" % str(thread_count))
    while True:
        log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'
        try:
            f = open(log_file, 'a+', encoding='utf-8')
            # sleep(1)
            now_time = datetime.now()
            res = QZ(FileObjectManager(FileObject(qz_path)).scan_with_depth(10).all_file_objects(),
                     ip_val, qz_path, now_time, white_list, wf_list)
            # print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            # count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')

            if status == "success":
                if res_status == "success":
                    res_status = '成功'
                    text.insert(tk.END,
                                "\n%s【电警】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【电警】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【电警】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【电警】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                elif res_status == "wfCodeError":
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【电警】【扫描到文件】%s，上传文件【%s】, 该违法代码后台未添加\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【电警】【扫描到文件】%s，上传文件【%s】, 该违法代码后台未添加\n" % (now_time, file_path, res_status))
                elif res_status == "fail":
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【电警】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【电警】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                else:
                    text.insert(tk.END, "\n%s【电警】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【电警】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
            elif status == "fail":
                text.insert(tk.END, "\n%s【电警】【扫描到文件夹】 %s，【未发现有效图片】\n" % (now_time, file_path))
                f.write("\n%s 【电警】【扫描到文件夹】 %s，【未发现图片】" % (now_time, file_path))
            elif status == "error":
                text.insert(tk.END, "\n%s【电警】【上传出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【电警】【上传出错，请检查日志】：%s %s\n" % (now_time, e, file_path))
            elif status == "over":
                # text.insert(tk.END, "\n%s 【电警】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                # f.write("\n%s 【电警】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                # text.see(tk.END)
                sleep(float(sleep_time))
            elif status == "scanError":
                text.insert(tk.END, "\n%s【电警】【扫描出错】：%s\n" % (now_time, e))
                f.write("\n%s【电警】【扫描出错】：%s\n" % (now_time, e))
            # count_qz_lb.config(text='\n已处理电警图片数：%s\n' % str(count))
            # f.write('\n%s 已处理电警图片数：%s\n' % (now_time, str(count)))
            text.see(tk.END)
            # 大量同时推送集成平台时，会出错
            if qz_time != '0':
                sleep(float(qz_time))
        except Exception as ee:
            strexc = traceback.format_exc()
            text.insert(tk.END, "\n%s 【电警】程序出错：%s\n" % (datetime.now(), str(ee)))
            text.see(tk.END)
            f.write("\n%s 【电警】程序出错：%s" % (datetime.now(), strexc))
        finally:
            f.close()


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


def auto_run(ip_val, white_list, sleep_time, qz_time, wf_list):
    log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    try:
        text.insert(tk.END, "%s %s秒后自动开始运行 【电警】取证扫描 \n" % (datetime.now(), qz_time))
        # f.write("%s 5秒后自动开始运行 【超速】取证扫描  \n" % datetime.now())

        sleep(float(qz_time))
        thread_it(QZ_run, qz_path, ip_val, white_list, sleep_time, qz_time, wf_list)
        # 避免在服务器重启时失败
    except Exception as e:
        # print(e)
        strexc = traceback.format_exc()
        f.write("%s 自动运行出错 %s\n" % (datetime.now(), strexc))
        text.insert(tk.END, "%s 自动运行出错 %s\n" % (datetime.now(), str(e)))
    finally:
        f.close()


if __name__ == '__main__':

    # log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'
    # f = open(log_file, 'a+', encoding='utf-8')
    # f.write('%s 正在读取配置文件...\n' % datetime.now())
    # f.close()

    if basic_info():
        qz_path, ip_val, white_list, sleep_time, qz_time, wf_list = basic_info()

        root = tk.Tk()

        root.title(__title__)

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        text.insert(tk.END, "配置信息如下：\n")
        text.insert(tk.END, "取证文件夹路径：%s\n" % qz_path)
        text.insert(tk.END, "服务器及端口：%s\n" % ip_val)
        text.insert(tk.END, "空闲间隔(秒)：%s\n" % sleep_time)
        text.insert(tk.END, "取证图片上传间隔(秒)：%s\n" % qz_time)
        # text.insert(tk.END, "白名单：%s\n" % white_list)

        # log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'

        text.grid(row=0, column=0)
        root.geometry('1000x800+600+50')
        lf = tk.LabelFrame(root, text='')
        lf.grid(row=0, column=1)

        qz_lb = tk.Label(lf, text="电警文件夹路径为：")
        qz_lb.grid()

        qz_val = tk.Label(lf, text=qz_path, wraplength=400)
        qz_val.grid()

        # count_qz_lb = tk.Label(lf, text="\n已处理取证图片数：0\n")
        # count_qz_lb.grid()

        count_thread_lb = tk.Label(lf, text="\n已开启扫描器数：0\n")
        count_thread_lb.grid()

        qz_bt = tk.Button(lf, text='开始扫描电警文件夹', fg='red',
                          command=lambda: thread_it(QZ_run, qz_path, ip_val, white_list, sleep_time,
                                                    qz_time, wf_list))

        qz_bt.grid(padx=5, pady=20)

        thread_it(auto_run, ip_val, white_list, sleep_time, qz_time, wf_list)

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()

