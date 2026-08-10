from PyQt6.QtWidgets import *
from datetime import timedelta

from ..widgets import *

class InfoButton(QPushButton):
    def __init__(self, info:dict, parent:QWidget|None = None):
        super().__init__('查看详情', parent)
        self.parent_ = parent
        self.info = info
        self.clicked.connect(self.create_dialog)

    def create_dialog(self):
        dialog = QDialog(self.parent_)
        layout = QVBoxLayout(dialog)
        dialog.setWindowTitle('详细信息')

        info_widget = JsonTreeWidget(dialog)
        info_widget.set_dict(self.info)
        layout.addWidget(info_widget)

        button = QPushButton('完成',dialog)
        button.clicked.connect(dialog.accept)
        layout.addWidget(button)

        dialog.exec()