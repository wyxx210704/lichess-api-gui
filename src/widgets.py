from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from json import *
from datetime import *
from berserk.types.common import *

from .translates import *
from .config_format import FunctionSettings
from .costants import CONFIG
from .chess_general_logic import *

class JsonTreeWidget(QTreeWidget):
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["索引", "数据"])
        self.setColumnWidth(0,250)

        self.value = None
        self.config:FunctionSettings = load(open(
            CONFIG,
            'r',
            encoding='utf-8',
            errors='ignore',
        ))['function_settings']
    
    def set_integer(self, value:int):
        """显示整数"""
        self.clear()
        self.value = value

        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, str(value))
        self.expandAll()
    
    def set_float(self, value:float):
        """显示小数"""
        self.clear()
        self.value = value

        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, str(value))
        self.expandAll()
    
    def set_string(self, value:str):
        """显示字符串"""
        self.clear()
        self.value = value
        if not isinstance(value, str):
            raise TypeError("参数必须是字符串类型")
        
        # 检查是否包含换行符
        if '\n' in value:
            # 多行字符串：按行分割
            lines = value.split('\n')
            for i, line in enumerate(lines, 1):
                item = QTreeWidgetItem(self)
                item.setText(0, f"第{i}行")
                item.setText(1, line)
        else:
            # 单行字符串：保持原样
            item = QTreeWidgetItem(self)
            item.setText(0, "返回结果")
            item.setText(1, value)
        
        self.expandAll()
    
    def set_bool(self, value:bool):
        """显示布尔值"""
        self.clear()
        self.value = value

        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, "True" if value else "False")
        self.expandAll()
    
    def set_list(self, value:list):
        """显示列表"""
        self.clear()
        self.value = value

        if not isinstance(value, list):
            raise TypeError("参数必须是列表类型")
        self._add_list_items(self, value)
        self.expandAll()
    
    def set_dict(self, value:dict):
        """显示字典"""
        self.clear()
        self.value = value

        if not isinstance(value, dict):
            raise TypeError("参数必须是字典类型")
        self._add_dict_items(self, value)
        self.expandAll()
    
    def _add_list_items(self, parent, data:list):
        """递归添加列表项"""
        for index, item_data in enumerate(data):
            item = QTreeWidgetItem(parent)
            item.setText(0, str(index))
            
            if isinstance(item_data, list):
                # 列表嵌套
                item.setText(1, "[]")
                self._add_list_items(item, item_data)
            elif isinstance(item_data, dict):
                # 字典嵌套
                item.setText(1, "{}")
                self._add_dict_items(item, item_data)
            elif isinstance(item_data, bool):
                item.setText(1, "True" if item_data else "False")
            elif item_data is None:
                item.setText(1, "None")
            elif isinstance(item_data, str):
                if '\n' in item_data:
                    # 多行字符串：展开为子项
                    item.setText(1, f"({item_data.count(chr(10)) + 1}行)")
                    lines = item_data.split('\n')
                    for i, line in enumerate(lines, 1):
                        line_item = QTreeWidgetItem(item)
                        line_item.setText(0, f"第{i}行")
                        line_item.setText(1, line)
                else:
                    if self.config["translate"]:
                        item.setText(1,get_value_translate(item_data))
                    else:
                        item.setText(1,item_data)
            else:
                item.setText(1, str(item_data))

    def _add_dict_items(self, parent, data:dict):
        """递归添加字典项"""
        for key, value in data.items():
            item = QTreeWidgetItem(parent)

            if self.config["translate"]:
                item.setText(0, get_key_translate(str(key)))
            else:
                item.setText(0,str(key))
            
            if isinstance(value, list):
                item.setText(1, "[]")
                self._add_list_items(item, value)
            elif isinstance(value, dict):
                item.setText(1, "{}")
                self._add_dict_items(item, value)
            elif isinstance(value, bool):
                item.setText(1, "True" if value else "False")
            elif value is None:
                item.setText(1, "null")
            elif isinstance(value, str):
                if '\n' in value:
                    # 多行字符串：展开为子项
                    item.setText(1, f"({value.count(chr(10)) + 1}行)")
                    lines = value.split('\n')
                    for i, line in enumerate(lines, 1):
                        line_item = QTreeWidgetItem(item)
                        line_item.setText(0, f"第{i}行")
                        line_item.setText(1, line)
                else:
                    if self.config["translate"]:
                        item.setText(1,get_value_translate(value))
                    else:
                        item.setText(1,value)
            else:
                item.setText(1, str(value))

    def contextMenuEvent(self, event:QContextMenuEvent):
        item = self.itemAt(event.pos())
        menu = QMenu()

        if item != None:
            copy_action = QAction('复制已选中的项')
            copy_action.triggered.connect(lambda:QApplication.clipboard().setText(item.text(1)))
            menu.addAction(copy_action)

        copy_all_action = QAction('复制全部内容')
        copy_all_action.triggered.connect(self.copy_all)
        menu.addAction(copy_all_action)

        menu.exec(event.globalPos())

    def copy_all(self):
        class DateTimeEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()  # 转换为 ISO 8601 字符串
                return super().default(obj)

        if self.config["copy_indent"]["enable"]:
            QApplication.clipboard().setText(dumps(
                self.value,
                ensure_ascii=False,
                indent=self.config["copy_indent"]["indent"],
                cls=DateTimeEncoder,
            ))
        else:
            QApplication.clipboard().setText(dumps(
                self.value,
                ensure_ascii=False,
                cls=DateTimeEncoder,
            ))

class NoStretchingSvgWidget(QSvgWidget):
    wheel_scrolled = pyqtSignal(bool)

    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)

    def load(self, contents:bytes):
        super().load(contents)
        self.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event:QWheelEvent):
        self.wheel_scrolled.emit(event.angleDelta().y() > 0)
        event.accept()

class StringDisplay(QLineEdit):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.setReadOnly(True)

class IntDisplay(QSpinBox):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximum(100000)

class BoolDisplay(QCheckBox):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.setEnabled(False)
        self.toggled.connect(self.update_state)
        self.setText('否')

    def update_state(self):
        self.setText('是' if self.isChecked() else '否')

class ControllableWizardPage(QWizardPage):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.state = True

    def change_state(self,state:bool):
        self.state = state
        self.completeChanged.emit()

    def isComplete(self):
        return self.state

class ChessBoardWidget(QSplitter):
    def __init__(self, init_moves:list[str]=[],parent:QWidget|None=None,variant:VariantKey='standard',
                 info_widget:QWidget|None=None,start_fen:str=chess.STARTING_FEN):
        super().__init__(Qt.Orientation.Horizontal,parent)
        self.moves = ['起始局面'] + init_moves
        self.orientation_ = chess.WHITE
        self.variant = variant
        self.start_fen = start_fen
        
        self.svg_widget = NoStretchingSvgWidget(self)
        self.addWidget(self.svg_widget)

        self.widget_on_right = QWidget(self)
        self.addWidget(self.widget_on_right)
        self.layout_on_right = QVBoxLayout(self.widget_on_right)

        if info_widget != None:
            self.layout_on_right.addWidget(info_widget)

        self.list_widget = QListWidget(self.widget_on_right)
        self.layout_on_right.addWidget(self.list_widget)
        self.list_widget.addItem('起始局面')
        self.list_widget.currentRowChanged.connect(self.turn_move)

        self.button_layout = QHBoxLayout()
        self.layout_on_right.addLayout(self.button_layout)

        self.begin_button = QPushButton(QIcon.fromTheme('media-seek-backward'),'到起始',self.widget_on_right)
        self.begin_button.clicked.connect(lambda:self.list_widget.setCurrentRow(0))
        self.button_layout.addWidget(self.begin_button)

        self.back_button = QPushButton(QIcon.fromTheme('media-skip-backward'),'上一步',self.widget_on_right)
        self.back_button.clicked.connect(lambda:self.list_widget.setCurrentRow(self.list_widget.currentRow() - 1))
        self.button_layout.addWidget(self.back_button)

        self.flip_button = QPushButton(QIcon.fromTheme('emblem-synchronized'),'翻转棋盘',self.widget_on_right)
        self.flip_button.clicked.connect(self.flip_the_board)
        self.button_layout.addWidget(self.flip_button)

        self.next_button = QPushButton(QIcon.fromTheme('media-skip-forward'),'下一步',self.widget_on_right)
        self.next_button.clicked.connect(lambda:self.list_widget.setCurrentRow(self.list_widget.currentRow() + 1))
        self.button_layout.addWidget(self.next_button)

        self.last_button = QPushButton(QIcon.fromTheme('media-seek-forward'),'到最后',self.widget_on_right)
        self.last_button.clicked.connect(lambda:self.list_widget.setCurrentRow(self.list_widget.count() - 1))
        self.button_layout.addWidget(self.last_button)

        self.svg_widget.wheel_scrolled.connect(self.receive_wheel)
        self.board = get_board(variant,start_fen)
        self.index = 0

        for uci in self.moves[1:]:
            move = self.board.parse_uci(uci)
            san =  self.board.san(move)
            self.board.push(move)
            number = f'{int((self.index / 2) + 1)}.' if self.index % 2 == 0 else ''
            self.list_widget.addItem(number + san)
            self.index += 1

        self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def turn_move(self,index:int):
        self.svg_widget.load(generate_svg_from_uci(
            self.moves[1:index+1],
            self.orientation_,
            self.variant,
            self.start_fen,
        ))

        is_not_first = not (index == 0)
        self.begin_button.setEnabled(is_not_first)
        self.back_button.setEnabled(is_not_first)

        is_not_last = not (index == (self.list_widget.count() - 1))
        self.next_button.setEnabled(is_not_last)
        self.last_button.setEnabled(is_not_last)

    def append_move(self,uci_move:str):
        self.moves.append(uci_move)
        #先保存旧的最后的数值
        old_last = self.list_widget.count() - 1
        
        move = self.board.parse_uci(uci_move)
        san =  self.board.san(move)
        self.board.push(move)
        number = f'{int(self.index / 2 + 1)}.' if self.index % 2 == 0 else ''
        self.list_widget.addItem(number + san)
        self.index += 1

        #判断如果在旧的最后那么就设置为新的最后
        if self.list_widget.currentRow() == old_last:
            self.list_widget.setCurrentRow(old_last + 1)

    def receive_wheel(self,state:bool):
        if state:self.back_button.click()
        else:self.next_button.click()

    def flip_the_board(self):
        # chess.Color其实就是布尔值
        # 白方是True
        # 黑方是False
        self.orientation_ = not self.orientation_
        self.svg_widget.load(generate_svg_from_uci(
            self.moves[1:self.list_widget.currentRow()+1],
            self.orientation_,
            self.variant,
            self.start_fen,
        ))

class TimedeltaDisplayWidget(QWidget):
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QHBoxLayout(self)

        self.day = IntDisplay(self)
        self.hour = IntDisplay(self)
        self.minute = IntDisplay(self)
        self.second = QDoubleSpinBox(self)
        self.second.setReadOnly(True)
        self.second.setDecimals(6)

        self.layout_.addWidget(self.day)
        self.layout_.addWidget(QLabel('天'))
        self.layout_.addWidget(self.hour)
        self.layout_.addWidget(QLabel('小时'))
        self.layout_.addWidget(self.minute)
        self.layout_.addWidget(QLabel('分钟'))
        self.layout_.addWidget(self.second)
        self.layout_.addWidget(QLabel('秒'))

    def set_time(self,time:timedelta):
        total = time.total_seconds()

        if total < 60:
            self.day.setValue(0)
            self.hour.setValue(0)
            self.minute.setValue(0)
            self.second.setValue(total)
        elif (total >= 60) and (total < 3600):
            self.day.setValue(0)
            self.hour.setValue(0)
            self.minute.setValue(int(total // 60))
            self.second.setValue(total % 60)
        elif (total >= 3600) and (total < 86400):
            self.day.setValue(0)
            self.hour.setValue(int(total // 3600))
            self.minute.setValue(int((total % 3600) // 60))
            self.second.setValue(total % 60)
        elif total >= 86400:
            self.day.setValue(int(total // 86400))
            self.hour.setValue(int((total % 86400) // 3600))
            self.minute.setValue(int(((total % 86400) % 3600) // 60))
            self.second.setValue(total % 60)

        if self.day.value() == 0:
            self.day.hide()
        else:self.day.show()

        if self.hour.value() == 0:
            self.hour.hide()
        else:self.hour.show()

        if self.minute.value() == 0:
            self.minute.hide()
        else:self.minute.show()

        if self.second.value() == 0:
            self.second.hide()
        else:self.second.show()

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

class GameInfoWidget(QScrollArea):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        self.scroll_area_widget = QWidget(self)
        self.setWidget(self.scroll_area_widget)
        self.layout_in_scroll_area = QVBoxLayout(self.scroll_area_widget)
    
        self.create_basic_info()
        self.create_time_display()
        self.create_variant()
        self.create_player_info()
    
    def create_basic_info(self):
        self.basic_info = QGroupBox('基本信息',self.scroll_area_widget)
        self.layout_in_scroll_area.addWidget(self.basic_info)
        self.layout_in_basic_info = QFormLayout(self.basic_info)
    
        self.id = StringDisplay(self.basic_info)
        self.speed = StringDisplay(self.basic_info)
        self.is_rated = BoolDisplay(self.basic_info)
        self.perf = StringDisplay(self.basic_info)
        self.start_fen = StringDisplay(self.basic_info)
    
        self.create_time = QDateTimeEdit(self.basic_info)
        self.create_time.setReadOnly(True)
    
        self.layout_in_basic_info.addRow('编号',self.id)
        self.layout_in_basic_info.addRow('速度',self.speed)
        self.layout_in_basic_info.addRow('是否排位',self.is_rated)
        self.layout_in_basic_info.addRow('种类',self.perf)
        self.layout_in_basic_info.addRow('创建时间',self.create_time)
        self.layout_in_basic_info.addRow('初始局面',self.start_fen)
    
    def create_time_display(self):
        self.time_display = QGroupBox('时间',self.scroll_area_widget)
        self.layout_in_scroll_area.addWidget(self.time_display)
        self.layout_in_time_display = QFormLayout(self.time_display)
    
        self.basic_time = TimedeltaDisplayWidget(self.time_display)
        self.increment = IntDisplay(self.time_display)
        self.layout_in_time_display.addRow('基本时间',self.basic_time)
        self.layout_in_time_display.addRow('每步增加时间（秒）',self.increment)
    
    def create_variant(self):
        self.variant = QGroupBox('变体',self.scroll_area_widget)
        self.layout_in_scroll_area.addWidget(self.variant)
        self.layout_in_variant = QFormLayout(self.variant)
    
        self.variant_key = StringDisplay(self.variant)
        self.variant_name = StringDisplay(self.variant)
        self.variant_short = StringDisplay(self.variant)
    
        self.layout_in_variant.addRow('键',self.variant_key)
        self.layout_in_variant.addRow('名称',self.variant_name)
        self.layout_in_variant.addRow('短名称',self.variant_short)
    
    def create_player_info(self):
        self.white_player = PlayerInfo(True,self.scroll_area_widget)
        self.black_player = PlayerInfo(False,self.scroll_area_widget)
        self.layout_in_scroll_area.addWidget(self.white_player)
        self.layout_in_scroll_area.addWidget(self.black_player)

    def load_info(self,id:str,speed:Speed,is_rated:bool,perf:PerfType,create_time:datetime,
                  start_fen:str,basic_time:timedelta,increment:int,variant_key:VariantKey,
                  variant_name:str,variant_short:str,white:dict,black:dict):
        self.id.setText(id)
        self.speed.setText(speed)
        self.is_rated.setChecked(is_rated)
        self.perf.setText(perf)
        self.create_time.setDateTime(create_time)
        self.start_fen.setText(start_fen)
        
        self.basic_time.set_time(basic_time)
        self.increment.setValue(increment)
        
        self.variant_key.setText(variant_key)
        self.variant_name.setText(variant_name)
        self.variant_short.setText(variant_short)
        
        if 'user' in white:
            #这种情况出现在tools.GameViewer
            'game_viewer_example'
            #示例数据太长，请跳转到game_viewer_example.py
            #如果使用vscode，可以直接ctrl+左键以上字符串就能直接跳转

            self.white_player.set_value({
                'id':white['user']['id'],
                'name':white['user']['name'],
                'title':(white['user']['title']
                if 'title' in white['user'] else None),
                'rating':white['rating'],

                'provisional':(white['provisional']
                if ('provisional' in white) and
                (white['provisional'] == True) 
                else False)
            })
        else:self.white_player.set_value(white)

        if 'user' in black:
            #这种情况出现在tools.GameViewer
            'game_viewer_example'
            #示例数据太长，请跳转到game_viewer_example.py
            #如果使用vscode，可以直接ctrl+左键以上字符串就能直接跳转
        
            self.black_player.set_value({
                'id':black['user']['id'],
                'name':black['user']['name'],
                'title':(black['user']['title']
                if 'title' in black['user'] else None),
                'rating':black['rating'],
        
                'provisional':(black['provisional']
                if ('provisional' in black) and
                (black['provisional'] == True) 
                else False)
            })
        else:self.black_player.set_value(black)