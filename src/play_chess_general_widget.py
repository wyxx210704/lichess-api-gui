from PyQt6.QtWidgets import *
from typing import Callable

from .widgets import *

class InfoButton(QToolButton):
    def __init__(self, info:dict, parent:QWidget|None = None):
        super().__init__(parent)
        self.parent_ = parent
        self.info = info
        self.setText('查看详情')
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.menu_ = QMenu('详细信息',self)
        self.setMenu(self.menu_)
        self.action = QWidgetAction(self.menu_)
        self.tree = JsonTreeWidget()
        self.action.setDefaultWidget(self.tree)
        self.tree.setFixedSize(500,200)
        self.tree.set_dict(info)
        self.menu_.addAction(self.action)

class ChatAndRecordWidget(QWidget):
    def __init__(self, send_message:Callable[[str,bool],None],parent:QWidget|None = None):
        super().__init__(parent)
        self.send_message = self.send_message_wrapper(send_message)
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

        self.send_button = QToolButton(self)
        self.send_button.setText('发送')
        self.send_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.msg_input = QLineEdit(self)
        self.msg_input.returnPressed.connect(self.send_button.showMenu)
        
        self.horizontal_layout.addWidget(self.msg_input)
        self.horizontal_layout.addWidget(self.send_button)
        self.create_send_menu()

    def create_send_menu(self):
        self.send_menu = QMenu('发送',self.send_button)
        self.send_button.setMenu(self.send_menu)

        self.send_to_player = QAction('发送到玩家',self.send_menu)
        self.send_to_player.triggered.connect(lambda:self.send_message(self.msg_input.text(),False))
        self.send_menu.addAction(self.send_to_player)

        self.send_to_spectator = QAction('发送到观众',self.send_menu)
        self.send_to_spectator.triggered.connect(lambda:self.send_message(self.msg_input.text(),True))
        self.send_menu.addAction(self.send_to_spectator)

    def send_message_wrapper(self,send_message:Callable[[str,bool],None]):
        def wrapper(text:str,is_spectator:bool):
            send_message(text,is_spectator)
            self.msg_input.clear()
        return wrapper
        
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