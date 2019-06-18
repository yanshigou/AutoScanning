import tkinter as tk
import time
import threading
import random

songs = ['爱情买卖', '朋友', '回家过年', '好日子']
movies = ['阿凡达', '猩球崛起']


def music(songs):
    while True:
        text.insert(tk.END, "听歌曲：%s \t-- %s\n" % (random.sample(songs, 1), time.ctime()))
        time.sleep(2)


def movie(movies, text):
    for m in movies:
        text.insert(tk.END, "看电影：%s \t-- %s\n" % (m, time.ctime()))
        time.sleep(5)


def thread_it(func, *args):
    """
    将函数打包进线程
    :param func:
    :param args:
    :return:
    """
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞--卡死界面！
    # t.join()


root = tk.Tk()

text = tk.Text(root)
text.pack()

tk.Button(root, text='音乐', command=lambda: thread_it(music, songs)).pack()
tk.Button(root, text='电影', command=lambda: thread_it(movie, movies, text)).pack()

root.mainloop()
