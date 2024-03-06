import logging
import logging.handlers
import zipfile
import os
from datetime import datetime, timedelta
import inspect
from unittest.mock import patch
import time

class ZipRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def close_and_rename_logfile(self):
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        dfn = self.rotation_filename(f"{self.baseFilename}_{yesterday.strftime('%Y%m%d')}")

        # Close the current log file
        if self.stream:
            self.stream.close()
            self.stream = None

        # Ensure the current log file is closed before renaming
        while True:
            try:
                with open(dfn, 'r'):
                    break
            except IOError:
                pass

        # Rename the log file
        temp_filename = f"{dfn}_temp"
        os.rename(dfn, temp_filename)

        return temp_filename, dfn

    def doRollover(self):
        # Check if we need to rollover at all
        if os.path.exists(self.baseFilename) and os.stat(self.baseFilename).st_mtime >= time.time() - self.interval:
            return

        temp_filename, dfn = self.close_and_rename_logfile()

        # Zip the old log file
        zip_filename = f"{dfn}.zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_filename, arcname=os.path.basename(dfn))

        # Delete the old log file
        try:
            os.remove(temp_filename)
        except Exception as e:
            print(f"Failed to delete temp_filename: {e}")

        # Create a new log file
        self.mode = 'w'
        self.stream = self._open()
    
class XXYLogger:
    def __init__(self, name, log_file='xixun_log.log', level=logging.DEBUG, when='midnight', interval=1, backupCount=7, fmt='【%(asctime)s】 文件名： %(caller_filename)s 函数入口： %(caller_filename)s \n %(levelname)s - %(message)s'):
        # Ensure the log folder exists
        if not os.path.exists('log'):
            os.makedirs('log')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a handler for writing log to a file
        fh = ZipRotatingFileHandler(os.path.join('log', log_file), when=when, interval=interval, backupCount=backupCount, encoding='utf-8')
        fh.setLevel(level)

        # Define the log format
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(fh)

    def info(self, message, caller_filename=None):
        if caller_filename is None:
            caller_filename = self.get_caller_filename()
        extra = {'caller_filename': caller_filename}
        self.logger.info(message, extra=extra)

    def debug(self, message, caller_filename=None):
        if caller_filename is None:
            caller_filename = self.get_caller_filename()
        extra = {'caller_filename': caller_filename}
        self.logger.debug(message, extra=extra)

    def warning(self, message, caller_filename=None):
        if caller_filename is None:
            caller_filename = self.get_caller_filename()
        extra = {'caller_filename': caller_filename}
        self.logger.warning(message, extra=extra)

    def get_caller_filename(self):
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back  # Get the caller's frame
        caller_filename = os.path.basename(inspect.getframeinfo(caller_frame).filename)
        return caller_filename




'''
# 创建数据库日志记录器
db_logger = XXYLogger('database', log_file='database.log')

# 创建任务日志记录器
task_logger = XXYLogger('task', log_file='task.log')

# 示例用法
db_logger.info('这是数据库日志信息')
task_logger.warning('这是任务日志信息')
'''