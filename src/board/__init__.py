from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from berserk import Client
from requests import get
import chess
import chess.variant

from ..tools import SettingsWindow
from ..chess_general_logic import generate_svg_from_uci
from .board_tools import *
from .board_thread_worker import *
from ..business_logic import *
from ..input_dialogs import get_item
from ..costants import ICON
from ..play_chess_general_widget import *

class BoardMain(QMainWindow):
    def __init__(self,client:Client):
        super().__init__()
        self.client = client
        self.game_window_list = []

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)
        
        self.tool_bar = self.addToolBar('工具')
        self.status_bar = self.statusBar()

        self.setWindowTitle('人类专用下棋页面')
        self.setWindowIcon(QIcon(ICON))
        
        self.mdi_area = QMdiArea(self.tab_widget)
        pixmap = QPixmap()
        pixmap.loadFromData(get('https://picsum.photos/1920/1080').content)
        self.mdi_area.setBackground(QBrush(pixmap))
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
        self.define_constants()
        self.start_thread()

        challenge_out = self.mdi_area.addSubWindow(ChallengeWindow(self.client))
        challenge_out.showMaximized()

    def define_constants(self):
        self.challenge_type_text = {
            'challenge':'创建',
            'cancel':'取消',
            'decline':'拒绝',
        }

        self.game_type_text = {
            'start':'开始',
            'finish':'结束',
        }

    def add_action(self):
        self.challenge_action = QAction('发起挑战')
        self.challenge_action.triggered.connect(lambda:self.mdi_area.addSubWindow(ChallengeWindow(self.client)).show())
        self.tool_bar.addAction(self.challenge_action)

        self.settings_action = QAction('设置')
        self.settings_action.triggered.connect(lambda:self.mdi_area.addSubWindow(SettingsWindow(self.client)).show())
        self.tool_bar.addAction(self.settings_action)
        
    def page_challenge(self):
        self.challenge_page = QWidget(self.splitter)
        self.splitter.addWidget(self.challenge_page)
        self.vertical_layout_in_challenge_page = QVBoxLayout(self.challenge_page)
        self.vertical_layout_in_challenge_page.addWidget(QLabel('收到的挑战'))

        self.tree_widget_for_challenge = ChallengeTreeWidget(self.challenge_page)
        self.vertical_layout_in_challenge_page.addWidget(self.tree_widget_for_challenge)
        
        self.horizontal_layout_in_challenge_page = QHBoxLayout()
        self.vertical_layout_in_challenge_page.addLayout(self.horizontal_layout_in_challenge_page)

        self.accept_button = QPushButton('接受',self.challenge_page)
        self.accept_button.clicked.connect(self.accept_challenge)
        self.horizontal_layout_in_challenge_page.addWidget(self.accept_button)

        self.decline_button = QPushButton('拒绝',self.challenge_page)
        self.decline_button.clicked.connect(self.decline_challenge)
        self.horizontal_layout_in_challenge_page.addWidget(self.decline_button)

    def accept_challenge(self):
        item = self.tree_widget_for_challenge.currentItem()

        if item:self.client.challenges.accept(item.text(0))
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一项挑战之后再点击接受',
        )
            
    def decline_challenge(self):
        item = self.tree_widget_for_challenge.currentItem()

        if item:self.client.challenges.decline(item.text(0),get_item(self,'选择要取消的原因',[
            "generic",
            "later",
            "tooFast",
            "tooSlow",
            "timeControl",
            "rated",
            "casual",
            "standard",
            "variant",
            "noBot",
            "onlyBot",
        ]))
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一项挑战之后再点击拒绝',
        )

    def page_game(self):
        self.game_page = QWidget(self.splitter)
        self.splitter.addWidget(self.game_page)
        self.vertical_layout_in_game_page = QVBoxLayout(self.game_page)
        self.vertical_layout_in_game_page.addWidget(QLabel('正在进行中的对局'))

        self.tree_widget_for_game = GameTreeWidget(self.game_page)
        self.vertical_layout_in_game_page.addWidget(self.tree_widget_for_game)
        
        self.horizontal_layout_in_game_page = QHBoxLayout()
        self.vertical_layout_in_game_page.addLayout(self.horizontal_layout_in_game_page)

        self.enter_button = QPushButton('进入',self.game_page)
        self.enter_button.clicked.connect(self.enter_game)
        self.horizontal_layout_in_game_page.addWidget(self.enter_button)

        self.defeat_button = QPushButton('认输',self.game_page)
        self.defeat_button.clicked.connect(self.defeat)
        self.horizontal_layout_in_game_page.addWidget(self.defeat_button)

    def enter_game(self):
        item = self.tree_widget_for_game.currentItem()

        if item:
            window = GameWindow(self.client,item.text(1))
            self.game_window_list.append(window)
            window.destroyed.connect(lambda:self.game_window_list.remove(window))
            window.show()
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一项对局之后再进入对局',
        )
            
    def defeat(self):
        item = self.tree_widget_for_game.currentItem()

        if item:self.client.board.resign_game(item.text(1))
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一项对局之后再认输',
        )

    def start_thread(self):
        self.worker_thread = QThread()
        self.worker = EventListen(self.client)
        self.worker.moveToThread(self.worker_thread)

        self.worker.challenge_update.connect(self.receive_challenge)
        self.worker.ongoing_game_update.connect(self.receive_game)
        self.worker.state_update.connect(self.receive_state)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def open_dialog(self,text:str,deta:dict):
        dialog = QDialog(self)
        dialog.setWindowTitle('消息')
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(text))
        tree_widget = JsonTreeWidget(dialog)
        tree_widget.set_dict(deta)
        layout.addWidget(tree_widget)

        button = QPushButton('完成',dialog)
        button.clicked.connect(dialog.accept)
        layout.addWidget(button)

        dialog.exec()

    def receive_state(self,state:State,challenge_list:list[ChallengeJson],game_list:list[GameEventInfo]):
        if state == 'both' or state == 'challenge' or state == 'game':
            self.tab_widget.setCurrentWidget(self.splitter)
            if state == 'both':self.status_bar.showMessage('当前同时有挑战和对局没处理')
            elif state == 'challenge':self.status_bar.showMessage('当前有挑战待处理')
            elif state == 'game':self.status_bar.showMessage('当前有对局待处理')
        elif state == 'both_not':self.status_bar.clearMessage()

        self.tree_widget_for_challenge.clear()
        self.tree_widget_for_game.clear()

        for challenge in challenge_list:
            item = QTreeWidgetItem(self.tree_widget_for_challenge)

            item.setText(0,challenge['id'])         
            item.setText(1,challenge['url'])        
            item.setText(2,challenge['status'])     
            item.setText(6,'是' if challenge['rated'] else '否')
            item.setText(7,challenge['speed'])      
            item.setText(9,challenge['color'])      
            item.setText(10,challenge['finalColor'])
            item.setText(12,challenge['direction']) 
            
            self.tree_widget_for_challenge.setItemWidget(item,3,InfoButton(challenge['challenger'],self.tree_widget_for_challenge))
            self.tree_widget_for_challenge.setItemWidget(item,4,InfoButton(challenge['destUser'],self.tree_widget_for_challenge))
            self.tree_widget_for_challenge.setItemWidget(item,5,InfoButton(challenge['variant'],self.tree_widget_for_challenge))
            self.tree_widget_for_challenge.setItemWidget(item,8,InfoButton(challenge['timeControl'],self.tree_widget_for_challenge))
            self.tree_widget_for_challenge.setItemWidget(item,11,InfoButton(challenge['perf'],self.tree_widget_for_challenge))

            if 'initialFen' in challenge:
                item.setText(13,challenge['initialFen'])
        
        for game in game_list:
            item = QTreeWidgetItem(self.tree_widget_for_game)

            item.setText(0,game['fullId'])
            item.setText(1,game['gameId'])
            item.setText(2,game['fen'])
            item.setText(3,game['color'])
            item.setText(4,game['lastMove'])
            item.setText(5,game['source'])
            item.setText(8,game['speed'])
            item.setText(9,game['perf'])
            item.setText(10,'是' if game['rated'] else '否')
            item.setText(11,'是' if game['hasMoved'] else '否')
            item.setText(13,'是' if game['isMyTurn'] else '否')
            item.setText(14,str(game['secondsLeft']))#这是整数要转
            item.setText(15,str(game['perf']))#这是整数要转

            self.tree_widget_for_game.setItemWidget(item,6,InfoButton(game['status'],self.tree_widget_for_game))
            self.tree_widget_for_game.setItemWidget(item,7,InfoButton(game['variant'],self.tree_widget_for_game))
            self.tree_widget_for_game.setItemWidget(item,12,InfoButton(game['opponent'],self.tree_widget_for_game))

    def receive_challenge(self,current_challenge:ChallengeJson,type_:ChallengeType):
        self.open_dialog(f'现在有挑战被{self.challenge_type_text[type_]}，请查收',current_challenge)

    def receive_game(self,current_game:GameEventInfo,type_:ChallengeType):
        self.open_dialog(f'现在有对局已经{self.game_type_text[type_]}，请查收',current_game)

    def example(self):
        #有进来的挑战
        {'in': [{
            'id': 'RV3g4qOa', 
            'url': 'https://lichess.org/RV3g4qOa', 
            'status': 'created', 
            'challenger': {
                'name': 'wyxx210704_bot', 
                'title': 'BOT', 
                'flair': 'symbols.python-logo', 
                'id': 'wyxx210704_bot', 
                'rating': 2595, 
                'provisional': True, 
                'online': True, 
                'lag': 3
            }, 
            'destUser': {
                'name': 'wyxx210704', 
                'flair': 'symbols.python-logo', 
                'id': 'wyxx210704', 
                'rating': 1512, 
                'online': True, 
                'lag': 3
            }, 
            'variant': {
                'key': 'standard', 
                'name': 'Standard', 
                'short': 'Std'
            }, 
            'rated': False, 
            'speed': 'classical', 
            'timeControl': {
                'type': 'clock', 
                'limit': 10800, 
                'increment': 180, 
                'show': '180+180'
            }, 
            'color': 'white', 
            'finalColor': 'white', 
            'perf': {
                'icon': '\ue00a', 
                'name': '慢棋'
            }, 
            'direction': 'in'
        }], 'out': []}

        #空的挑战
        {'in': [], 'out': []}

        #正在进行中的对局
        [{
            'fullId': 'RV3g4qOaipkw', 
            'gameId': 'RV3g4qOa', 
            'fen': 'rnbqkbnr/ppp1pppp/8/3p4/3P4/2N5/PPP1PPPP/R1BQKBNR b KQkq - 1 2', 
            'color': 'black', 
            'lastMove': 'b1c3', 
            'source': 'friend', 
            'status': {
                'id': 20, 
                'name': 'started'
            }, 
            'variant': {
                'key': 'standard', 
                'name': 'Standard'
            }, 
            'speed': 'classical', 
            'perf': 'classical', 
            'rated': False, 
            'hasMoved': True, 
            'opponent': {
                'id': 'wyxx210704_bot', 
                'username': 'BOT wyxx210704_bot', 
                'rating': 2595
            }, 
            'isMyTurn': True, 
            'secondsLeft': 10796, 
            'rating': 1512
        }]

class GameWindow(QMainWindow):
    def __init__(self,client:Client,game_id:str):
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

        self.client = client
        self.game_id = game_id
        self.setWindowTitle(f'下棋窗口，对局{self.game_id}')
        self.setWindowIcon(QIcon(ICON))

        for game in self.client.games.get_ongoing():
            if game['gameId'] == self.game_id:#判断是不是这一局
                if game['color'] == 'white':
                    self.color = chess.WHITE
                elif game['color'] == 'black':
                    self.color = chess.BLACK

                break#防止多余的循环出现

        self.chess_board = NoStretchingSvgWidget(self.splitter)
        self.splitter.addWidget(self.chess_board)
        self.create_info_widget()
        self.create_chat_and_record_widget()
        self.start_thread()

    def create_info_widget(self):
        self.info_widget = QSplitter(Qt.Orientation.Vertical,self.splitter)
        self.splitter.addWidget(self.info_widget)

        self.create_scroll_area()
        self.create_current_clock()
        self.create_game_operation()

    def create_scroll_area(self):
        self.scroll_area = GameInfoWidget(self)
        self.scroll_area.setWidgetResizable(True)
        self.info_widget.addWidget(self.scroll_area)

    def create_current_clock(self):
        self.current_clock = CurrentClock(self.info_widget)
        self.info_widget.addWidget(self.current_clock)

    def create_game_operation(self):
        self.game_operation = QGroupBox('对局操作',self.info_widget)
        self.info_widget.addWidget(self.game_operation)
        self.vertical_layout_in_game_operation = QVBoxLayout(self.game_operation)

        self.horizontal_layout_in_game_operation_1 = QHBoxLayout()
        self.horizontal_layout_in_game_operation_2 = QHBoxLayout()
        self.vertical_layout_in_game_operation.addLayout(self.horizontal_layout_in_game_operation_1)
        self.vertical_layout_in_game_operation.addLayout(self.horizontal_layout_in_game_operation_2)

        self.confirm_move_button = QPushButton('确认走棋',self.game_operation)
        self.confirm_move_button.clicked.connect(self.confirm_move)
        
        self.move_input = QLineEdit(self.game_operation)
        self.move_input.setPlaceholderText('下棋请用UCI格式')
        self.move_input.returnPressed.connect(self.confirm_move_button.click)
        
        self.horizontal_layout_in_game_operation_1.addWidget(self.move_input)
        self.horizontal_layout_in_game_operation_1.addWidget(self.confirm_move_button)

        self.regret_making_the_move_button = QPushButton('悔棋',self.game_operation)
        self.regret_making_the_move_button.clicked.connect(self.regret_making_the_move)
        self.horizontal_layout_in_game_operation_2.addWidget(self.regret_making_the_move_button)

        self.draw_button = QPushButton('和棋',self.game_operation)
        self.draw_button.clicked.connect(self.draw)
        self.horizontal_layout_in_game_operation_2.addWidget(self.draw_button)

        self.defeat_button = QPushButton('认输',self.game_operation)
        self.defeat_button.clicked.connect(self.defeat)
        self.horizontal_layout_in_game_operation_2.addWidget(self.defeat_button)

    def create_chat_and_record_widget(self):
        self.chat_and_record_widget = ChatAndRecordWidget(self.send_message,self.splitter)
        self.splitter.addWidget(self.chat_and_record_widget)

    def ask_quastion(self,text:str):
        button = QMessageBox.question(
            self,
            '对局消息',
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        # 直接把条件返回，不用多写一个if
        return button == QMessageBox.StandardButton.Yes

    def confirm_move(self):
        if self.ask_quastion('是否确认走棋'):
            try:
                self.client.board.make_move(
                    self.game_id,
                    self.move_input.text(),
                ) 

                self.move_input.clear()
            except ResponseError as error:
                show_api_error_dialog(
                    error,
                    '走棋时发生错误',
                    self,
                )
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '走棋时发生错误',
                    self,
                )

    def regret_making_the_move(self):
        if self.abortable:
            if self.ask_quastion('对局暂未走满一步，是否终止对局'):
                try:self.client.board.abort_game(self.game_id) 
                except ResponseError as error:
                    show_api_error_dialog(
                        error,
                        '终止对局时发生错误',
                        self,
                    )
                except Exception as error:
                    show_error_dialog(
                        *get_error_details(error),
                        '终止对局时发生错误',
                        self,
                    )
        else:
            if self.ask_quastion('是否确认悔棋（需要对手同意）'):
                try:self.client.board.offer_takeback(self.game_id) 
                except ResponseError as error:
                    show_api_error_dialog(
                        error,
                        '悔棋时发生错误',
                        self,
                    )
                except Exception as error:
                    show_error_dialog(
                        *get_error_details(error),
                        '悔棋时发生错误',
                        self,
                    )

    def draw(self):
        if self.ask_quastion('是否确认和棋（需要对手同意）'):
            try:self.client.board.offer_draw(self.game_id) 
            except ResponseError as error:
                show_api_error_dialog(
                    error,
                    '和棋时发生错误',
                    self,
                )
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '和棋时发生错误',
                    self,
                )

    def defeat(self):
        if self.ask_quastion('是否认输'):
            try:self.client.board.resign_game(self.game_id) 
            except ResponseError as error:
                show_api_error_dialog(
                    error,
                    '认输时发生错误',
                    self,
                )
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '认输时发生错误',
                    self,
                )

    def send_message(self,text:str,is_spectator:bool):
        try:
            self.client.board.post_message(
                self.game_id,
                text,
                is_spectator,
            )
        except ResponseError as error:
            show_api_error_dialog(
                error,
                '发送消息时发生错误',
                self,
            )
        except Exception as error:
            show_error_dialog(
                *get_error_details(error),
                '发送消息时发生错误',
                self,
            )

    def start_thread(self):
        self.worker_thread = QThread()
        self.worker = PlayChessStream(self.client,self.game_id)
        self.worker.moveToThread(self.worker_thread)
        self.worker.send_dict.connect(self.receive_dict)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def receive_dict(self,value:dict):
        # 这里由于有判断逻辑，所以请大家使用下方的example函数进行查看，证明为什么要这样子设计
        if value['type'] == 'gameState':
            self.change_state(value)
        elif value['type'] == 'gameFull':
            if value['speed'] == 'correspondence':
                basic_time = timedelta(days=value['daysPerTurn'])
                increment = 0#通讯棋没有加时这种说法
            else:
                #毫秒要转成秒，所以这两项都会除以1000
                basic_time = timedelta(seconds=value['clock']['initial'] / 1000)
                increment = int(value['clock']['increment'] / 1000)

            self.scroll_area.load_info(
                value['id'],
                value['speed'],
                value['rated'],
                value['perf']['name'],
                value['createdAt'],
                value['initialFen'],
                basic_time,
                increment,
                value['variant']['key'],
                value['variant']['name'],
                value['variant']['short'],
                value['white'],
                value['black'],
            )

            self.variant_key_text = value['variant']['key']
            self.start_fen_text = value['initialFen']

            if self.variant_key_text == 'chess960':
                board = chess.Board(self.start_fen_text)
                start_pos = board.chess960_pos(ignore_counters=False)
                if start_pos == None:
                    self.status_bar.showMessage(
                        '暂未找到chess960编号',
                        5000,
                    )
                else:self.info_label.setText(f'这局使用的chess960起始局面编号是{start_pos}')

            #这些是官网里面出现的机制
            if self.color == chess.WHITE:
                if ('title' in value['black']) and (value['black']['title'] == 'BOT'):
                    #bot账号不给悔棋
                    self.regret_making_the_move_button.setEnabled(False)
                elif 'aiLevel' in value['black']:
                    #人机对弈不给提出和棋
                    self.draw_button.setEnabled(False)
            if self.color == chess.BLACK:
                if ('title' in value['white']) and (value['white']['title'] == 'BOT'):
                    #bot账号不给悔棋
                    self.regret_making_the_move_button.setEnabled(False)
                elif 'aiLevel' in value['white']:
                    #人机对弈不给提出和棋
                    self.draw_button.setEnabled(False)

            self.change_state(value['state'])
        elif value['type'] == 'chatLine':
            item = QTreeWidgetItem(
                self.chat_and_record_widget.get_tree_widget(),
                [
                    value['room'],
                    value['username'],
                    value['text'],
                ]
            )
        elif (value['type'] == 'opponentGone') and (value['gone'] == True):
            self.status_bar.showMessage(
                f'对手已离开对局，{value['claimWinInSeconds']}秒后可以取得胜利',
                5000,
            )

            if value['claimWinInSeconds'] == 0:
                if self.ask_quastion('对方离开对局时间已达上限，是否直接取得胜利'):
                    self.client.board.claim_victory(self.game_id)

    def change_state(self,value:dict):
        #对局进行中
        moves_str:str = value['moves']
        moves_list = moves_str.split(' ')

        if (self.variant_key_text == 'chess960') or (self.variant_key_text == 'fromPosition'):
            self.chess_board.load(generate_svg_from_uci(
                moves_list,
                self.color,
                self.variant_key_text,
                self.start_fen_text
            ))
        else:self.chess_board.load(generate_svg_from_uci(
            moves_list,
            self.color,
            self.variant_key_text,
        ))
            
        if (self.variant_key_text == 'crazyhouse') and (moves_str != ''):
            board = chess.variant.CrazyhouseBoard()
            for move_uci in moves_list:
                board.push(chess.Move.from_uci(move_uci))
            self.info_label.setText(f'我的棋子：{str(board.pockets[self.color])}')
        
        #直接把条件写进去，免得再写多一个if
        #如果对局还没走满一步，那就不能悔棋，只能终止对局
        self.abortable = (len(moves_list) == 1)

        if self.color == chess.WHITE:
            #已走的棋是偶数那么就轮到白方走（0也是偶数）
            #直接把条件写进去，免得再写多一个if
            self.confirm_move_button.setEnabled((len(moves_list) % 2 == 0) or (moves_str == ''))#特殊情况：棋局刚开始

            if ('btakeback' in value) and (value['btakeback'] == True):
                self.status_bar.showMessage(
                    '对方发来悔棋申请',
                    5000,
                )

                if self.ask_quastion('对方发来悔棋申请，是否接受'):self.client.board.accept_takeback(self.game_id)
                else:self.client.board.decline_takeback(self.game_id)

            if ('bdraw' in value) and (value['bdraw'] == True):
                self.status_bar.showMessage(
                    '对方发来和棋申请',
                    5000,
                )

                if self.ask_quastion('对方发来和棋申请，是否接受'):self.client.board.accept_draw(self.game_id)
                else:self.client.board.decline_draw(self.game_id)
        elif self.color == chess.BLACK:
            #已走的棋是奇数那么就轮到黑方走，与上面相反
            #直接把条件写进去，免得再写多一个if
            self.confirm_move_button.setEnabled(len(moves_list) % 2 == 1)

            if ('wtakeback' in value) and (value['wtakeback'] == True):
                self.status_bar.showMessage(
                    '对方发来悔棋申请',
                    5000,
                )

                if self.ask_quastion('对方发来悔棋申请，是否接受'):self.client.board.accept_takeback(self.game_id)
                else:self.client.board.decline_takeback(self.game_id)

            if ('wdraw' in value) and (value['wdraw'] == True):
                self.status_bar.showMessage(
                    '对方发来和棋申请',
                    5000,
                )

                if self.ask_quastion('对方发来和棋申请，是否接受'):self.client.board.accept_draw(self.game_id)
                else:self.client.board.decline_draw(self.game_id)

        if (type(value['wtime']) == timedelta) and (type(value['btime']) == timedelta):
            self.current_clock.set_time(value['wtime'],value['btime'])
        else:
            self.current_clock.set_time(
                timedelta(seconds=value['wtime'] / 1000),
                timedelta(seconds=value['btime'] / 1000),
            )
        
        self.chat_and_record_widget.set_moves(moves_list)

        if value['status'] != 'started':
            #对局已结束
            QMessageBox.information(
                self,
                '对局结束',
                f'结束原因：{value["status"]}'
            )

            if 'winner' in value:
                QMessageBox.information(
                    self,
                    '对局结束',
                    f'胜利者：{value['winner']}'
                )

            self.draw_button.setEnabled(False)
            self.defeat_button.setEnabled(False)
            self.confirm_move_button.setEnabled(False)
            self.regret_making_the_move_button.setEnabled(False)

    def example(self):
        # 真实对局示例1：悔棋、和棋、聊天消息、匿名账号
        import datetime
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

        # 真实对局示例2：人机对弈、变体
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

        # 真实对局示例3：对手离开
        {
            'id': 'v53dhSiP', 
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
                7, 12, 
                10, 58, 
                37, 752000, 
                tzinfo=datetime.timezone.utc
            ), 
            'white': {
                'id': 'wyxx210704', 
                'name': 'wyxx210704', 
                'title': None, 
                'rating': 1512
            }, 
            'black': {}, 
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
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 140}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 135}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 130}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 125}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 120}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 115}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 110}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 105}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 100}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 95}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 90}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 85}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 80}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 75}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 70}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 65}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=10888, microseconds=610000), 'btime': datetime.timedelta(seconds=10800), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'started'}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 60}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 55}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 50}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 45}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 40}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 35}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 30}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 25}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 20}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 15}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 10}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 5}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 0}
        {'type': 'opponentGone', 'gone': True, 'claimWinInSeconds': 0}
        {'type': 'gameState', 'moves': 'd2d4 d7d5 b1c3', 'wtime': datetime.timedelta(seconds=10888, microseconds=610000), 'btime': datetime.timedelta(seconds=10730, microseconds=420000), 'winc': datetime.timedelta(seconds=180), 'binc': datetime.timedelta(seconds=180), 'status': 'timeout', 'winner': 'white'}
        
        #真实对局示例4：bot账号、通讯棋
        {
            'id': 'zG7dJP54', 
            'variant': {
                'key': 'standard', 
                'name': 'Standard', 
                'short': 'Std'
            }, 
            'speed': 'correspondence', 
            'perf': {'name': '通讯棋'}, 
            'rated': False, 
            'createdAt': datetime.datetime(
                2026, 
                7, 15, 
                13, 22, 
                46, 433000, 
                tzinfo=datetime.timezone.utc
            ), 
            'white': {
                'id': 'wyxx210704', 
                'name': 'wyxx210704', 
                'title': None, 
                'rating': 1500, 
                'provisional': True
            }, 
            'black': {
                'id': 'wyxx210704_bot', 
                'name': 'wyxx210704_bot', 
                'title': 'BOT', 
                'rating': 3000, 
                'provisional': True
            }, 
            'initialFen': 'startpos', 
            'daysPerTurn': 14, 
            'type': 'gameFull', 
            'state': {
                'type': 'gameState', 
                'moves': '', 
                'wtime': 1209563000, 
                'btime': 1209600000, 
                'winc': 0, 
                'binc': 0, 
                'status': 'started'
            }
        }

        {'type': 'gameState', 'moves': 'e2e4', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5 d1h5', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5 d1h5 b8c6', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5 d1h5 b8c6 f1c4', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5 d1h5 b8c6 f1c4 g8f6', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'started'}
        {'type': 'gameState', 'moves': 'e2e4 e7e5 d1h5 b8c6 f1c4 g8f6 h5f7', 'wtime': datetime.timedelta(days=14), 'btime': datetime.timedelta(days=14), 'winc': datetime.timedelta(0), 'binc': datetime.timedelta(0), 'status': 'mate', 'winner': 'white'}