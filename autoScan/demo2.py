# -*- coding: utf-8 -*-
# author: dzt
# datetime: 2024-08-05
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

root = tk.Tk()

# 创建一个只读的ScrolledText
scrolled_text = ScrolledText(root, state='disabled')
scrolled_text.pack(fill='both', expand=True)

# 向文本框中添加内容
scrolled_text.insert('end', '这是一个只读的ScrolledText文本框。\n')
scrolled_text.insert('end', '你不能在这里输入任何文本。\n')

root.mainloop()