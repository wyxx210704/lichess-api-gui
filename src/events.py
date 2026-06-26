from PyQt6.QtWidgets import *
from typing import Callable

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

    try:
        func()
    except Exception as error:QMessageBox.critical(
        None,
        '错误',
        f'登录发生错误：{error}',
    )

    progress_bar.setRange(0,100)
    progress_bar.setValue(100)

def get_user_name(parent:QWidget|None=None,title:str='输入用户'):
    text, ok = QInputDialog.getText(
        parent,
        title,          # 对话框标题
        "请输入用户名称：",   # 提示标签文本
    )

    if ok and text:
        return text
    else:
        return 'default'
    
def get_item(parent:QWidget|None=None,title:str='选择一个选项',items:list[str]=['默认选项']):
    text, ok = QInputDialog.getItem(
        parent,
        title,
        '请选择一个项目',
        items,
    )

    if ok and text:
        return text
    else:
        return 'default'

def get_int(parent:QWidget|None=None,title:str='输入一个数字'):
    text, ok = QInputDialog.getInt(
        parent,
        title,          # 对话框标题
        "请输入数字：",   # 提示标签文本
    )

    if ok and text:
        return text
    else:
        return 5