from berserk import *
import sys
from typing import Callable
from PyQt6.QtWidgets import *
from json import load

from tools import LoginWizard,ErrorMessageBox
from config_format import ConfigFormat

def load_config_with_format() -> ConfigFormat:
    return load(open(
        '../configuration_and_resources/config.json',
        'r',
        encoding='utf-8',
        errors='ignore',
    ))

def login_with_wizard():
    login_dialog = LoginWizard()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:return login_dialog.get_info()
    else:exit()

def login():
    try:auto_login = load_config_with_format()['auto_login']['enable']
    except Exception as error:
        auto_login = False
        show_error_dialog(*get_error_details(error),'自动登录状态加载失败')

    if auto_login:
        try:
            client = Client(TokenSession(load_config_with_format()['auto_login']['token']))
            user_info = client.account.get()
        except Exception as error:
            show_error_dialog(*get_error_details(error),'自动登录失败')
            return login_with_wizard()
        else:
            if ('title' in user_info) and (user_info['title'] == 'BOT'):is_bot = True
            else:is_bot = False
            return client,is_bot
    else:return login_with_wizard()

def run_function(progress_bar:QProgressBar,func:Callable):
    progress_bar.setValue(0)
    progress_bar.setRange(0,0)

    try:func()
    except Exception as error:show_error_dialog(*get_error_details(error),'调用API报错')

    progress_bar.setRange(0,100)
    progress_bar.setValue(100)

def get_error_details(e: Exception) -> tuple[str, int, str, str]:
    """
    从异常对象中提取完整的报错信息
    
    参数:
        e: except捕获的异常对象
        
    返回:
        (文件名, 行号, 错误类型, 错误提示信息)
    """
    # 1. 获取错误类型（如 ZeroDivisionError）
    error_type = type(e).__name__
    
    # 2. 获取错误提示信息（如 "division by zero"）
    error_msg = str(e)
    
    # 3. 获取当前栈帧信息（文件路径 + 行号）
    exc_type, exc_value, exc_tb = sys.exc_info()
    
    if exc_tb is not None:
        # 获取报错发生的文件路径
        filename = exc_tb.tb_frame.f_code.co_filename
        # 获取报错发生的行号
        line_number = exc_tb.tb_lineno
    else:
        # 极端情况：没有栈帧信息时给默认值
        filename = "未知文件"
        line_number = -1
    
    return filename, line_number, error_type, error_msg

def show_error_dialog(filename:str, line_number:int, error_type:str, error_message:str, title:str,parent:QWidget|None=None):
    """
    显示错误消息框的便捷函数
    
    Args:
        filename: 发生错误的文件名
        line_number: 错误发生的行号
        error_type: 错误类型
        error_message: 错误详细信息
        parent: 父窗口
    """
    dialog = ErrorMessageBox(filename, line_number, error_type, error_message, title,parent)
    dialog.exec()