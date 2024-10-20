# -*- coding: utf-8 -*-
# author: dzt
# datetime: 2023-03-27

import logging
import logging.handlers
from logging import handlers
import time


class MyLogger:

    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

        # 添加按分钟切割的Handler
        minute_handler = logging.handlers.TimedRotatingFileHandler(
            filename='mylog_minute.log', when='M', backupCount=10, encoding='utf-8')
        minute_handler.setFormatter(formatter)
        self.logger.addHandler(minute_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


class Logger:
    # 日志级别关系映射
    LEVEL_RELATIONS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(
        self,
        filename,
        level='debug',
        when='D',
        # interval=1,
        back_count=10,
        fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    ):
        self.logger = logging.getLogger(filename)

        # 如果该logger已有handler，则先删除
        if self.logger.handlers:
            self.logger.handlers = []

        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.LEVEL_RELATIONS.get(level))

        th = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=back_count,
            # interval=interval,
            encoding='utf-8'
        )

        th.setFormatter(format_str)

        self.logger.addHandler(th)


if __name__ == '__main__':
    logger = MyLogger(__name__)
    log_file = '违停日志.log'
    logg = Logger(log_file, level="info")
    while True:
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warning message')
        logger.error('error message')
        logger.critical('critical message')
        time.sleep(5)  # 等待一分钟，以便进行分钟级别的切割测试

        logg.logger.info("【事件】【扫描到文件夹】 %s，【未发现任何图片，休息%s秒】" % ("d:test", "5"))
        time.sleep(5)


