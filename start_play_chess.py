from berserk import Client#用于类型注解
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import *
from traceback import print_exc
from typing import Callable
import os.path
import sys

from src.bot import BotMain
from src.board import BoardMain
from src.business_logic import login

class QtMessageFilter:
    def __init__(self, filter_patterns):
        """
        filter_patterns: 要过滤的字符串列表
        """
        self.filter_patterns = filter_patterns
        self.original_handler = None
    
    def handler(self, msg_type, context, message):
        """
        自定义消息处理器
        msg_type: QtMsgType 枚举值
        context: QMessageLogContext 对象
        message: 消息字符串
        """
        # 检查是否包含要过滤的字符串
        if any(pattern in message for pattern in self.filter_patterns):
            return  # 直接忽略，不输出
        
        # 对于不需要过滤的消息，可以重定向到原始处理器或直接输出
        if self.original_handler:
            self.original_handler(msg_type, context, message)
        else:
            # 默认处理方式
            msg_type_map = {
                QtMsgType.QtDebugMsg: "Debug",
                QtMsgType.QtInfoMsg: "Info",
                QtMsgType.QtWarningMsg: "Warning",
                QtMsgType.QtCriticalMsg: "Critical",
                QtMsgType.QtFatalMsg: "Fatal",
            }
            print(f"[{msg_type_map.get(msg_type, 'Unknown')}] {message}", file=sys.stderr)
    
    def install(self):
        """安装过滤器"""
        # 保存原始处理器
        self.original_handler = qInstallMessageHandler(None)
        # 安装自定义处理器
        qInstallMessageHandler(self.handler)
    
    def uninstall(self):
        """卸载过滤器，恢复原始处理器"""
        qInstallMessageHandler(self.original_handler)

window_list = []
_filter_instance = None

def init_filter(func:Callable):
    def wrapper():
        global _filter_instance
        # 如果过滤器还未创建或已失效，重新创建
        if _filter_instance is None:
            _filter_instance = QtMessageFilter([
                'QThread: Destroyed while thread',
                'libpng warning: iCCP: known incorrect sRGB profile',
            ])
            _filter_instance.install()
        func()
    return wrapper

def choice_window(client:Client,is_bot:bool):#client参数以后才会用得到
    if is_bot:return BotMain(client)
    else:return BoardMain(client)

@init_filter
def turn_from_main(client:Client,is_bot:bool):
    window = choice_window(client,is_bot)
    window_list.append(window)
    window.destroyed.connect(lambda:window_list.remove(window))
    window.show()

@init_filter
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