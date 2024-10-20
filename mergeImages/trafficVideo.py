# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/12"
__title__ = "视频纠违v1.0_20241020"

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ping3 import ping
from PIL import Image, ImageTk
from merge_images import merge_images_with_text, generate_security_code
from getCarId import get_carid
from dateAndAddress import extract_info_from_image
import threading
import re
import requests
from loggmodel import Logger
import traceback
import os
from datetime import datetime

# pyinstaller -D -w -i mergeImages\tv.ico mergeImages\trafficVideo.py --collect-all paddleocr --version-file mergeImages\version.txt
# 然后把 python 虚拟环境中的依赖项 paddle -> libs 文件夹内的文件 复制一份，粘贴到打包的项目的 paddle -> libs 文件夹内，全部替换即可
# 已解决 字体放在同级exe下生效


def display_images(image_paths, frame):
    """按2x2格式展示图片，支持交换位置，并自动识别车牌和车辆类型"""
    try:
        # 清空frame中的所有组件
        for widget in frame.winfo_children():
            widget.destroy()

        # 遍历图片路径并展示
        for idx, path in enumerate(image_paths):
            image = Image.open(path)
            image.thumbnail((300, 300), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(frame, image=photo, bg='white', relief='solid', borderwidth=1)
            label.image = photo  # 防止垃圾回收
            label.path = path
            label.idx = idx  # 保存索引

            # 使用 grid 布局展示图片
            label.grid(row=idx // 2, column=idx % 2, padx=10, pady=10)

            # # 绑定事件，用于拖动交换，并加选中边框
            # label.bind("<ButtonPress-1>", lambda e, lbl=label: thread_it(on_drag_start, e, lbl))
            # label.bind("<ButtonRelease-1>", lambda e, lbl=label, fr=frame: thread_it(on_drag_release, e, lbl, fr))
            # 绑定事件：开始拖动、拖动过程、释放
            label.bind("<ButtonPress-1>", lambda e, lbl=label: thread_it(on_drag_start, e, lbl))
            label.bind("<B1-Motion>", lambda e, lbl=label, fr=frame: thread_it(on_drag_motion, e, lbl, fr))
            label.bind("<ButtonRelease-1>", lambda e, lbl=label, fr=frame: thread_it(on_drag_release, e, lbl, fr))

        # 调用 get_carid() 获取识别结果
        if not image_paths:
            return
        image_path = image_paths[-1]
        res = get_carid(image_path, logg)  # 取最后一张图片进行识别
        if res:
            car_id = res.get('car_id', '')
            color = res.get('color', '')

            # # 根据颜色自动选择车辆类型
            # if color == '蓝色':
            #     vehicle_type = "小型汽车"
            # elif color == '黄色':
            #     vehicle_type = "大型汽车"
            # elif color == '渐变绿':
            #     vehicle_type = "新能源大型汽车"
            # elif color == '绿':
            #     vehicle_type = "新能源小型汽车"
            # else:
            #     vehicle_type = "未知类型"


            # 自动填充车牌号码和车辆类型
            car_id_entry.delete(0, tk.END)
            car_id_entry.insert(0, car_id)

            color_combobox.set(color)
            if "学" in car_id:
                vehicle_type = "教练车"
                car_id -= car_id.replace("学", "")
                vehicle_type_combobox.set(vehicle_type)  # 为了教练车

            # print(f"识别结果: 车牌号={car_id}, 颜色={color}, 车辆类型={vehicle_type}")
        else:
            car_id_entry.delete(0, tk.END)
            car_id_entry.insert(0, "")
            # print("未能识别车牌或车辆类型")

        time_info, address_info = extract_info_from_image(image_path, logg)
        if time_info:
            time_entry.delete(0, tk.END)
            time_entry.insert(0, time_info)
        else:
            time_entry.delete(0, tk.END)
            time_entry.insert(0, "")

        if address_info:
            address_combobox.delete(0, tk.END)
            address_combobox.insert(0, address_info)

        else:
            address_combobox.delete(0, tk.END)
            address_combobox.set("")
    except Exception as ee:
        strexc = traceback.format_exc()
        logg.logger.error(f"按2x2格式展示图片，支持交换位置，并自动识别车牌和车辆类型失败！{strexc}")


def on_drag_start(event, label):
    """记录起始位置，并给当前图片加红色选中边框"""
    label.startX = event.x
    label.startY = event.y
    label.is_selected = True  # 标记为选中
    label.config(borderwidth=3, relief='ridge', bg='red')  # 选中时高亮显示


def on_drag_motion(event, label, frame):
    """拖动过程中高亮悬停的目标图片"""
    x, y = event.widget.winfo_pointerxy()
    target = event.widget.winfo_containing(x, y)

    # 如果悬停在另一个图片上，则高亮它
    if target and target != label and isinstance(target, tk.Label):
        highlight_label(target)

    # 移动离开时恢复默认样式
    reset_labels_except(target, label, frame)


def on_drag_release(event, label, frame):
    """交换图片位置并刷新显示"""
    x, y = event.widget.winfo_pointerxy()
    target = event.widget.winfo_containing(x, y)

    if target and target != label:
        # 交换图片路径并刷新显示
        selected_image_paths[label.idx], selected_image_paths[target.idx] = (
            selected_image_paths[target.idx], selected_image_paths[label.idx]
        )

    # 重置所有标签样式
    reset_labels(frame)
    thread_it(display_images, selected_image_paths, frame)


def highlight_label(label):
    """高亮当前悬停的目标图片"""
    label.config(borderwidth=3, relief='ridge', bg='red')


def reset_labels_except(target, selected_label, frame):
    """重置除选中和悬停标签以外的所有标签样式"""
    for widget in frame.winfo_children():
        if widget not in [target, selected_label]:
            widget.config(borderwidth=1, relief='solid', bg='white')


def reset_labels(frame):
    """重置所有标签样式"""
    for widget in frame.winfo_children():
        widget.config(borderwidth=1, relief='solid', bg='white')


def is_valid_time_format(time_string):
    """验证时间格式是否为 YYYY-MM-DD HH:MM:SS"""
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    return pattern.match(time_string) is not None


def generate_custom_text():
    """生成合成图片所需的custom_text"""
    try:
        wf_time = time_entry.get()
        if not wf_time or not is_valid_time_format(wf_time):
            messagebox.showerror("时间格式错误", "请确保输入有效的时间，并且格式为 YYYY-MM-DD HH:MM:SS")
            return

        district = district_entry.get()
        if not district:
            messagebox.showerror("输入错误", "行政区划不能为空")
            return

        car_id = car_id_entry.get()
        if not car_id:
            messagebox.showerror("输入错误", "车牌号不能为空")
            return

        car_color = color_entry.get()
        if not car_color:
            messagebox.showerror("输入错误", "车牌颜色不能为空")
            return

        vehicle_type = vehicle_type_combobox.get()
        if not vehicle_type:
            messagebox.showerror("输入错误", "车辆类型不能为空")
            return

        address = address_entry.get()
        if not address:
            messagebox.showerror("输入错误", "违法地点不能为空")
            return

        device_id = device_entry.get()
        if not device_id:
            messagebox.showerror("输入错误", "设备编号不能为空")
            return

        wf_code = violation_code_entry.get()
        if not wf_code:
            messagebox.showerror("输入错误", "违法代码不能为空")
            return

        wf_name = violation_name_entry.get()
        if not wf_name:
            messagebox.showerror("输入错误", "违法行为不能为空")
            return
        # district = district_entry.get()
        # car_id = car_id_entry.get()
        # car_color = color_entry.get()
        # vehicle_type = vehicle_type_combobox.get()
        # address = address_entry.get()
        # device_id = device_entry.get()
        # wf_code = violation_code_entry.get()
        # wf_name = violation_name_entry.get()


        # 根据选择的车辆类型设置实际的 car_type
        if vehicle_type == "小型汽车":
            actual_car_type = "02"
        elif vehicle_type == "大型汽车":
            actual_car_type = "01"
        elif vehicle_type == "新能源小型汽车":
            actual_car_type = "51"
        elif vehicle_type == "新能源大型汽车":
            actual_car_type = "52"
        elif vehicle_type == "摩托车":
            actual_car_type = "07"
        elif vehicle_type == "教练车":
            actual_car_type = "16"
        else:
            actual_car_type = "02"  # 或者根据需要设定默认值

        security_code = generate_security_code()

        custom_text = f"违法时间：{wf_time} 行政区划：{district} 违法地点：{address} 车牌号：{car_id} 车牌颜色：{car_color} " \
                      f"违法代码：{wf_code} 违法行为：{wf_name} 设备编号：{device_id} 车辆类型：{vehicle_type} " \
                      f"防伪码：{security_code}"
        try:
            ip = address_ip_map[address]
        except Exception as e:
            strexc = traceback.format_exc()
            logg.logger.error(f"违法地点识别错误！{strexc}")
            messagebox.showerror("违法地点识别错误", "违法地点识别错误，请手动选择违法地点")
            return
        data = dict(
                data_type=wf_code,
                ip=ip,
                car_id=car_id,
                car_type=actual_car_type,
                wf_time=wf_time.replace(" ", "").replace("-", "").replace(":", ""),
                speed="",
                lim_speed="",
                img_type="",
                model_name="视频纠违",
                car_color=car_color
            )
        # print(data)
        # print(custom_text)
        logg.logger.info(f"识别成功{custom_text}")
        return custom_text, data
    except Exception as e:
        strexc = traceback.format_exc()
        logg.logger.error(f"违法地点识别错误！{strexc}")


def create_image():
    """合成图片并展示"""
    try:
        custom_text, data = generate_custom_text()
        logg.logger.info(f"合成图片并展示按钮进程1")
        res, file_name = merge_images_with_text(selected_image_paths, custom_text, data, logg)
        logg.logger.info(f"合成图片并展示按钮进程2")
        show_merged_image(res, data, file_name, logg)
        logg.logger.info(f"合成图片并展示按钮进程3")
    except Exception as e:
        strexc = traceback.format_exc()
        logg.logger.error(f"合成图片并展示失败！{strexc}")


def show_merged_image(image_path, data, file_name, logg):
    """在新窗口展示合成的图片"""
    try:
        new_window = tk.Toplevel()
        new_window.title("合成图片展示")

        merged_image = Image.open(image_path)
        window_width = 1000
        window_height = 600
        merged_image.thumbnail((window_width, window_height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(merged_image)

        label = tk.Label(new_window, image=photo)
        label.image = photo
        label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)  # 修改为 columnspan=2

        # 设置窗口大小和最小尺寸，并居中
        new_window.update_idletasks()
        center_window(new_window, photo.width(), photo.height() + 100)
        new_window.minsize(400, 300)

        # 上传按钮
        push_btn = tk.Button(
            new_window, text='上传至平台',
            command=lambda: thread_it(upload_to_platform, image_path, data, new_window, file_name), width=15
        )
        push_btn.grid(row=1, column=0, padx=10, pady=10, sticky="e")  # 右对齐

        # 关闭按钮
        close_btn = tk.Button(new_window, text='关闭并清空数据', command=lambda: close_and_reset(new_window), width=15)
        close_btn.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # # 监听窗口关闭事件
        # new_window.protocol("WM_DELETE_WINDOW", lambda: close_and_reset(new_window))

        new_window.grid_rowconfigure(0, weight=1)
        new_window.grid_columnconfigure(0, weight=1)
        new_window.grid_columnconfigure(1, weight=1)
        logg.logger.info(f"在新窗口展示合成的图片成功！")
    except Exception as e:
        strexc = traceback.format_exc()
        logg.logger.error(f"在新窗口展示合成的图片失败！{strexc}")


def close_and_reset(window):
    """关闭合成图片窗口，并重置表单"""
    window.destroy()
    reset_form()


def upload_to_platform(image_path, data, window, file_name):
    """处理上传图片到平台的逻辑"""
    ip_val = ip_entry.get()
    # print(data)

    try:
        with open(image_path, 'rb') as f:
            files = {'image_file': (file_name, f, 'image/jpg')}
            with requests.Session() as maxrequests:
                res = maxrequests.post(f'http://{ip_val}{dj_url}', files=files, data=data, timeout=5)
                res_json = res.json()
                status = res_json.get('status')
                strexc = res_json.get('e')
                if status == "success":

                    show_countdown_message(window, "图片上传成功！", 5)  # 显示倒计时提示框
                    logg.logger.info(f"图片上传成功{file_name}")
                else:
                    messagebox.showerror("错误", f"图片上传错误！！{strexc}")
                    logg.logger.warning(f"上传图片出错{strexc}")

    except Exception as e:
        print(f"Exception: {e}")
        messagebox.showerror("错误", str(e))
        strexc = traceback.format_exc()
        logg.logger.error(f"上传图片报错{strexc}")


def show_countdown_message(parent, message, seconds):
    """显示带倒计时的自定义提示框"""
    countdown_window = tk.Toplevel(parent)
    countdown_window.title("提示")

    label = tk.Label(countdown_window, text=f"{message} ({seconds}秒后关闭)", font=("pf10.tff", 12))
    label.pack(padx=20, pady=20)

    # 居中提示框
    countdown_window.update_idletasks()
    center_window(countdown_window, countdown_window.winfo_width(), countdown_window.winfo_height())

    def update_label():
        nonlocal seconds
        seconds -= 1
        if seconds > 0:
            label.config(text=f"{message} ({seconds}秒后关闭)")
            countdown_window.after(1000, update_label)
        else:
            countdown_window.destroy()
            parent.destroy()
            reset_form()

    update_label()


def select_images(image_frame):
    """选择4张图片并展示"""
    global selected_image_paths
    filetypes = (('Image files', '*.jpg *.jpeg *.png *.gif'), ('All files', '*.*'))
    filenames = filedialog.askopenfilenames(title='选择4张图片', filetypes=filetypes)

    if len(filenames) != 4:
        messagebox.showwarning("选择错误", "请确保选择4张图片！")
        return

    selected_image_paths = list(filenames)
    thread_it(display_images, selected_image_paths, image_frame)

    # # 填充当前时间
    # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # time_entry.delete(0, tk.END)
    # time_entry.insert(0, current_time)


def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]{1,5})?$")
    return pattern.match(ip) is not None


def check_server_connection():
    """检查服务器连接并反馈"""
    ip_val = ip_entry.get()
    url = f"http://{ip_val}/devices/infoForMergeImages/"
    # print(f"测试连接URL: {url}")
    test_connection_btn.config(text='连接中···')
    logg.logger.info(f"服务器【{ip_val}】连接中···")

    if not is_valid_ip(ip_val):
        messagebox.showerror("连接测试", f"无效的IP地址: {ip_val}")
        test_connection_btn.config(text='连接无效', fg='red')
        logg.logger.info(f"服务器【{ip_val}】无效的IP地址！")
        return

    delay = ping(ip_val, timeout=1)
    if delay is not None:

        try:
            response = requests.post(url, data={
                "district": "全部区域",
                "area": "全部片区",
                "address": "全部地址"
            })
            data = response.json().get('data', [])
            wf_data = response.json().get('wf_data', [])
            district = response.json().get('district', "")
            if district:
                district_entry.delete(0, tk.END)
                district_entry.insert(0, district)
            # print("data:", data)
            # print("wf_data:", wf_data)
            thread_it(populate_address_dropdown, data)
            thread_it(populate_violation_dropdown, wf_data)
            thread_it(populate_color_dropdown)
            messagebox.showinfo("连接测试", f"服务器连接成功: {ip_val}")
            test_connection_btn.config(text='已连接', fg='green')
            logg.logger.info(f"服务器【{ip_val}】连接成功！")
        except Exception as e:
            strexc = traceback.format_exc()
            messagebox.showerror("连接测试", f"获取数据失败: {e}")
            test_connection_btn.config(text='连接失败', fg='red')
            logg.logger.info(f"服务器【{ip_val}】获取数据失败！{strexc}")
    else:
        messagebox.showerror("连接测试", f"服务器连接失败，请检查服务器：{ip_val}")
        test_connection_btn.config(text='连接失败', fg='red')
        logg.logger.info(f"服务器【{ip_val}】服务器连接失败，请检查服务器！")


def populate_address_dropdown(data):
    """根据服务器返回的地址和设备数据填充下拉框，并建立映射"""
    global address_device_map, device_address_map, address_ip_map
    address_device_map = {item["address"]: item["device_id"] for item in data}
    address_ip_map = {item["address"]: item["ip"] for item in data}
    device_address_map = {item["device_id"]: item["address"] for item in data}

    address_combobox['values'] = list(address_device_map.keys())
    device_combobox['values'] = list(device_address_map.keys())

    address_combobox.bind("<<ComboboxSelected>>", on_address_selected)
    device_combobox.bind("<<ComboboxSelected>>", on_device_selected)

    address_entry.trace("w", on_address_input)
    device_entry.trace("w", on_device_input)


def on_address_selected(event):
    """当选择违法地点时，自动填充对应的设备编号"""
    address = address_combobox.get()
    if address in address_device_map:
        device_combobox.set(address_device_map[address])


def on_device_selected(event):
    """当选择设备编号时，自动填充对应的违法地点"""
    device = device_combobox.get()
    if device in device_address_map:
        address_combobox.set(device_address_map[device])


def on_address_input(*args):
    """当违法地点输入时自动更新设备编号"""
    address = address_entry.get()
    if address in address_device_map:
        device_combobox.set(address_device_map[address])


def on_device_input(*args):
    """当设备编号输入时自动更新违法地点"""
    device = device_entry.get()
    if device in device_address_map:
        address_combobox.set(device_address_map[device])


def thread_it(func, *args):
    """
    将函数打包进线程
    :param func:
    :param args:
    :return:
    """
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞--卡死界面！
    # t.join()


def populate_color_dropdown():

    color_combobox['values'] = list(color_types_map.keys())
    color_combobox.bind("<<ComboboxSelected>>", on_color_selected)
    color_entry.trace("w", on_color_input)


def on_color_selected(event):
    color = color_combobox.get()
    if color in color_types_map:
        vehicle_type_combobox.set(color_types_map[color])


def on_color_input(*args):

    color = color_entry.get()
    if color in color_types_map:
        vehicle_type_combobox.set(color_types_map[color])


def populate_violation_dropdown(data):
    """根据服务器返回数据填充违法行为和代码下拉框，并建立映射"""
    global wf_code_name_map, wf_name_code_map
    wf_code_name_map = {item["wf_code"]: item["wf_name"] for item in data}
    wf_name_code_map = {item["wf_name"]: item["wf_code"] for item in data}

    violation_code_combobox['values'] = list(wf_code_name_map.keys())
    violation_name_combobox['values'] = list(wf_name_code_map.keys())

    violation_code_combobox.bind("<<ComboboxSelected>>", on_violation_code_selected)
    violation_name_combobox.bind("<<ComboboxSelected>>", on_violation_name_selected)

    violation_code_entry.trace("w", on_violation_code_input)
    violation_name_entry.trace("w", on_violation_name_input)


def on_violation_code_selected(event):
    """当选择违法代码时，自动填充对应的违法行为"""
    code = violation_code_combobox.get()
    if code in wf_code_name_map:
        violation_name_combobox.set(wf_code_name_map[code])


def on_violation_name_selected(event):
    """当选择违法行为时，自动填充对应的违法代码"""
    name = violation_name_combobox.get()
    if name in wf_name_code_map:
        violation_code_combobox.set(wf_name_code_map[name])


def on_violation_code_input(*args):
    """当违法代码输入时自动更新违法行为"""
    code = violation_code_entry.get()
    if code in wf_code_name_map:
        violation_name_combobox.set(wf_code_name_map[code])


def on_violation_name_input(*args):
    """当违法行为输入时自动更新违法代码"""
    name = violation_name_entry.get()
    if name in wf_name_code_map:
        violation_code_combobox.set(wf_name_code_map[name])


def center_window(window, width, height):
    """将窗口显示在屏幕中心"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def reset_form():
    """重置动态信息和图片展示区域，准备下一次录入"""
    # 清空输入框和下拉框
    time_entry.delete(0, tk.END)
    car_id_entry.delete(0, tk.END)
    color_entry.set("")
    vehicle_type_combobox.set("")
    address_combobox.set("")
    device_combobox.set("")
    violation_code_combobox.set("")
    violation_name_combobox.set("")

    # 清空图片展示区域
    global selected_image_paths
    selected_image_paths = []
    display_images(selected_image_paths, image_frame)


def logFile():
    now_time = datetime.now().strftime("%Y年%m月%d日")
    log_file = os.path.join(logs_file_folder, f'{now_time}.log')
    return log_file


if __name__ == '__main__':
    file_folder = os.getcwd()
    logs_file_folder = os.path.join(file_folder, "logs")
    if not os.path.exists(logs_file_folder):
        os.makedirs(logs_file_folder)
    log_file = logFile()
    logg = Logger(log_file, level="info")
    logg.logger.info("开始")
    dj_url = "/djDataInfo/djDataInfoUpload/"
    selected_image_paths = []

    # 用于保存违法行为与违法代码的映射
    wf_code_name_map = {}
    wf_name_code_map = {}
    # 用于保存违法地点与设备编号的映射
    address_device_map = {}
    address_ip_map = {}
    device_address_map = {}

    # 颜色类型
    color_types_map = {
        "蓝色": "小型汽车",
        "黄色": "大型汽车",
        "绿色": "新能源小型汽车",
        "渐变绿色": "新能源大型汽车"
    }

    types_color_map = {
        "小型汽车": "蓝色",
        "大型汽车": "黄色",
        "新能源小型汽车": "绿色",
        "新能源大型汽车": "渐变绿色"
    }

    root = tk.Tk()
    root.title(__title__)

    # 主窗口居中
    # root.geometry('1000x460')  # 窗口默认大小
    root.update_idletasks()
    center_window(root, 1000, 460)

    root.grid_rowconfigure(0, weight=1)  # 使输入框部分自适应
    root.grid_columnconfigure(1, weight=1)  # 使图片展示部分自适应


    # 输入框区域
    input_frame = tk.Frame(root)
    input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # 增加列权重，确保输入框宽度自适应
    input_frame.grid_columnconfigure(1, weight=1)

    # 手动定义每个标签和输入框
    # 违法时间
    tk.Label(input_frame, text="违法时间：").grid(row=0, column=0, sticky="e")
    time_entry = tk.Entry(input_frame, width=30)
    time_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 行政区划
    tk.Label(input_frame, text="行政区划：").grid(row=1, column=0, sticky="e")
    district_entry = tk.Entry(input_frame, width=30)
    district_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    # district_entry.insert(0, "重庆市沙坪坝")

    # 车牌号
    tk.Label(input_frame, text="车牌号码：").grid(row=2, column=0, sticky="e")
    car_id_entry = tk.Entry(input_frame, width=30)
    car_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # 车牌颜色
    tk.Label(input_frame, text="车辆颜色：").grid(row=3, column=0, sticky="e")
    # color_types = ['蓝色', '黄色', '绿色', '渐变绿色']
    color_entry = tk.StringVar()
    color_combobox = ttk.Combobox(input_frame, textvariable=color_entry, width=30)
    color_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    # 车辆类型（下拉框）
    tk.Label(input_frame, text="车辆类型：").grid(row=4, column=0, sticky="w")
    vehicle_types = ["小型汽车", "大型汽车", "新能源小型汽车", "新能源大型汽车", "摩托车", "教练车"]
    # type_entry = tk.StringVar()
    vehicle_type_combobox = ttk.Combobox(input_frame, values=vehicle_types, width=30)
    # vehicle_type_combobox = ttk.Combobox(input_frame, textvariable=type_entry)
    # vehicle_type_combobox.set("选择车辆类型")
    vehicle_type_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    # 违法地点
    tk.Label(input_frame, text="违法地点：").grid(row=5, column=0, sticky="w")
    address_entry = tk.StringVar()
    address_combobox = ttk.Combobox(input_frame, textvariable=address_entry, width=30)
    address_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    # 设备编号
    tk.Label(input_frame, text="设备编号：").grid(row=6, column=0, sticky="w")
    device_entry = tk.StringVar()
    device_combobox = ttk.Combobox(input_frame, textvariable=device_entry, width=30)
    device_combobox.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    # 违法代码
    tk.Label(input_frame, text="违法代码：").grid(row=7, column=0, sticky="w")
    violation_code_entry = tk.StringVar()
    violation_code_combobox = ttk.Combobox(input_frame, textvariable=violation_code_entry, width=30)
    violation_code_combobox.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

    # 违法行为
    tk.Label(input_frame, text="违法行为：").grid(row=8, column=0, sticky="w")
    violation_name_entry = tk.StringVar()
    violation_name_combobox = ttk.Combobox(input_frame, textvariable=violation_name_entry, width=30)
    violation_name_combobox.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

    # 服务器IP
    tk.Label(input_frame, text="服务器IP：").grid(row=9, column=0, sticky="e")
    ip_entry = tk.Entry(input_frame, width=30)
    ip_entry.grid(row=9, column=1, padx=5, pady=5, sticky="ew")
    ip_entry.insert(0, "127.0.0.1:8000")

    # 测试连接按钮
    test_connection_btn = tk.Button(input_frame, text='连接服务器', command=lambda: thread_it(check_server_connection))
    test_connection_btn.grid(row=10, column=0, columnspan=2, pady=10)

    # 图片展示区域的 Frame
    image_frame = tk.Frame(root, width=620, height=300, bg='lightgray')
    image_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # 使图片展示区域自适应大小
    image_frame.grid_rowconfigure(0, weight=1)
    image_frame.grid_columnconfigure(0, weight=1)

    # 新增按钮区域 Frame，用于放置上传、合成图片、退出按钮
    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

    # 上传图片按钮
    upload_btn = tk.Button(button_frame, text='上传4张图片', command=lambda: thread_it(select_images, image_frame), width=15)
    upload_btn.pack(side=tk.LEFT, padx=40)

    # 合成图片按钮
    merge_btn = tk.Button(button_frame, text='合成图片', command=lambda: thread_it(create_image), width=15)
    merge_btn.pack(side=tk.LEFT, padx=40)

    # 退出按钮
    quit_btn = tk.Button(button_frame, text='退  出', command=root.quit, width=15)
    quit_btn.pack(side=tk.LEFT, padx=40)

    root.mainloop()
