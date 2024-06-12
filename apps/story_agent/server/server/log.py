import os
import logging
from logging.handlers import TimedRotatingFileHandler


class LoggerConfigurator:
    def __init__(self, log_dir, log_filename="app.log"):
        self.log_dir = log_dir
        self.log_filename = log_filename
        self.logger = None

    def _create_log_directory(self):
        """创建日志目录，如果不存在的话"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def configure_logger(self):
        """配置日志"""
        self._create_log_directory()
        log_path = os.path.join(self.log_dir, self.log_filename)

        # 创建 logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 创建 TimedRotatingFileHandler 以每天轮换日志
        file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # 添加 handler 到 logger
        self.logger.addHandler(file_handler)

        # 为了防止日志重复，在添加 handler 之后调用
        self.logger.propagate = False

        return self.logger


home_dir = os.path.dirname(os.path.dirname(__file__))
log_dir = os.path.join(home_dir, "logs")
logger = LoggerConfigurator(log_dir, 'story_book.log').configure_logger()
