# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2024/10/11"

from PIL import Image, ImageDraw, ImageFont
import random
import string
import hashlib
import os
import traceback


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


def resize_to_target_aspect_ratio(image, target_width, target_height):
    """调整图片大小以符合目标宽高比，保持原始比例"""
    img_width, img_height = image.size
    target_aspect_ratio = target_width / target_height
    img_aspect_ratio = img_width / img_height

    if img_aspect_ratio > target_aspect_ratio:
        # 图片太宽，按宽度调整
        new_width = target_width
        new_height = int(target_width / img_aspect_ratio)
    else:
        # 图片太高，按高度调整
        new_height = target_height
        new_width = int(target_height * img_aspect_ratio)

    return image.resize((new_width, new_height), Image.ANTIALIAS)


def merge_images_with_text(image_paths, custom_text, data, logg, max_text_width_ratio=1, padding=10):
    try:
        images = [Image.open(img_path) for img_path in image_paths]

        # 获取最大宽度和高度
        max_width = max(img.size[0] for img in images)
        max_height = max(img.size[1] for img in images)

        # 创建合成图片的初始大小（2x2布局）
        merged_image_width = 2 * max_width
        merged_image_height = 2 * max_height

        # 创建合成图片
        merged_image = Image.new('RGB', (merged_image_width, merged_image_height), (255, 255, 255))

        # 调整所有图片大小并粘贴
        for index, img in enumerate(images):
            resized_img = resize_to_target_aspect_ratio(img, max_width, max_height)
            x_offset = (index % 2) * max_width + (max_width - resized_img.size[0]) // 2  # 居中对齐
            y_offset = (index // 2) * max_height + (max_height - resized_img.size[1]) // 2  # 居中对齐
            merged_image.paste(resized_img, (x_offset, y_offset))

        # 设置字体
        file_folder = os.getcwd()
        font_folder = os.path.join(file_folder, "_internal")
        font_file = os.path.join(font_folder, "pf10.ttf")
        font = ImageFont.truetype(font_file, 80) if os.path.exists(font_file) else ImageFont.load_default()

        # 确定文本区域的最大宽度
        max_text_width = merged_image_width - 2 * padding

        # 自动换行
        def wrap_text(text, font, max_width):
            wrapped_lines = []
            lines = text.split('\n')
            for line in lines:
                words = line.split(' ')
                current_line = ''
                for word in words:
                    test_line = current_line + word + ' '
                    if draw.textsize(test_line, font=font)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            wrapped_lines.append(current_line.strip())
                        current_line = word + ' '
                if current_line:
                    wrapped_lines.append(current_line.strip())
            return wrapped_lines

        draw = ImageDraw.Draw(merged_image)
        lines = wrap_text(custom_text, font, max_text_width)

        # 计算文本区域的高度
        line_height = font.getsize('A')[1]
        text_area_height = len(lines) * line_height + 2 * padding

        # 创建一个新图片，增加文本区域高度
        total_height = merged_image_height + text_area_height
        final_image = Image.new('RGB', (merged_image_width, total_height), (255, 255, 255))
        final_image.paste(merged_image, (0, 0))

        draw = ImageDraw.Draw(final_image)
        draw.rectangle([(0, merged_image_height), (merged_image_width, total_height)], fill=(0, 0, 0))

        # 绘制文本
        current_y = merged_image_height + padding
        for line in lines:
            draw.text((padding, current_y), line, font=font, fill=(255, 255, 255))
            current_y += line_height

        # 保存合成后的图片
        data_type = data.get('data_type')
        ip = data.get('ip')
        car_id = data.get('car_id')
        wf_time = data.get('wf_time')
        car_color = data.get('car_color')
        file_name = f"{data_type}_{wf_time[:8]}_{wf_time[8:]}_000_视频纠违_{ip}_{car_id}_{car_color}.jpg"

        img_folder_path = os.path.join(file_folder, "mergeImgs")
        if not os.path.exists(img_folder_path):
            os.makedirs(img_folder_path)
        output_path = os.path.join(img_folder_path, file_name)

        final_image.save(output_path)
        logg.logger.info(f"合成图片及信息成功！保存至{output_path}，文件名称{file_name}")
        return os.path.abspath(output_path), file_name
    except Exception as e:
        strexc = traceback.format_exc()
        logg.logger.error(f"合成图片及信息失败！{strexc}")


if __name__ == '__main__':
    # 生成一个随机的防伪码
    security_code = generate_security_code()
    print(f"生成的防伪码：{security_code}")

    # 验证生成的防伪码
    is_valid = verify_security_code(security_code)
    print(f"防伪码验证结果：{'有效' if is_valid else '无效'}")

    # 图片路径和自定义文字
    image_paths = [
        "D:\\历史项目管理\\AutoScanning交通扫描软件\\AutoScanning\\mergeImages\\1.jpg",
        "D:\\历史项目管理\\AutoScanning交通扫描软件\\AutoScanning\\mergeImages\\2.jpg",
        "D:\\历史项目管理\\AutoScanning交通扫描软件\\AutoScanning\\mergeImages\\3.jpg",
        "D:\\历史项目管理\\AutoScanning交通扫描软件\\AutoScanning\\mergeImages\\4.jpg",
    ]
    output_path = "merged_image.jpg"
    custom_text = "违法时间：2024-10-12 13:24:55 行政区划：重庆市沙坪坝 违法地点：都市花园东路临江苑停车库 车牌号：渝A0LQ91 车牌颜色：蓝色 违法代码：10398 违法行为：路中长时间停车 设备编号：1111111 车辆类型：小型汽车 防伪码：Td9gwkOTcXmJ16b3"

    # 合成图片并添加文字
    merge_images_with_text(image_paths, output_path, custom_text)
