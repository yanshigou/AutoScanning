# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests
import os
import shutil
from time import sleep


# 给定文件夹路径
eventFilesList = FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\事件")).scan_with_depth(10).all_file_objects()
# eventFilesList = FileObjectManager(FileObject("G:\dzt\资料\交警\image_test")).scan_with_depth(10).all_file_objects()
filesList = FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\取证")).scan_with_depth(10).all_file_objects()

# 拼接路径数组
filesString = ""
# 建立连接 获取csrftoken
client = requests.session()
# client.get('http://127.0.0.1:8000/users/login/')
# if 'csrftoken' in client.cookies:
#     csrftoken = client.cookies['csrftoken']
#     print(csrftoken)
# else:
#     csrftoken = client.cookies['csrf']
#     print(csrftoken)
count = 0


def event():
    count = 0
    for file in eventFilesList:
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


def QZ():
    count = 0
    for file in filesList:
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


if __name__ == '__main__':
    c = 0
    while True:
        try:
            sleep(1)
            print('开始事件')
            c += event()
            print('开始取证')
            c += QZ()
            sleep(60 * 2)
            print(c)
        except Exception as e:
            print(e)
            print(c)
