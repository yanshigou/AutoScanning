import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QListView, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QStringListModel
from PIL import Image
import tkinter as tk
from tkinter import filedialog


class ThumbnailViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("选择图片")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout(self)
        self.list_view = QListView(self)
        self.layout.addWidget(self.list_view)

        self.selected_files = []

        self.select_images()

    def select_images(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            self.selected_files = file_dialog.selectedFiles()
            self.display_thumbnails()

    def display_thumbnails(self):
        if not self.selected_files:
            QMessageBox.warning(self, "选择错误", "未选择任何文件！")
            return

        model = QStringListModel()
        thumbnail_paths = []

        for file_path in self.selected_files:
            thumbnail_path = self.create_thumbnail(file_path)
            thumbnail_paths.append(thumbnail_path)

        model.setStringList(thumbnail_paths)
        self.list_view.setModel(model)

    def create_thumbnail(self, file_path):
        """生成缩略图并返回其路径"""
        try:
            image = Image.open(file_path)
            image.thumbnail((100, 100))  # 设置缩略图的大小
            thumbnail_path = f"{os.path.splitext(file_path)[0]}_thumbnail.png"
            image.save(thumbnail_path)  # 保存缩略图
            return thumbnail_path
        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {e}")
            return ""


def select_files():
    filenames = filedialog.askopenfilenames(title='选择文件', filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if filenames:
        print("选择的文件（按选择顺序）：")
        for filename in filenames:
            print(filename)
    else:
        print("没有选择文件")




if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # viewer = ThumbnailViewer()
    # viewer.show()
    # sys.exit(app.exec_())

    root = tk.Tk()
    button = tk.Button(root, text="选择文件", command=select_files)
    button.pack()
    tk_version = root.tk.call('info', 'patchlevel')
    root.mainloop()