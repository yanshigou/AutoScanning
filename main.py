# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from upload_image import event, QZ
from datetime import datetime
from time import sleep


# 建立连接 获取csrftoken
client = requests.session()


# client.get('http://127.0.0.1:8000/users/login/')
# if 'csrftoken' in client.cookies:
#     csrftoken = client.cookies['csrftoken']
#     print(csrftoken)
# else:
#     csrftoken = client.cookies['csrf']
#     print(csrftoken)
def basic_info():
    white_list = ['渝DJD020', '渝AZC452']
    try:
        f = open("ACconfig.txt", 'r', encoding='utf-8')
        all_data = f.readlines()
        event_path = all_data[0].split('=')[-1].strip()
        qz_path = all_data[1].split('=')[-1].strip()
        move_folder = all_data[2].split('=')[-1].strip()
        ip_val = all_data[3].split('=')[-1].strip()
        car_id = all_data[4].split('=')[-1].split(' ')
        for i in car_id:
            white_list.append(i)
        f.close()

        print(event_path)
        print(qz_path)
        print(move_folder)
        print(ip_val)
        print(white_list)
        return event_path, qz_path, move_folder, ip_val, white_list
    except Exception as e:
        print(e)
        return False


def event_run(event_path, move_folder, ip_val, white_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始扫描事件文件夹：%s\n" % event_path)
    f.write("开始扫描事件文件夹：%s" % event_path)
    f.close()
    count = 0
    event_bt.config(state="disabled", text='正在扫描事件文件夹')
    while True:
        log_file = datetime.now().strftime('%Y-%m-%d') + '日志.txt'
        try:
            f = open(log_file, 'a+', encoding='utf-8')
            # sleep(1)
            now_time = datetime.now()
            res = event(FileObjectManager(FileObject(event_path)).scan_with_depth(10).all_file_objects(), move_folder,
                        ip_val, event_path, now_time, white_list)
            print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')
            folder = res.get('folder')
            count_event_lb.config(text='\n已处理事件图片数：%s\n' % count)
            now_time = datetime.now()
            if status == "success":

                if res_status == "success":
                    res_status = '成功'
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (now_time, file_path, res_status, folder))
                f.write("\n%s 【事件】【扫描到文件】%s，上传文件【%s】，【移动至】%s" % (now_time, file_path, res_status, folder))
            elif status == "fail":
                text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, file_path))
                f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】" % (now_time, file_path))
            elif status == "error":
                text.insert(tk.END, "\n%s 【事件】【上传图片出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【事件】【上传图片出错，请检查日志】：%s" % (now_time, e))
            elif status == "over":
                text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息2分钟】\n" % (now_time, file_path))
                f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息2分钟】\n" % (now_time, file_path))
                text.see(tk.END)
                sleep(60 * 2)
            text.see(tk.END)
        except Exception as e:
            text.insert(tk.END, "\n%s 【事件】程序出错：%s\n" % (datetime.now(), e))
            text.see(tk.END)
            f.write("\n%s 【事件】程序出错：%s" % (datetime.now(), e))
            f.close()
        finally:
            f.close()


def QZ_run(qz_path, move_folder, ip_val, white_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始扫描取证文件夹：%s\n" % qz_path)
    f.write("开始扫描取证文件夹：%s" % event_path)
    f.close()
    count = 0
    qz_bt.config(state="disabled", text='正在扫描取证文件夹')
    while True:
        log_file = datetime.now().strftime('%Y-%m-%d') + '日志.txt'
        try:
            f = open(log_file, 'a+', encoding='utf-8')
            # sleep(1)
            now_time = datetime.now()
            res = QZ(FileObjectManager(FileObject(qz_path)).scan_with_depth(10).all_file_objects(), move_folder,
                     ip_val, qz_path, now_time, white_list)
            print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')
            folder = res.get('folder')
            count_qz_lb.config(text='\n已处理取证图片数：%s\n' % str(count))

            if status == "success":
                if res_status == "success":
                    res_status = '成功'
                    text.insert(tk.END, "\n%s【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (now_time, file_path, res_status, folder))
                    f.write("\n%s 【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s" % (now_time, file_path, res_status, folder))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【取证】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【取证】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                    text.insert(tk.END, "\n%s【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (now_time, file_path, res_status, folder))
                    f.write("\n%s 【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s" % (now_time, file_path, res_status, folder))
            elif status == "fail":
                text.insert(tk.END, "\n%s【取证】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, file_path))
                f.write("\n%s 【取证】【扫描到文件夹】 %s，【未发现图片】" % (now_time, file_path))
            elif status == "error":
                text.insert(tk.END, "\n%s【取证】【上传出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【取证】【上传出错，请检查日志】：%s" % (now_time, e))
            elif status == "over":
                print("1")
                text.insert(tk.END, "\n%s 【取证】【扫描到文件夹】 %s，【未发现任何图片，休息2分钟】\n" % (now_time, file_path))
                f.write("\n%s 【取证】【扫描到文件夹】 %s，【未发现任何图片，休息2分钟】\n" % (now_time, file_path))
                text.see(tk.END)
                sleep(60 * 2)
            text.see(tk.END)
        except Exception as e:
            text.insert(tk.END, "\n%s 【取证】程序出错：%s\n" % (datetime.now(), e))
            text.see(tk.END)
            f.write("\n%s 【取证】程序出错：%s" % (datetime.now(), e))
            f.close()
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


if __name__ == '__main__':
    if not basic_info():
        root = tk.Tk()

        root.title('违法图片扫描器v2.12')

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)
        text.grid(row=0, column=0)
        root.geometry('1000x800+600+50')
        lf = tk.LabelFrame(root, text='请检查配置文件ACconfig.txt是否在同级目录下')
        lf.grid(row=0, column=1)
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n")
        text.insert(tk.END, "\n并且仅支持如下格式\n")
        text.insert(tk.END, "\n事件地址=G:\dzt\资料\交警\测试文件夹\事件\n")
        text.insert(tk.END, "取证地址=G:\dzt\资料\交警\测试文件夹\取证\n")
        text.insert(tk.END, "移动地址=G:\dzt\资料\交警\备份\n")
        text.insert(tk.END, "IP=192.168.31.54:8000\n")
        text.insert(tk.END, "白名单=渝DDD000 渝ADA233\n")

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()
    else:
        event_path, qz_path, move_folder, ip_val, white_list = basic_info()

        root = tk.Tk()

        root.title('违法图片扫描器v3.0')

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        text.insert(tk.END, "配置信息如下：\n")
        text.insert(tk.END, "事件文件夹路径：%s\n" % event_path)
        text.insert(tk.END, "取证文件夹路径：%s\n" % qz_path)
        text.insert(tk.END, "移动文件夹路径：%s\n" % move_folder)
        text.insert(tk.END, "服务器及端口：%s\n" % ip_val)
        # text.insert(tk.END, "白名单：%s\n" % white_list)

        log_file = datetime.now().strftime('%Y-%m-%d') + '日志.txt'
        f = open(log_file, 'a+', encoding='utf-8')
        text.insert(tk.END, "开始删除服务器上打包的文件\n")
        res = requests.post('http://%s/dataInfo/autoDelView/' % ip_val).json()
        if res["status"] == "success":
            f.write("删除服务器上打包的文件成功\n")
            text.insert(tk.END, "删除服务器上打包的文件成功\n")
        else:
            f.write("删除服务器上打包的文件失败 %s\n" % res['e'])
            text.insert(tk.END, "删除服务器上打包的文件失败\n")
        f.close()

        text.grid(row=0, column=0)
        root.geometry('1000x800+600+50')
        lf = tk.LabelFrame(root, text='')
        lf.grid(row=0, column=1)

        event_lb = tk.Label(lf, text="事件文件夹路径为：")
        event_lb.grid()

        event_val = tk.Label(lf, text=event_path, wraplength=400)
        event_val.grid()

        count_event_lb = tk.Label(lf, text="\n已处理事件图片数：0\n")
        count_event_lb.grid()

        qz_lb = tk.Label(lf, text="取证文件夹路径为：")
        qz_lb.grid()

        qz_val = tk.Label(lf, text=qz_path, wraplength=400)
        qz_val.grid()

        count_qz_lb = tk.Label(lf, text="\n已处理取证图片数：0\n")
        count_qz_lb.grid()

        event_bt = tk.Button(lf, text='开始扫描事件文件夹', fg='red',
                             command=lambda: thread_it(event_run, event_path, move_folder, ip_val, white_list))
        qz_bt = tk.Button(lf, text='开始扫描取证文件夹', fg='red',
                          command=lambda: thread_it(QZ_run, qz_path, move_folder, ip_val, white_list))
        event_bt.grid(padx=5, pady=20)
        qz_bt.grid(padx=5, pady=20)

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()
