from PyQt6.QtWidgets import *

class BoardMain(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget(self)
        self.setCentralWidget(widget)
        QVBoxLayout(widget).addWidget(QLabel('功能将在下一版本更新，敬请期待'))