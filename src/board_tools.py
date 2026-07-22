from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThread,Qt
from berserk import Client
from berserk.types.challenges import ChallengeJson

from board_tools_thread_worker import *
from board_widget import InfoButton
from input_dialogs import *
from business_logic import get_error_details,show_error_dialog

class CreateChallengeDialog(QDialog):
    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent)
        self.setWindowTitle('创建挑战')
        self.layout_ = QFormLayout(self)

        self.normal_time = QRadioButton('普通对局',self)
        self.normal_time.setChecked(True)
        self.normal_time.clicked.connect(self.turn_to_normal_time)
        self.correspondence = QRadioButton('通讯棋',self)
        self.correspondence.clicked.connect(self.turn_to_correspondence)

        self.layout_.addRow(
            self.normal_time,
            self.correspondence,
        )

        self.clock_limit = QSpinBox(self)
        self.clock_limit.setRange(0,10800)
        self.layout_.addRow(
            '基本时间（秒）',
            self.clock_limit,
        )

        self.clock_increment = QSpinBox(self)
        self.clock_increment.setRange(0,180)
        self.layout_.addRow(
            '每步增加时间（秒）',
            self.clock_increment,
        )

        self.days = QSpinBox(self)
        self.days.setRange(1,14)
        self.days.setEnabled(False)
        self.layout_.addRow(
            '天数（仅限通讯棋）',
            self.days,
        )

        self.color = QComboBox(self)
        self.color.addItems([
            'white',
            'black',
            '随机',
        ])

        self.layout_.addRow(
            '颜色',
            self.color,
        )

        self.variant = QComboBox(self)
        self.variant.addItems([
            'standard',
            'chess960', 
            'kingOfTheHill', 
            'threeCheck', 
            'antichess', 
            'atomic', 
            'horde', 
            'racingKings', 
            'crazyhouse', 
            'fromPosition', 
        ])

        self.layout_.addRow(
            '变体',
            self.variant,
        )

        self.position = QLineEdit(self)
        self.position.setEnabled(False)
        self.variant.currentIndexChanged.connect(self.enable_position)
        self.layout_.addRow(
            '起始局面',
            self.position,
        )

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout_.addRow(self.buttons)

    def turn_to_normal_time(self):
        self.clock_limit.setEnabled(True)
        self.clock_increment.setEnabled(True)
        self.days.setEnabled(False)

    def turn_to_correspondence(self):
        self.clock_limit.setEnabled(False)
        self.clock_increment.setEnabled(False)
        self.days.setEnabled(True)

    def enable_position(self):
        self.position.setEnabled(self.variant.currentText() == 'fromPosition')

    def get_deta(self):
        return [
            self.clock_limit.value() if self.clock_limit.isEnabled() else None,
            self.clock_increment.value() if self.clock_increment.isEnabled() else None,
            self.days.value() if self.days.isEnabled() else None,
            None if self.color.currentText() == '随机' else self.color.currentText(),
            self.variant.currentText(),
            self.position.text() if self.position.isEnabled() else None,
        ]

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
        self.create_challenge_button.clicked.connect(self.create_challenge)
        self.layout_for_buttons.addWidget(self.create_challenge_button)

        self.match_ai_button = QPushButton('挑战AI',self)
        self.match_ai_button.clicked.connect(self.challenge_ai)
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

    def create_challenge(self):
        user_name = get_user_name(self,'输入被挑战的用户')
        is_rated = get_bool(self,'是否排位')
        dialog = CreateChallengeDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.client.challenges.create(
                    user_name,
                    is_rated,
                    *dialog.get_deta(),
                ) 
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '创建挑战时报错',
                    self,
                )

    def challenge_ai(self):
        ai_level = get_int(self,'输入AI等级',1,8)
        dialog = CreateChallengeDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.client.challenges.create_ai(
                    ai_level,
                    *dialog.get_deta(),
                ) 
            except Exception as error:
                show_error_dialog(
                    *get_error_details(error),
                    '创建挑战时报错',
                    self,
                )

    def create_game(self):
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
        
        self.create_game_worker.end_event.connect(self.create_game_end)
        self.create_game_worker.error_event.connect(self.receive_error)

        self.create_game_worker.moveToThread(self.create_game_thread)
        self.create_game_thread.started.connect(self.create_game_worker.run_event)
        self.create_game_thread.finished.connect(self.create_game_thread.deleteLater)
        self.create_game_thread.start()

        self.create_game_button.setEnabled(False)
        self.create_game_button.setText('等待中')

    def create_game_end(self):
        self.create_game_button.setEnabled(True)
        self.create_game_button.setText('在大厅中创建对局')

    def receive_error(self,error:Exception):
        show_error_dialog(
            *get_error_details(error),
            '创建对局时报错',
            self,
        )

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