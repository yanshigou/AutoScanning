__author__ = "dzt"
__date__ = "2019/8/2"

from platform import system as system_name
# from os import system, popen
# import requests
import subprocess


def ping(host):

    # 判断系统
    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

    # return popen("ping " + parameters + " " + host).read()
    # return system("ping " + parameters + " " + host) == 0
    return subprocess.call("ping " + parameters + " " + host) == 0
    # a, b = subprocess.getstatusoutput("ping " + parameters + " " + host)
    # return a == 0


if __name__ == '__main__':
    l = ["cloud.tencent.com", 'www.baidu.com', '50.45.109.1']
    for ip in l:
        is_online = ping(ip)
        print(ip, is_online)
    # res = requests.get('http://192.168.31.54:8000/devices/allDevices/')
    # print(res)
    # print(res.json())
    # ip_list = res.json().get('devices')
    # for ip in ip_list:
    #     is_online = ping(ip)
    #     print(ip, is_online)
    #     if is_online:
    #         res = requests.get('http://192.168.31.54:8000/devices/statusModify/?is_online=1&ip=%s' % ip)
    #     else:
    #         res = requests.get('http://192.168.31.54:8000/devices/statusModify/?is_online=0&ip=%s' % ip)

