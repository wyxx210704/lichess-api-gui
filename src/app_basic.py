from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from winmica import EnableMica, BackdropType, is_mica_supported
import os

from .costants import GENERAL_PATH

def get_app():
    app = QApplication([])
    translator = QTranslator()
    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qm_file_path = os.path.join(qt_translations_path, "qt_zh_CN.qm")
    
    if translator.load(qm_file_path):app.installTranslator(translator)
    return app

def apply_style(window:QMainWindow):
    #win11专属待遇，不是win11的就好好用着默认样式
    if is_mica_supported():
        window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        EnableMica(int(window.winId()),BackdropType.MICA)
        window.setStyleSheet(open(GENERAL_PATH + 'style.qss','r',encoding='utf-8',errors='ignore').read())