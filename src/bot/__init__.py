from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from berserk import Client
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl

'''
from berserk.types.bots import GameEventInfo
from json import load
from typing import cast
'''

from ..costants import ICON,GENERAL_PATH

'''
from ..play_chess_general.widgets import *
from ..business_logic import *
from ..input_dialog_tools import CreateChallengeDialog
from ..input_dialogs import get_user_name,get_bool
from .bot_widget import *
from .bot_thread_worker import *
from ..bot_settings import BotSettings
from ..bot_settings.format import ConfigFormat
from ..bot_settings.base import CONFIG_PATH
'''

class BotMain(QMainWindow):
    def __init__(self,client:Client):
        super().__init__()
        self.setWindowTitle('你被骗了')
        self.setWindowIcon(QIcon(ICON))
        self.resize(800,600)

        '''
        #暂时不确定搞不搞这个对话框
        QMessageBox.information(
            self,
            '功能已弃用',
            '由于此功能现存很多bug，所以打算暂时弃用'
        )
        '''

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget(self)
        self.setCentralWidget(self.video_widget)
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile(GENERAL_PATH + 'rickroll.mp4'))
        self.player.play()

        '''
        self.client = client
        self.config = self.get_config()
        self.sub_windows = []

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)

        self.status_bar = self.statusBar()
        self.auto_match_info_label = QLabel('暂无自动匹配信息',self.status_bar)
        self.status_bar.addPermanentWidget(self.auto_match_info_label)

        self.setWindowTitle('bot专用下棋主窗口')
        self.setWindowIcon(QIcon(ICON))

        self.create_challenge_and_game_page()
        self.create_game_manager_and_bot_settings()
        self.create_tool_bar()
        self.start_thread()

        self.game_windows = cast(dict[str,QMdiSubWindow],{})
        '''

    def closeEvent(self, a0):
        self.player.stop()
        return super().closeEvent(a0)

    '''
    def get_config(self):
        return cast(
            ConfigFormat,
            load(open(
                CONFIG_PATH,
                'r',
                encoding='utf-8',
                errors='ignore',
            ))
        )

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
        self.bot_settings = QScrollArea(self.tab_widget)
        self.bot_settings.setWidget(BotSettings(self.bot_settings))
        self.tab_widget.addTab(self.game_manager,'对局查看')
        self.tab_widget.addTab(self.bot_settings,'设置')

    def create_tool_bar(self):
        self.tool_bar = self.addToolBar('工具')

        self.apply_settings_action = QAction('应用最新设置')
        self.apply_settings_action.triggered.connect(self.apply_settings)
        self.tool_bar.addAction(self.apply_settings_action)

        self.create_custom_challenge_action = QAction('发起自定义挑战')
        self.create_custom_challenge_action.triggered.connect(self.create_custom_challenge)
        self.tool_bar.addAction(self.create_custom_challenge_action)

        self.general_settings_action = QAction('打开通用设置')
        self.general_settings_action.triggered.connect(self.create_settings_window)
        self.tool_bar.addAction(self.general_settings_action)

    def apply_settings(self):
        if get_bool(self,'是否应用最新设置（正在进行的对局不会应用设置）'):
            QMessageBox.information(
                self,
                '提示',
                '操作成功',
            )

            self.config = self.get_config()
            self.event_listen_worker.apply_settings(self.config)
            self.challenge_out_worker.apply_settings(self.config)

    def create_custom_challenge(self):
        user_name = get_user_name(self.client,self,'输入被挑战的用户')
        is_rated = get_bool(self,'是否排位')
        dialog = CreateChallengeDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.client.challenges.create(
                    user_name,
                    is_rated,
                    *dialog.get_deta(),
                ) 
            except ResponseError as error:
                show_api_error_dialog(
                    error,
                    '创建挑战时报错',
                    self,
                )
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '创建挑战时报错',
                    self,
                )

    def create_settings_window(self):
        window = SettingsWindow(self.client)
        self.sub_windows.append(window)
        window.destroyed.connect(lambda:self.sub_windows.remove(window))
        window.show()

    def start_thread(self):
        self.event_listen_thread = QThread()
        self.event_listen_worker = EventListen(self.client,self.config)
        self.event_listen_worker.moveToThread(self.event_listen_thread)

        self.event_listen_worker.challenge_update.connect(self.receive_challenge_in)
        self.event_listen_worker.ongoing_game_update.connect(self.receive_game)
        self.event_listen_worker.state_update.connect(self.receive_state)

        self.event_listen_thread.started.connect(self.event_listen_worker.run_event)
        self.event_listen_thread.finished.connect(self.event_listen_thread.deleteLater)
        self.event_listen_thread.start()

        self.challenge_out_thread = QThread()
        self.challenge_out_worker = ChallengeOutTimer(self.client,self.config)
        self.challenge_out_worker.moveToThread(self.challenge_out_thread)
        
        self.challenge_out_worker.current_state.connect(self.auto_match_info_label.setText)
        self.challenge_out_worker.challenge_out.connect(self.receive_challenge_out)
        
        self.challenge_out_thread.started.connect(self.challenge_out_worker.run_event)
        self.challenge_out_thread.finished.connect(self.challenge_out_thread.deleteLater)
        self.challenge_out_thread.start()

    def receive_challenge_in(self,challenge:ChallengeJson,state:Literal['challenge','cancel','decline']):
        final_state = {
            'challenge':'发起',
            'cancel':'取消',
            'decline':'拒绝',
        }[state]

        match challenge['timeControl']['type']:
            case 'clock':
                time_control = challenge['timeControl']['show']
            case 'correnpondence':
                time_control = str(challenge['timeControl']['days']) + '天'
            case _:
                time_control = '未知'

        self.status_bar.showMessage(
            f'由{challenge["challenger"]["name"]}到{challenge['destUser']["name"]}的'
            f'{time_control + challenge["perf"]["name"]}'
            f'{'排位' if challenge["rated"] else '休闲'}挑战已经被{final_state + (
                f'，拒绝原因：{challenge["declineReason"]}'
                if state == 'decline' else ''
            )}',
            10000,
        )
    
    def receive_game(self,game:GameEventInfo,state:Literal['start','finish']):
        final_state = {
            'start':'开始',
            'finish':'结束',
        }[state]

        self.status_bar.showMessage(
            f'与{game["opponent"]["username"]}对弈的{game["perf"]}'
            f'{'排位' if game["rated"] else '休闲'}对局{game["gameId"]}已经{final_state}',
            10000,
        )

        if state == 'start':
            game_window = self.game_manager.addSubWindow(GameWindow(
                self.client,
                game['gameId'],
                self.config['basic_settings'],
            ))

            self.game_windows[game['gameId']] = game_window
            game_window.show()
        elif state == 'finish':
            QTimer.singleShot(15000,self.game_windows[game['gameId']].close)

    def receive_state(self,challenge_in:list[ChallengeJson],ongoing_game:list[GameEventInfo]):
        self.challenge_in.clear()
        self.current_game.clear()
        
        for challenge in challenge_in:
            item = QTreeWidgetItem(self.challenge_in)
        
            item.setText(0,challenge['id'])         
            item.setText(1,challenge['url'])        
            item.setText(2,challenge['status'])     
            item.setText(6,'是' if challenge['rated'] else '否')
            item.setText(7,challenge['speed'])      
            item.setText(9,challenge['color'])      
            item.setText(10,challenge['finalColor'])
            item.setText(12,challenge['direction']) 
        
            self.challenge_in.setItemWidget(item,3,InfoButton(challenge['challenger'],self.challenge_in))
            self.challenge_in.setItemWidget(item,4,InfoButton(challenge['destUser'],self.challenge_in))
            self.challenge_in.setItemWidget(item,5,InfoButton(challenge['variant'],self.challenge_in))
            self.challenge_in.setItemWidget(item,8,InfoButton(challenge['timeControl'],self.challenge_in))
            self.challenge_in.setItemWidget(item,11,InfoButton(challenge['perf'],self.challenge_in))
        
            if 'initialFen' in challenge:
                item.setText(13,challenge['initialFen'])
        
        for game in ongoing_game:
            item = QTreeWidgetItem(self.current_game)
        
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
        
            self.current_game.setItemWidget(item,6,InfoButton(game['status'],self.current_game))
            self.current_game.setItemWidget(item,7,InfoButton(game['variant'],self.current_game))
            self.current_game.setItemWidget(item,12,InfoButton(game['opponent'],self.current_game))

    def receive_challenge_out(self,challenge_out:ChallengeJson):
        self.challenge_out.clear()
        for challenge in challenge_out:
            item = QTreeWidgetItem(self.challenge_out)
        
            item.setText(0,challenge['id'])         
            item.setText(1,challenge['url'])        
            item.setText(2,challenge['status'])     
            item.setText(6,'是' if challenge['rated'] else '否')
            item.setText(7,challenge['speed'])      
            item.setText(9,challenge['color'])      
            item.setText(10,challenge['finalColor'])
            item.setText(12,challenge['direction']) 
        
            self.challenge_out.setItemWidget(item,3,InfoButton(challenge['challenger'],self.challenge_out))
            self.challenge_out.setItemWidget(item,4,InfoButton(challenge['destUser'],self.challenge_out))
            self.challenge_out.setItemWidget(item,5,InfoButton(challenge['variant'],self.challenge_out))
            self.challenge_out.setItemWidget(item,8,InfoButton(challenge['timeControl'],self.challenge_out))
            self.challenge_out.setItemWidget(item,11,InfoButton(challenge['perf'],self.challenge_out))
        
            if 'initialFen' in challenge:
                item.setText(13,challenge['initialFen'])

    def closeEvent(self, event:QCloseEvent):
        try:
            if self.challenge_out_thread.isRunning():
                self.challenge_out_worker.stop()
                self.challenge_out_thread.quit()
                self.challenge_out_thread.wait()
            self.challenge_out_thread.deleteLater()
        except AttributeError:pass
        super().closeEvent(event)

class GameWindow(QMainWindow):
    def __init__(self,client:Client,game_id:str,config:BasicSettings):
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
        self.config = config
        
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
        self.chat_and_record_widget = ChatAndRecordWidget(self.send_message,self.splitter)
        self.splitter.addWidget(self.chat_and_record_widget)

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
        self.worker = PlayChessStream(self.client,self.game_id,self.color,self.config)
        self.worker.moveToThread(self.worker_thread)

        self.worker.send_dict.connect(self.receive_dict)
        self.worker.engine_info_changed.connect(self.engine_info.set_dict)
        self.worker.state_changed.connect(self.status_bar.showMessage)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def receive_dict(self,value:EventInGame):
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

    def change_state(self,value:GameStste):
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
'''