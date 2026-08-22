from PyQt6.QtWidgets import *
from berserk import Client
from datetime import *
from typing import get_args
from berserk.types.common import Color,PerfType

class GetUserNameDialog(QDialog):
    def __init__(self,client:Client,parent:QWidget|None = None):
        super().__init__(parent)
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(QLabel('请输入一个用户'))

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText('在此处输入用户')
        self.layout_.addWidget(self.line_edit)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        self.layout_.addWidget(line)
        self.layout_.addWidget(QLabel('或者在已关注列表中选择用户'))

        self.list_widget = QListWidget(self)
        self.list_widget.currentTextChanged.connect(self.line_edit.setText)
        self.layout_.addWidget(self.list_widget)

        for user in client.relations.get_users_followed():
            self.list_widget.addItem(user['username'])

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout_.addWidget(self.buttons)

    def get_user_name(self):return self.line_edit.text()

class GetExportGameOprationDialog(QDialog):
    def __init__(self,parent:QWidget|None = None):
        '''
        现在标出两个函数共有的参数

        以下是export的定义
        def export(
            self,
            game_id: str,
            as_pgn: bool | None = None,
            
           #moves: bool | None = None,
           #tags: bool | None = None,
           #clocks: bool | None = None,
           #evals: bool | None = None,
           #opening: bool | None = None,
           #literate: bool | None = None,
        ) -> str | Dict[str, Any]

        以下是export_by_player的定义
        def export_by_player(
            self,
            username: str,
            as_pgn: bool | None = None,

            since: int | None = None,
            until: int | None = None,
            max: int | None = None,
            vs: str | None = None,
            rated: bool | None = None,
            perf_type: PerfType | None = None,
            color: Color | None = None,
            analysed: bool | None = None,
           #moves: bool | None = None,
            pgn_in_json: bool | None = None,
           #tags: bool | None = None,
           #clocks: bool | None = None,
           #evals: bool | None = None,
           #opening: bool | None = None,
            ongoing: bool | None = None,
            finished: bool | None = None,
            players: str | None = None,
            sort: str | None = None,
           #literate: bool | None = None,
        ) -> Iterator[str] | Iterator[Dict[str, Any]]
        '''

        super().__init__(parent)
        self.setWindowTitle('导出对局选项')
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(QLabel('导出对局时要添加的一些东西'))

        self.moves = QCheckBox('走棋步骤',self)
        self.tags = QCheckBox('标签',self)
        self.clocks = QCheckBox('时钟',self)
        self.evals = QCheckBox('分析',self)
        self.opening = QCheckBox('开局',self)
        self.literate = QCheckBox('注释',self)

        self.layout_.addWidget(self.moves)
        self.layout_.addWidget(self.tags)
        self.layout_.addWidget(self.clocks)
        self.layout_.addWidget(self.evals)
        self.layout_.addWidget(self.opening)
        self.layout_.addWidget(self.literate)
    
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
    
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout_.addWidget(self.buttons)

    def get_value(self):return {
        'moves':self.moves.isChecked(),
        'tags':self.tags.isChecked(),
        'clocks':self.clocks.isChecked(),
        'evals':self.evals.isChecked(),
        'opening':self.opening.isChecked(),
        'literate':self.literate.isChecked(),
    }

class GetExportGameScreeningDialog(QDialog):
    def __init__(self,parent:QWidget|None = None):
        '''
        现在标出不需要传的参数
    
        以下是export_by_player的定义
        def export_by_player(
            self,
            username: str,
            as_pgn: bool | None = None,
    
            since: int | None = None,
            until: int | None = None,
            max: int | None = None,
            vs: str | None = None,
            rated: bool | None = None,
            perf_type: PerfType | None = None,
            color: Color | None = None,
            analysed: bool | None = None,
           #moves: bool | None = None,
            pgn_in_json: bool | None = None,
           #tags: bool | None = None,
           #clocks: bool | None = None,
           #evals: bool | None = None,
           #opening: bool | None = None,
            ongoing: bool | None = None,
            finished: bool | None = None,
            players: str | None = None,
            sort: str | None = None,
           #literate: bool | None = None,
        ) -> Iterator[str] | Iterator[Dict[str, Any]]
        '''
    
        super().__init__(parent)
        self.setWindowTitle('导出对局筛选')
        self.layout_ = QFormLayout(self)
        self.layout_.addRow(QLabel('左侧复选框表示是否按该项筛选'))

        minimum_datetime = datetime(
            2013,
            1,
            1,
            0,
            0,
            0,
            70000,
            timezone.utc,
        )# API文档就是这样写的，不信就看https://lichess.org/api#tag/games/GET/api/games/user/{username}

        self.enable_since = QCheckBox('从',self)
        self.enable_until = QCheckBox('到',self)
        self.enable_max = QCheckBox('最多',self)
        self.enable_vs = QCheckBox('对手',self)
        self.enable_rated = QCheckBox('排位',self)
        self.enable_perf_type = QCheckBox('种类',self)
        self.enable_color = QCheckBox('颜色',self)
        self.enable_analysed = QCheckBox('分析',self)

        self.enable_since.clicked.connect(lambda:self.since.setEnabled(self.enable_since.isChecked()))
        self.enable_until.clicked.connect(lambda:self.until.setEnabled(self.enable_until.isChecked()))
        self.enable_max.clicked.connect(lambda:self.max_.setEnabled(self.enable_max.isChecked()))
        self.enable_vs.clicked.connect(lambda:self.vs.setEnabled(self.enable_vs.isChecked()))
        self.enable_rated.clicked.connect(lambda:self.rated.setEnabled(self.enable_rated.isChecked()))
        self.enable_perf_type.clicked.connect(lambda:self.perf_type.setEnabled(self.enable_perf_type.isChecked()))
        self.enable_color.clicked.connect(lambda:self.color.setEnabled(self.enable_color.isChecked()))
        self.enable_analysed.clicked.connect(lambda:self.analysed.setEnabled(self.enable_analysed.isChecked()))
        
        self.since = QDateTimeEdit(self)
        self.until = QDateTimeEdit(self)
        self.max_ = QSpinBox(self)
        self.vs = QLineEdit(self)
        self.rated = QCheckBox('否',self)
        self.perf_type = QComboBox(self)
        self.color = QComboBox(self)
        self.analysed = QCheckBox('否',self)
        
        self.since.setDateTimeRange(minimum_datetime,datetime.now())
        self.since.setDateTime(datetime.now() - timedelta(weeks=8))
        self.until.setDateTimeRange(minimum_datetime,datetime.now())
        self.until.setDateTime(datetime.now())
        self.max_.setRange(1,1000)
        self.rated.clicked.connect(lambda:self.rated.setText('是' if self.rated.isChecked() else '否'))
        self.perf_type.addItems(["bullet", "blitz", "rapid", "classical", "ultraBullet","chess960",
        "kingOfTheHill","threeCheck","antichess","atomic","horde","racingKings","crazyhouse","fromPosition"])
        self.color.addItems(["white", "black"])
        self.analysed.clicked.connect(lambda:self.analysed.setText('是' if self.analysed.isChecked() else '否'))

        #因为那些筛选按钮默认是不勾选的所以呢这些要跟着设置不给用
        self.since.setEnabled(False)
        self.until.setEnabled(False)
        self.max_.setEnabled(False)
        self.vs.setEnabled(False)
        self.rated.setEnabled(False)
        self.perf_type.setEnabled(False)
        self.color.setEnabled(False)
        self.analysed.setEnabled(False)

        self.layout_.addRow(self.enable_since,self.since)
        self.layout_.addRow(self.enable_until,self.until)
        self.layout_.addRow(self.enable_max,self.max_)
        self.layout_.addRow(self.enable_vs,self.vs)
        self.layout_.addRow(self.enable_rated,self.rated)
        self.layout_.addRow(self.enable_perf_type,self.perf_type)
        self.layout_.addRow(self.enable_color,self.color)
        self.layout_.addRow(self.enable_analysed,self.analysed)

        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        self.layout_.addRow(line)

        self.ongoing = QCheckBox('正在进行的对局',self)
        self.finished_ = QCheckBox('已结束的对局',self)
        self.pgn_in_json = QCheckBox('PGN在JSON里',self)
        self.sort = QComboBox(self)

        self.sort.addItems(['dateAsc','dateDesc'])
        self.sort.setCurrentIndex(1)
        self.ongoing.setChecked(True)
        self.finished_.setChecked(True)

        self.layout_.addRow(
            self.ongoing,
            self.finished_,
        )

        self.layout_.addRow(
            self.pgn_in_json,
            self.sort,
        )
    
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout_.addRow(self.buttons)

    def get_value(self):return {
        'since':self.since.dateTime().toUTC().toMSecsSinceEpoch() if self.since.isEnabled() else None,
        'until':self.until.dateTime().toUTC().toMSecsSinceEpoch() if self.until.isEnabled() else None,

        'max':self.max_.value()                     if self.max_.isEnabled() else None,
        'vs':self.vs.text()                         if self.vs.isEnabled() else None,
        'rated':self.rated.isChecked()              if self.rated.isEnabled() else None,
        'perf_type':self.perf_type.currentText()    if self.perf_type.isEnabled() else None,
        'color':self.color.currentText()            if self.color.isEnabled() else None,
        'analysed':self.analysed.isChecked()        if self.until.isEnabled() else None,

        'pgn_in_json':self.pgn_in_json.isChecked(),
        'ongoing':self.ongoing.isChecked(),
        'finished':self.finished_.isChecked(),
        'players':None,
        'sort':self.sort.currentText(),
    }

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