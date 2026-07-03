from PyQt6.QtWidgets import *
from berserk import *
from typing import *
import sys

from tools import *
sub_window_list = []
PERFS = [
    #标准
    "ultraBullet", 
    "bullet", 
    "blitz", 
    "rapid", 
    "classical", 
    "correspondence",
    #变体
    "chess960",
    "kingOfTheHill",
    "threeCheck",
    "antichess",
    "atomic",
    "horde",
    "racingKings",
    "crazyhouse",
]

def login():
    login_dialog = LoginWizard()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        return login_dialog.get_info()
    else:exit()

def run_function(progress_bar:QProgressBar,func:Callable):
    progress_bar.setValue(0)
    progress_bar.setRange(0,0)

    try:func()
    except Exception as error:show_error_dialog(*get_error_details(error),'调用API报错')

    progress_bar.setRange(0,100)
    progress_bar.setValue(100)

def start_game_viewer(generator:Generator):
    try:
        window = GameViewer(generator)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动对局查看器报错')

def start_puzzle_viewer(client:Client,parent:QWidget|None=None):
    mode = get_item(parent,'选择获取谜题的模式',[
        '特定编号',
        '每日谜题',
        '根据难度选择',
    ])

    if mode == '特定编号':puzzle_deta = client.puzzles.get(get_id(parent,True))
    elif mode == '每日谜题':puzzle_deta = client.puzzles.get_daily()
    elif mode == '根据难度选择':puzzle_deta = client.puzzles.get_next(None,get_item(parent,'选择难度',[
        "easiest", 
        "easier", 
        "normal", 
        "harder", 
        "hardest"
    ]))
        
    try:
        window = ChessPuzzleViewer(puzzle_deta)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动谜题查看器报错',parent)

def get_error_details(e: Exception) -> Tuple[str, int, str, str]:
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

def get_user_name(parent:QWidget|None=None,title:str='输入用户'):
    text, ok = QInputDialog.getText(
        parent,
        title,          # 对话框标题
        "请输入用户名称：",   # 提示标签文本
    )

    if ok and text:return text
    else:return 'default'
    
def get_id(parent:QWidget|None=None,puzzles:bool=False,title:str='输入编号'):
    # puzzles的意思是获取的是谜题编号还是对局编号
    text, ok = QInputDialog.getText(
        parent,
        title,          # 对话框标题
        f"请输入{'谜题' if puzzles else '对局'}编号：",   # 提示标签文本
    )

    if ok and text:
        return text
    else:
        if puzzles:return 'OCfB9'#默认值就随便写一个谜题编号
        else:return 'OYzGF6fS'#默认值随便写一个已经结束的对局编号
    
def get_item(parent:QWidget|None=None,title:str='选择一个选项',items:list[str]=PERFS):
    text, ok = QInputDialog.getItem(
        parent,
        title,
        '请选择一个项目',
        items,
    )

    if ok and text:return text
    else:return items[0]

def get_int(parent:QWidget|None=None,title:str='输入一个数字',min_:int=1,max_:int=100000):
    text, ok = QInputDialog.getInt(
        parent,
        title,          # 对话框标题
        "请输入数字：",   # 提示标签文本
        1,
        min_,
        max_,
    )

    if ok and text:return text
    else:return 1
    
def get_bool(parent:QWidget|None=None,text:str='是否执行操作'):
    button = QMessageBox.question(
        parent,
        '是否执行操作',
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )

    if button == QMessageBox.StandardButton.Yes:return True
    else:return False

def get_screening(parent:QWidget|None=None,filtering_content:str='筛选内容'):
    button = QMessageBox.question(
        parent,
        '筛选（点中间按钮则不筛选）',
        '是否包含'+filtering_content,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ignore,
    )

    if button == QMessageBox.StandardButton.Yes:return True
    elif button == QMessageBox.StandardButton.No:return False
    else:return None

def get_pgn(parent:QWidget|None=None,title:str='输入PGN'):
    text, ok = QInputDialog.getMultiLineText(
        parent,
        title,          # 对话框标题
        "请输入或者粘贴pgn：",   # 提示标签文本
    )

    if ok and text:return text
    else:return '*'