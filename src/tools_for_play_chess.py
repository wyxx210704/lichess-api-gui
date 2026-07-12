from PyQt6.QtWidgets import *

class ChallengeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_ = QVBoxLayout(self)
        self.setWindowTitle('发出去的挑战')

        self.tree_widget = QTreeWidget(self)
        self.layout_.addWidget(self.tree_widget)
        self.tree_widget.setColumnCount(14)
        self.tree_widget.setHeaderLabels([
            '编号',
            '链接',
            '状态',
            '挑战者',
            '被挑战者',
            '变体',
            '是否排位',
            '速度',
            '时间控制',
            '颜色',
            '最终颜色',
            '种类',
            '进来还是出去',
            '初始局面',
        ])

        default_item = QTreeWidgetItem(
            self.tree_widget,
            [
                '占位、',
                '测试专用',
                '几个版本之后',
                '才会更新功能',
                '并且正式启用',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
                '/',
            ]
        )

        self.layout_for_buttons = QHBoxLayout()
        self.layout_.addLayout(self.layout_for_buttons)

        self.create_button = QPushButton('创建',self)
        self.create_button.setEnabled(False)#暂未启用
        self.layout_for_buttons.addWidget(self.create_button)

        self.cancel_button = QPushButton('取消',self)
        self.cancel_button.setEnabled(False)#暂未启用
        self.layout_for_buttons.addWidget(self.cancel_button)