# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2022/8/2"

from file_manager import FileObjectManager, FileObject
import requests
import os
import re
from time import sleep
from datetime import datetime
import random


dj_url = "/csDataInfo/csDataInfoUpload/"


def QZ(files_list, ip_val, qz_path, now_time, white_list, wf_list):
    log_file = datetime.now().strftime('%Y-%m-%d') + '超速日志.txt'
    flog = open(log_file, 'a+', encoding='utf-8')

    try:
        if files_list:
            file = random.choice(files_list)
        else:
            return {"status": "over", "count": 0}
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
                ip = ""
                i_type = ""
                car_color = ""

                for i in file_name_list:
                    re_car_id = re.findall('^[无京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z].*', i, re.S)
                    if re_car_id:
                        car_id = i
                        # print("carId=", car_id)

                    re_ip = re.findall('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', i, re.S)
                    if re_ip:
                        ip = i
                        # print("ip", ip)

                    re_i_type = re.findall('^\d{4,5}$', i, re.S)
                    if re_i_type:
                        i_type = i
                        # print("i_type", i_type)

                    re_car_color = re.findall('^.*\.jpg$', i, re.S)
                    if re_car_color:
                        car_color = i
                        # print("carColor", car_color)

                # print("file_path", file_path)
                # print("file_name", file_name)
                # print("file_name_list", file_name_list)
                if '无' in car_id:
                    print(car_id)
                    os.remove(file_path)
                    # continue
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                if i_type in wf_list:
                    # 对取证进行操作
                    if i_type == '13453' and file_name_list[0] == '2':
                        os.remove(file_path)
                        # continue
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    if car_id in white_list:
                        os.remove(file_path)
                        # continue
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    start_time = file_name_list[1]
                    end_time = file_name_list[2]
                    speed = file_name_list[-4]  # 只有超速才能正确取到
                    lim_speed = file_name_list[-3]  # 只有超速才能正确取到
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
                            data_type=i_type,
                            ip=ip,
                            car_id=car_id,
                            car_type=car_type,
                            start_time=start_time,
                            wf_time=end_time,
                            speed=speed,
                            lim_speed=lim_speed,
                        )
                        try:
                            # print('http://' + ip_val + dj_url)
                            # print(data)
                            # break
                            res = requests.post('http://' + ip_val + dj_url, files=files, data=data).json()
                            status = res['status']
                        except Exception as e:
                            # print("Exception=" + str(e))
                            flog.write("\n%s 【超速扫描上传出错】【%s】\n" % (now_time, e))
                            # continue
                            status = "error"
                        finally:
                            f.close()
                    except Exception as e:
                        print(e)
                        flog.write("\n%s 【超速扫描上传出错】【%s】\n" % (now_time, e))
                        # continue
                        status = "error"

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
                        flog.write("\n%s 【超速扫描删除或移动出错】【%s】\n" % (now_time, ex))

                    finally:
                        # sleep(1)
                        return {"status": "success", "count": count, "res_status": status, "file_path": file_path}
                else:
                    os.remove(file_path)

            else:
                file_path = file.file_path
                os.remove(file_path)
                # continue
                return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}

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
                flog.write("\n%s 【超速扫描删除空文件夹出错】【%s】\n" % (now_time, exc))
                pass
        return {"status": "over", "count": 0}
    except Exception as e:
        print(e)
        sleep(1)
        return {"status": "error", "e": str(e), "res_status": "error", "count": 0}
    finally:
        flog.close()


if __name__ == '__main__':
    wf_list = ["60461", "60462", "60480"]
    file_list = FileObjectManager(FileObject("/Users/yanshigou/Downloads/16")).scan_with_depth(10).all_file_objects()
    b = QZ(file_list, r'0.0.0.0:8000', "/Users/yanshigou/Downloads/16",
           datetime.now(), [], wf_list)
    print(b)
