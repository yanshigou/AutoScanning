# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests
import os
import shutil
from time import sleep
import tkinter as tk
import threading
from tkinter import scrolledtext
from upload_image import event, QZ


# 建立连接 获取csrftoken
client = requests.session()
# client.get('http://127.0.0.1:8000/users/login/')
# if 'csrftoken' in client.cookies:
#     csrftoken = client.cookies['csrftoken']
#     print(csrftoken)
# else:
#     csrftoken = client.cookies['csrf']
#     print(csrftoken)


def event2(event_files_list):
    count = 0
    for file in event_files_list:
        # 如果是文件,则打印
        if file.is_file:
            sleep(1)
            if file.file_name[-3:] == 'jpg':
                count += 1
                file_path = file.file_path

                path_list = file_path.split('\\')
                path_list[4] = "测试文件夹"
                folder = "\\".join(path_list[:-1])
                print(folder)

                if not os.path.exists(folder):
                    os.makedirs(folder)

                file_name = file.file_name
                file_name_list = file_name.split('_')
                print(file_name_list)
                i_type = file_name_list[0]
                if i_type == '2':
                    print('2')
                    # 进行对事件进行操作
                    ip = file_name_list[4]
                    car_id = file_name_list[5]
                    car_type = file_name_list[6]
                    wf_time = file_name_list[1] + file_name_list[2]
                    f = open(file_path, 'rb')
                    files = {'image_file': (file_name, f, 'image/jpg')}

                    data = dict(
                        data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                        wf_time=wf_time
                    )

                    res = requests.post('http://127.0.0.1:8000/dataInfo/wtDataEventUpload/', files=files, data=data).json()
                    status = res['status']
                    print(status)
                    print(res['is_del'])
                    f.close()
                    if res['is_del']:
                        os.remove(file_path)
                        print('删除成功')
                    else:
                        shutil.move(file_path, folder)
                        print('移动成功')
    return count


def QZ2(files_list):
    count = 0
    for file in files_list:
        # 如果是文件,则打印
        if file.is_file:
            sleep(1)
            if file.file_name[-3:] == 'jpg':
                count += 1
                file_path = file.file_path
                path_list = file_path.split('\\')
                path_list[4] = "测试文件夹"
                folder = "\\".join(path_list[:-1])
                print(folder)

                if not os.path.exists(folder):
                    os.makedirs(folder)

                file_path = file.file_path
                file_name = file.file_name
                file_name_list = file_name.split('_')
                print(file_name_list)
                i_type = file_name_list[0]
                if i_type == 1039 or 10396:
                    print(i_type)
                    # 对取证进行操作
                    ip = file_name_list[4]
                    car_id = file_name_list[5]
                    car_type = file_name_list[6]
                    wf_time = file_name_list[1]+file_name_list[2]
                    f = open(file_path, 'rb')
                    files = {'image_file': (file_name, f, 'image/jpg')}

                    data = dict(
                        data_type='WT', ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
                    )

                    res = requests.post('http://127.0.0.1:8000/dataInfo/wtDataInfoUpload/', files=files, data=data).json()
                    status = res['status']
                    print(status)
                    print(res['is_del'])
                    f.close()
                    if res['is_del']:
                        os.remove(file_path)
                        print('删除成功')
                    else:
                        try:
                            shutil.move(file_path, folder)
                            print('移动成功')
                        except Exception as e:
                            print(e)
                            os.remove(file_path)
                            print('删除成功')
    return count


def event_run(text, event_path, move_folder, ip_val):
    text.insert(tk.END, "开始扫描事件文件夹：%s\n" % event_path)
    count = 0
    while True:
        try:
            # sleep(1)
            res = event(FileObjectManager(FileObject(event_path)).scan_with_depth(10).all_file_objects(), move_folder, ip_val)
            print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')
            folder = res.get('folder')
            count_event_lb.config(text='\n已处理事件图片数：%s\n' % count)
            if status == "success":

                if res_status == "success":
                    res_status = '成功'
                else:
                    res_status = '失败'
                text.insert(tk.END, "\n【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (file_path, res_status, folder))
            elif status == "fail":
                text.insert(tk.END, "\n【扫描到文件夹】 %s，【未发现图片】\n" % file_path)
            elif status == "error":
                text.insert(tk.END, "\n【上传图片出错，请检查日志】：%s\n" % e)
            text.see(tk.END)
            # sleep(60 * 2)
        except Exception as e:
            print(e)


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

    f = open("ACconfig.txt", 'r', encoding='utf-8')
    all = f.readlines()
    event_path = all[0].split('=')[-1].strip()
    qz_path = all[1].split('=')[-1].strip()
    move_folder = all[2].split('=')[-1].strip()
    ip_val = all[3].split('=')[-1].strip()
    f.close()

    print(event_path)
    print(qz_path)
    print(move_folder)
    print(ip_val)

    root = tk.Tk()

    root.title('违法图片扫描器')

    # 滚动条
    scroll = tk.Scrollbar()

    text = scrolledtext.ScrolledText(root, width=90, height=60)
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

    event_bt = tk.Button(lf, text='开始扫描事件文件夹', command=lambda: thread_it(event_run, text, event_path, move_folder, ip_val))
    qz_bt = tk.Button(lf, text='开始扫描取证文件夹')
    event_bt.grid(padx=5, pady=20)
    qz_bt.grid(padx=5, pady=20)

    q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
    q.grid(padx=5, pady=10)

    root.mainloop()

    # while True:
    #     c = 0
    #     try:
    #         # sleep(1)
    #         # print('开始事件')
    #         # c += event(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\事件")).scan_with_depth(
    #         #     10).all_file_objects())
    #         # print('开始取证')
    #         # c += QZ(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\取证")).scan_with_depth(10).all_file_objects())
    #         # sleep(60 * 2)
    #         # print(c)
    #
    #         # 重复上传并移动回去
    #         print("开始事件2")
    #         c += event2(FileObjectManager(FileObject("G:\dzt\资料\交警\备份\事件")).scan_with_depth(
    #             10).all_file_objects())
    #         print("开始取证2")
    #         c += QZ2(FileObjectManager(FileObject("G:\dzt\资料\交警\备份\取证")).scan_with_depth(10).all_file_objects())
    #         print(c)
    #     except Exception as e:
    #         print(e)
    #         print(c)
