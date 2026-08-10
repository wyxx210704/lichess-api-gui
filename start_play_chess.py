from berserk import Client#用于类型注解
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import *
from traceback import print_exc
import os.path

from src.bot import BotMain
from src.board import BoardMain
from src.business_logic import login

window_list = []
def choice_window(client:Client,is_bot:bool):#client参数以后才会用得到
    if is_bot:return BotMain()
    else:return BoardMain(client)

def turn_from_main(client:Client,is_bot:bool):
    window = choice_window(client,is_bot)
    window_list.append(window)
    window.destroyed.connect(lambda:window_list.remove(window))
    window.show()

def main():
    app = QApplication([])
    translator = QTranslator()
    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qm_file_path = os.path.join(qt_translations_path, "qt_zh_CN.qm")
    
    if translator.load(qm_file_path):app.installTranslator(translator)
    window = choice_window(*login())
    window.show()

    try:app.exec()
    except Exception:
        print('运行时发生暂未处理到的错误')
        print_exc()
        print('正在尝试重启')
        main()

if __name__ == '__main__':
    main()