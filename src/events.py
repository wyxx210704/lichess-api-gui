from PyQt6.QtWidgets import *
from typing import *

from widgets import GameViewer
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

def run_function(progress_bar:QProgressBar,func:Callable):
    progress_bar.setValue(0)
    progress_bar.setRange(0,0)

    try:func()
    except Exception as error:QMessageBox.critical(
        None,
        '错误',
        f'运行发生错误：{error}',
    )

    progress_bar.setRange(0,100)
    progress_bar.setValue(100)

def start_game_viewer(generator:Generator):
    window = GameViewer(generator)
    sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
    window.destroyed.connect(lambda:sub_window_list.remove(window))
    window.show()

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