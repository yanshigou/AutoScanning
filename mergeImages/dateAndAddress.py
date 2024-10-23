import cv2
import re
from paddleocr import PaddleOCR
from tkinter import messagebox
import os

# 初始化 PaddleOCR
# ocr = PaddleOCR(use_angle_cls=True, lang='ch')

file_folder = os.getcwd()
# file_folder = "D:\\trafficVideo\\"
logs_file_folder = os.path.join(file_folder, "_internal")
_DEFAULT_FOLDER_ = os.path.join(logs_file_folder, ".paddleocr")

# print(_DEFAULT_FOLDER_)
# # 打印拼接后的路径
# print(f"det_model_dir: {os.path.join(_DEFAULT_FOLDER_, 'ch_PP-OCRv4_det_infer')}")
# print(f"rec_model_dir: {os.path.join(_DEFAULT_FOLDER_, 'ch_PP-OCRv4_rec_infer')}")
# print(f"cls_model_dir: {os.path.join(_DEFAULT_FOLDER_, 'ch_ppocr_mobile_v2.0_cls_infer')}")
#
# # 检查文件是否存在
# for folder in ["ch_PP-OCRv4_det_infer", "ch_PP-OCRv4_rec_infer", "ch_ppocr_mobile_v2.0_cls_infer"]:
#     model_path = os.path.join(_DEFAULT_FOLDER_, folder, "inference.pdmodel")
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"{model_path} 文件未找到，请检查路径或文件是否完整")

ocr = PaddleOCR(
    det_model_dir=os.path.join(_DEFAULT_FOLDER_, "ch_PP-OCRv4_det_infer"),
    rec_model_dir=os.path.join(_DEFAULT_FOLDER_, "ch_PP-OCRv4_rec_infer"),
    cls_model_dir=os.path.join(_DEFAULT_FOLDER_, "ch_ppocr_mobile_v2.0_cls_infer"),  # 可选
    use_angle_cls=True,  # 如果需要使用方向分类模型
    lang='ch'  # 识别中文
)


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
def extract_info_from_image(image_path, logg):
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
        logg.logger.info(f"识别地址{address_info} 识别时间{time_info}")
        return time_info, address_info
    except Exception as e:
        messagebox.showerror("错误", f"无法识别图片内容，请检查文件路径是否包含中文字符！")
        logg.logger.error(f"无法识别图片内容，请检查文件路径是否包含中文字符！")
        return "", ""


if __name__ == "__main__":

    from loggmodel import Logger
    from datetime import datetime

    file_folder = os.getcwd()
    logs_file_folder = os.path.join(file_folder, "logs")
    now_time = datetime.now().strftime("%Y年%m月%d日")
    log_file = os.path.join(logs_file_folder, f'{now_time}.log')
    logg = Logger(log_file, level="info")

    # 图片路径
    image_path = "D:\\4.jpg"

    # 提取信息
    time_info, address_info = extract_info_from_image(image_path, logg)

    # 打印结果
    if time_info:
        print(f"提取的日期和时间：{time_info}")
    else:
        print("未找到有效的日期和时间。")

    if address_info:
        print(f"提取的地址：{address_info}")
    else:
        print("未找到有效的地址信息。")
