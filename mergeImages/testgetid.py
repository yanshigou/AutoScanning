import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import threading

def thread_it(func, *args):
    """将函数打包进线程中执行"""
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

def center_window(window, width, height):
    """将窗口显示在屏幕中心"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_merged_image(image_path, data):
    """在新窗口展示合成的图片"""
    new_window = tk.Toplevel()
    new_window.title("合成图片展示")

    # 加载并调整图片大小
    merged_image = Image.open(image_path)
    window_width, window_height = 1000, 600
    merged_image.thumbnail((window_width, window_height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(merged_image)

    # 显示图片
    label = tk.Label(new_window, image=photo)
    label.image = photo
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # 设置窗口大小和最小尺寸，并居中
    new_window.update_idletasks()
    center_window(new_window, photo.width(), photo.height() + 100)
    new_window.minsize(400, 300)

    # 上传按钮
    push_btn = tk.Button(
        new_window, text='上传至平台',
        font=("仿宋", 12), bg="#4CAF50", fg="white", padx=10, pady=5,
        command=lambda: thread_it(upload_to_platform, image_path, data, new_window)
    )
    push_btn.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    # 关闭按钮（优化样式）
    close_btn = tk.Button(
        new_window, text='退出',
        font=("仿宋", 12), bg="#f44336", fg="white", padx=10, pady=5,
        relief="raised", borderwidth=2,
        command=new_window.destroy
    )
    close_btn.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    new_window.grid_rowconfigure(0, weight=1)
    new_window.grid_columnconfigure(0, weight=1)
    new_window.grid_columnconfigure(1, weight=1)

def upload_to_platform(image_path, data, window):
    """处理上传图片到平台的逻辑"""
    ip_val = ip_entry.get()
    print(data)
    try:
        with open(image_path, 'rb') as f:
            files = {'image_file': ("mergelImage.jpg", f, 'image/jpg')}
            with requests.Session() as maxrequests:
                res = maxrequests.post(f'http://{ip_val}{dj_url}', files=files, data=data, timeout=5)
                res_json = res.json()
                status = res_json.get('status')
                strexc = res_json.get('e')

                if status == "success":
                    show_countdown_message(window, "图片上传成功！", 5)  # 显示倒计时提示框
                else:
                    messagebox.showerror("错误", f"图片上传错误！！{strexc}")

    except Exception as e:
        print(f"Exception: {e}")
        messagebox.showerror("错误", str(e))

def show_countdown_message(parent, message, seconds):
    """显示带倒计时的自定义提示框，并居中"""
    countdown_window = tk.Toplevel(parent)
    countdown_window.title("提示")

    label = tk.Label(countdown_window, text=f"{message} ({seconds}秒后关闭)", font=("仿宋", 12))
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

    update_label()

# 示例输入框和URL配置
root = tk.Tk()
ip_entry = tk.Entry(root)
ip_entry.insert(0, "127.0.0.1")  # 默认IP
ip_entry.pack()

dj_url = "/upload"  # 示例URL

# 测试显示合成图片的功能
tk.Button(root, text="测试合成图片", command=lambda: show_merged_image("D:\历史项目管理\AutoScanning交通扫描软件\AutoScanning\mergeImages\merged_image.jpg", {"key": "value"})).pack()

# 主窗口居中
root.update_idletasks()
center_window(root, 800, 600)

root.mainloop()
