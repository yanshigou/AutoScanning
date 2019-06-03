# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests

# 给定文件夹路径
filesList = FileObjectManager(FileObject("G:\dzt\资料\交警\image_test")).scan_with_depth(2).all_file_objects()

# 拼接路径数组
filesString = ""
# 建立连接 获取csrftoken
client = requests.session()
client.get('http://127.0.0.1:8000/users/login/')
if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']
    print(csrftoken)
else:
    csrftoken = client.cookies['csrf']
    print(csrftoken)

for file in filesList:

    # 如果是文件,则打印
    if file.is_file:
        if file.file_name[-3:] == 'jpg':
            file_path = file.file_path
            file_name = file.file_name
            print(file_path)
            file_name_list = file_name.split('_')
            print(file_name_list)
            ip = file_name_list[4]
            car_id = file_name_list[5]
            car_type = file_name_list[6]
            wf_time = file_name_list[1]+file_name_list[2]
            f = open(file_path, 'rb')
            files = {'image_file': (file_name, f, 'image/jpg')}

            data = dict(
                csrfmiddlewaretoken=csrftoken, data_type='WT', ip=ip, car_id=car_id, car_type=car_type, wf_time=wf_time
            )

            res = client.post('http://127.0.0.1:8000/dataInfo/wtDataInfoUpload/', files=files, data=data)
            f.close()

