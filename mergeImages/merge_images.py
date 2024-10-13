# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/11"

from PIL import Image, ImageDraw, ImageFont
import random
import string
import hashlib
import os


# 生成随机防伪码函数
def generate_security_code(length=16):
    characters = string.ascii_letters + string.digits
    random_code = ''.join(random.choices(characters, k=length - 4))
    checksum = hashlib.md5(random_code.encode()).hexdigest()[:4]
    security_code = random_code + checksum
    return security_code


# 验证防伪码合法性函数
def verify_security_code(security_code):
    if len(security_code) != 16:
        return False
    random_code = security_code[:-4]
    checksum = security_code[-4:]
    expected_checksum = hashlib.md5(random_code.encode()).hexdigest()[:4]
    return checksum == expected_checksum


# 图片合成函数
def merge_images_with_text(image_paths, output_path, custom_text):
    # 打开所有图片
    images = [Image.open(img_path) for img_path in image_paths]

    # 获取图像的宽度和高度（假设所有图像的大小相同）
    img_width, img_height = images[0].size

    # 设置合成图片最大尺寸（原始图片宽高的两倍）
    max_width = img_width * 2
    max_height = img_height * 2

    # 假设文本区域的高度为 100 像素
    text_area_height = 100

    # 计算新图像的大小，按 2x2 布局计算
    merged_image_width = 2 * img_width
    merged_image_height = 2 * img_height + text_area_height

    # 如果超出最大尺寸，则按比例缩小图片
    if merged_image_width > max_width or merged_image_height > max_height:
        scale_factor = min(max_width / merged_image_width, max_height / merged_image_height)
        img_width = int(img_width * scale_factor)
        img_height = int(img_height * scale_factor)
        merged_image_width = int(merged_image_width * scale_factor)
        merged_image_height = int(merged_image_height * scale_factor)

    # 创建新图像
    merged_image = Image.new('RGB', (merged_image_width, merged_image_height), (255, 255, 255))

    # 将四张图片分别粘贴到新图像的四个象限中
    images_resized = [img.resize((img_width, img_height)) for img in images]
    merged_image.paste(images_resized[0], (0, 0))  # 左上
    merged_image.paste(images_resized[1], (img_width, 0))  # 右上
    merged_image.paste(images_resized[2], (0, img_height))  # 左下
    merged_image.paste(images_resized[3], (img_width, img_height))  # 右下

    # 创建绘图对象以在图像上绘制文本
    draw = ImageDraw.Draw(merged_image)

    # 设置支持中文的字体路径
    try:
        font = ImageFont.truetype("pf10.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # 计算文本的宽度和高度，以便居中绘制
    text_width, text_height = draw.textsize(custom_text, font=font)
    text_x = (merged_image_width - text_width) // 2
    text_y = 2 * img_height + (text_area_height - text_height) // 2

    # 绘制黑色背景的矩形框（作为文本框）
    draw.rectangle(
        [(0, 2 * img_height), (merged_image_width, merged_image_height)],
        fill=(0, 0, 0)
    )

    # 在黑色背景上绘制白色文本
    draw.text((text_x, text_y), custom_text, font=font, fill=(255, 255, 255))

    # 保存合成后的图像
    merged_image.save(output_path)
    # print(f"合成图片已保存为 {output_path}")
    return os.path.abspath(output_path)


if __name__ == '__main__':

    # 生成一个随机的防伪码
    security_code = generate_security_code()
    print(f"生成的防伪码：{security_code}")

    # 验证生成的防伪码
    is_valid = verify_security_code(security_code)
    print(f"防伪码验证结果：{'有效' if is_valid else '无效'}")


    # 图片路径和自定义文字
    # image_paths = [
    #     "/Users/yanshigou/dzt/trafficmgmtspb/apps/myutils/2_20240918_160305_410_50.123.123.322_渝CBC050_蓝牌.jpg",
    #     "/Users/yanshigou/dzt/trafficmgmtspb/apps/myutils/2_20240918_160305_410_50.123.123.322_渝CBC050_蓝牌.jpg",
    #     "/Users/yanshigou/dzt/trafficmgmtspb/apps/myutils/2_20240918_160305_410_50.123.123.322_渝CBC050_蓝牌.jpg",
    #     "/Users/yanshigou/dzt/trafficmgmtspb/apps/myutils/2_20240918_160305_410_50.123.123.322_渝CBC050_蓝牌.jpg"
    # ]
    image_paths = [
        "D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\mergeImages\\1.jpg",
        "D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\mergeImages\\2.jpg",
        "D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\mergeImages\\3.jpg",
        "D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\mergeImages\\4.jpg",


    ]
    output_path = "merged_image.jpg"
    custom_text = "违法时间：%s 行政区划：%s 违法地点：%s 设备编号：%s 车牌号：%s 防伪码：%s" % (
        "2024-10-12 13:24:55", "重庆市沙坪坝区", "都市花园东路临江苑停车库", "501300000000070021", "渝A0LQ9", security_code
    )

    # 合成图片并添加文字
    merge_images_with_text(image_paths, output_path, custom_text)
