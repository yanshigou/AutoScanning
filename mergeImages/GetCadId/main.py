import sys
import cv2
import hyperlpr3 as lpr3
import requests
import numpy as np
from PIL import Image

catcher = lpr3.LicensePlateCatcher(logger_level=3)


def get_carid(image_path):

    image = cv2.imread(image_path)

    # 检查图像是否成功加载
    if image is None:
        print(f"图像加载失败: {image_path}")
        return  # 或者抛出一个异常
    result = catcher(image)
    idx = 0
    img = Image.open(image_path)
    # print(result)

    for i in result:


        cropped_img = img.crop((i[3][0], i[3][1], i[3][2], i[3][3]))
        cropped_img.save("cropped_image" + str(idx) + ".jpg")

        # 读取车牌图片
        image = cv2.imread("cropped_image" + str(idx) + ".jpg")

        # 获取图像尺寸，划分为前后两个区域
        height, width, _ = image.shape
        half_width = width // 2

        # 将图像分为前半部分（黄色）和后半部分（绿色）
        front_plate = image[:, :half_width]
        back_plate = image[:, half_width:]

        # 定义黄色和绿色的 HSV 范围
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])

        green_lower = np.array([35, 100, 100])
        green_upper = np.array([85, 255, 255])

        # 将图像转换为 HSV
        hsv_front = cv2.cvtColor(front_plate, cv2.COLOR_BGR2HSV)
        hsv_back = cv2.cvtColor(back_plate, cv2.COLOR_BGR2HSV)

        # 对前半部分检测黄色
        yellow_mask = cv2.inRange(hsv_front, yellow_lower, yellow_upper)
        yellow_pixels = cv2.countNonZero(yellow_mask)

        # 对后半部分检测绿色
        green_mask = cv2.inRange(hsv_back, green_lower, green_upper)
        green_pixels = cv2.countNonZero(green_mask)

        # 判断颜色是否匹配
        if yellow_pixels > 0 and green_pixels > 0:
            print("车牌是新能源大车牌（前黄后绿）")
        else:
            # 将图片转换为 HSV 色彩空间
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # 定义颜色范围
            color_ranges = {
                '白色': (np.array([0, 0, 220]), np.array([180, 20, 255])),
                '黄色': (np.array([20, 100, 100]), np.array([30, 255, 255])),
                '蓝色': (np.array([100, 150, 0]), np.array([140, 255, 255])),
                '新能源': (np.array([35, 100, 100]), np.array([85, 255, 255]))  # 绿色
            }

            # 初始化结果字典
            color_count = {color: 0 for color in color_ranges}

            # 生成掩码并统计像素
            for color, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv_image, lower, upper)
                color_count[color] = cv2.countNonZero(mask)

            # 找出最多的颜色
            predicted_color = max(color_count, key=color_count.get)
            car_id = i[0]
            # print("车牌识别结果为：", i[0])
            # print(f"车牌颜色是: {predicted_color}")
            # print(f"idx: {idx}")
            return {"car_id": car_id, "color": predicted_color}
        idx += 1

if __name__ == '__main__':
    res = get_carid("D:\\4.jpg")
    print(res)
