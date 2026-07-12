from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from berserk import Client
import datetime

from tools import SettingsWindow
from tools_for_play_chess import ChallengeWindow
from board_widget import *

class BoardMain(QMainWindow):
    def __init__(self,client:Client):
        super().__init__()
        self.client = client
        self.mdi_sub_window_list = []
        self.client.board.make_move()
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)
        
        self.tool_bar = self.addToolBar('工具')
        self.status_bar = self.statusBar()

        self.setWindowTitle('人类专用下棋页面')
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

        self.mdi_area = QMdiArea(self.tab_widget)
        self.mdi_area.setBackground(QBrush())
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tab_widget.addTab(
            self.mdi_area,
            '工具',
        )

        self.splitter = QSplitter(
            Qt.Orientation.Horizontal,
            self.tab_widget,
        )

        self.tab_widget.addTab(
            self.splitter,
            '待处理',
        )

        self.page_challenge()
        self.page_game()
        self.add_action()
        self.add_sub_window()

    def add_action(self):
        self.challenge_action = QAction('发起挑战')
        self.challenge_action.triggered.connect(lambda:self.add_sub_window(False,ChallengeWindow()))
        self.tool_bar.addAction(self.challenge_action)

        self.settings_action = QAction('设置')
        self.settings_action.triggered.connect(lambda:self.add_sub_window(False,SettingsWindow(self.client)))
        self.tool_bar.addAction(self.settings_action)

    def add_sub_window(self,is_all:bool=True,window:QWidget|None=None):
        type_summary = [
            SettingsWindow(self.client),
            ChallengeWindow(),
        ]

        if is_all:
            for type_class in type_summary:
                self.mdi_area.addSubWindow(type_class)
        else:
            self.mdi_area.addSubWindow(window).show()

    def page_challenge(self):
        self.challenge_page = QWidget(self.splitter)
        self.splitter.addWidget(self.challenge_page)
        self.vertical_layout_in_challenge_page = QVBoxLayout(self.challenge_page)
        self.vertical_layout_in_challenge_page.addWidget(QLabel('收到的挑战列表（暂未启用）'))

        self.tree_widget_for_challenge = QTreeWidget(self.challenge_page)
        self.vertical_layout_in_challenge_page.addWidget(self.tree_widget_for_challenge)

        self.tree_widget_for_challenge.setColumnCount(14)
        self.tree_widget_for_challenge.setHeaderLabels([
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
            self.tree_widget_for_challenge,
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
            ]
        )
        
        self.horizontal_layout_in_challenge_page = QHBoxLayout()
        self.vertical_layout_in_challenge_page.addLayout(self.horizontal_layout_in_challenge_page)

        self.accept_button = QPushButton('接受',self.challenge_page)
        self.accept_button.setEnabled(False)#暂未启用
        self.horizontal_layout_in_challenge_page.addWidget(self.accept_button)

        self.decline_button = QPushButton('拒绝',self.challenge_page)
        self.decline_button.setEnabled(False)#暂未启用
        self.horizontal_layout_in_challenge_page.addWidget(self.decline_button)

    def page_game(self):
        self.game_page = QWidget(self.splitter)
        self.splitter.addWidget(self.game_page)
        self.vertical_layout_in_game_page = QVBoxLayout(self.game_page)
        self.vertical_layout_in_game_page.addWidget(QLabel('正在进行中的对局列表（暂未启用）'))

        self.tree_widget_for_game = QTreeWidget(self.game_page)
        self.vertical_layout_in_game_page.addWidget(self.tree_widget_for_game)

        self.tree_widget_for_game.setColumnCount(16)
        self.tree_widget_for_game.setHeaderLabels([
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

        default_item = QTreeWidgetItem(
            self.tree_widget_for_game,
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
        
        self.horizontal_layout_in_game_page = QHBoxLayout()
        self.vertical_layout_in_game_page.addLayout(self.horizontal_layout_in_game_page)

        self.enter_button = QPushButton('进入',self.game_page)
        self.enter_button.setEnabled(False)#暂未启用
        self.horizontal_layout_in_game_page.addWidget(self.enter_button)

        self.defeat_button = QPushButton('认输',self.game_page)
        self.defeat_button.setEnabled(False)#暂未启用
        self.horizontal_layout_in_game_page.addWidget(self.defeat_button)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.status_bar = self.statusBar()
        self.splitter = QSplitter(Qt.Orientation.Horizontal,self)
        self.setCentralWidget(self.splitter)

        self.setWindowTitle('下棋窗口（当前暂为内测状态，暂未投入使用）')
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

        self.chess_board = NoStretchingSvgWidget(self.splitter)
        self.splitter.addWidget(self.chess_board)

        self.create_info_widget()
        self.create_chat_and_record_widget()

    def create_info_widget(self):
        self.info_widget = QSplitter(Qt.Orientation.Vertical,self.splitter)
        self.splitter.addWidget(self.info_widget)

        self.create_scroll_area()
        self.create_current_clock()
        self.create_game_operation()

    def create_scroll_area(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.info_widget.addWidget(self.scroll_area)

        self.scroll_area_widget = QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_widget)
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
        self.layout_in_time_display.addRow('每步增加时间',self.increment)

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
        self.white_player = PlayererInfo(True,self.scroll_area_widget)
        self.black_player = PlayererInfo(False,self.scroll_area_widget)
        self.layout_in_scroll_area.addWidget(self.white_player)
        self.layout_in_scroll_area.addWidget(self.black_player)

    def create_current_clock(self):
        self.current_clock = QGroupBox('剩余时间',self.info_widget)
        self.info_widget.addWidget(self.current_clock)
        self.layout_in_current_clock = QFormLayout(self.current_clock)

        self.white_clock = TimedeltaDisplayWidget(self.current_clock)
        self.black_clock = TimedeltaDisplayWidget(self.current_clock)
        self.layout_in_current_clock.addRow('白方',self.white_clock)
        self.layout_in_current_clock.addRow('黑方',self.black_clock)

    def create_game_operation(self):
        self.game_operation = QGroupBox('对局操作',self.info_widget)
        self.info_widget.addWidget(self.game_operation)
        self.vertical_layout_in_game_operation = QVBoxLayout(self.game_operation)

        self.horizontal_layout_in_game_operation_1 = QHBoxLayout()
        self.horizontal_layout_in_game_operation_2 = QHBoxLayout()
        self.vertical_layout_in_game_operation.addLayout(self.horizontal_layout_in_game_operation_1)
        self.vertical_layout_in_game_operation.addLayout(self.horizontal_layout_in_game_operation_2)

        self.move_input = QLineEdit(self.game_operation)
        self.move_input.setPlaceholderText('下棋请用UCI格式')
        self.horizontal_layout_in_game_operation_1.addWidget(self.move_input)

        self.confirm_move_button = QPushButton('确认走棋',self.game_operation)
        #self.confirm_move_button.clicked.connect()
        self.horizontal_layout_in_game_operation_1.addWidget(self.confirm_move_button)

        self.regret_making_the_move_button = QPushButton('悔棋',self.game_operation)
        #self.regret_making_the_move_button.clicked.connect()
        self.horizontal_layout_in_game_operation_2.addWidget(self.regret_making_the_move_button)

        self.draw_button = QPushButton('和棋',self.game_operation)
        #self.draw_button.clicked.connect()
        self.horizontal_layout_in_game_operation_2.addWidget(self.draw_button)

        self.defeat_button = QPushButton('认输',self.game_operation)
        #self.defeat_button.clicked.connect()
        self.horizontal_layout_in_game_operation_2.addWidget(self.defeat_button)

    def create_chat_and_record_widget(self):
        self.chat_and_record_widget = QWidget(self.splitter)
        self.splitter.addWidget(self.chat_and_record_widget)
        self.vertical_layout_in_chat_and_record_widget = QVBoxLayout(self.chat_and_record_widget)

        self.create_chat_widget()
        self.create_send_msg_widget()
        self.create_move_record_widget()

    def create_chat_widget(self):
        self.vertical_layout_in_chat_and_record_widget.addWidget(QLabel('聊天对话'))
        self.chat_tree_widget = QTreeWidget(self.chat_and_record_widget)
        self.vertical_layout_in_chat_and_record_widget.addWidget(self.chat_tree_widget)

        self.chat_tree_widget.setColumnCount(3)
        self.chat_tree_widget.setHeaderLabels([
            '房间',
            '用户',
            '消息内容',
        ])

    def create_send_msg_widget(self):
        self.horizontal_layout_in_chat_and_record_widget = QHBoxLayout()
        self.vertical_layout_in_chat_and_record_widget.addLayout(self.horizontal_layout_in_chat_and_record_widget)

        self.msg_input = QLineEdit(self.chat_and_record_widget)
        self.horizontal_layout_in_chat_and_record_widget.addWidget(self.msg_input)
        self.send_to_observation_area = QCheckBox('发送到观战区',self.chat_and_record_widget)
        self.horizontal_layout_in_chat_and_record_widget.addWidget(self.send_to_observation_area)

        self.send_button = QPushButton('发送',self.chat_and_record_widget)
        #self.send_button.clicked.connect()
        self.horizontal_layout_in_chat_and_record_widget.addWidget(self.send_button)

    def create_move_record_widget(self):
        self.vertical_layout_in_chat_and_record_widget.addWidget(QLabel('走棋记录'))
        self.move_record_widget = QListWidget(self.chat_and_record_widget)
        self.vertical_layout_in_chat_and_record_widget.addWidget(self.move_record_widget)

    def example(self):
        # 真实对局示例1
        {
            'id': 'f0cEIixZ', 
            'variant': {
                'key': 'standard', 
                'name': 'Standard', 
                'short': 'Std'
            }, 
            'speed': 'classical', 
            'perf': {'name': '慢棋'}, 
            'rated': False, 
            'createdAt': datetime.datetime(
                2026, 
                7, 9, 
                12, 45, 
                54, 358000, 
                tzinfo=datetime.timezone.utc
            ), 
            'white': {
                'id': 'wyxx210704', 
                'name': 'wyxx210704', 
                'title': None, 
                'rating': 1512
            }, 
            'black': {}, #未登录
            'initialFen': 'startpos', 
            'clock': {
                'initial': 10800000, 
                'increment': 180000
            }, 
            'type': 'gameFull', 
            'state': {
                'type': 'gameState', 
                'moves': '', 
                'wtime': 10800000, 
                'btime': 10800000, 
                'winc': 180000, 
                'binc': 180000, 
                'status': 'started'
            }
        }
        
        {'type': 'gameState', 'moves': 'd2d4', 'wtime': datetime.timedelta(seconds=10800), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5', 'wtime': datetime.timedelta(seconds=10800), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5', 'wtime': datetime.timedelta(seconds=10794, microseconds=830000), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started', 'wtakeback': True}
        {'type': 'gameState', 'moves': '', 'wtime': datetime.timedelta(seconds=10800), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4', 'wtime': datetime.timedelta(seconds=10956, microseconds=470000), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5', 'wtime': datetime.timedelta(seconds=10956, microseconds=470000), 'btime': datetime.timedelta(seconds=10976, microseconds=940000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=11132, microseconds=90000), 'btime': datetime.timedelta(seconds=10976, microseconds=940000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3 g8f6', 'wtime': datetime.timedelta(seconds=11132, microseconds=90000), 'btime': datetime.timedelta(seconds=11154, microseconds=610000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3 g8f6', 'wtime': datetime.timedelta(seconds=11128, microseconds=80000), 'btime': datetime.timedelta(seconds=11154, microseconds=610000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started', 'btakeback': True}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=11132, microseconds=90000), 'btime': datetime.timedelta(seconds=11154, microseconds=610000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=11132, microseconds=90000), 'btime': datetime.timedelta(seconds=11145, microseconds=690000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started', 'wdraw': True}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=11132, microseconds=90000), 'btime': datetime.timedelta(seconds=11135, microseconds=30000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'draw'}

        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'White proposes takeback (1.d4 d5)'}
        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'Black accepts takeback'}
        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'Black proposes takeback (2...Nf6)'}
        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'White accepts takeback'}
        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'White offers draw'}
        {'type': 'chatLine', 'room': 'player', 'username': 'lichess', 'text': 'Draw offer accepted'}

        # 真实对局示例2
        {
            'id': 'Y7Niaxm9', 
            'variant': {
                'key': 'atomic', 
                'name': 'Atomic', 
                'short': 'Atom'
            }, 
            'speed': 'classical', 
            'perf': {'name': '原子棋'}, 
            'rated': False, 
            'createdAt': datetime.datetime(
                2026, 
                7, 11, 
                9, 8, 
                24, 453000, 
                tzinfo=datetime.timezone.utc
            ), 
            'white': {
                'id': 'wyxx210704', 
                'name': 'wyxx210704', 
                'title': None, 
                'rating': 1500, 
                'provisional': True
            }, 
            'black': {'aiLevel': 1}, 
            'initialFen': 'startpos', 
            'clock': {
                'initial': 10800000, 
                'increment': 180000
            }, 
            'type': 'gameFull', 
            'state': {
                'type': 'gameState', 
                'moves': '', 
                'wtime': 10800000, 
                'btime': 10800000, 
                'winc': 180000, 
                'binc': 180000, 
                'status': 'started'
            }
        }
        
        {'type': 'gameState', 'moves': 'd2d4', 'wtime': datetime.timedelta(seconds=10800), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5', 'wtime': datetime.timedelta(seconds=10800), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5', 'wtime': datetime.timedelta(seconds=10977, microseconds=990000), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5 f8a3', 'wtime': datetime.timedelta(seconds=10977, microseconds=990000), 'btime': datetime.timedelta(seconds=10977, microseconds=750000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5 f8a3 c1g5', 'wtime': datetime.timedelta(seconds=11155, microseconds=300000), 'btime': datetime.timedelta(seconds=10977, microseconds=750000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5 f8a3 c1g5 g8f6', 'wtime': datetime.timedelta(seconds=11155, microseconds=300000), 'btime': datetime.timedelta(seconds=11155, microseconds=440000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5 f8a3', 'wtime': datetime.timedelta(seconds=11155, microseconds=300000), 'btime': datetime.timedelta(seconds=10977, microseconds=750000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'gameState', 'moves': 'd2d4 e7e5 d4e5 f8a3 d1d7', 'wtime': datetime.timedelta(seconds=11150, microseconds=850000), 'btime': datetime.timedelta(seconds=10977, microseconds=750000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'variantEnd', 'winner': 'white'}

if __name__ == '__main__':
    app = QApplication([])
    window = GameWindow()
    window.show()
    app.exec()