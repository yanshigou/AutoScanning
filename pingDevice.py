# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/10/30"
from deviceStatus import ping
from datetime import datetime

# is_online = ping(ip)
# if is_online:
#     text.insert(tk.END, '\n%s 设备 %s 在线' % (now_time, ip))
#     f.write('\n%s 设备 %s 在线' % (now_time, ip))
#     requests.get('http://%s/devices/statusModify/?is_online=1&ip=%s' % (ip_val, ip))
# else:
#     text.insert(tk.END, '\n%s 设备 %s 离线' % (now_time, ip))
#     f.write('\n%s 设备 %s 离线' % (now_time, ip))
#     requests.get('http://%s/devices/statusModify/?is_online=0&ip=%s' % (ip_val, ip))

device_f = open('device_file.txt', encoding='utf-8')
ip_list = device_f.readlines()
device_f.close()

out_file = datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '设备状态.txt'
with open(out_file, 'a+', encoding='utf-8') as f:

    for ip in ip_list:
        ip = ip.strip()
        is_online = ping(ip)
        print(is_online)
        if is_online:
            f.write('设备 %s 在线\n' % ip)
        else:
            f.write('设备 %s 离线\n' % ip)


