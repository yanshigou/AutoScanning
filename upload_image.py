# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from file_manager import FileObjectManager, FileObject
import requests
import os
import shutil
from time import sleep
from datetime import datetime


def event(event_files_list, move_folder, ip_val, event_path, now_time):
    count = 0
    try:
        for file in event_files_list:
            # 如果是文件,则打印
            split_val = event_path.split("\\")[-1]
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

                    file_name = file.file_name
                    file_name_list = file_name.split('_')
                    print(file_name_list)
                    i_type = file_name_list[0]
                    if i_type == '2':
                        print('事件图片')
                        # 进行对事件进行操作
                        ip = file_name_list[4]
                        car_id = file_name_list[5]

                        car_color = file_name_list[-1][0]
                        print(car_color)
                        car_type = '00'
                        if car_color == "蓝":
                            car_type = '00'
                        elif car_color == '黄':
                            car_type = '01'
                        elif car_color == '绿':
                            car_type = '04'

                        wf_time = file_name_list[1] + file_name_list[2]
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}

                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type,
                            wf_time=wf_time
                        )

                        res = requests.post('http://%s:8000/dataInfo/wtDataEventUpload/' % ip_val, files=files, data=data).json()
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
                            return {"status": "success", "count": count, "res_status": status, "file_path": file_path, "folder": folder}
            else:
                try:
                    folder_path = file.file_path
                    print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val:
                        print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
        return {"status": "over", "count": count}
    except Exception as e:
        print(e)
        return {"status": "error", "e": e, "res_status": "error", "count": count}


def QZ(files_list, move_folder, ip_val, qz_path, now_time):
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
                        car_color = file_name_list[-1][0]
                        print(car_color)
                        car_type = '00'
                        if car_color == "蓝":
                            car_type = '00'
                        elif car_color == '黄':
                            car_type = '01'
                        elif car_color == '绿':
                            car_type = '04'
                        wf_time = file_name_list[1]+file_name_list[2]
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}

                        data = dict(
                            data_type='WT', ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
                        )

                        res = requests.post('http://%s:8000/dataInfo/wtDataInfoUpload/' % ip_val, files=files, data=data).json()
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
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val:
                        print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
    except Exception as e:
        print(e)
        return {"status": "error", "e": e, "res_status": "error", "count": count}


if __name__ == '__main__':
    # a = event(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\事件")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54', "G:\dzt\资料\交警\测试文件夹\事件", datetime.now())
    # print(a)

    b = QZ(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\取证")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54', "G:\dzt\资料\交警\测试文件夹\取证", datetime.now())
    print(b)
