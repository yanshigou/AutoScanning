import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal


class WorkerThread(QThread):
    update_signal = pyqtSignal(str)

    def run(self):
        for i in range(1, 11):
            time.sleep(1)  # 模拟后台处理
            self.update_signal.emit(f"后台处理结果：{i}")


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('后台处理示例')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button = QPushButton('启动后台处理')
        self.button.clicked.connect(self.start_thread)
        self.layout.addWidget(self.button)

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        self.worker_thread = WorkerThread()
        self.worker_thread.update_signal.connect(self.update_text)

    def start_thread(self):
        if not self.worker_thread.isRunning():
            self.text_edit.append("后台处理启动中...")
            self.worker_thread.start()

    def update_text(self, message):
        self.text_edit.append(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
