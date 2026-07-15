from PyQt6.QtWidgets import *
from datetime import timedelta

from board_tools import InfoDialog
from widgets import *

class TimedeltaDisplayWidget(QWidget):
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QHBoxLayout(self)

        self.minute = IntDisplay(self)
        self.second = QDoubleSpinBox(self)
        self.second.setReadOnly(True)
        self.second.setDecimals(6)

        self.layout_.addWidget(self.minute)
        self.layout_.addWidget(QLabel('分钟'))
        self.layout_.addWidget(self.second)
        self.layout_.addWidget(QLabel('秒'))

    def set_time(self,time:timedelta):
        total = time.total_seconds()
        self.minute.setValue(int(total // 60))
        self.second.setValue(total % 60)

class PlayerInfo(QGroupBox):
    def __init__(self, white:bool,parent:QWidget|None=None):
        super().__init__(f'{'白' if white else '黑'}方',parent)
        self.layout_ = QFormLayout(self)
        
        self.id = StringDisplay(self)
        self.name = StringDisplay(self)
        self.title_ = StringDisplay(self)
        self.rating = IntDisplay(self)
        self.is_provisional = BoolDisplay(self)

        self.layout_.addRow('编号',self.id)
        self.layout_.addRow('名称',self.name)
        self.layout_.addRow('头衔',self.title_)
        self.layout_.addRow('等级分',self.rating)
        self.layout_.addRow('是否为不确定等级分',self.is_provisional)

    def set_value(self,value:dict):
        # 这里由于有判断逻辑，所以请大家使用下方的example函数进行查看，证明为什么要这样子设计

        if value:#用来判断字典是否是空的
            if 'aiLevel' in value:
                self.id.setText('无')
                self.name.setText('【人机对弈】里面的ai，AI等级将显示在下方的等级分')
                self.title_.setText('无')
                self.rating.setValue(value['aiLevel'])
            else:#是账号
                self.id.setText(value['id'])
                self.name.setText(value['name'])
                self.rating.setValue(value['rating'])

                if value['title'] == None:#如果没有头衔
                    self.title_.setText('无')
                else:#有头衔
                    self.title_.setText(value['title'])

                if ('provisional' in value) and (value['provisional'] == True):
                    self.is_provisional.setChecked(True)
                else:self.is_provisional.setChecked(False)
        else:#字典是空的那么就表示是匿名
            self.id.setText('无')
            self.name.setText('匿名')
            self.title_.setText('无')
            self.rating.setValue(0)

    def example(self):
        #有账号的玩家（等级分已确定）
        #数据来源：该用户的慢棋等级分
        #############################
        {                           #
            'id': 'wyxx210704',     #
            'name': 'wyxx210704',   #
            'title': None,          #
            'rating': 1512          #
        }                           #
        #############################

        #有账号的玩家（等级分不确定）
        #数据来源：该用户的原子棋等级分
        #############################
        {                           #
            'id': 'wyxx210704',     #
            'name': 'wyxx210704',   #
            'title': None,          #
            'rating': 1500,         #
            'provisional': True     #
        }                           #
        #############################

        {}#未登录
        {'aiLevel': 1}#首页【人机对弈】里面的内置引擎（不是bot账号）

class InfoButton(QPushButton):
    def __init__(self, info:dict, parent:QWidget|None = None):
        super().__init__('查看详情', parent)
        self.clicked.connect(lambda:InfoDialog(info,parent).exec())