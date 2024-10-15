# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/12"
__title__ = "4合1专用v1.0_20241012"

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ping3 import ping
from PIL import Image, ImageTk
from mergeImages.merge_images import merge_images_with_text, generate_security_code
from mergeImages.GetCadId.main import get_carid
import threading
import re
from datetime import datetime
import requests

# 保存地址与设备编号的映射


def load_images_async(image_paths, frame):
    threading.Thread(target=display_images, args=(image_paths, frame)).start()


def display_images(image_paths, frame):
    """按2x2格式展示图片，支持交换位置，并自动识别车牌和车辆类型"""
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

        # 绑定事件，用于拖动交换，并加选中边框
        label.bind("<ButtonPress-1>", lambda e, lbl=label: on_drag_start(e, lbl))
        label.bind("<ButtonRelease-1>", lambda e, lbl=label, fr=frame: on_drag_release(e, lbl, fr))

    # 调用 get_carid() 获取识别结果
    res = get_carid(image_paths[-1])  # 取最后一张图片进行识别
    if res:
        car_id = res.get('car_id', '')
        color = res.get('color', '')

        # 根据颜色自动选择车辆类型
        if color == '蓝色':
            vehicle_type = "小型汽车"
        elif color == '黄色':
            vehicle_type = "大型汽车"
        elif color == '渐变绿':
            vehicle_type = "新能源大型汽车"
        elif color == '绿':
            vehicle_type = "新能源小型汽车"
        else:
            vehicle_type = "未知类型"

        # 自动填充车牌号码和车辆类型
        plate_number_entry.delete(0, tk.END)
        plate_number_entry.insert(0, car_id)

        vehicle_type_combobox.set(vehicle_type)

        print(f"识别结果: 车牌号={car_id}, 颜色={color}, 车辆类型={vehicle_type}")
    else:
        print("未能识别车牌或车辆类型")


def on_drag_start(event, label):
    """记录起始位置，并给当前图片加红色选中边框"""
    label.startX = event.x
    label.startY = event.y
    label.config(borderwidth=3, relief='ridge', bg='red')  # 选中时高亮显示


def on_drag_release(event, label, frame):
    """交换图片位置并刷新显示"""
    x, y = event.widget.winfo_pointerxy()
    target = event.widget.winfo_containing(x, y)

    if target and target != label:
        selected_image_paths[label.idx], selected_image_paths[target.idx] = (
            selected_image_paths[target.idx],
            selected_image_paths[label.idx]
        )

    label.config(borderwidth=1, relief='solid', bg='white')
    display_images(selected_image_paths, frame)

def is_valid_time_format(time_string):
    """验证时间格式是否为 YYYY-MM-DD HH:MM:SS"""
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    return pattern.match(time_string) is not None


def generate_custom_text():
    """生成合成图片所需的custom_text"""
    time = time_entry.get()

    if not is_valid_time_format(time):
        messagebox.showerror("时间格式错误", "请确保时间格式为 YYYY-MM-DD HH:MM:SS")
        return

    district = district_entry.get()
    location = location_entry.get()
    device_id = device_id_entry.get()
    plate_number = plate_number_entry.get()

    # 根据选择的车辆类型设置实际的 car_type
    vehicle_type = vehicle_type_combobox.get()
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

    custom_text = f"违法时间：{time} 行政区划：{district} 违法地点：{location} 设备编号：{device_id} 车牌号：{plate_number} 车辆类型：{vehicle_type} 防伪码：{security_code}"
    data = {
        "wf_time": time,
        "area": district,
        "wfdd": location,
        "device_id": device_id,
        "car_id": plate_number,
        "car_type": actual_car_type,  # 使用实际的 car_type
        "security_code": security_code
    }
    print(data)
    return custom_text


def create_image():
    """合成图片并展示"""
    custom_text = generate_custom_text()
    output_path = "test.jpg"
    res = merge_images_with_text(selected_image_paths, output_path, custom_text)
    show_merged_image(res)


def show_merged_image(image_path):
    """在新窗口展示合成的图片"""
    new_window = tk.Toplevel()
    new_window.title("合成图片展示")

    merged_image = Image.open(image_path)
    window_width = 1000
    window_height = 600
    merged_image.thumbnail((window_width, window_height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(merged_image)

    label = tk.Label(new_window, image=photo)
    label.image = photo
    label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    new_window.geometry(f"{photo.width()}x{photo.height() + 100}")
    new_window.minsize(400, 300)

    push_btn = tk.Button(new_window, text='上传至平台', command=lambda: upload_to_platform(image_path))
    push_btn.grid(row=1, column=0, padx=10, pady=10)

    new_window.grid_rowconfigure(0, weight=1)
    new_window.grid_columnconfigure(0, weight=1)


def upload_to_platform(image_path):
    """处理上传图片到平台的逻辑"""
    messagebox.showinfo("上传", f"图片 {image_path} 已上传至平台！")


def select_images(image_frame):
    """选择4张图片并展示"""
    global selected_image_paths
    filetypes = (('Image files', '*.jpg *.jpeg *.png *.gif'), ('All files', '*.*'))
    filenames = filedialog.askopenfilenames(title='选择4张图片', filetypes=filetypes)

    if len(filenames) != 4:
        messagebox.showwarning("选择错误", "请确保选择4张图片！")
        return

    selected_image_paths = list(filenames)
    load_images_async(selected_image_paths, image_frame)

    # 填充当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_entry.delete(0, tk.END)
    time_entry.insert(0, current_time)



def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]{1,5})?$")
    return pattern.match(ip) is not None


def check_server_connection():
    """检查服务器连接并反馈"""
    ip_val = ip_entry.get()
    url = f"http://{ip_val}/devices/infoForMergeImages/"
    print(f"测试连接URL: {url}")

    if not is_valid_ip(ip_val):
        messagebox.showerror("连接测试", f"无效的IP地址: {ip_val}")
        test_connection_btn.config(text='连接无效', fg='red')
        return

    delay = ping(ip_val, timeout=1)
    if delay is not None:
        test_connection_btn.config(text='已连接', fg='green')
        messagebox.showinfo("连接测试", f"服务器连接成功: {ip_val}")

        try:
            response = requests.post(url, data={
                "district": "全部区域",
                "area": "全部片区",
                "address": "全部地址"
            })
            data = response.json().get('data', [])
            print("服务器返回数据:", data)
            populate_address_dropdown(data)
        except Exception as e:
            messagebox.showerror("连接测试", f"获取数据失败: {e}")
            test_connection_btn.config(text='连接失败', fg='red')
    else:
        messagebox.showerror("连接测试", f"服务器连接失败，请检查服务器：{ip_val}")
        test_connection_btn.config(text='连接失败', fg='red')

def populate_address_dropdown(data):
    """根据返回数据填充违法地点下拉框并建立地址-设备编号映射"""
    global address_device_map
    address_device_map = {item['address']: item['device_id'] for item in data}

    address_dropdown['values'] = list(address_device_map.keys())
    address_dropdown.bind("<<ComboboxSelected>>", on_address_selected)

def on_address_selected(event):
    """当选择违法地点时，自动填充对应的设备编号"""
    selected_address = location_entry.get()
    device_id = address_device_map.get(selected_address, "")
    if device_id:
        device_id_entry.delete(0, tk.END)
        device_id_entry.insert(0, device_id)


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


if __name__ == '__main__':

    address_device_map = {}
    selected_image_paths = []

    root = tk.Tk()
    root.title(__title__)
    root.geometry('1000x800+700+300')

    # 输入框区域
    input_frame = tk.Frame(root)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    # 手动定义每个标签和输入框
    # 违法时间
    tk.Label(input_frame, text="违法时间：").grid(row=0, column=0, sticky="w")
    time_entry = tk.Entry(input_frame)
    time_entry.grid(row=0, column=1, padx=5, pady=5)

    # 行政区划
    tk.Label(input_frame, text="行政区划：").grid(row=1, column=0, sticky="w")
    district_entry = tk.Entry(input_frame)
    district_entry.grid(row=1, column=1, padx=5, pady=5)
    district_entry.insert(0, "沙坪坝区")

    # 违法地点
    tk.Label(input_frame, text="违法地点：").grid(row=2, column=0, sticky="w")
    location_entry = tk.StringVar()
    address_dropdown = ttk.Combobox(input_frame, textvariable=location_entry, state="readonly")
    address_dropdown.grid(row=2, column=1, padx=5, pady=5)

    # 设备编号
    tk.Label(input_frame, text="设备编号：").grid(row=3, column=0, sticky="w")
    device_id_entry = tk.Entry(input_frame)
    device_id_entry.grid(row=3, column=1, padx=5, pady=5)

    # 车牌号
    tk.Label(input_frame, text="车牌号：").grid(row=4, column=0, sticky="w")
    plate_number_entry = tk.Entry(input_frame)
    plate_number_entry.grid(row=4, column=1, padx=5, pady=5)

    # 车辆类型（下拉框）
    tk.Label(input_frame, text="车辆类型：").grid(row=5, column=0, sticky="w")
    vehicle_types = ["小型汽车", "大型汽车", "新能源小型汽车", "新能源大型汽车", "摩托车", "教练车"]
    vehicle_type_combobox = ttk.Combobox(input_frame, values=vehicle_types)
    vehicle_type_combobox.set("选择车辆类型")
    vehicle_type_combobox.grid(row=5, column=1, padx=5, pady=5)

    # 服务器IP
    tk.Label(input_frame, text="服务器IP：").grid(row=6, column=0, sticky="w")
    ip_entry = tk.Entry(input_frame)
    ip_entry.grid(row=6, column=1, padx=5, pady=5)
    ip_entry.insert(0, "127.0.0.1:8000")

    # 测试连接按钮
    test_connection_btn = tk.Button(input_frame, text='测试连接', command=lambda: thread_it(check_server_connection))
    test_connection_btn.grid(row=7, column=0, columnspan=2, pady=10)

    # 图片展示区域的 Frame
    image_frame = tk.Frame(root, width=600, height=300, bg='lightgray')
    image_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # 上传图片按钮
    upload_btn = tk.Button(root, text='上传4张图片', command=lambda: select_images(image_frame))
    upload_btn.grid(row=1, column=1, padx=5, pady=10)

    # 合成图片按钮
    merge_btn = tk.Button(root, text='合成图片', command=create_image)
    merge_btn.grid(row=2, column=1, padx=5, pady=10)

    # 退出按钮
    quit_btn = tk.Button(root, text='退  出', command=root.quit)
    quit_btn.grid(row=3, column=1, padx=5, pady=10)

    root.mainloop()
