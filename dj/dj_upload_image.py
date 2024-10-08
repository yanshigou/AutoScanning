# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2022/08/05"


from dj_file_manager import FileObjectManager, FileObject
import requests
import os
import re
from datetime import datetime
import random
import traceback
from requests.adapters import HTTPAdapter

dj_url = "/djDataInfo/djDataInfoUpload/"


def QZ(files_list, ip_val, qz_path, now_time, white_list, wf_list):
    log_file = "logs\\" + datetime.now().strftime('%Y-%m-%d') + '电警日志.txt'
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
                    folder_hour = datetime.strftime(now_time, '%H')
                    folder_path_hour = split_val + "\\" + folder_day + "\\" + datetime.strftime(now_time, '%H')
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
                            # print("del", folder_path)
                        if ("\\" + folder_hour) != folder_path[-3:]:
                            flog.write("\n%s 【电警扫描删除空文件夹】【%s】\n" % (now_time, folder_path))
                            os.rmdir(folder_path)

                except Exception as exc:
                    strexc = traceback.format_exc()
                    flog.write("\n%s 【电警扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
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
        strexc = traceback.format_exc()
        flog.write("\n%s 【电警扫描清理文件出错】%s\n" % (now_time, strexc))
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0}

    try:
        if jpgFileList:
            file = random.choice(jpgFileList)
            file_path = file.file_path
            fileSize = file.size / 1024  # size  (self.size / 1024.0)
            if fileSize <= 1:
                flog.write("\n%s 【电警扫描删除】【0KB图片】%s\n" % (now_time, file_path))
                os.remove(file_path)
                return {"status": "over", "count": 0}

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

                # print(file_name)  60950_20220608_115324_728_50.22.36.211_渝AQ39C9_47_40_蓝.jpg
                # print(file_name)  11160_20240714_115324_728_进口_教练车限行_50.22.36.211_渝AQ39C9_47_40_蓝.jpg
                car_id = ""
                img_type = ""
                model_name = ""
                ip = ""
                car_color = ""
                time1 = file_name_list[1]
                time2 = file_name_list[2]
                speed = file_name_list[-3]  # 只有超速才能正确取到
                lim_speed = file_name_list[-2]  # 只有超速才能正确取到
                car_type = '02'

                # 兼容未改格式
                if not re.findall('^\d{1,3}$', speed, re.S):
                    speed = ""
                if not re.findall('^\d{1,3}$', lim_speed, re.S):
                    lim_speed = ""
                for i in file_name_list:
                    re_car_id = re.findall('^[无京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z].*', i, re.S)
                    if re_car_id:
                        car_id = i

                    re_type = re.findall('^进口$|^出口$', i, re.S)
                    if re_type:
                        img_type = i

                    re_type = re.findall('^限时通行$|^教练车限行$', i, re.S)
                    if re_type:
                        model_name = i

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

                    re_car_type = re.findall('^CAR\d{2}$', i, re.S)
                    if re_car_type:
                        car_type = i[3:].zfill(2)

                i_type = file_name_list[0]
                wf_time = time1 + time2
                if "出口" in img_type:
                    flog.write("\n%s 【电警扫描删除】【出口图】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                if '无' in car_id:
                    flog.write("\n%s 【电警扫描删除】【无车牌】%s\n" % (now_time, file_path))
                    os.remove(file_path)
                    return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                if i_type in wf_list:
                    # 对取证进行操作
                    if file_name_list[0] == '2':
                        flog.write("\n%s 【电警扫描删除】【违法代码疑似事件图】%s\n" % (now_time, file_path))
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}
                    if car_id in white_list:
                        os.remove(file_path)
                        return {"status": "fail", "count": 0, "res_status": "error", "file_path": file_path}

                    if car_type == "07":
                        pass
                    else:
                        if '黄' in car_color:
                            car_type = '01'
                        elif "渐" in car_color:  # 渐变绿
                            car_type = "52"
                        elif "绿" in car_color:
                            car_type = "52"

                        if "黄绿" in car_color:  # 黄绿双拼
                            car_type = "51"
                        if "学" in car_id:
                            car_type = "16"
                    try:
                        f = open(file_path, 'rb')
                        files = {'image_file': (file_name, f, 'image/jpg')}
                        data = dict(
                            data_type=i_type,
                            ip=ip,
                            car_id=car_id,
                            car_type=car_type,
                            wf_time=wf_time,
                            speed=speed,
                            lim_speed=lim_speed,
                            img_type=img_type,
                            model_name=model_name
                        )
                        try:
                            with requests.Session() as maxrequests:
                                # maxrequests = requests.Session()
                                maxrequests.mount('http://', HTTPAdapter(max_retries=2))  # 设置重试次数为3次
                                res = maxrequests.post('http://' + ip_val + dj_url, files=files, data=data, timeout=5)
                                res_json = res.json()
                                status = res_json.get('status')
                                strexc = res_json.get('e')
                                res.close()
                                maxrequests.cookies.clear()
                        except Exception as e:
                            # print("Exception=" + str(e))
                            strexc = traceback.format_exc()
                            flog.write("\n%s 【电警扫描上传出错】【%s】\n" % (now_time, strexc))
                            # continue
                            status = "失败，" + str(e)
                        finally:
                            f.close()
                    except Exception as e:
                        # print(e)
                        strexc = traceback.format_exc()
                        flog.write("\n%s 【电警扫描上传出错】【%s】\n" % (now_time, strexc))
                        # continue
                        status = "失败，" + str(e)

                    # print("status=" + status)
                    count = 0
                    # 只有删除才去使用移动后的路径，
                    try:
                        # 直接删除不进行备份
                        os.remove(file_path)
                        count = 1
                    except Exception as ex:
                        strexc = traceback.format_exc()
                        flog.write("\n%s 【电警扫描删除或移动出错】【%s】\n" % (now_time, strexc))

                    finally:
                        # sleep(1)
                        return {"status": "success", "count": count, "res_status": status, "file_path": file_path, "e": strexc}
                else:
                    flog.write("\n%s 【电警扫描删除】【未在违法代码列表中】%s\n" % (now_time, file_path))
                    os.remove(file_path)

            else:
                file_path = file.file_path
                flog.write("\n%s 【电警扫描删除】【非jpg文件】%s\n" % (now_time, file_path))
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
                strexc = traceback.format_exc()
                folder_path = file.file_path
                flog.write("\n%s 【电警扫描删除空文件夹出错】【%s】\n" % (now_time, strexc))
                return {"status": "scanError", "count": 0, "res_status": "error", "file_path": folder_path, "e": strexc}
        return {"status": "over", "count": 0}
    except Exception as e:
        strexc = traceback.format_exc()
        flog.write("\n%s 【电警扫描出错】【%s】\n" % (now_time, strexc))
        return {"status": "scanError", "e": strexc, "res_status": "error", "count": 0}
    finally:
        flog.close()


if __name__ == '__main__':
    wf_list = ["60461", "60462", "60480", "16250", "60950"]
    file_list = FileObjectManager(FileObject("/Users/yanshigou/Downloads/16")).scan_with_depth(10).all_file_objects()
    b = QZ(file_list, r'0.0.0.0:8000', "/Users/yanshigou/Downloads/16",
           datetime.now(), [], wf_list)
    print(b)
