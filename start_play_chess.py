from berserk import Client#用于类型注解
from PyQt6.QtCore import *
from traceback import print_exc
from typing import Callable
from sys import argv
import os

from src.bot import BotMain
from src.board import BoardMain
from src.business_logic import login
from src.app_basic import *
from src.main_classes import QtMessageFilter

window_list = []
_filter_instance = None

def init_filter(func:Callable):
    def wrapper(*args,**kw):
        global _filter_instance
        # 如果过滤器还未创建或已失效，重新创建
        if _filter_instance is None:
            _filter_instance = QtMessageFilter([
                'QThread: Destroyed while thread',
                'libpng warning: iCCP: known incorrect sRGB profile',
            ])
            _filter_instance.install()
        func(*args,**kw)
    return wrapper

def choice_window(client:Client,is_bot:bool):#client参数以后才会用得到
    if is_bot:return BotMain(client)
    else:return BoardMain(client)

#@init_filter
def turn_from_main(client:Client,is_bot:bool):
    window = choice_window(client,is_bot)
    apply_style(window)
    window_list.append(window)
    window.destroyed.connect(lambda:window_list.remove(window))
    window.show()

#@init_filter
def main():
    app = QApplication(argv)
    translator = QTranslator()
    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qm_file_path = os.path.join(qt_translations_path, "qt_zh_CN.qm")
    
    if translator.load(qm_file_path):app.installTranslator(translator)
    window = choice_window(*login())
    apply_style(window)
    window.show()
    
    try:app.exec()
    except Exception:
        print('运行时发生暂未处理到的错误')
        print_exc()
        print('正在尝试重启')
        main()

if __name__ == '__main__':
    main()