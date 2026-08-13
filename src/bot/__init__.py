from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
#from berserk import Client

from ..costants import ICON
from ..play_chess_general_widget import *
from .bot_widget import *
from ..bot_settings import BotSettings

class BotMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)
        self.status_bar = self.statusBar()

        self.setWindowTitle('bot专用下棋主窗口')
        self.setWindowIcon(QIcon(ICON))

        self.create_challenge_and_game_page()
        self.create_game_manager_and_bot_settings()
        self.create_example_game_window()

    def create_challenge_and_game_page(self):
        self.challenge_and_game_page = QWidget(self.tab_widget)
        self.tab_widget.addTab(self.challenge_and_game_page,'挑战与对局')
        self.layout_in_challenge_and_game_page = QVBoxLayout(self.challenge_and_game_page)

        self.challenge_in = ChallengeTreeWidget(self.challenge_and_game_page)
        self.layout_in_challenge_and_game_page.addWidget(QLabel('进来的挑战'))
        self.layout_in_challenge_and_game_page.addWidget(self.challenge_in)

        self.challenge_out = ChallengeTreeWidget(self.challenge_and_game_page)
        self.layout_in_challenge_and_game_page.addWidget(QLabel('出去的挑战'))
        self.layout_in_challenge_and_game_page.addWidget(self.challenge_out)

        self.current_game = GameTreeWidget(self.challenge_and_game_page)
        self.layout_in_challenge_and_game_page.addWidget(QLabel('正在进行的对局'))
        self.layout_in_challenge_and_game_page.addWidget(self.current_game)

    def create_game_manager_and_bot_settings(self):
        self.game_manager = GameManager(self.tab_widget)
        self.bot_settings = BotSettings(self.tab_widget)
        self.tab_widget.addTab(self.game_manager,'对局查看')
        self.tab_widget.addTab(self.bot_settings,'设置')

    def create_example_game_window(self):
        self.example_game_window = GameWindow()
        self.game_manager.addSubWindow(self.example_game_window).show()

class GameWindow(QMainWindow):
    #def __init__(self,client:Client,game_id:str):
    def __init__(self):
        super().__init__()
        self.status_bar = self.statusBar()
        self.info_label = QLabel(self.status_bar)
        self.status_bar.addWidget(self.info_label)
        self.splitter = QSplitter(Qt.Orientation.Horizontal,self)
        self.setCentralWidget(self.splitter)

        self.resize(
            1490,
            630,
        )

        '''
        self.client = client
        self.game_id = game_id
        
        self.setWindowTitle(f'下棋窗口，对局{self.game_id}')
        '''
        self.setWindowTitle('示例对局')
        self.setWindowIcon(QIcon(ICON))

        '''
        for game in self.client.games.get_ongoing():
            if game['gameId'] == self.game_id:#判断是不是这一局
                if game['color'] == 'white':
                    self.color = chess.WHITE
                elif game['color'] == 'black':
                    self.color = chess.BLACK

                break#防止多余的循环出现
        '''

        self.chess_board = NoStretchingSvgWidget(self.splitter)
        self.splitter.addWidget(self.chess_board)
        self.create_info_widget()
        self.create_chat_and_record_widget()
        #self.start_thread()
        self.chess_board.load(generate_svg_from_board(chess.Board(),chess.WHITE))

    def create_info_widget(self):
        self.info_widget = QSplitter(Qt.Orientation.Vertical,self.splitter)
        self.splitter.addWidget(self.info_widget)

        self.create_scroll_area()
        self.create_current_clock()
        self.create_engine_info()

    def create_scroll_area(self):
        self.scroll_area = GameInfoWidget(self)
        self.scroll_area.setWidgetResizable(True)
        self.info_widget.addWidget(self.scroll_area)

    def create_current_clock(self):
        self.current_clock = CurrentClock(self.info_widget)
        self.info_widget.addWidget(self.current_clock)

    def create_engine_info(self):
        self.engine_info = JsonTreeWidget(self.info_widget)
        self.info_widget.addWidget(self.engine_info)

    def create_chat_and_record_widget(self):
        self.chat_and_record_widget = ChatAndRecordWidget(lambda text,is_spectator:None,self.splitter)
        self.splitter.addWidget(self.chat_and_record_widget)