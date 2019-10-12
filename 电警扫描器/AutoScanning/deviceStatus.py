__author__ = "dzt"
__date__ = "2019/8/2"

from platform import system as system_name
# from os import system, popen
# import requests
import subprocess


def ping(host):

    # 判断系统
    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

    return subprocess.call("ping " + parameters + " " + host) == 0


if __name__ == '__main__':
    l = ["cloud.tencent.com", 'www.baidu.com', '50.45.109.1']
    for ip in l:
        is_online = ping(ip)
        print(ip, is_online)
