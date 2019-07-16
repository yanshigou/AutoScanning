# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from file_manager import FileObjectManager, FileObject
import requests
import os
import shutil
from time import sleep
from datetime import datetime
import base64


def event(event_files_list, move_folder, ip_val, event_path, now_time, white_list):
    count = 0
    sms_count = 0
    try:
        for file in event_files_list:
            # 如果是文件,则打印
            split_val = event_path.split("\\")[-1]
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    file_path = file.file_path
                    print(file_path)
                    image_folder = "\\".join(file_path.split("\\")[:-1]) + '\\'
                    print(image_folder)
                    # path_list = file_path.split('\\')
                    # path_list[4] = "备份"
                    # folder = "\\".join(path_list[:-1])

                    print("event_path", event_path)
                    print("split_val", split_val)
                    split_path_list = file_path.split(split_val)[-1]
                    print('split_path_list', split_path_list)
                    path_list = split_path_list.split("\\")[:-1]
                    print('path_list', path_list)
                    path_list_folder = "\\".join(path_list)
                    print('path_list_folder', path_list_folder)
                    folder = move_folder + ("\\%s" % split_val) + path_list_folder

                    print("folder", folder)

                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    file_name = file.file_name
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
                            continue
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
                            return {"status": "success", "count": count, "sms_count": sms_count, "res_status": status, "file_path": file_path, "folder": folder, "zpname": zpname}
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
                            continue
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
                            return {"status": "success", "count": count, "sms_count": sms_count, "res_status": status, "file_path": file_path,
                                    "folder": folder, "zp": "success"}
            else:
                try:
                    folder_path = file.file_path
                    print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
                        print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
        return {"status": "over", "count": count, "sms_count": sms_count}
    except Exception as e:
        print(e)
        return {"status": "error", "e": e, "res_status": "error", "count": count, "sms_count": sms_count}


def QZ(files_list, move_folder, ip_val, qz_path, now_time, white_list):
    count = 0
    # for path, dirs, files in os.walk(qz_path):
    #     print("path", path)
    #     print("dirs", dirs)
    #     print("files", files)
    #     if not dirs and not files:
    #         print('空文件夹，删除')
    #         os.rmdir(path)
    try:
        for file in files_list:
            # 如果是文件,则打印
            split_val = qz_path.split("\\")[-1]
            print(split_val)
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    count += 1
                    file_path = file.file_path

                    # path_list = file_path.split('\\')
                    # path_list[4] = "备份"
                    # folder = "\\".join(path_list[:-1])

                    split_path_list = file_path.split(split_val)[-1]
                    path_list = split_path_list.split("\\")[:-1]
                    path_list_folder = "\\".join(path_list)
                    folder = move_folder + ("\\%s" % split_val) + path_list_folder

                    print(folder)

                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    file_path = file.file_path
                    file_name = file.file_name
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
                            continue
                        car_color = file_name_list[-1][0]
                        print(car_color)
                        car_type = '00'
                        if car_color == "蓝":
                            car_type = '02'
                        elif car_color == '黄':
                            car_type = '01'
                        elif car_color == '绿':
                            car_type = '19'
                        wf_time = file_name_list[1]+file_name_list[2]
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}

                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
                        )

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
                            return {"status": "success", "count": count, "res_status": status, "file_path": file_path, "folder": folder}
            else:
                try:
                    folder_path = file.file_path
                    print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    print(folder_val)
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
                        print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
        return {"status": "over", "count": count}
    except Exception as e:
        print(e)
        return {"status": "error", "e": e, "res_status": "error", "count": count}


if __name__ == '__main__':
    a = event(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\测试文件夹\梭梭树")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54:8000', "G:\dzt\资料\交警\测试文件夹\测试文件夹\梭梭树", datetime.now(), [])
    print(a)

    b = QZ(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\测试文件夹\对对对")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54:8000', "G:\dzt\资料\交警\测试文件夹\测试文件夹\对对对", datetime.now(), [])
    print(b)
