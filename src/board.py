from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *

class BoardMain(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.test_action()

    def test_action(self):
        self.action = QAction('测试')
        self.action.triggered.connect(lambda:QMessageBox.information(self,
        '恭喜你点开了彩蛋','下一版本的时候，将完善这个页面，下两个版本的时候，就要开始搞功能了'))
        self.tool_bar.addAction(self.action)

    def page_challenge(self):
        self.challenge_page = QWidget(self.splitter)
        self.splitter.addWidget(self.challenge_page)
        self.vertical_layout_in_challenge_page = QVBoxLayout(self.challenge_page)
        self.vertical_layout_in_challenge_page.addWidget(QLabel('挑战列表（暂未启用）'))

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
                '两个版本之后',
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
                '两个版本之后',
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