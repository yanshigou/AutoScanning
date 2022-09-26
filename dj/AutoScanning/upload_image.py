# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from file_manager import FileObjectManager, FileObject
import requests
import os
import re
from time import sleep
from datetime import datetime


dj_url = "/djDataInfo/djDataInfoUpload/"
wfmd_url = "/wfmdDataInfo/wfmdMp4Upload/"


def QZ(files_list, move_folder, ip_val, qz_path, now_time, white_list, wf_list):
    # print(wf_list)
    try:
        for file in files_list:
            # 如果是文件,则打印
            split_val = qz_path.split("\\")[-1]
            # print(split_val)
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    file_path = file.file_path
                    file_name = file.file_name
                    file_name_list = file_name.split('_')

                    # print(file_name)
                    car_id = ""
                    time1 = ""
                    time2 = ""
                    ip = ""
                    i_type = ""
                    car_color = ""

                    for i in file_name_list:
                        re_car_id = re.findall('^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z].*', i, re.S)
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

                        re_i_type = re.findall('^\d{4,5}$', i, re.S)
                        if re_i_type:
                            i_type = i

                        re_car_color = re.findall('^.*\.jpg$', i, re.S)
                        if re_car_color:
                            car_color = i

                    # print("file_path", file_path)
                    # print("file_name", file_name)
                    # print("file_name_list", file_name_list)
                    if '无' in car_id:
                        # print(car_id)
                        os.remove(file_path)
                        continue
                    if i_type in wf_list:
                        # 对取证进行操作
                        if i_type == '13453' and file_name_list[0] == '2':
                            os.remove(file_path)
                            continue
                        if car_id in white_list:
                            os.remove(file_path)
                            continue
                        wf_time = time1 + time2
                        speed = file_name_list[-2]  # 只有超速才能正确取到
                        car_type = '02'
                        if '黄' in car_color:
                            car_type = '01'
                        elif "绿" in car_color:
                            car_type = "52"
                        elif "渐" in car_color:  # 渐变绿
                            car_type = "51"
                        try:
                            f = open(file_path, 'rb')
                            files = {'image_file': (file_name, f, 'image/jpg')}
                            data = dict(
                                data_type=i_type, ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time, speed=speed
                            )
                            try:
                                res = requests.post('http://' + ip_val + dj_url, files=files, data=data).json()
                            except Exception as e:
                                print("Exception=" + str(e))
                                continue
                            finally:
                                f.close()
                        except Exception as e:
                            print(e)
                            continue

                        status = res['status']
                        # print("status=" + status)
                        count = 0
                        # 只有删除才去使用移动后的路径，
                        try:
                            # 直接删除不进行备份
                            os.remove(file_path)
                            count = 1
                        except Exception as ex:
                            print(ex)
                            print('删除或移动出错')
                        finally:
                            # sleep(1)
                            return {"status": "success", "count": count, "res_status": status, "file_path": file_path}
                    else:
                        os.remove(file_path)
                elif file.file_name[-3:] == 'mp4':
                    print(file.file_name)
                    file_path = file.file_path
                    file_name = file.file_name
                    file_name_list = file_name.split('_')
                    # print("file_path", file_path)
                    # print("file_name", file_name)
                    # print("file_name_list", file_name_list)
                    i_type = file_name_list[0]
                    # print(i_type)
                    # print(type(i_type))
                    try:
                        car_id = file_name_list[5]
                        # print(car_id)
                    except Exception as e:
                        print(e)
                        os.remove(file_path)
                        continue
                    if '无' in car_id:
                        # print(car_id)
                        os.remove(file_path)
                        continue
                    if i_type in wf_list:
                        # 对取证进行操作
                        ip = file_name_list[4]
                        if car_id in white_list:
                            os.remove(file_path)
                            continue
                        wf_time = file_name_list[1] + file_name_list[2]
                        car_color = file_name_list[-1][0]
                        # print(car_color)
                        car_type = '02'
                        if '黄' in car_color:
                            car_type = '01'
                        elif "绿" in car_color:
                            car_type = "52"
                        elif "渐" in car_color:  # 渐变绿
                            car_type = "51"
                        try:
                            f = open(file_path, 'rb')
                            files = {'mp4_file': (file_name, f)}
                            data = dict(
                                data_type=i_type, ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
                            )
                            try:
                                res = requests.post('http://' + ip_val + wfmd_url, files=files, data=data).json()
                            except Exception as e:
                                print("Exception=" + str(e))
                                continue
                            finally:
                                f.close()
                        except Exception as e:
                            print(e)
                            continue

                        status = res['status']
                        # print("status=" + status)
                        count = 0
                        # 只有删除才去使用移动后的路径，
                        try:
                            # 直接删除不进行备份
                            os.remove(file_path)
                            count = 1
                        except Exception as ex:
                            print(ex)
                            print('删除或移动出错')
                        finally:
                            # sleep(1)
                            return {"status": "success", "count": count, "res_status": status, "file_path": file_path}
                    else:
                        os.remove(file_path)
                else:
                    file_path = file.file_path
                    os.remove(file_path)
                    continue

            else:
                try:
                    folder_path = file.file_path
                    # print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    # print(folder_val)
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and (
                            '.' not in folder_val):
                        # print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
        return {"status": "over", "count": 0}
    except Exception as e:
        print(e)
        sleep(1)
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0}


if __name__ == '__main__':
    wf_list = ['13443', '10395', '13442', '13453', '10482', '12082', '10482', '1048', '13452']
    file_list = FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\测试文件夹\电警")).scan_with_depth(10).all_file_objects()
    b = QZ(file_list, r"D:\WorkDocument\ITS\backup", r'192.168.31.54:8000', "G:\dzt\资料\交警\测试文件夹\测试文件夹\电警",
           datetime.now(), [], wf_list)
    print(b)
