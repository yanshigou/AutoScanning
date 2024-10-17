import cv2
import re
from paddleocr import PaddleOCR
from tkinter import messagebox

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')


# 解析 OCR 结果并提取文本
def ocr_image(image_path):
    # 读取图片
    image = cv2.imread(image_path)

    # 使用 OCR 识别整个图片的文本
    result = ocr.ocr(image, cls=True)

    texts = []
    for line in result:
        for box, (text, score) in line:
            # print('box', box)
            # print('text', text)
            # print('len', len(text))
            # print('score', score)
            texts.append(text)

    return texts


# 从文本中提取日期和时间
def extract_dates_and_times(texts):
    text = ' '.join(texts)
    date_patterns = [
        r'\d{4}年\d{1,2}月\d{1,2}日',
        r'\d{4}-\d{1,2}-\d{1,2}'
    ]
    time_pattern = r'\d{2}:\d{2}:\d{2}'

    date, time = None, None

    for pattern in date_patterns:
        match_date = re.search(pattern, text)
        if match_date:
            date = match_date.group().replace('年', '-').replace('月', '-').replace('日', '')

    match_time = re.search(time_pattern, text)
    if match_time:
        time = match_time.group()

    if date and time:
        return f"{date} {time}"
    return ""


# 从文本中提取地址信息
def extract_address(texts):
    # print(texts)
    # for text in texts:
    #     if len(text) > 5:
    #         return text.strip()
    # return None
    if texts:
        return texts[-1]
    else:
        return ""


# 主函数：识别并提取信息
def extract_info_from_image(image_path):
    # 使用 OCR 识别图片中的文本
    try:
        texts = ocr_image(image_path)

        # print(f"OCR识别出的文本: {texts}")  # 打印识别出的所有文本，方便调试

        # 提取日期时间和地址信息
        time_info = extract_dates_and_times(texts)
        # try:
        #     texts.remove(time_info)
        # except Exception as e:
        #     for i in time_info.split(" "):
        #         texts.remove(i)
        address_info = extract_address(texts)

        return time_info, address_info
    except Exception as e:
        messagebox.showerror("错误", f"无法识别图片内容，请检查文件路径是否包含中文字符！")
        return "", ""


if __name__ == "__main__":
    # 图片路径
    image_path = "D:\\4.jpg"

    # 提取信息
    time_info, address_info = extract_info_from_image(image_path)

    # 打印结果
    if time_info:
        print(f"提取的日期和时间：{time_info}")
    else:
        print("未找到有效的日期和时间。")

    if address_info:
        print(f"提取的地址：{address_info}")
    else:
        print("未找到有效的地址信息。")
