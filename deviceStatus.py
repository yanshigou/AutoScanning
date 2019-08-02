__author__ = "dzt"
__date__ = "2019/8/2"

from platform import system as system_name
from os import system
import requests


def ping(host):

    # 判断系统
    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

    return system("ping " + parameters + " " + host) == 0


if __name__ == '__main__':
    res = requests.get('http://192.168.31.54:8000/devices/allDevices/')
    print(res)
    print(res.json())
    ip_list = res.json().get('devices')
    for ip in ip_list:
        is_online = ping(ip)
        print(ip, is_online)
        if is_online:
            res = requests.get('http://192.168.31.54:8000/devices/statusModify/?is_online=1&ip=%s' % ip)
        else:
            res = requests.get('http://192.168.31.54:8000/devices/statusModify/?is_online=0&ip=%s' % ip)

