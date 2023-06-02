import os
import sys
import time
import platform
import traceback
import logging

# local imports
from ecg_viewer import VERSION, LOG_LEVEL


def log_sys_info() -> None:
    """Logs system info."""
    logging.info(f"Build: {VERSION}")
    logging.info(time.ctime())
    logging.info(platform.platform())
    logging.info(f"Python Version: {platform.python_version()}")
    logging.info(f"Directory: {os.getcwd()}")

def exception_handler_hook(ex_type, ex_val, ex_tb):
    """Extend the exception handler to log unhandled exceptions"""
    logging.critical("Unhandled exception: ", exc_info = (ex_type, ex_val, ex_tb))
    print(''.join(traceback.format_exception(ex_type, ex_val, ex_tb)))

def init_logging(log_level: int = logging.INFO):
    lfmt = "%(levelname)s [%(funcName)s]: %(message)s"
    log_file_name = 'ecg_viewer.log'
    log_file_path = ''
    if hasattr(sys, "_MEIPASS"):
        plat = sys.platform
        log_file_dir = ''
        if plat == "darwin":
            log_file_dir = os.path.expanduser('~/Library/Logs/')
        elif plat == "win32":
            log_file_dir = os.path.expanduser('~/APPDATA/LOCAL/')
        elif plat == "linux":
            log_file_dir = os.path.expanduser('~/.config/')
        else:
            raise OSError(f"Unsupported platform: {sys.platform}")
        log_file_path = os.path.join(log_file_dir, log_file_name)
    else:
        log_file_path = os.path.join(".", log_file_name)
    try:
        logging.basicConfig(filename=log_file_path, level=log_level, filemode='w', format=lfmt)
    except OSError as e:
        logging.basicConfig(level=logging.INFO, format=lfmt)
        logging.error(e)
    sys.excepthook = exception_handler_hook
    logging.info("LOG START")
    log_sys_info()
