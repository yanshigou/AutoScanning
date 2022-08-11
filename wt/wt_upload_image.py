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
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def event(event_files_list, ip_val, event_path, now_time, white_list):
    log_file = BASE_DIR + "/logs/" + datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    flog = open(log_file, 'a+', encoding='utf-8')

    split_val = event_path.split("\\")[-1]
    jpgFileList = []
    try:
        for file in event_files_list:
            if not file.is_file:
                try:
                    folder_path = file.file_path
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    folder_path_hour = split_val + "/" + folder_day + "/" + datetime.strftime(now_time, '%H')
                    # print(folder_path)
                    # print(folder_path_hour)
                    if len(folder_path_hour) == len(folder_path) and folder_path != folder_path_hour:
                        # print("folder_path_hour", folder_path_hour)
                        # print("folder_path_xxxx", folder_path)
                        if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                            flog.write("\n%s 【电警扫描删除非当前时间段空文件夹】【%s】\n" % (now_time, folder_path))
                            os.rmdir(folder_path)
                            continue
                    if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                        # print("空文件夹，删除")
                        if folder_day not in folder_path:
                            flog.write("\n%s 【电警扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            os.rmdir(folder_path)
                            print("del", folder_path)

                except Exception as exc:
                    flog.write("\n%s 【电警扫描删除空文件夹出错】【%s】\n" % (now_time, exc))
            else:
                file_path = file.file_path
                file_name = file.file_name
                if file_name[-3:] != 'jpg':

                    flog.write("\n%s 【电警扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                else:
                    jpgFileList.append(file)
                    # print(file_name, file.is_file)
    except Exception as e:
        flog.write("\n%s 【电警扫描清理文件出错】%s\n" % (now_time, e))
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0}

    try:
        if jpgFileList:
            file = random.choice(jpgFileList)
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
                    flog.write("\n%s 【事件扫描删除】【无车牌】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                if i_type == '2' and ('短信' not in last_str):

                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    car_type = '02'
                    if car_color == '黄':
                        car_type = '01'
                    elif car_color == "绿":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "51"

                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            res = requests.post('http://%s/dataInfo/wtDataEventUpload/' % ip_val, files=files,
                                                data=data).json()
                            status = res['status']
                        except Exception as e:
                            flog.write("\n%s 【事件扫描上传出错】【%s】\n" % (now_time, e))
                            # continue
                            status = "error"
                            res = {"zp": "", "sms_image": ""}
                        finally:
                            f.close()
                    except Exception as e:
                        flog.write("\n%s 【事件扫描上传出错】【%s】\n" % (now_time, e))
                        # continue
                        status = "error"
                        res = {"zp": "", "sms_image": ""}

                    zp = res.get('zp')
                    image_file = res.get('sms_image')
                    zpname = ""
                    if zp:
                        # 存在本机后再传图片至服务器
                        imgdata = base64.b64decode(zp)
                        l = image_file.split('.jpg')
                        l_name = l[0].split('_')
                        l_name[0] = '1039'
                        dx_name = '_'.join(l_name)
                        zpname = image_folder + dx_name + '_短信' + '.jpg'
                        img = open(zpname, 'wb')
                        img.write(imgdata)
                        img.close()
                    count = 0
                    try:
                        os.remove(file_path)
                        count = 1
                    except Exception as ex:
                        flog.write("\n%s 【事件扫描删除或移动出错】【%s】\n" % (now_time, ex))
                    finally:

                        return {
                            "status": "success", "count": count, "sms_count": 0, "res_status": status, "file_path": file_path,
                            "zpname": zpname, "e": res.get('e')}
                        # return {
                        #     "status": "success", "count": count, "sms_count": 0, "res_status": status, "file_path": file_path,
                        #     "zpname": "", "e": ""}
                elif '短信' in last_str:
                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    # car_color = file_name_list[-2][0]
                    car_type = '02'
                    if car_color == '黄':
                        car_type = '01'
                    elif car_color == "绿":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "51"
                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            res = requests.post('http://%s/dataInfo/wtDataEventSMSUpload/' % ip_val, files=files,
                                                data=data).json()
                            status = res['status']
                        except Exception as e:
                            flog.write("\n%s 【事件扫描上传出错】【%s】\n" % (now_time, e))
                            status = "error"
                        finally:
                            f.close()
                    except Exception as e:
                        flog.write("\n%s 【事件扫描上传出错】【%s】\n" % (now_time, e))
                        status = "error"

                    sms_count = 0
                    try:
                        # 直接删除不进行备份
                        os.remove(file_path)
                        sms_count = 1
                    except Exception as ex:
                        flog.write("\n%s 【事件扫描删除或移动出错】【%s】\n" % (now_time, ex))
                    finally:
                        return {"status": "success", "count": 0, "sms_count": sms_count, "res_status": status, "file_path": file_path,
                                "zp": "success"}
                else:
                    os.remove(file_path)
                    flog.write("\n%s 【事件扫描删除】【未在违法代码列表中】%s\n" % (now_time, file_path))
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
            else:
                file_path = file.file_path
                flog.write("\n%s 【事件扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
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
                folder_path = file.file_path
                flog.write("\n%s 【事件扫描删除空文件夹出错】【%s】\n" % (now_time, exc))
                return {"status": "fail", "count": 0, "res_status": "error", "file_path": folder_path}
        return {"status": "over", "count": 0, "sms_count": 0}
    except Exception as e:
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0, "sms_count": 0}
    finally:
        flog.close()


def QZ(files_list, ip_val, qz_path, now_time, white_list, wf_list):
    log_file = BASE_DIR + "/logs/" + datetime.now().strftime('%Y-%m-%d') + '违停日志.txt'
    flog = open(log_file, 'a+', encoding='utf-8')

    split_val = qz_path.split("\\")[-1]
    jpgFileList = []
    try:
        for file in files_list:
            if not file.is_file:
                try:
                    folder_path = file.file_path
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    folder_path_hour = split_val + "/" + folder_day + "/" + datetime.strftime(now_time, '%H')
                    # print(folder_path)
                    # print(folder_path_hour)
                    if len(folder_path_hour) == len(folder_path) and folder_path != folder_path_hour:
                        # print("folder_path_hour", folder_path_hour)
                        # print("folder_path_xxxx", folder_path)
                        if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                            flog.write("\n%s 【电警扫描删除非当前时间段空文件夹】【%s】\n" % (now_time, folder_path))
                            os.rmdir(folder_path)
                            continue
                    if not os.listdir(folder_path) and folder_val != split_val and ('.' not in folder_val):
                        # print("空文件夹，删除")
                        if folder_day not in folder_path:
                            flog.write("\n%s 【电警扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            os.rmdir(folder_path)
                            print("del", folder_path)

                except Exception as exc:
                    flog.write("\n%s 【电警扫描删除空文件夹出错】【%s】\n" % (now_time, exc))
            else:
                file_path = file.file_path
                file_name = file.file_name
                if file_name[-3:] != 'jpg':

                    flog.write("\n%s 【电警扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                else:
                    jpgFileList.append(file)
                    # print(file_name, file.is_file)
    except Exception as e:
        flog.write("\n%s 【电警扫描清理文件出错】%s\n" % (now_time, e))
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0}

    try:
        if jpgFileList:
            file = random.choice(jpgFileList)
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
                    flog.write("\n%s 【取证扫描删除】【无车牌】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}

                if i_type in wf_list:

                    # 对取证进行操作
                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    car_type = '02'
                    if car_color == '黄':
                        car_type = '01'
                    elif car_color == "绿":
                        car_type = "52"
                    elif "渐" in car_color:  # 渐变绿
                        car_type = "51"

                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )
                        try:
                            res = requests.post('http://%s/dataInfo/wtDataInfoUpload/' % ip_val, files=files,
                                                data=data).json()
                            status = res['status']
                        except Exception as e:
                            flog.write("\n%s 【取证扫描上传出错】【%s】\n" % (now_time, e))
                            # continue
                            status = "error"
                        finally:
                            f.close()
                    except Exception as e:
                        flog.write("\n%s 【取证扫描上传出错】【%s】\n" % (now_time, e))
                        # continue
                        status = "error"

                    count = 0
                    try:

                        # 直接删除不进行备份
                        os.remove(file_path)
                        count = 1
                    except Exception as ex:
                        flog.write("\n%s 【取证扫描删除或移动出错】【%s】\n" % (now_time, ex))
                    finally:
                        return {"status": "success", "count": count, "res_status": status, "file_path": file_path}
                else:
                    flog.write("\n%s 【取证扫描删除】【未在违法代码列表中】%s\n" % (now_time, file_path))
                    os.remove(file_path)
            else:
                file_path = file.file_path
                flog.write("\n%s 【取证扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
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
                folder_path = file.file_path
                flog.write("\n%s 【取证扫描删除空文件夹出错】【%s】\n" % (now_time, exc))
                return {"status": "fail", "count": 0, "res_status": "error", "file_path": folder_path}
        return {"status": "over", "count": 0}
    except Exception as e:
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0}
    finally:
        flog.close()


if __name__ == '__main__':
    a = event(FileObjectManager(FileObject("/Users/yanshigou/Downloads/15")).scan_with_depth(10).all_file_objects(), '0.0.0.0:8000', "/Users/yanshigou/Downloads/15", datetime.now(), [])
    print(a)

    b = QZ(FileObjectManager(FileObject("/Users/yanshigou/Downloads/16")).scan_with_depth(10).all_file_objects(), '0.0.0.0:8000', "/Users/yanshigou/Downloads/16", datetime.now(), [], "1039,10395,10396")
    print(b)
