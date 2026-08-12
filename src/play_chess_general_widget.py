from PyQt6.QtWidgets import *
from typing import Callable

from .widgets import *

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

class ChatAndRecordWidget(QWidget):
    def __init__(self, send_message:Callable,parent:QWidget|None = None):
        super().__init__(parent)
        self.send_message = send_message
        self.vertical_layout = QVBoxLayout(self)
        
        self.create_chat_widget()
        self.create_send_msg_widget()
        self.create_move_record_widget()
        
    def create_chat_widget(self):
        self.vertical_layout.addWidget(QLabel('聊天对话'))
        self.chat_tree_widget = QTreeWidget(self)
        self.vertical_layout.addWidget(self.chat_tree_widget)
        
        self.chat_tree_widget.setColumnCount(3)
        self.chat_tree_widget.setHeaderLabels([
            '房间',
            '用户',
            '消息内容',
        ])
        
    def create_send_msg_widget(self):
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout)
        
        self.send_button = QPushButton('发送',self)
        self.send_button.clicked.connect(self.send_message)
        
        self.msg_input = QLineEdit(self)
        self.msg_input.returnPressed.connect(self.send_button.click)
        self.send_to_observation_area = QCheckBox('发送到观战区',self)
        
        self.horizontal_layout.addWidget(self.msg_input)
        self.horizontal_layout.addWidget(self.send_to_observation_area)
        self.horizontal_layout.addWidget(self.send_button)
        
    def create_move_record_widget(self):
        self.vertical_layout.addWidget(QLabel('走棋记录'))
        self.move_record_widget = QListWidget(self)
        self.vertical_layout.addWidget(self.move_record_widget)

    def set_moves(self,moves_list:list[str]):
        self.move_record_widget.clear()
        self.move_record_widget.addItems(moves_list)

    def get_tree_widget(self):
        #添加一个item的时候要用到
        return self.chat_tree_widget

class CurrentClock(QGroupBox):
    def __init__(self, parent:QWidget|None = None):
        super().__init__('剩余时间', parent)
        self.layout_in = QFormLayout(self)

        self.white_clock = TimedeltaDisplayWidget(self)
        self.black_clock = TimedeltaDisplayWidget(self)
        self.layout_in.addRow('白方',self.white_clock)
        self.layout_in.addRow('黑方',self.black_clock)

    def set_time(self,white:timedelta,black:timedelta):
        self.white_clock.set_time(white)
        self.black_clock.set_time(black)

class GameTreeWidget(QTreeWidget):
    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent)

        self.setColumnCount(16)
        self.setHeaderLabels([
            '完整编号',
            '对局编号',
            'fen局面',
            '颜色',
            '上一步棋',
            '来源',
            '状态',
            '变体',
            '速度',
            '种类',
            '是否排位',
            '是否已走过棋',
            '对手',
            '是否到我走棋',
            '剩余时间（秒）',
            '等级分',
        ])

class ChallengeTreeWidget(QTreeWidget):
    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent)

        self.setColumnCount(14)
        self.setHeaderLabels([
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