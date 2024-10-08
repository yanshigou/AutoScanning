# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/18"
from file_manager import FileObjectManager, FileObject
import requests
import os
# import shutil
from time import sleep
from datetime import datetime
import base64
# import re


def event(event_files_list, move_folder, ip_val, event_path, now_time, white_list):
    try:
        for file in event_files_list:
            # 如果是文件,则打印
            split_val = event_path.split("\\")[-1]
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    file_path = file.file_path
                    # print(file_path)
                    image_folder = "\\".join(file_path.split("\\")[:-1]) + '\\'
                    # print(image_folder)
                    # path_list = file_path.split('\\')
                    # path_list[4] = "备份"
                    # folder = "\\".join(path_list[:-1])

                    # print("event_path", event_path)
                    # print("split_val", split_val)
                    # split_path_list = file_path.split(split_val)[-1]
                    # print('split_path_list', split_path_list)
                    # path_list = split_path_list.split("\\")[:-1]
                    # print('path_list', path_list)
                    # path_list_folder = "\\".join(path_list)
                    # print('path_list_folder', path_list_folder)
                    # folder = move_folder + ("\\%s" % split_val) + path_list_folder
                    #
                    # print("folder", folder)
                    #
                    # if not os.path.exists(folder):
                    #     os.makedirs(folder)

                    file_name = file.file_name
                    file_name_list = file_name.split('_')
                    # print(file_name_list)
                    i_type = file_name_list[0]
                    last_str = file_name_list[-1]
                    try:
                        car_id = file_name_list[5]
                    except Exception as e:
                        print(e)
                        os.remove(file_path)
                        continue
                    # # 匹配渝、有车牌、非警等特殊车辆
                    # re_all = re.findall('^[渝]{1}[A-Z]{1}[A-Z0-9]{6}|[渝]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学]{1}', car_id, re.S)
                    # if not re_all:
                    #     print('%s 不在匹配中' % car_id)
                    #     os.remove(file_path)
                    #     continue
                    # print('%s 在匹配中' % car_id)
                    if '无' in car_id:
                        # print(car_id)
                        os.remove(file_path)
                        continue
                    # print(last_str)
                    if i_type == '2' and ('短信' not in last_str):

                        # 进行对事件进行操作
                        ip = file_name_list[4]
                        # car_id = file_name_list[5]
                        if car_id in white_list:
                            os.remove(file_path)

                            continue
                        car_color = file_name_list[-1][0]
                        # print(car_color)
                        car_type = '02'
                        if car_color == '黄':
                            car_type = '01'
                        elif car_color == "绿":
                            car_type = "52"

                        wf_time = file_name_list[1] + file_name_list[2]
                        # # 提前移动  再打开移动后的文件
                        # move_name = folder + '\\' + file_name  # 移动后的文件路径
                        # try:
                        #     shutil.move(file_path, folder)
                        #     print('移动成功')
                        #     print(move_name)
                        # except Exception as e:
                        #     if "exists" in str(e):
                        #         os.remove(file_path)
                        #
                        # f = open(move_name, 'rb')
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
                            except Exception as e:
                                print(e)
                                continue
                            finally:
                                f.close()
                        except Exception as e:
                            print(e)
                            continue

                        status = res['status']
                        # print(status)
                        zp = res.get('zp')
                        image_file = res.get('sms_image')
                        # print(image_file)
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
                        # print(res['is_del'])
                        count = 0
                        try:
                            # if res['is_del']:
                            #     count = 1
                            #     # os.remove(file_path)
                            #     os.remove(move_name)
                            #     print('删除成功')
                            # else:
                            #     count = 1
                            #     # shutil.move(file_path, folder)
                            #     print('移动成功')
                            # 直接删除不进行备份
                            os.remove(file_path)
                            count = 1
                        except Exception as ex:
                            os.remove(file_path)
                            # print('删除成功')
                        finally:
                            sleep(0.1)

                            return {"status": "success", "count": count, "sms_count": 0, "res_status": status, "file_path": file_path, "zpname": zpname, "e": res.get('e')}
                    elif '短信' in last_str:
                        # print('凭证图片')
                        # 进行对凭证进行操作
                        ip = file_name_list[4]
                        car_id = file_name_list[5]
                        wf_time = file_name_list[1] + file_name_list[2]
                        if car_id in white_list:
                            os.remove(file_path)
                            continue
                        car_color = file_name_list[-2][0]
                        # print(car_color)
                        car_type = '02'
                        if car_color == '黄':
                            car_type = '01'
                        elif car_color == "绿":
                            car_type = "52"
                        # with open(file_path, 'rb') as f:
                        #     files = {'image_file': (file_name, f, 'image/jpg')}
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
                            except Exception as e:
                                print(e)
                                continue
                            finally:
                                f.close()
                        except Exception as e:
                            print(e)
                            continue

                        status = res['status']
                        # print(status)
                        # print(res['is_del'])

                        sms_count = 0
                        try:
                            # if res['is_del']:
                            #     sms_count = 1
                            #     os.remove(file_path)
                            #     print('删除成功')
                            # else:
                            #     sms_count = 1
                            #     shutil.move(file_path, folder)
                            #     print('移动成功')
                            # 直接删除不进行备份
                            os.remove(file_path)
                            sms_count = 1
                        except Exception as ex:
                            os.remove(file_path)
                            print('删除成功')
                        finally:
                            sleep(0.1)
                            return {"status": "success", "count": 0, "sms_count": sms_count, "res_status": status, "file_path": file_path,
                                    "zp": "success"}
                    else:
                        os.remove(file_path)
            else:
                try:
                    folder_path = file.file_path
                    # print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
                        # print("空文件夹，删除")
                        os.rmdir(folder_path)
                except Exception as exc:
                    print(exc)
                    pass
        return {"status": "over", "count": 0, "sms_count": 0}
    except Exception as e:
        print(e)
        sleep(1)
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0, "sms_count": 0}


def QZ(files_list, move_folder, ip_val, qz_path, now_time, white_list, wf_list):
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
            # print(split_val)
            if file.is_file:
                if file.file_name[-3:] == 'jpg':
                    # file_path = file.file_path

                    # path_list = file_path.split('\\')
                    # path_list[4] = "备份"
                    # folder = "\\".join(path_list[:-1])

                    # split_path_list = file_path.split(split_val)[-1]
                    # path_list = split_path_list.split("\\")[:-1]
                    # path_list_folder = "\\".join(path_list)
                    # folder = move_folder + ("\\%s" % split_val) + path_list_folder

                    # print("folder", folder)
                    #
                    # if not os.path.exists(folder):
                    #     os.makedirs(folder)

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
                    except Exception as e:
                        print(e)
                        os.remove(file_path)
                        continue
                    # re_all = re.findall('^[渝]{1}[A-Z]{1}[A-Z0-9]{6}|[渝]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学]{1}', car_id,
                    #                     re.S)
                    # if not re_all:
                    #     print('%s 不在匹配中' % car_id)
                    #     os.remove(file_path)
                    #     continue
                    # print('%s 在匹配中' % car_id)
                    if '无' in car_id:
                        # print(car_id)
                        os.remove(file_path)
                        continue

                    if i_type in wf_list:

                        # 对取证进行操作
                        ip = file_name_list[4]
                        # car_id = file_name_list[5]
                        if car_id in white_list:
                            os.remove(file_path)
                            continue
                        car_color = file_name_list[-1][0]
                        # print(car_color)
                        car_type = '02'
                        if car_color == '黄':
                            car_type = '01'
                        elif car_color == "绿":
                            car_type = "52"
                        wf_time = file_name_list[1]+file_name_list[2]

                        # move_name = folder + '\\' + file_name  # 移动后的文件路径
                        # # 先移动，再打开图片
                        # try:
                        #     shutil.move(file_path, folder)
                        #     print('移动成功')
                        #     print(move_name)
                        # except Exception as e:
                        #     if "exists" in str(e):
                        #         os.remove(file_path)

                        # with open(file_path, 'rb') as f:
                        #     files = {'image_file': (file_name, f, 'image/jpg')}
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
                            except Exception as e:
                                print(e)
                                continue
                            finally:
                                f.close()
                        except Exception as e:
                            print(e)
                            continue

                        status = res['status']
                        # print(status)
                        # print(res['is_del'])
                        count = 0
                        # 只有删除才去使用移动后的路径，
                        try:
                            # if res['is_del']:
                            #     count = 1
                            #     # os.remove(file_path)
                            #     os.remove(move_name)
                            #     print('删除成功')
                            # elif res['is_del'] == 2:
                            #     count = 0
                            #     print("未发现事件，等待下一次上传")
                            # else:
                            #     count = 1
                            #     # shutil.move(file_path, folder)
                            #     print('移动成功')

                            # 直接删除不进行备份
                            os.remove(file_path)
                            count = 1
                        except Exception as ex:
                            print(ex)
                            print('删除或移动出错')
                        finally:
                            return {"status": "success", "count": count, "res_status": status, "file_path": file_path}
                    else:
                        os.remove(file_path)
            else:
                try:
                    folder_path = file.file_path
                    # print(folder_path)
                    folder_val = folder_path.split('\\')[-1]
                    # print(folder_val)
                    folder_day = datetime.strftime(now_time, '%Y%m%d')
                    if not os.listdir(folder_path) and (folder_day not in folder_path) and folder_val != split_val and ('.' not in folder_val):
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
    a = event(FileObjectManager(FileObject("I:\\16")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54:8000', "I:\\16", datetime.now(), [])
    print(a)

    # b = QZ(FileObjectManager(FileObject("G:\dzt\资料\交警\测试文件夹\测试文件夹\对对对")).scan_with_depth(10).all_file_objects(), "G:\dzt\资料\交警\备份", '192.168.31.54:8000', "G:\dzt\资料\交警\测试文件夹\测试文件夹\对对对", datetime.now(), [])
    # print(b)
