# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from file_manager import FileObjectManager, FileObject
import requests
import os
import shutil
from time import sleep


def event(event_files_list, move_folder, ip_val):
    count = 0
    try:
        for file in event_files_list:
            # 如果是文件,则打印
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    count += 1
                    file_path = file.file_path

                    # path_list = file_path.split('\\')
                    # path_list[4] = "备份"
                    # folder = "\\".join(path_list[:-1])
                    print(file_path.split('事件'))
                    path_list = file_path.split('事件')
                    folder = move_folder + "\\事件" + path_list[-1]

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
                        car_type = file_name_list[6]
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
                        if res['is_del']:
                            os.remove(file_path)
                            print('删除成功')
                        else:
                            shutil.move(file_path, folder)
                            print('移动成功')
                        sleep(0.5)
                        return {"status": "success", "count": count, "res_status": status, "file_path": file_path, "folder": folder}
    except Exception as e:
        print(e)
        return {"status": "error", "e": e, "res_status": "fail", "count": count}


def QZ(files_list):
    count = 0
    for file in files_list:
        # 如果是文件,则打印
        if file.is_file:
            sleep(1)
            if file.file_name[-3:] == 'jpg':
                count += 1
                file_path = file.file_path
                path_list = file_path.split('\\')
                path_list[4] = "备份"
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
                    print("取证图片")
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


if __name__ == '__main__':
    a = event(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\事件")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54')
    print(a)
