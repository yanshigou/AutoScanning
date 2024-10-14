# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/12"
__title__ = "4合1专用v1.0_20241012"

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ping3 import ping
from PIL import Image, ImageTk
from mergeImages.merge_images import merge_images_with_text, generate_security_code
# import sys
# from PyQt5.QtWidgets import QApplication, QFileDialog
from mergeImages.GetCadId.main import get_carid
import threading
import re


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



def generate_custom_text():
    """生成合成图片所需的custom_text"""
    time = time_entry.get()
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
    # display_images(selected_image_paths, image_frame)
    load_images_async(selected_image_paths, image_frame)

# def select_images_pyqt(image_frame):
#     """使用PyQt选择图片并展示"""
#     global selected_image_paths
#     app = QApplication(sys.argv)
#
#     dialog = QFileDialog()
#     dialog.setFileMode(QFileDialog.ExistingFiles)
#     dialog.setOption(QFileDialog.DontUseNativeDialog, True)
#     dialog.setAcceptMode(QFileDialog.AcceptOpen)
#     dialog.setViewMode(QFileDialog.List)
#     dialog.setOption(QFileDialog.ShowDirsOnly, False)
#
#     if dialog.exec_() == QFileDialog.Accepted:
#         file_paths = dialog.selectedFiles()
#         if len(file_paths) != 4:
#             messagebox.showwarning("选择错误", "请确保选择4张图片！")
#             return
#         selected_image_paths = list(file_paths)
#         display_images(selected_image_paths, image_frame)
#
#     app.quit()


def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None


def check_server_connection():
    """检查服务器连接并反馈"""
    ip_val = ip_entry.get()
    if not is_valid_ip(ip_val):
        messagebox.showerror("连接测试", f"无效的IP地址: {ip_val}")
        return

    delay = ping(ip_val, timeout=1)
    if delay is not None:
        messagebox.showinfo("连接测试", f"服务器连接成功: {ip_val}")
    else:
        messagebox.showerror("连接测试", f"服务器连接失败，请检查服务器：{ip_val}")


if __name__ == '__main__':
    selected_image_paths = []

    root = tk.Tk()
    root.title(__title__)
    root.geometry('1000x800+700+300')

    # 输入框区域
    input_frame = tk.Frame(root)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    # 初始化输入框
    time_entry = tk.Entry(input_frame)
    district_entry = tk.Entry(input_frame)
    location_entry = tk.Entry(input_frame)
    device_id_entry = tk.Entry(input_frame)
    plate_number_entry = tk.Entry(input_frame)
    ip_entry = tk.Entry(input_frame)

    # 车辆类型下拉框
    vehicle_types = ["小型汽车", "大型汽车", "新能源小型汽车", "新能源大型汽车", "摩托车", "教练车"]
    vehicle_type_combobox = ttk.Combobox(input_frame, values=vehicle_types)
    vehicle_type_combobox.set("选择车辆类型")  # 默认提示文本

    # 输入框和标签的列表
    labels_and_entries = [
        ("违法时间：", time_entry),
        ("行政区划：", district_entry),
        ("违法地点：", location_entry),
        ("设备编号：", device_id_entry),
        ("车牌号：", plate_number_entry),
        ("车辆类型：", vehicle_type_combobox),  # 添加车辆类型标签和选择框
        ("服务器IP：", ip_entry),
    ]

    # 遍历列表并创建标签和输入框
    for idx, (label_text, entry) in enumerate(labels_and_entries):
        tk.Label(input_frame, text=label_text).grid(row=idx, column=0, sticky="w")
        entry.grid(row=idx, column=1, padx=5, pady=5)

    # 测试连接按钮
    test_connection_btn = tk.Button(input_frame, text='测试连接', command=check_server_connection)
    test_connection_btn.grid(row=len(labels_and_entries), column=0, columnspan=2, pady=10)

    # 图片展示区域的 Frame
    image_frame = tk.Frame(root, width=600, height=300, bg='lightgray')
    image_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # 上传图片按钮
    upload_btn = tk.Button(root, text='上传4张图片', command=lambda: select_images(image_frame))
    upload_btn.grid(row=1, column=1, padx=5, pady=10)

    # 合成图片按钮
    merge_btn = tk.Button(root, text='合成图片', command=create_image)
    merge_btn.grid(row=3, column=1, padx=5, pady=10)

    # 退出按钮
    quit_btn = tk.Button(root, text='退  出', command=root.quit)
    quit_btn.grid(row=4, column=1, padx=5, pady=10)

    root.mainloop()
