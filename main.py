# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests
import tkinter as tk
import threading
from tkinter import scrolledtext
from upload_image import event, QZ
from deviceStatus import ping
from datetime import datetime
from time import sleep
import configparser

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
    white_list = ['渝DJD020', '渝AA6W72', '渝A015EY', '渝AZC452']
    try:
        cf = configparser.ConfigParser()
        cf.read("ACconfig.ini", encoding="utf-8-sig")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块


        # options = cf.options("DJConfig")  # 获取某个section名为BasicConfig所对应的键
        # print(options)
        #
        # items = cf.items("DJConfig")  # 获取section名为BasicConfig所对应的全部键值对
        # print(items)

        qz_path = cf.get("WTConfig", "qz_path")  # 获取[BasicConfig]中qz_path对应的值

        event_path = cf.get("WTConfig", "event_path")  # 获取[BasicConfig]中qz_path对应的值

        move_folder = cf.get("WTConfig", "move_folder")  # 获取[BasicConfig]中move_folder对应的值

        ip_val = cf.get("WTConfig", "ip_val")  # 获取[BasicConfig]中ip_val对应的值

        sleep_time = cf.get("WTConfig", "sleep_time")  # 获取[BasicConfig]中sleep_time对应的值

        qz_time = cf.get("WTConfig", "qz_time")  # 获取[BasicConfig]中qz_time对应的值

        push_time = cf.get("WTConfig", "push_time")  # 获取[BasicConfig]中push_time对应的值

        wf_list_str = cf.get("WTConfig", "wf_list")  # 获取[BasicConfig]中wf_list对应的值
        wf_list = wf_list_str.split(',')

        global is_check_online
        is_check_online = cf.get("WTConfig", "is_check_online")  # 获取[BasicConfig]中is_check_online对应的值

        global is_push
        is_push = cf.get("WTConfig", "is_push")  # 获取[BasicConfig]中is_push对应的值

        return event_path, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list
    except Exception as e:
        print(e)
        return False


def event_run(event_path, move_folder, ip_val, white_list, sleep_time):
    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始扫描事件文件夹：%s\n" % event_path)
    f.write("开始扫描事件文件夹：%s\n" % event_path)
    f.close()
    count = 0
    sms_count = 0
    event_bt.config(state="disabled", text='正在扫描事件文件夹')
    while True:
        log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
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
            sms_count += res.get('sms_count')
            e = res.get('e')
            file_path = res.get('file_path')

            zpname = res.get('zpname')
            zp = res.get('zp')

            now_time = datetime.now()
            if zpname:
                text.insert(tk.END, '\n%s 短信发送成功，已收到短信图片%s，等待扫描上传' % (now_time, zpname))
                f.write('\n%s 短信发送成功，已收到短信图片%s，等待扫描上传' % (now_time, zpname))
            if status == "success" and zp != 'success':

                if res_status == "success":
                    res_status = '成功'
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【事件】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                text.insert(tk.END, "\n%s 【事件】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                f.write("\n%s 【事件】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
            elif status == "success" and zp == 'success':
                if res_status == "success":
                    res_status = '成功'
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【事件-短信】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                text.insert(tk.END,
                            "\n%s 【事件-短信】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                f.write("\n%s 【事件-短信】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
            elif status == "fail":
                text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, event_path))
                f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现图片】" % (now_time, event_path))
            elif status == "error":
                text.insert(tk.END, "\n%s 【事件】【上传图片出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【事件】【上传图片出错，请检查日志】：%s" % (now_time, e))
            elif status == "over":
                text.insert(tk.END, "\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, event_path, sleep_time.strip()))
                f.write("\n%s 【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, event_path, sleep_time.strip()))
                text.see(tk.END)
                sleep(int(sleep_time))
            count_event_lb.config(text='\n已处理事件图片数：%s\n' % count)
            sms_lb.config(text='\n已处理短信图片数：%s\n' % sms_count)
            f.write('\n%s 【事件】已处理事件图片数：%s\n' % (now_time, count))
            f.write('\n%s 【事件-短信】已处理短信图片数：%s\n' % (now_time, sms_count))
            text.see(tk.END)
            sleep(0.1)
        except Exception as ee:
            text.insert(tk.END, "\n%s 【事件】程序出错：%s\n" % (datetime.now(), str(ee)))
            text.see(tk.END)
            f.write("\n%s 【事件】程序出错：%s" % (datetime.now(), str(ee)))
        finally:
            f.close()


def QZ_run(qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, wf_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "\n开始扫描取证文件夹：%s\n" % qz_path)
    f.write("%s \n开始扫描取证文件夹：%s" % (qz_path, datetime.now()))
    f.close()
    count = 0
    qz_bt.config(state="disabled", text='正在扫描取证文件夹')
    while True:
        log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
        try:
            f = open(log_file, 'a+', encoding='utf-8')
            # sleep(1)
            now_time = datetime.now()
            res = QZ(FileObjectManager(FileObject(qz_path)).scan_with_depth(10).all_file_objects(), move_folder,
                     ip_val, qz_path, now_time, white_list, wf_list)
            print(res)
            status = res.get('status')
            res_status = res.get('res_status')
            count += res.get('count')
            e = res.get('e')
            file_path = res.get('file_path')

            if status == "success":
                if res_status == "success":
                    res_status = '成功'
                    text.insert(tk.END,
                                "\n%s【取证】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【取证】【扫描到文件】%s，上传文件【%s】\n" % (now_time, file_path, res_status))
                elif res_status == "error":
                    res_status = '出错'
                    text.insert(tk.END, "\n%s 【取证】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【取证】【扫描到文件】%s，服务器【%s】，%s" % (now_time, file_path, res_status, e))
                elif res_status == "wait":
                    res_status = '再次推送'
                    text.insert(tk.END,
                                "\n%s 【取证】【扫描到文件】%s，已上传取证图片，未推送成功，【%s】，%s" % (now_time, file_path, res_status, e))
                    f.write("\n%s 【取证】【扫描到文件】%s，已上传取证图片，未推送成功，【%s】，%s" % (now_time, file_path, res_status, e))
                else:
                    res_status = '失败'
                    text.insert(tk.END,
                                "\n%s【取证】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
                    f.write("\n%s 【取证】【扫描到文件】%s，上传文件【%s】, 该设备未启用\n" % (now_time, file_path, res_status))
            elif status == "fail":
                text.insert(tk.END, "\n%s【取证】【扫描到文件夹】 %s，【未发现图片】\n" % (now_time, qz_path))
                f.write("\n%s 【取证】【扫描到文件夹】 %s，【未发现图片】" % (now_time, qz_path))
            elif status == "error":
                text.insert(tk.END, "\n%s【取证】【上传出错，请查看日志】：%s\n" % (now_time, e))
                f.write("\n%s 【取证】【上传出错，请检查日志】：%s" % (now_time, e))
            elif status == "over":
                text.insert(tk.END, "\n%s 【取证】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                f.write("\n%s 【取证】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】\n" % (now_time, qz_path, sleep_time.strip()))
                text.see(tk.END)
                sleep(int(sleep_time))
            count_qz_lb.config(text='\n已处理取证图片数：%s\n' % str(count))
            f.write('\n%s 已处理取证图片数：%s\n' % (now_time, str(count)))
            text.see(tk.END)
            # 大量同时推送集成平台时，会出错
            if qz_time != '0':
                sleep(int(qz_time))
        except Exception as ee:
            text.insert(tk.END, "\n%s 【取证】程序出错：%s\n" % (datetime.now(), str(ee)))
            text.see(tk.END)
            f.write("\n%s 【取证】程序出错：%s" % (datetime.now(), str(ee)))
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


def check_device_online(ip_val):
    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始检测设备状态")
    f.write("开始检测设备状态")
    f.close()
    ping_bt.config(state="disabled", text='开始检测设备状态')
    while True:
        f = open(log_file, 'a+', encoding='utf-8')
        try:
            res = requests.get('http://%s/devices/allDevices/' % ip_val)
            ip_list = res.json().get('devices')
            for ip in ip_list:
                now_time = datetime.now()
                is_online = ping(ip)
                if is_online:
                    text.insert(tk.END, '\n%s 设备 %s 在线' % (now_time, ip))
                    f.write('\n%s 设备 %s 在线' % (now_time, ip))
                    requests.get('http://%s/devices/statusModify/?is_online=1&ip=%s' % (ip_val, ip))
                else:
                    text.insert(tk.END, '\n%s 设备 %s 离线' % (now_time, ip))
                    f.write('\n%s 设备 %s 离线' % (now_time, ip))
                    requests.get('http://%s/devices/statusModify/?is_online=0&ip=%s' % (ip_val, ip))

            sleep(60 * 5)
        except Exception as e:
            print(e)
            f.write("%s 检测设备在线状态出错 %s\n" % (datetime.now(), str(e)))
            text.insert(tk.END, "%s 检测设备在线状态出错 %s\n" % (datetime.now(), str(e)))
        finally:
            f.close()


def push(ip_val, push_time):
    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    text.insert(tk.END, "开始推送至集成平台")
    f.write("开始推送至集成平台")
    f.close()
    while True:
        f = open(log_file, 'a+', encoding='utf-8')
        try:
            # 加入再次推送失败的
            r = requests.get('http://%s/dataInfo/push/' % ip_val)
            status = r.json().get('status')
            if status == "success":
                car_id = r.json().get('car_id')
                text.insert(tk.END, '\n%s 【违停】再次推送未成功入库的数据: 【%s】' % (datetime.now(), car_id))
                f.write('\n%s 【违停】再次推送未成功入库的数据: 【%s】' % (datetime.now(), car_id))
            elif status == "fail":
                push_result = r.json().get('push_result')
                text.insert(tk.END, '\n%s 【违停】再次推送未成功入库的数据: 【%s】' % (datetime.now(), push_result))
                f.write('\n%s 【违停】再次推送未成功入库的数据: 【%s】' % (datetime.now(), push_result))
            else:
                car_id = r.json().get('car_id')
                push_result = r.json().get('push_result')
                text.insert(tk.END, '\n%s 【违停】再次推送未成功入库的数据: 【%s-%s】' % (datetime.now(), car_id, push_result))
                f.write('\n%s 【违停】再次推送未成功入库的数据: 【%s-%s】' % (datetime.now(), car_id, push_result))
            sleep(int(push_time))
        except Exception as e:
            print(e)
            f.write("%s 【违停】推送数据出错 %s\n" % (datetime.now(), str(e)))
            text.insert(tk.END, "%s 【违停】推送数据出错 %s\n" % (datetime.now(), str(e)))
        finally:
            f.close()


def auto_run(event_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time):
    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    try:
        text.insert(tk.END, "%s 5秒后自动开始运行 事件扫描、设备在线检测 \n" % datetime.now())
        text.insert(tk.END, "%s 30秒后自动开始运行 取证扫描 \n" % datetime.now())
        f.write("%s 5秒后自动开始运行 事件扫描、设备在线检测 \n" % datetime.now())
        f.write("%s 30秒后自动开始运行 取证扫描  \n" % datetime.now())
        sleep(5)
        thread_it(event_run, event_path, move_folder, ip_val, white_list, sleep_time)
        if is_check_online == "1":
            thread_it(check_device_online, ip_val)
        if is_push == "1":
            thread_it(push, ip_val, push_time)
        sleep(25)
        thread_it(QZ_run, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, wf_list)
        # 避免在服务器重启时删除失败
        requests.post('http://%s/dataInfo/delWTImage/' % ip_val).json()
        requests.post('http://%s/dataInfo/autoDelView/' % ip_val).json()
    except Exception as e:
        print(e)
        f.write("%s 自动运行出错 %s\n" % (datetime.now(), str(e)))
        text.insert(tk.END, "%s 自动运行出错 %s\n" % (datetime.now(), str(e)))
    finally:
        f.close()


if __name__ == '__main__':

    log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    f = open(log_file, 'a+', encoding='utf-8')
    f.write('%s 正在读取配置文件...\n' % datetime.now())
    f.close()

    # if not basic_info():
    #     try:
    #         root = tk.Tk()
    #
    #         root.title('巴南区违停扫描器v5.0.1_20191010')
    #
    #         # 滚动条
    #         scroll = tk.Scrollbar()
    #
    #         text = scrolledtext.ScrolledText(root, width=90, height=60)
    #         text.grid(row=0, column=0)
    #         root.geometry('1000x800+600+50')
    #         lf = tk.LabelFrame(root, text='请检查配置文件ACconfig.txt是否在同级目录下')
    #         lf.grid(row=0, column=1)
    #         log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    #         f = open(log_file, 'a+', encoding='utf-8')
    #         f.write("%s 未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n" % datetime.now())
    #         f.write("\n并且仅支持如下格式\n")
    #         f.write("\n事件地址=G:\dzt\资料\交警\测试文件夹\事件\n")
    #         f.write("取证地址=G:\dzt\资料\交警\测试文件夹\取证\n")
    #         f.write("移动地址(暂取消备份)=G:\dzt\资料\交警\备份\n")
    #         f.write("IP=192.168.31.54:8000\n")
    #         f.write("空闲间隔(秒)=5\n")
    #         f.write("取证图片上传间隔(秒)=30\n")
    #         f.write("推送平台间隔(秒)=10\n")
    #
    #         text.insert(tk.END, "%s 未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n" % datetime.now())
    #         text.insert(tk.END, "%s 未找到配置文件，请检查ACconfig.txt是否在同级目录下！！\n" % datetime.now())
    #         text.insert(tk.END, "\n并且仅支持如下格式\n")
    #         text.insert(tk.END, "\n事件地址=G:\dzt\资料\交警\测试文件夹\事件\n")
    #         text.insert(tk.END, "取证地址=G:\dzt\资料\交警\测试文件夹\取证\n")
    #         text.insert(tk.END, "移动地址(暂取消备份)=G:\dzt\资料\交警\备份\n")
    #         text.insert(tk.END, "IP=192.168.31.54:8000\n")
    #         text.insert(tk.END, "空闲间隔(秒)=5\n")
    #         text.insert(tk.END, "取证图片上传间隔(秒)=30\n")
    #         text.insert(tk.END, "推送平台间隔(秒)=10\n")
    #
    #         q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
    #         q.grid(padx=5, pady=10)
    #
    #         root.mainloop()
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         f.close()
    # else:
    if basic_info():
        event_path, qz_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time, wf_list = basic_info()

        root = tk.Tk()

        root.title('违停扫描器v5.0.5_20191209')

        # 滚动条
        scroll = tk.Scrollbar()

        text = scrolledtext.ScrolledText(root, width=90, height=60)

        text.insert(tk.END, "配置信息如下：\n")
        text.insert(tk.END, "事件文件夹路径：%s\n" % event_path)
        text.insert(tk.END, "取证文件夹路径：%s\n" % qz_path)
        text.insert(tk.END, "移动文件夹路径(暂取消备份)：%s\n" % move_folder)
        text.insert(tk.END, "服务器及端口：%s\n" % ip_val)
        text.insert(tk.END, "空闲间隔(秒)：%s\n" % sleep_time)
        text.insert(tk.END, "取证图片上传间隔(秒)：%s\n" % qz_time)
        text.insert(tk.END, "推送平台间隔(秒)：%s\n" % push_time)
        # text.insert(tk.END, "白名单：%s\n" % white_list)

        log_file = datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
        f = open(log_file, 'a+', encoding='utf-8')
        f.write('%s 配置读取成功\n ' % datetime.now())
        f.write("\n%s 配置信息如下\n" % datetime.now())
        f.write("事件文件夹路径：%s\n" % event_path)
        f.write("取证文件夹路径：%s\n" % qz_path)
        f.write("移动文件夹路径(暂取消备份)：%s\n" % move_folder)
        f.write("服务器及端口：%s\n" % ip_val)
        f.write("空闲间隔(秒)：%s\n" % sleep_time)
        f.write("取证图片上传间隔(秒)：%s\n" % qz_time)
        f.write("推送平台间隔(秒)：%s\n" % push_time)

        try:
            text.insert(tk.END, "%s 开始删除服务器上打包的【违停】文件\n" % datetime.now())
            f.write("%s 开始删除服务器上打包的【违停】文件\n" % datetime.now())
            res = requests.post('http://%s/dataInfo/autoDelView/' % ip_val).json()
            if res["status"] == "success":
                f.write("%s 删除服务器上打包的【违停】文件成功\n" % datetime.now())
                text.insert(tk.END, "删除服务器上打包的【违停】文件成功\n")
            else:
                f.write("%s 删除服务器上打包的【违停】文件失败 %s\n" % (datetime.now(), res['e']))
                text.insert(tk.END, "%s 删除服务器上打包的【违停】文件失败 %s\n" % (datetime.now(), res['e']))

            text.insert(tk.END, "%s 开始删除服务器上90天以前的【违停】事件、取证、短信图片\n" % datetime.now())
            f.write("%s 开始删除服务器上90天以前的【违停】事件、取证、短信图片\n" % datetime.now())
            res = requests.post('http://%s/dataInfo/delWTImage/' % ip_val).json()
            if res["status"] == "success":
                f.write("%s 删除服务器上90天以前的【违停】事件、取证、短信图片成功\n" % datetime.now())
                text.insert(tk.END, "删除服务器上90天以前的【违停】事件、取证、短信图片成功\n")
            else:
                f.write("%s 删除服务器上90天以前的【违停】事件、取证、短信图片失败 %s\n" % (datetime.now(), res['e']))
                text.insert(tk.END, "%s 删除服务器上90天以前的【违停】事件、取证、短信图片失败 %s\n" % (datetime.now(), res['e']))
        except Exception as e:
            print(e)
            f.write("%s 删除服务器上【违停】打包的文件出错，请检查服务器是否开启\n" % datetime.now())
            text.insert(tk.END, "%s 删除服务器上【违停】打包的文件出错，请检查服务器是否开启\n" % datetime.now())
        finally:
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

        sms_lb = tk.Label(lf, text="已处理短信图片数：0\n")
        sms_lb.grid()

        qz_lb = tk.Label(lf, text="取证文件夹路径为：")
        qz_lb.grid()

        qz_val = tk.Label(lf, text=qz_path, wraplength=400)
        qz_val.grid()

        count_qz_lb = tk.Label(lf, text="\n已处理取证图片数：0\n")
        count_qz_lb.grid()

        event_bt = tk.Button(lf, text='开始扫描事件文件夹', fg='red',
                             command=lambda: thread_it(event_run, event_path, move_folder, ip_val, white_list,
                                                       sleep_time))
        qz_bt = tk.Button(lf, text='开始扫描取证文件夹', fg='red',
                          command=lambda: thread_it(QZ_run, qz_path, move_folder, ip_val, white_list, sleep_time,
                                                    qz_time, wf_list))
        ping_bt = tk.Button(lf, text='开始检测设备状态', fg='red',
                            command=lambda: thread_it(check_device_online, ip_val))
        event_bt.grid(padx=5, pady=20)
        qz_bt.grid(padx=5, pady=20)
        ping_bt.grid(padx=5, pady=20)

        thread_it(auto_run, event_path, move_folder, ip_val, white_list, sleep_time, qz_time, push_time)

        q = tk.Button(lf, text='退  出', command=root.quit, padx=10, pady=5)
        q.grid(padx=5, pady=10)

        root.mainloop()
