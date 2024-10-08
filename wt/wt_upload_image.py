# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from wt_file_manager import FileObjectManager, FileObject
import requests
import os
import re
from datetime import datetime
import base64
import random
import traceback
from requests.adapters import HTTPAdapter
from loggmodel import Logger
# import logging
# from logging import handlers
#
#
# class Logger:
#     # 日志级别关系映射
#     LEVEL_RELATIONS = {
#         'debug': logging.DEBUG,
#         'info': logging.INFO,
#         'warning': logging.WARNING,
#         'error': logging.ERROR,
#         'crit': logging.CRITICAL
#     }
#
#     def __init__(
#         self,
#         filename,
#         level='debug',
#         when='M',
#         # interval=1,
#         back_count=10,
#         fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
#     ):
#         self.logger = logging.getLogger(filename)
#
#         # 如果该logger已有handler，则先删除
#         if self.logger.handlers:
#             self.logger.handlers = []
#
#         # 设置日志格式
#         format_str = logging.Formatter(fmt)
#         # 设置日志级别
#         self.logger.setLevel(self.LEVEL_RELATIONS.get(level))
#
#         th = handlers.TimedRotatingFileHandler(
#             filename=filename,
#             when=when,
#             backupCount=back_count,
#             # interval=interval,
#             encoding='utf-8'
#         )
#
#         th.setFormatter(format_str)
#
#         self.logger.addHandler(th)


def event(event_files_list, ip_val, event_path, now_time, white_list, file_folder):
    log_file = os.path.join(file_folder, '违停日志事件.log')
    # flog = open(log_file, 'a+', encoding='utf-8')
    logg = Logger(log_file, level="info")

    split_val = event_path.split("\\")[-1]
    jpgFileList = []
    try:
        for file in event_files_list:
            if not file.is_file:
                try:
                    folder_path = file.file_path
                    if not folder_path:
                        # flog.write("\n%s 【文件夹地址错误】【%s】\n" % (now_time, folder_path))
                        logg.logger.error("【文件夹地址错误】【%s】" % folder_path)
                        continue
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    folder_hour = datetime.strftime(now_time, '%H')
                    folder_path_hour = split_val + "\\" + folder_day + "\\" + datetime.strftime(now_time, '%H')
                    # print("folder_path", folder_path)
                    # print("folder_path_hour", folder_path_hour)
                    if len(folder_path_hour) == len(folder_path) and folder_path != folder_path_hour:
                        # print("空文件夹，删除")
                        # print("folder_val", folder_val)
                        # print("split_val", split_val)
                        # print("folder_path_hour", folder_path_hour)
                        # print("folder_path_xxxx", folder_path)
                        # print("folder_day", folder_day)
                        if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                            # flog.write("\n%s 【违停事件扫描删除非当前时间段空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停事件扫描删除非当前时间段空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)
                            continue
                    if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                        # print("空文件夹，删除2")
                        # print("folder_path_hour2", folder_path_hour)
                        # print("folder_val2", folder_val)
                        # print("split_val2", split_val)
                        # print("folder_path_xxxx2", folder_path)
                        # print("folder_path[:-2]", folder_path[-2:])
                        # print("folder_day2", folder_day)
                        if folder_day not in folder_path:
                            # flog.write("\n%s 【违停事件扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停事件扫描删除空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)
                            # print("del", folder_path)
                        if ("\\" + folder_hour) != folder_path[-3:]:
                            # flog.write("\n%s 【违停事件扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停事件扫描删除空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)

                except Exception as exc:
                    strexc = traceback.format_exc()
                    # flog.write("\n%s 【违停事件扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
                    logg.logger.error("【违停事件扫描删除空文件夹出错】【%s】" % strexc)
            else:
                file_path = file.file_path
                file_name = file.file_name
                if file_name[-3:] != 'jpg':

                    # flog.write("\n%s 【违停事件扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                    logg.logger.warning("【违停事件扫描删除】【非jpg文件】%s" % file_path)
                    os.remove(file_path)
                else:
                    jpgFileList.append(file)
                    # print(file_name, file.is_file)
    except Exception as e:
        strexc = traceback.format_exc()
        # flog.write("\n%s 【违停事件扫描清理文件出错】%s\n" % (now_time, strexc))
        logg.logger.error("【违停事件扫描清理文件出错】%s" % strexc)
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0}

    try:
        if jpgFileList:
            file = random.choice(jpgFileList)
            file_path = file.file_path
            fileSize = file.size / 1024  # size  (self.size / 1024.0)
            if fileSize <= 1:
                # flog.write("\n%s 【违停扫描删除】【0KB图片】%s\n" % (now_time, file_path))
                logg.logger.warning("【违停扫描删除】【0KB图片】%s" % file_path)
                os.remove(file_path)
                return {"status": "over", "count": 0}

        else:
            return {"status": "over", "count": 0}
        # 如果是文件,则打印
        split_val = event_path.split("\\")[-1]
        if file.is_file:
            if file.file_name[-3:] == 'jpg':
                file_path = file.file_path
                file_name = file.file_name
                file_name_list = file_name.split('_')
                image_folder = "\\".join(file_path.split("\\")[:-1]) + '\\'

                i_type = file_name_list[0]
                last_str = file_name_list[-1]
                car_id = ""
                ip = ""
                car_color = ""
                time1 = file_name_list[1]
                time2 = file_name_list[2]

                for i in file_name_list:
                    re_car_id = re.findall('^[无京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z].*', i, re.S)
                    if re_car_id:
                        car_id = i

                    re_time1 = re.findall('^20\d{6}$', i, re.S)
                    if re_time1:
                        time1 = i
                    re_time2 = re.findall('^\d{6}$', i, re.S)
                    if re_time2:
                        time2 = i

                    re_ip = re.findall('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', i, re.S)
                    if re_ip:
                        ip = i

                    re_car_color = re.findall('^.*\.jpg$', i, re.S)
                    if re_car_color:
                        car_color = i
                wf_time = time1 + time2
                if '无' in car_id:
                    # flog.write("\n%s 【违停事件扫描删除】【无车牌】%s\n" % (now_time, file_path))
                    logg.logger.warning("【违停事件扫描删除】【无车牌】%s" % file_path)
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                if i_type == '2' and ('短信' not in last_str):

                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    car_type = '02'
                    if '黄' in car_color:
                        car_type = '01'
                    elif car_color == "绿.jpg":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "52"

                    if "黄绿" in car_color:  # 黄绿双拼
                        car_type = "51"
                    if "学" in car_id:
                        car_type = "16"
                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            with requests.Session() as maxrequests:
                                maxrequests.mount('http://', HTTPAdapter(max_retries=2))  # 设置重试次数为3次
                                res = maxrequests.post('http://%s/dataInfo/wtDataEventUpload/' % ip_val, files=files,
                                                    data=data, timeout=10)
                                res_josn = res.json()
                                status = res_josn.get("status")
                                strexc = res_josn.get('e')
                                res.close()
                                maxrequests.cookies.clear()

                        except Exception as e:
                            strexc = traceback.format_exc()
                            # flog.write("\n%s 【违停事件扫描上传出错】【%s】\n" % (now_time, strexc))
                            logg.logger.error("【违停事件扫描上传出错】【%s】" % strexc)
                            # continue
                            status = "失败，" + str(e)
                            res_josn = {"zp": "", "sms_image": ""}
                        finally:
                            f.close()
                    except Exception as e:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【违停事件扫描上传出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【违停事件扫描上传出错】【%s】" % strexc)
                        # continue
                        status = "失败，" + str(e)
                        res_josn = {"zp": "", "sms_image": ""}

                    zp = res_josn.get('zp')
                    image_file = res_josn.get('sms_image')
                    zpname = ""
                    if zp:
                        # 存在本机后再传图片至服务器
                        imgdata = base64.b64decode(zp)
                        l = image_file.split('.jpg')
                        l_name = l[0].split('_')
                        l_name[0] = '1039'
                        dx_name = '_'.join(l_name)
                        zpname = image_folder + dx_name + '短信' + '.jpg'
                        img = open(zpname, 'wb')
                        img.write(imgdata)
                        img.close()
                    count = 0
                    try:
                        os.remove(file_path)
                        count = 1
                    except Exception as ex:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【违停事件扫描删除或移动出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【违停事件扫描删除或移动出错】【%s】" % strexc)
                    finally:

                        return {
                            "status": "success", "count": count, "sms_count": 0, "res_status": status, "file_path": file_path,
                            "zpname": zpname, "e": strexc}
                        # return {
                        #     "status": "success", "count": count, "sms_count": 0, "res_status": status, "file_path": file_path,
                        #     "zpname": "", "e": ""}
                elif '短信' in last_str:
                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    # car_color = file_name_list[-2][0]
                    car_type = '02'
                    if '黄' in car_color:
                        car_type = '01'
                    elif car_color == "绿短信.jpg":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "52"

                    if "黄绿" in car_color:  # 黄绿双拼
                        car_type = "51"
                    if "学" in car_id:
                        car_type = "16"
                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            with requests.Session() as maxrequests:
                                maxrequests = requests.Session()
                                maxrequests.mount('http://', HTTPAdapter(max_retries=2))  # 设置重试次数为3次
                                res = maxrequests.post('http://%s/dataInfo/wtDataEventSMSUpload/' % ip_val, files=files,
                                                    data=data, timeout=10)
                                res_josn = res.json()
                                status = res_josn.get("status")
                                strexc = res_josn.get('e')
                                res.close()
                                maxrequests.cookies.clear()
                        except Exception as e:
                            strexc = traceback.format_exc()
                            # flog.write("\n%s 【短信扫描上传出错】【%s】\n" % (now_time, strexc))
                            logg.logger.error("【短信扫描上传出错】【%s】" % strexc)
                            status = "失败，" + str(e)
                        finally:
                            f.close()
                    except Exception as e:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【短信扫描上传出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【短信扫描上传出错】【%s】" % strexc)
                        status = "失败，" + str(e)

                    sms_count = 0
                    try:
                        # 直接删除不进行备份
                        os.remove(file_path)
                        sms_count = 1
                    except Exception as ex:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【短信扫描删除或移动出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【短信扫描删除或移动出错】【%s】" % strexc)
                    finally:
                        return {"status": "success", "count": 0, "sms_count": sms_count, "res_status": status, "file_path": file_path,
                                "zp": "success", "e": strexc}
                else:
                    os.remove(file_path)
                    # flog.write("\n%s 【短信扫描删除】【未在违法代码列表中】%s\n" % (now_time, file_path))
                    logg.logger.warning("【短信扫描删除】【未在违法代码列表中】%s" % file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
            else:
                file_path = file.file_path
                # flog.write("\n%s 【短信扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                logg.logger.warning("【短信扫描删除】【非jpg文件】%s" % file_path)
                os.remove(file_path)
                # continue
                return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
        else:
            try:
                folder_path = file.file_path
                folder_val = folder_path.split('\\')[-1]
                folder_day = datetime.strftime(now_time, '%Y%m%d')
                if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
                    os.rmdir(folder_path)
            except Exception as exc:
                strexc = traceback.format_exc()
                folder_path = file.file_path
                # flog.write("\n%s 【违停事件扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
                logg.logger.error("【违停事件扫描删除空文件夹出错】【%s】" % strexc)
                return {"status": "scanError", "count": 0, "res_status": "error", "file_path": folder_path, "e": strexc}
        return {"status": "over", "count": 0, "sms_count": 0}
    except Exception as e:
        strexc = traceback.format_exc()
        # flog.write("\n%s 【违停事件扫描出错】【%s】\n" % (now_time, strexc))
        logg.logger.error("【违停事件扫描出错】【%s】" % strexc)
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0, "sms_count": 0}
    # finally:
        # flog.close()


def QZ(files_list, ip_val, qz_path, now_time, white_list, wf_list):
    log_file = "logs\\" + '违停日志取证扫描.log'
    # flog = open(log_file, 'a+', encoding='utf-8')
    logg = Logger(log_file, level="info")

    split_val = qz_path.split("\\")[-1]
    jpgFileList = []
    try:
        for file in files_list:
            if not file.is_file:
                try:
                    folder_path = file.file_path
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    folder_hour = datetime.strftime(now_time, '%H')
                    folder_path_hour = split_val + "\\" + folder_day + "\\" + datetime.strftime(now_time, '%H')
                    # print(folder_path)
                    # print(folder_path_hour)
                    if len(folder_path_hour) == len(folder_path) and folder_path != folder_path_hour:
                        # print("folder_path_hour", folder_path_hour)
                        # print("folder_path_xxxx", folder_path)
                        if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                            # flog.write("\n%s 【违停取证扫描删除非当前时间段空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停取证扫描删除非当前时间段空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)
                            continue
                    if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                        # print("空文件夹，删除")
                        if folder_day not in folder_path:
                            # flog.write("\n%s 【违停取证扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停取证扫描删除空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)
                            # print("del", folder_path)
                        if ("\\" + folder_hour) != folder_path[-3:]:
                            # flog.write("\n%s 【违停取证扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            logg.logger.info("【违停取证扫描删除空文件夹】【%s】" % folder_path)
                            os.rmdir(folder_path)

                except Exception as exc:
                    strexc = traceback.format_exc()
                    # flog.write("\n%s 【违停取证扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
                    logg.logger.error("【违停取证扫描删除空文件夹出错】【%s】" % strexc)
            else:
                file_path = file.file_path
                file_name = file.file_name
                if file_name[-3:] != 'jpg':

                    # flog.write("\n%s 【违停取证扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                    logg.logger.warning("【违停取证扫描删除】【非jpg文件】%s" % file_path)
                    os.remove(file_path)
                else:
                    jpgFileList.append(file)
                    # print(file_name, file.is_file)
    except Exception as e:
        strexc = traceback.format_exc()
        # flog.write("\n%s 【违停取证扫描清理文件出错】%s\n" % (now_time, strexc))
        logg.logger.error("【违停取证扫描清理文件出错】%s" % strexc)
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0}

    try:
        if jpgFileList:
            file = random.choice(jpgFileList)
            file_path = file.file_path
            fileSize = file.size / 1024  # size  (self.size / 1024.0)
            if fileSize <= 1:
                # flog.write("\n%s 【违停扫描删除】【0KB图片】%s\n" % (now_time, file_path))
                logg.logger.warning("【违停扫描删除】【0KB图片】%s" % file_path)
                os.remove(file_path)
                return {"status": "over", "count": 0}

        else:
            return {"status": "over", "count": 0}
        # 如果是文件,则打印
        split_val = qz_path.split("\\")[-1]
        if file.is_file:
            if file.file_name[-3:] == 'jpg':
                file_path = file.file_path
                file_name = file.file_name
                file_name_list = file_name.split('_')

                i_type = file_name_list[0]
                car_id = ""
                ip = ""
                car_color = ""
                time1 = file_name_list[1]
                time2 = file_name_list[2]

                for i in file_name_list:
                    re_car_id = re.findall('^[无京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z].*', i, re.S)
                    if re_car_id:
                        car_id = i

                    re_time1 = re.findall('^20\d{6}$', i, re.S)
                    if re_time1:
                        time1 = i
                    re_time2 = re.findall('^\d{6}$', i, re.S)
                    if re_time2:
                        time2 = i

                    re_ip = re.findall('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', i, re.S)
                    if re_ip:
                        ip = i

                    re_car_color = re.findall('^.*\.jpg$', i, re.S)
                    if re_car_color:
                        car_color = i
                wf_time = time1 + time2
                if '无' in car_id:
                    # flog.write("\n%s 【违停取证扫描删除】【无车牌】%s\n" % (now_time, file_path))
                    logg.logger.warning("【违停取证扫描删除】【无车牌】%s" % file_path)
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}

                if i_type in wf_list:

                    # 对取证进行操作
                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    car_type = '02'
                    if '黄' in car_color:
                        car_type = '01'
                    elif car_color == "绿.jpg":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "52"

                    if "黄绿" in car_color:  # 黄绿双拼
                        car_type = "51"
                    if "学" in car_id:
                        car_type = "16"
                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            with requests.Session() as maxrequests:
                                maxrequests.mount('http://', HTTPAdapter(max_retries=2))  # 设置重试次数为3次
                                res = maxrequests.post('http://%s/dataInfo/wtDataInfoUpload/' % ip_val, files=files,
                                                    data=data, timeout=10)
                                res_josn = res.json()
                                status = res_josn.get("status")
                                strexc = res_josn.get('e')
                                res.close()
                                maxrequests.cookies.clear()
                        except Exception as e:
                            strexc = traceback.format_exc()
                            # flog.write("\n%s 【违停取证扫描上传出错】【%s】\n" % (now_time, strexc))
                            logg.logger.error("【违停取证扫描上传出错】【%s】" % strexc)
                            # continue
                            status = "失败，" + str(e)
                        finally:
                            f.close()
                    except Exception as e:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【违停取证扫描上传出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【违停取证扫描上传出错】【%s】" % strexc)
                        # continue
                        status = "失败，" + str(e)

                    count = 0
                    try:

                        # 直接删除不进行备份
                        os.remove(file_path)
                        count = 1
                    except Exception as ex:
                        strexc = traceback.format_exc()
                        # flog.write("\n%s 【违停取证扫描删除或移动出错】【%s】\n" % (now_time, strexc))
                        logg.logger.error("【违停取证扫描删除或移动出错】【%s】" % strexc)
                    finally:
                        return {"status": "success", "count": count, "res_status": status, "file_path": file_path, "e": strexc}
                else:
                    # flog.write("\n%s 【违停取证扫描删除】【未在违法代码列表中】%s\n" % (now_time, file_path))
                    logg.logger.warning("【违停取证扫描删除】【未在违法代码列表中】%s" % file_path)
                    os.remove(file_path)
            else:
                file_path = file.file_path
                # flog.write("\n%s 【违停取证扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                logg.logger.warning("【违停取证扫描删除】【非jpg文件】%s" % file_path)
                os.remove(file_path)
                # continue
                return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
        else:
            try:
                folder_path = file.file_path
                folder_val = folder_path.split('\\')[-1]
                folder_day = datetime.strftime(now_time, '%Y%m%d')
                if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
                    os.rmdir(folder_path)
            except Exception as exc:
                strexc = traceback.format_exc()
                folder_path = file.file_path
                # flog.write("\n%s 【违停取证扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
                logg.logger.error("【违停取证扫描删除空文件夹出错】【%s】" % strexc)
                return {"status": "scanError", "count": 0, "res_status": "error", "file_path": folder_path, "e": strexc}
        return {"status": "over", "count": 0}
    except Exception as e:
        strexc = traceback.format_exc()
        # flog.write("\n%s 【违停取证扫描出错】【%s】\n" % (now_time, strexc))
        logg.logger.error("【违停取证扫描出错】【%s】" % strexc)
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0}
    # finally:
    #     flog.close()


if __name__ == '__main__':
    a = event(FileObjectManager(FileObject("D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\dist\新版扫描器合集\\test")).scan_with_depth(10).all_file_objects(), '0.0.0.0:8000', "D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\dist\新版扫描器合集\\test", datetime.now(), [])
    print(a)

    # b = QZ(FileObjectManager(FileObject("/Users/yanshigou/Downloads/16")).scan_with_depth(10).all_file_objects(), '0.0.0.0:8000', "/Users/yanshigou/Downloads/16", datetime.now(), [], "1039,10395,10396")
    # print(b)
