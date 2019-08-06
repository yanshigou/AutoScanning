# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/8/6"
import traceback
from datetime import datetime
import tkinter as tk
import tkinter.filedialog
from tkinter import scrolledtext
import threading
import requests
import os
import shutil
from time import sleep
import base64


def TkWindow():
    root.title("---手动单次上传图片---")

    btn = tk.Button(root, text='上传事件或短信图片', command=lambda: thread_it(file2))
    btn2 = tk.Button(root, text='上传取证图片', command=lambda: thread_it(file))
    lb.pack()
    lb2.pack()

    btn.pack()
    btn2.pack()

    root.geometry('1000x500+800+400')
    root.mainloop()


def file():
    try:
        count = 0
        filename = tk.filedialog.askopenfilename()
        split_val = qz_path.split("\\")[-1]
        print(split_val)
        if filename != "":
            lb2.config(text="上传的图片为：" + filename)
            file_path = filename

            split_path_list = file_path.split(split_val)[-1]
            path_list = split_path_list.split("\\")[:-1]
            path_list_folder = "\\".join(path_list)
            folder = move_folder + ("\\%s" % split_val) + path_list_folder

            print(folder)

            if not os.path.exists(folder):
                os.makedirs(folder)

            file_path = filename
            file_name = filename.split('/')[-1]
            file_name_list = file_name.split('_')
            print(file_name_list)
            i_type = file_name_list[0]
            print(i_type)
            print(type(i_type))
            if i_type == ('1039' or "10396"):

                print("取证图片")
                # 对取证进行操作
                ip = file_name_list[4]
                car_id = file_name_list[5]
                if car_id in white_list:
                    os.remove(file_path)
                    print('在白名单内，删除成功')
                else:
                    car_color = file_name_list[-1][0]
                    print(car_color)
                    car_type = '00'
                    if car_color == "蓝":
                        car_type = '02'
                    elif car_color == '黄':
                        car_type = '01'
                    elif car_color == '绿':
                        car_type = '19'
                    wf_time = file_name_list[1] + file_name_list[2]
                    f = open(file_path, 'rb')
                    files = {'image_file': (file_name, f, 'image/jpg')}

                    data = dict(
                        data_type='WT', ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
                    )
                    print(data)
                    res = requests.post('http://%s/dataInfo/wtDataInfoUpload/' % ip_val, files=files, data=data).json()
                    status = res['status']
                    print(status)
                    print(res['is_del'])
                    f.close()
                    try:
                        if res['is_del']:
                            os.remove(file_path)
                            print('删除成功')
                        else:
                            shutil.move(file_path, folder)
                            print('移动成功')
                    except Exception as ex:
                        os.remove(file_path)
                        print('删除成功')
                    finally:
                        sleep(0.5)
                        now_time = datetime.now()
                        res = {"status": "success", "count": count, "res_status": status, "file_path": file_path,
                               "folder": folder}
                        print(res)
                        status = res.get('status')
                        res_status = res.get('res_status')
                        count += res.get('count')
                        e = res.get('e')
                        file_path = res.get('file_path')
                        folder = res.get('folder')

                        if status == "success":
                            if res_status == "success":
                                res_status = '成功'
                                text.insert(tk.END, "\n%s【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (
                                    now_time, file_path, res_status, folder))
                            elif res_status == "error":
                                res_status = '出错'
                                text.insert(tk.END,
                                            "\n%s 【取证】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                            else:
                                res_status = '失败'
                                text.insert(tk.END, "\n%s【取证】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (
                                    now_time, file_path, res_status, folder))
                        elif status == "fail":
                            text.insert(tk.END, "\n%s【取证】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, file_path))
                        elif status == "error":
                            text.insert(tk.END, "\n%s【取证】【上传出错，请查看日志】：%s\n" % (now_time, e))
                        elif status == "over":
                            print("1")
                            text.insert(tk.END,
                                        "\n%s 【取证】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, file_path, sleep_time))
                            text.see(tk.END)
                            sleep(int(sleep_time))
                        text.see(tk.END)

        else:
            lb2.config(text="您没有选择任何需要发送的文件")
    except Exception as e:
        print(e)
        text.insert(tk.END, "\n%s 【取证】出错" % datetime.now())


def file2():
    try:
        count = 0
        sms_count = 0
        split_val = event_path.split("\\")[-1]
        filename = tk.filedialog.askopenfilename()
        if filename != "":
            lb2.config(text="上传的图片为：" + filename)
            file_path = filename
            print(file_path)
            image_folder = "/".join(file_path.split("/")[:-1]) + '/'
            print(image_folder)
            # path_list = file_path.split('\\')
            # path_list[4] = "备份"
            # folder = "\\".join(path_list[:-1])

            print("event_path", event_path)
            print("split_val", split_val)
            split_path_list = file_path.split(split_val)[-1]
            print('split_path_list', split_path_list)
            path_list = split_path_list.split("/")[:-1]
            print('path_list', path_list)
            path_list_folder = "/".join(path_list)
            print('path_list_folder', path_list_folder)
            folder = move_folder + ("/%s" % split_val) + path_list_folder

            print("folder", folder)

            if not os.path.exists(folder):
                os.makedirs(folder)

            file_name = filename.split('/')[-1]
            file_name_list = file_name.split('_')
            print(file_name_list)
            i_type = file_name_list[0]
            last_str = file_name_list[-1]
            print(last_str)
            if i_type == '2' and ('短信' not in last_str):
                count += 1
                print('事件图片')
                # 进行对事件进行操作
                ip = file_name_list[4]
                car_id = file_name_list[5]
                if car_id in white_list:
                    os.remove(file_path)
                    print('在白名单内，删除成功')
                else:
                    car_color = file_name_list[-1][0]
                    print(car_color)
                    car_type = '00'
                    if car_color == "蓝":
                        car_type = '02'
                    elif car_color == '黄':
                        car_type = '01'
                    elif car_color == '绿':
                        car_type = '19'

                    wf_time = file_name_list[1] + file_name_list[2]
                    f = open(file_path, 'rb')
                    files = {'image_file': (file_name, f, 'image/jpg')}

                    data = dict(
                        data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                        wf_time=wf_time
                    )
                    print("data", data)

                    res = requests.post('http://%s/dataInfo/wtDataEventUpload/' % ip_val, files=files, data=data).json()
                    status = res['status']
                    print(status)
                    zp = res.get('zp')
                    image_file = res.get('sms_image')
                    print(image_file)
                    zpname = ""
                    if zp:
                        # 存在本机后再传图片至服务器
                        imgdata = base64.b64decode(zp)
                        l = image_file.split('.jpg')
                        zpname = image_folder + l[0] + '_短信' + '.jpg'
                        img = open(zpname, 'wb')
                        img.write(imgdata)
                        img.close()
                    print(res['is_del'])
                    f.close()
                    try:
                        if res['is_del']:
                            os.remove(file_path)
                            print('删除成功')
                        else:
                            shutil.move(file_path, folder)
                            print('移动成功')
                    except Exception as ex:
                        os.remove(file_path)
                        print('删除成功')
                    finally:
                        sleep(0.1)
                        res = {"status": "success", "count": count, "sms_count": sms_count, "res_status": status,
                               "file_path": file_path, "folder": folder, "zpname": zpname}
                        print(res)
                        status = res.get('status')
                        res_status = res.get('res_status')
                        count += res.get('count')
                        sms_count += res.get('sms_count')
                        e = res.get('e')
                        file_path = res.get('file_path')
                        folder = res.get('folder')
                        zpname = res.get('zpname')
                        zp = res.get('zp')

                        now_time = datetime.now()
                        if zpname:
                            text.insert(tk.END, '\n%s 短信发送成功，已收到短信图片%s，等待扫描上传' % (now_time, zpname))
                        if status == "success" and zp != 'success':

                            if res_status == "success":
                                res_status = '成功'
                            elif res_status == "error":
                                res_status = '出错'
                                text.insert(tk.END,
                                            "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                            else:
                                res_status = '失败'
                            text.insert(tk.END,
                                        "\n%s 【事件】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (
                                        now_time, file_path, res_status, folder))
                        elif status == "success" and zp == 'success':
                            if res_status == "success":
                                res_status = '成功'
                            elif res_status == "error":
                                res_status = '出错'
                                text.insert(tk.END,
                                            "\n%s 【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                            else:
                                res_status = '失败'
                            text.insert(tk.END, "\n%s 【事件-短信】【扫描到文件】%s，上传文件【%s】，【移动至】%s\n" % (
                                now_time, file_path, res_status, folder))
                        elif status == "fail":
                            text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, file_path))
                        elif status == "error":
                            text.insert(tk.END, "\n%s 【事件】【上传图片出错，请查看日志】：%s\n" % (now_time, e))
                        elif status == "over":
                            text.insert(tk.END,
                                        "\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, file_path, sleep_time))
                            text.see(tk.END)
                            sleep(int(sleep_time))
                        text.see(tk.END)
                        sleep(0.1)
            elif i_type == '2' and '短信' in last_str:
                sms_count += 1
                print('凭证图片')
                # 进行对凭证进行操作
                ip = file_name_list[4]
                car_id = file_name_list[5]
                wf_time = file_name_list[1] + file_name_list[2]
                if car_id in white_list:
                    os.remove(file_path)
                    print('在白名单内，删除成功')
                else:
                    car_color = file_name_list[-2][0]
                    print(car_color)
                    car_type = '00'
                    if car_color == "蓝":
                        car_type = '02'
                    elif car_color == '黄':
                        car_type = '01'
                    elif car_color == '绿':
                        car_type = '19'
                    f = open(file_path, 'rb')
                    files = {'image_file': (file_name, f, 'image/jpg')}

                    data = dict(
                        data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                        wf_time=wf_time
                    )

                    res = requests.post('http://%s/dataInfo/wtDataEventSMSUpload/' % ip_val, files=files,
                                        data=data).json()
                    status = res['status']
                    print(status)
                    print(res['is_del'])
                    f.close()
                    try:
                        if res['is_del']:
                            os.remove(file_path)
                            print('删除成功')
                        else:
                            shutil.move(file_path, folder)
                            print('移动成功')
                    except Exception as ex:
                        os.remove(file_path)
                        print('删除成功')
                    finally:
                        sleep(0.1)
                        return {"status": "success", "count": count, "sms_count": sms_count, "res_status": status,
                                "file_path": file_path,
                                "folder": folder, "zp": "success"}
            # res = sendMail(content, date, filename, to_mail)
            # if res is True:
            #     lb2.config(text=filename + "发送成功")
            # else:
            #     lb2.config(text=res)
        else:
            lb2.config(text="您没有选择任何需要发送的文件")
    except Exception as e:
        print(e)
        text.insert(tk.END, "\n%s 【事件】出错" % datetime.now())


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


def basic_info():
    white_list = []
    try:
        f = open("ACconfig.txt", 'r', encoding='utf-8')
        all_data = f.readlines()
        event_path = all_data[0].split('=')[-1].strip()
        qz_path = all_data[1].split('=')[-1].strip()
        move_folder = all_data[2].split('=')[-1].strip()
        ip_val = all_data[3].split('=')[-1].strip()
        sleep_time = all_data[4].split('=')[-1]
        qz_time = all_data[5].split('=')[-1]
        # car_id = all_data[4].split('=')[-1].split(' ')
        # for i in car_id:
        #     white_list.append(i)
        f.close()

        print(event_path)
        print(qz_path)
        print(move_folder)
        print(ip_val)
        print(white_list)
        print(sleep_time)
        print(qz_time)
        return event_path, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    event_path, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time = basic_info()
    root = tk.Tk()
    # 滚动条
    scroll = tk.Scrollbar()
    text = scrolledtext.ScrolledText(root, width=90, height=20)
    text.pack()
    lb = tk.Label(root, text="您没有选择任何事件或短信图片")
    lb2 = tk.Label(root, text="您没有选择任何取证图片")
    TkWindow()
