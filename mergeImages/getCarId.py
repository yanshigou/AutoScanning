import cv2
import hyperlpr3 as lpr3
import numpy as np
from PIL import Image
from tkinter import messagebox
import os
import traceback

catcher = lpr3.LicensePlateCatcher(logger_level=3)


def get_carid(image_path, logg):
    """识别车牌号并判断车牌颜色"""
    image = cv2.imread(image_path)

    # 检查图像是否成功加载
    if image is None:
        messagebox.showwarning("警告", f"图像加载失败: {image_path}")
        return None

    # 使用 LicensePlateCatcher 识别车牌
    result = catcher(image)
    # print(result)
    if not result:
        messagebox.showwarning("警告", "未检测到车牌")
        return None
    if len(result) >= 2:
        messagebox.showwarning("警告", "识别到多个车牌，请确保最后一张图只有一个车牌，或手动输入车牌信息！")
        return None

    try:
        # 获取车牌信息和坐标
        car_id, bbox = result[0][0], result[0][3]
        img = Image.open(image_path)

        # current_file_folder = os.path.dirname(os.path.abspath(__file__))
        file_folder = os.getcwd()
        img_folder_path = os.path.join(file_folder, "mergeImgs")
        img_folder_path = os.path.join("D:\\", "mergeImgs")
        # 检查 mergeImgs 文件夹是否存在，如果不存在则创建
        if not os.path.exists(img_folder_path):
            os.makedirs(img_folder_path)
        output_path = os.path.join(img_folder_path, "cropped_image.jpg")

        # 裁剪车牌区域并转换为 RGB 模式
        cropped_img = img.crop((bbox[0], bbox[1], bbox[2], bbox[3])).convert("RGB")
        cropped_img_path = output_path
        cropped_img.save(cropped_img_path, format="JPEG")

        # 加载裁剪后的车牌图像
        cropped_image = cv2.imread(cropped_img_path)
        height, width, _ = cropped_image.shape
        half_width = width // 2

        # 前半部分（检测黄色）和后半部分（检测绿色）
        front_plate = cropped_image[:, :half_width]
        back_plate = cropped_image[:, half_width:]

        # 定义 HSV 色彩范围
        yellow_range = (np.array([20, 100, 100]), np.array([30, 255, 255]))
        green_range = (np.array([35, 100, 100]), np.array([85, 255, 255]))

        # 检测颜色区域
        if has_color(front_plate, yellow_range) and has_color(back_plate, green_range):
            logg.logger.info(f"识别成功{car_id}渐变绿")
            return {"car_id": car_id, "color": "渐变绿"}

        # 使用 HSV 识别整体车牌颜色
        predicted_color = detect_main_color(cropped_image)
        logg.logger.info(f"识别成功{car_id}{predicted_color}")
        return {"car_id": car_id, "color": predicted_color}
    except Exception as e:
        strexc = traceback.format_exc()
        logg.logger.error(f"识别车牌号并判断车牌颜色失败！{strexc}")


def has_color(image, color_range):
    """检查图像是否包含指定颜色范围的像素"""
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, *color_range)
    return cv2.countNonZero(mask) > 0


def detect_main_color(image):
    """检测车牌的主要颜色"""
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_ranges = {
        '白色': (np.array([0, 0, 220]), np.array([180, 20, 255])),
        '黄色': (np.array([20, 100, 100]), np.array([30, 255, 255])),
        '蓝色': (np.array([100, 150, 0]), np.array([140, 255, 255])),
        '绿色': (np.array([35, 100, 100]), np.array([85, 255, 255]))  # 绿色
    }

    color_count = {color: 0 for color in color_ranges}
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_image, lower, upper)
        color_count[color] = cv2.countNonZero(mask)

    return max(color_count, key=color_count.get)


if __name__ == '__main__':
    from loggmodel import Logger
    from datetime import datetime

    file_folder = os.getcwd()
    logs_file_folder = os.path.join(file_folder, "logs")
    now_time = datetime.now().strftime("%Y年%m月%d日")
    log_file = os.path.join(logs_file_folder, f'{now_time}.log')
    logg = Logger(log_file, level="info")

    res = get_carid("D:\\4.jpg", logg)
    if res:
        print(res)
