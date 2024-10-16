# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/11"

from PIL import Image, ImageDraw, ImageFont
import random
import string
import hashlib
import os
import textwrap


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
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def merge_images_with_text(image_paths, output_path, custom_text, max_text_width_ratio=0.9, padding=10):
    # 打开所有图片
    images = [Image.open(img_path) for img_path in image_paths]

    # 获取每张图片的宽度和高度（假设所有图片大小相同）
    img_width, img_height = images[0].size

    # 创建合成图片的初始大小（2x2布局，不含文本区域）
    merged_image_width = 2 * img_width
    merged_image_height = 2 * img_height

    # 创建合成图片并粘贴四张图片
    merged_image = Image.new('RGB', (merged_image_width, merged_image_height), (255, 255, 255))
    images_resized = [img.resize((img_width, img_height)) for img in images]
    merged_image.paste(images_resized[0], (0, 0))  # 左上
    merged_image.paste(images_resized[1], (img_width, 0))  # 右上
    merged_image.paste(images_resized[2], (0, img_height))  # 左下
    merged_image.paste(images_resized[3], (img_width, img_height))  # 右下

    # 设置支持中文的字体
    try:
        font = ImageFont.truetype("pf10.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # 确定文本区域的最大宽度（根据图片宽度的比例）
    max_text_width = int(merged_image_width * max_text_width_ratio)

    # 使用 textwrap 自动换行
    def wrap_text(text, font, max_width):
        """根据最大宽度自动换行"""
        lines = []
        for paragraph in text.split('\n'):  # 支持手动换行符
            wrapped_lines = textwrap.wrap(paragraph, width=100)
            for line in wrapped_lines:
                # 按字体测量实际宽度，并在超出时换行
                while draw.textsize(line, font=font)[0] > max_width:
                    line = line[:-1]
                lines.append(line)
        return lines

    # 获取换行后的所有文本行
    draw = ImageDraw.Draw(merged_image)  # 先创建绘图对象以测量文字
    lines = wrap_text(custom_text, font, max_text_width)

    # 计算文本区域的高度
    line_height = font.getsize('A')[1]
    text_area_height = len(lines) * line_height + 2 * padding

    # 创建一个新图片，增加文本区域高度
    total_height = merged_image_height + text_area_height
    final_image = Image.new('RGB', (merged_image_width, total_height), (255, 255, 255))

    # 将原始合成图片粘贴到新图片的顶部
    final_image.paste(merged_image, (0, 0))

    # 更新绘图对象以在新图片上绘制文本
    draw = ImageDraw.Draw(final_image)

    # 绘制黑色背景作为文本框
    draw.rectangle(
        [(0, merged_image_height), (merged_image_width, total_height)],
        fill=(0, 0, 0)
    )

    # 将文本居中绘制在黑色背景内
    current_y = merged_image_height + padding
    for line in lines:
        text_width, _ = draw.textsize(line, font=font)
        text_x = (merged_image_width - text_width) // 2  # 水平居中
        draw.text((text_x, current_y), line, font=font, fill=(255, 255, 255))
        current_y += line_height  # 移动到下一行

    # 保存合成后的图片
    final_image.save(output_path)
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
    custom_text = "违法时间：2024-10-12 13:24:22 行政区划：重庆市沙坪坝 违法地点：都市花园东路临江苑亭车库 车牌号：渝A0LQ91 " \
                  "车牌颜色：蓝色 违法代码：10398 违法行为：路中长时间停车 设备编号：1111111 车辆类型：小型汽车 " \
                  "防伪码：1k20kqlQioBT43b1"

    # 合成图片并添加文字
    merge_images_with_text(image_paths, output_path, custom_text)
