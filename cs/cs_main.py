# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2022/8/2"

from cs.file_manager import FileObjectManager, FileObject
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from cs.cs_upload_image import QZ
from datetime import datetime
from time import sleep
import configparser

# 建立连接 获取csrftoken
client = requests.session()

cs_push_url = "/csDataInfo/push/"

is_push_cs = "0"
thread_count = 0


def basic_info():
    white_list = ['渝DJD020']
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

        # options = cf.options("DJConfig")  # 获取某个section名为BasicConfig所对应的键
        # print(options)
        #
        # items = cf.items("DJConfig")  # 获取section名为BasicConfig所对应的全部键值对
        # print(items)

        qz_path = cf.get("DJConfig", "qz_path")  # 获取[BasicConfig]中qz_path对应的值

        move_folder = cf.get("DJConfig", "move_folder")  # 获取[BasicConfig]中move_folder对应的值

        ip_val = cf.get("DJConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值

        sleep_time = cf.get("DJConfig", "sleep_time")  # 获取[BasicConfig]中sleep_time对应的值

        qz_time = cf.get("DJConfig", "qz_time")  # 获取[BasicConfig]中qz_time对应的值

        push_time = cf.get("DJConfig", "push_time")  # 获取[BasicConfig]中push_time对应的值

        wf_list_str = cf.get("DJConfig", "wf_list")  # 获取[BasicConfig]中wf_list对应的值
        wf_list = wf_list_str.split(',')



        global is_push_cs
        is_push_cs = cf.get("DJConfig", "is_push_cs")  # 获取[BasicConfig]中is_push对应的值

        return qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list
    except Exception as e:
        print(e)
        return False


def QZ_run(qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, wf_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "\n开始扫描超速文件夹：%s\n" % qz_path)
    # f.write("%s \n开始扫描超速文件夹：%s" % (qz_path, datetime.now()))
    # f.close()
    # count = 0
    global thread_count
    thread_count += 1
    # qz_bt.config(state="disabled", text='正在扫描超速文件夹')
    count_thread_lb.config(text="\n已开启扫描器数：%s\n" % str(thread_count))
    while True:
        log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
        try:
            f = open(log_file, 'a+', encoding='utf-8')
            # sleep(1)
            now_time = datetime.now()
            res = QZ(FileObjectManager(FileObject(qz_path)).scan_with_depth(10).all_file_objects(), move_folder,
                     ip_val, qz_path, now_time, white_list, wf_list)
            print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            # count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')

            if status == "success":
                if res_status == "success":
                    res_status = '成功'
                    text.insert(tk.END,
                                "\n%s【超速】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【超速】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【超速】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【超速】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                elif res_status == "wait":
                    res_status = '再次推送'
                    text.insert(tk.END,
                                "\n%s 【超速】【扫描到文件】%s，已上传取证图片，未推送成功，【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【超速】【扫描到文件】%s，已上传取证图片，未推送成功，【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【超速】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【超速】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
            elif status == "fail":
                text.insert(tk.END, "\n%s【超速】【扫描到文件夹】 %s，【未发现有效图片】\n" % (now_time, qz_path))
                f.write("\n%s 【超速】【扫描到文件夹】 %s，【未发现图片】" % (now_time, qz_path))
            elif status == "error":
                text.insert(tk.END, "\n%s【超速】【上传出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【超速】【上传出错，请检查日志】：%s" % (now_time, e))
            elif status == "over":
                text.insert(tk.END, "\n%s 【超速】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                f.write("\n%s 【超速】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                text.see(tk.END)
                sleep(int(sleep_time))
            # count_qz_lb.config(text='\n已处理超速图片数：%s\n' % str(count))
            # f.write('\n%s 已处理超速图片数：%s\n' % (now_time, str(count)))
            text.see(tk.END)
            # 大量同时推送集成平台时，会出错
            if qz_time != '0':
                sleep(int(qz_time))
        except Exception as ee:
            text.insert(tk.END, "\n%s 【超速】程序出错：%s\n" % (datetime.now(), str(ee)))
            text.see(tk.END)
            f.write("\n%s 【超速】程序出错：%s" % (datetime.now(), str(ee)))
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


def push_cs(ip_val, push_time):
    log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始推送【超速】至集成平台")
    f.write("开始推送【超速】至集成平台")
    f.close()
    while True:
        f = open(log_file, 'a+', encoding='utf-8')
        try:
            # 加入再次推送失败的
            r = requests.get('http://' + ip_val + cs_push_url)
            status = r.json().get('status')
            if status == "success":
                car_id = r.json().get('car_id')
                text.insert(tk.END, '\n%s 【超速】再次推送未成功入库的数据: 【%s】' % (datetime.now(), car_id))
                f.write('\n%s 【超速】再次推送未成功入库的数据: 【%s】' % (datetime.now(), car_id))
            elif status == "fail":
                push_result = r.json().get('push_result')
                text.insert(tk.END, '\n%s 【超速】再次推送未成功入库的数据: 【%s】' % (datetime.now(), push_result))
                f.write('\n%s 【超速】再次推送未成功入库的数据: 【%s】' % (datetime.now(), push_result))
            else:
                car_id = r.json().get('car_id')
                push_result = r.json().get('push_result')
                text.insert(tk.END, '\n%s 【超速】再次推送未成功入库的数据: 【%s-%s】' % (datetime.now(), car_id, push_result))
                f.write('\n%s 【超速】再次推送未成功入库的数据: 【%s-%s】' % (datetime.now(), car_id, push_result))
            sleep(int(push_time))
        except Exception as e:
            print(e)
            f.write("%s 【超速】推送数据出错 %s\n" % (datetime.now(), str(e)))
            text.insert(tk.END, "%s 【超速】推送数据出错 %s\n" % (datetime.now(), str(e)))
        finally:
            f.close()


def auto_run(move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    try:
        text.insert(tk.END, "%s 5秒后自动开始运行 【超速】取证扫描 \n" % datetime.now())
        # f.write("%s 5秒后自动开始运行 【超速】取证扫描  \n" % datetime.now())

        if is_push_cs == "1":
            thread_it(push_cs, ip_val, push_time)
        sleep(5)
        thread_it(QZ_run, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, wf_list)
        # 避免在服务器重启时失败
        # requests.post('http://%s/djDataInfo/delOutTimeDJImage/' % ip_val).json()
    except Exception as e:
        print(e)
        f.write("%s 自动运行出错 %s\n" % (datetime.now(), str(e)))
        text.insert(tk.END, "%s 自动运行出错 %s\n" % (datetime.now(), str(e)))
    finally:
        f.close()


if __name__ == '__main__':

    log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    # f.write('%s 正在读取配置文件...\n' % datetime.now())
    # f.close()

    if basic_info():
        qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list = basic_info()

        root = tk.Tk()

        root.title('超速扫描器v0.0.1_20220802')

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        text.insert(tk.END, "配置信息如下：\n")
        text.insert(tk.END, "取证文件夹路径：%s\n" % qz_path)
        text.insert(tk.END, "移动文件夹路径(暂取消备份)：%s\n" % move_folder)
        text.insert(tk.END, "服务器及端口：%s\n" % ip_val)
        text.insert(tk.END, "空闲间隔(秒)：%s\n" % sleep_time)
        text.insert(tk.END, "取证图片上传间隔(秒)：%s\n" % qz_time)
        text.insert(tk.END, "推送平台间隔(秒)：%s\n" % push_time)
        # text.insert(tk.END, "白名单：%s\n" % white_list)

        log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
        # f = open(log_file, 'a+', encoding='utf-8')
        # f.write('%s 配置读取成功\n ' % datetime.now())
        # f.write("\n%s 配置信息如下\n" % datetime.now())
        # f.write("取证文件夹路径：%s\n" % qz_path)
        # f.write("移动文件夹路径(暂取消备份)：%s\n" % move_folder)
        # f.write("服务器及端口：%s\n" % ip_val)
        # f.write("空闲间隔(秒)：%s\n" % sleep_time)
        # f.write("取证图片上传间隔(秒)：%s\n" % qz_time)
        # f.write("推送平台间隔(秒)：%s\n" % push_time)

        text.grid(row=0, column=0)
        root.geometry('1000x800+600+50')
        lf = tk.LabelFrame(root, text='')
        lf.grid(row=0, column=1)

        qz_lb = tk.Label(lf, text="超速文件夹路径为：")
        qz_lb.grid()

        qz_val = tk.Label(lf, text=qz_path, wraplength=400)
        qz_val.grid()

        # count_qz_lb = tk.Label(lf, text="\n已处理取证图片数：0\n")
        # count_qz_lb.grid()

        count_thread_lb = tk.Label(lf, text="\n已开启扫描器数：0\n")
        count_thread_lb.grid()

        # qz_bt = tk.Button(lf, text='开始扫描取证文件夹', fg='red',
        #                   command=lambda: thread_it(QZ_run, qz_path, move_folder, ip_val, white_list, sleep_time,
        #                                             qz_time, wf_list))
        qz_bt = tk.Button(lf, text='开始扫描超速文件夹', fg='red',
                          command=lambda: thread_it(QZ_run, qz_path, move_folder, ip_val, white_list, sleep_time,
                                                    qz_time, wf_list))

        qz_bt.grid(padx=5, pady=20)

        thread_it(auto_run, move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list)

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()

