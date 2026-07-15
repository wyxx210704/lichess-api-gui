from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThread
from berserk import Client
from berserk.types.challenges import ChallengeJson

from board_tools_thread_worker import *
from board_widget import InfoButton
from input_dialogs import *

class ChallengeWindow(QWidget):
    def __init__(self,client:Client):
        super().__init__()
        self.client = client
        self.create_game_thread = None
        self.create_game_worker = None
        
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

        self.layout_for_buttons = QHBoxLayout()
        self.layout_.addLayout(self.layout_for_buttons)

        self.create_challenge_button = QPushButton('创建',self)
        self.create_challenge_button.clicked.connect(lambda:self.client.challenges.create(
            get_user_name(self,'输入被挑战的用户'),
            get_bool(self,'是否排位'),
            get_int(self,'输入基础时间（秒）',1,10800),
            get_int(self,'输入每步增加时间（秒）',1,180),
            None,
            get_item(self,'选择自己执棋颜色',["white", "black"]),
            (get_item(self,'选择变体',[
                "chess960",
                "kingOfTheHill",
                "threeCheck",
                "antichess",
                "atomic",
                "horde",
                "racingKings",
                "crazyhouse",
            ]) if get_bool(
                self,
                '是否为变体',
            ) else None),
        ))
        self.layout_for_buttons.addWidget(self.create_challenge_button)

        self.match_ai_button = QPushButton('挑战AI',self)
        self.match_ai_button.clicked.connect(lambda:self.client.challenges.create_ai(
            get_int(self,'输入AI等级',1,8),
            get_int(self,'输入基础时间（秒）',1,10800),
            get_int(self,'输入每步增加时间（秒）',1,180),
            None,
            get_item(self,'选择自己执棋颜色',["white", "black"]),
            (get_item(self,'选择变体',[
                "chess960",
                "kingOfTheHill",
                "threeCheck",
                "antichess",
                "atomic",
                "horde",
                "racingKings",
                "crazyhouse",
            ]) if get_bool(
                self,
                '是否为变体',
            ) else None),
        ))
        self.layout_for_buttons.addWidget(self.match_ai_button)

        self.create_game_button = QPushButton('在大厅中创建对局',self)
        self.create_game_button.clicked.connect(self.create_game)
        self.layout_for_buttons.addWidget(self.create_game_button)

        self.start_thread()

    def start_thread(self):
        self.worker_thread = QThread()
        self.worker = ChallengeListen(self.client)
        self.worker.moveToThread(self.worker_thread)
        self.worker.challenge_update.connect(self.receive_challenge)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def create_game(self):
        self.create_game_button.setEnabled(False)
        self.create_game_button.setText('等待中')

        time = get_int(self,'输入基础时间（分钟）',0,180)
        incr = get_int(self,'输入每步增加时间（秒）',0,180)
        
        variant = (get_item(self,'选择变体',[
            "chess960",
            "kingOfTheHill",
            "threeCheck",
            "antichess",
            "atomic",
            "horde",
            "racingKings",
            "crazyhouse",
        ]) if get_bool(
            self,
            '是否为变体',
        ) else 'standard')

        if variant == 'standard':
            # 这里时间分配用的逻辑跟官方一致
            minute = (time + (incr + 40)) // 60

            if minute < 3:perf = 'bullet'
            elif (minute >= 3) and (minute < 8):perf = 'blitz'
            elif (minute >= 8) and (minute < 25):perf = 'rapid'
            elif minute >= 25:perf = 'classical'
        else:perf = variant

        if self.create_game_thread is not None:
            if self.create_game_thread.isRunning():
                self.create_game_thread.quit()
                self.create_game_thread.wait()
            self.create_game_thread.deleteLater()
            self.create_game_thread = None
            self.create_game_worker = None

        self.create_game_thread = QThread()
        self.create_game_worker = CreateGameWorker(
            self.client,
            time,
            incr,
            get_bool(self,'是否排位'),
            variant,
            get_item(self,'选择自己执棋颜色',["white", "black",'random']),
            (
                get_int(self,'期待匹配到等级分最低的对手是多少分',400,self.client.account.get()['perfs'][perf]['rating']),
                get_int(self,'期待匹配到等级分最高的对手是多少分',self.client.account.get()['perfs'][perf]['rating'],3000),
            )
        )

        self.create_game_worker.moveToThread(self.create_game_thread)
        self.create_game_worker.end_event.connect(self.create_game_end)
        self.create_game_thread.started.connect(self.create_game_worker.run_event)
        self.create_game_thread.start()

    def create_game_end(self):
        self.create_game_button.setEnabled(True)
        self.create_game_button.setText('在大厅中创建对局')

    def receive_challenge(self,challenge_dict:dict[str, list[ChallengeJson]]):
        self.tree_widget.clear()
        for challenge in challenge_dict['out']:
            item = QTreeWidgetItem(self.tree_widget)

            item.setText(0,challenge['id'])         
            item.setText(1,challenge['url'])        
            item.setText(2,challenge['status'])     
            item.setText(6,'是' if challenge['rated'] else '否')
            item.setText(7,challenge['speed'])      
            item.setText(9,challenge['color'])      
            item.setText(10,challenge['finalColor'])
            item.setText(12,challenge['direction']) 

            self.tree_widget.setItemWidget(item,3,InfoButton(challenge['challenger'],self.tree_widget))
            self.tree_widget.setItemWidget(item,4,InfoButton(challenge['destUser'],self.tree_widget))
            self.tree_widget.setItemWidget(item,5,InfoButton(challenge['variant'],self.tree_widget))
            self.tree_widget.setItemWidget(item,8,InfoButton(challenge['timeControl'],self.tree_widget))
            self.tree_widget.setItemWidget(item,11,InfoButton(challenge['perf'],self.tree_widget))

            if 'initialFen' in challenge:
                item.setText(13,challenge['initialFen'])

    def closeEvent(self, a0):
        if self.worker_thread is not None:
            if self.worker_thread.isRunning():
                if self.worker is not None:
                    self.worker.stop()
                self.worker_thread.quit()
                self.worker_thread.wait()
            self.worker_thread.deleteLater()
            self.worker_thread = None
            self.worker = None

        super().closeEvent(a0)