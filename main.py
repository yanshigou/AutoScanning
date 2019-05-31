# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/31"

from file_manager import FileObjectManager, FileObject
import requests

# 给定文件夹路径
filesList = FileObjectManager(FileObject("G:\dzt\image_test")).scan_with_depth(2).all_file_objects()

# 拼接路径数组
filesString = ""
# for file in filesList:
#
#     # 如果是文件,则打印
#     if file.is_file:
#         if file.file_name[-3:] == 'jpg':
#             print(file.file_path)

        # print(file.file_name)
        # print(file.dir_name)
        # print(file.show_info)
client = requests.session()
client.get('http://127.0.0.1:8000/users/login/')
if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']
    print(csrftoken)
else:
    csrftoken = client.cookies['csrf']
    print(csrftoken)

login_data = dict(username='1', password='123456', csrfmiddlewaretoken=csrftoken)
r = client.post('http://127.0.0.1:8000/users/login/', data=login_data, headers=dict(Referer='http://127.0.0.1:8000/users/login/'))

f = open('G:\dzt\image_test\quzheng\default.png', 'rb')
files = {'attachment_file': ('default.png', f, 'image/png', {})}

data = dict(csrfmiddlewaretoken=csrftoken)

res = client.post('http://127.0.0.1:8000/dataInfo/wtDataInfoUpload/', files=files, data=data)
f.close()

