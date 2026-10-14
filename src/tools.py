from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from typing import Generator
from berserk import *
from berserk.exceptions import ResponseError
from datetime import datetime

from .widgets import *
from .settings import *
from .thread_worker import *
from .costants import *
from .app_basic import apply_style

class GameViewer(QMainWindow):
    def __init__(self,game_generator:Generator):
        super().__init__()
        first_deta = next(game_generator)
        second_deta = next(game_generator)

        self.info_widget = GameInfoWidget(self)
        self.chess_board = ChessBoardWidget(
            [],
            self,
            first_deta['variant']['key'],
            self.info_widget,
            second_deta['fen'],
        )

        self.setWindowTitle('观看对局')
        self.setWindowIcon(QIcon(ICON))
        apply_style(self)
        self.setCentralWidget(self.chess_board)
        self.info_widget.load_info(
            first_deta['id'],
            first_deta['speed'],
            first_deta['rated'],
            first_deta['perf'],
            datetime.fromtimestamp(first_deta['createdAt'] / 1000),
            second_deta['fen'],
            timedelta(),
            0,#数据不提供基本时间跟每步增加时间,
            first_deta['variant']['key'],
            first_deta['variant']['name'],
            first_deta['variant']['short'],
            first_deta['players']['white'],
            first_deta['players']['black'],
        )

        self.status_bar = self.statusBar()
        if ('wc' in second_deta) and ('bc' in second_deta):
            self.status_bar.showMessage(f'对局开始，白方初始时钟：{second_deta['wc']}，黑方初始时钟：{second_deta['bc']}')

        self.worker_thread = QThread()
        self.worker = GameViewerWorker(game_generator)
    
        self.worker.moveToThread(self.worker_thread)
        self.worker.send_dict.connect(self.receive_dict)
    
        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def receive_dict(self,deta:dict):
        # 这里由于有判断逻辑，所以请大家使用下方的example函数进行查看，证明为什么要这样子设计

        if 'status' in deta:#证明这是最后一个
            text = f'对局因{deta['status']['name']}结束'

            if 'winner' in deta:
                text += f'，胜利方是{deta['winner']}'

            if 'drawOffers' in deta:
                text += ('，和棋请求在' 
                + '、'.join([str(number / 2) 
                for number in sorted(deta['drawOffers'])])
                + '这些棋步中出现')

            if 'ratingDiff' in deta['players']['white']:
                white_diff = deta['players']['white']['ratingDiff']
                if white_diff > 0:text += f'，白方等级分增加了{white_diff}分'
                elif white_diff == 0:text += f'，白方等级分不变'
                elif white_diff < 0:text += f'，白方等级分减少了{white_diff}分'

            if 'ratingDiff' in deta['players']['black']:
                black_diff = deta['players']['black']['ratingDiff']
                if black_diff > 0:text += f'，黑方等级分增加了{black_diff}分'
                elif black_diff == 0:text += f'，黑方等级分不变'
                elif black_diff < 0:text += f'，黑方等级分减少了{black_diff}分'

            self.status_bar.showMessage(text)
        else:
            self.chess_board.append_move(deta['lm']),

            if ('wc' in deta) and ('bc' in deta):
                self.status_bar.showMessage(f'对局进行中，白方剩余时间：{deta['wc']}，黑方剩余时间：{deta['bc']}')
        
    def example(self):
        'game_viewer_example'
        #示例数据太长，请跳转到game_viewer_example.py
        #如果使用vscode，可以直接ctrl+左键以上字符串就能直接跳转

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.layout_ = QVBoxLayout(self)

        self.setWindowTitle('选择权限')
        self.setWindowIcon(QIcon(ICON))
        apply_style(self)
        self.layout_.addWidget(QLabel('在这里选择权限，可以选择是否自动登录'))

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['scope','描述'])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.layout_.addWidget(self.tree)

        self.tree.addTopLevelItems([self.create_item(scope,description) for scope,description in {
            'email:read':'读取邮箱地址',
            'preference:read':'读取偏好设置',
            'preference:write':'写入偏好设置',

            'challenge:read':'读取收到的挑战',
            'challenge:write':'发送、接受和拒绝挑战',
            'challenge:bulk':'为其他棋手批量创建对局',

            'puzzle:read':'读取谜题活动记录',
            'puzzle:write':'解答谜题',
            'racer:write':'创建和加入谜题赛事',

            'study:read':'读取私人研习与直播',
            'study:write':'创建、更新、删除研习与直播',

            'engine:read':'查看和使用您的外部引擎',
            'engine:write':'创建和更新外部引擎',

            'follow:read':'读取已关注的棋手',
            'follow:write':'关注和取消关注其他棋手',
            'msg:write':'向其他棋手发送私信',
            'note:write':'查看和撰写其他棋手的备注',

            'team:read':'读取私人团队信息',
            'team:write':'加入和离开团队',
            'team:lead':'管理您所带领的团队：发送私信、移除成员',

            'tournament:read':'查看私人锦标赛',
            'tournament:write':'创建、更新和加入锦标赛',

            'board:play':'使用棋盘 API 进行对局',
            'bot:play':'使用机器人 API 进行对局'
        }.items()])

        self.auto_login = QCheckBox('自动登录',self)
        self.layout_.addWidget(self.auto_login)

        self.confirm_button = QPushButton('选择账号并登录',self)
        self.confirm_button.clicked.connect(self.accept)
        self.layout_.addWidget(self.confirm_button)

    def get_data(self):
        return {
            'auto_login':self.auto_login.isChecked(),
            'scopes':' '.join([item.text(0) for item in self.tree.selectedItems()])
        }

    def create_item(self,scope:str,description:str):
        item = QTreeWidgetItem()
        item.setText(0,scope)
        item.setText(1,description)
        return item

class ErrorMessageBox(QDialog):
    def __init__(self, file_name:str, line_number:int, error_type:str, error_message:str, title:str="错误", parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QFormLayout(self)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(ICON))

        self.file_name = file_name
        self.line_number = str(line_number)
        self.error_type = error_type
        self.error_message = error_message

        self.layout_.addRow('文件名称',QLabel(self.file_name))
        self.layout_.addRow('第几行',QLabel(self.line_number))
        self.layout_.addRow('报错类型',QLabel(self.error_type))
        self.layout_.addRow('报错信息',QLabel(self.error_message))

        self.button_1 = QPushButton(
            '复制',
            self
        )

        self.button_2 = QPushButton(
            '完成',
            self
        )

        self.button_1.clicked.connect(self.copy_info_to_clipboard)
        self.button_2.clicked.connect(self.accept)
        self.layout_.addRow(self.button_1,self.button_2)

    def copy_info_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(
            f'''
            报错日志
            ------------------------------
            文件名称：{self.file_name}
            第几行：{self.line_number}
            报错类型：{self.error_type}
            报错信息：{self.error_message}
            '''
        )

class ApiErrorMessageBox(QDialog):
    def __init__(self, error:ResponseError, title:str="错误", parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QFormLayout(self)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(ICON))

        self.status_code = error.status_code
        self.reason = error.reason
        self.cause = error.cause

        self.layout_.addRow('状态码',QLabel(str(self.status_code)))
        self.layout_.addRow('报错文字',QLabel(str(self.reason)))
        self.layout_.addRow('详细信息',QLabel(str(self.cause)))

        self.button_1 = QPushButton(
            '复制',
            self
        )

        self.button_2 = QPushButton(
            '完成',
            self
        )

        self.button_1.clicked.connect(self.copy_info_to_clipboard)
        self.button_2.clicked.connect(self.accept)
        self.layout_.addRow(self.button_1,self.button_2)

    def copy_info_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(
            f'''
            api调用出错
            ------------------------------
            状态码：{self.status_code}
            报错文字：{self.reason}
            详细信息：{self.cause}
            '''
        )

class SettingsWindow(QMainWindow):
    def __init__(self,client:Client):
        super().__init__()
        self.scroll_area = QScrollArea(self)
        self.setCentralWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)

        self.widget_in_scroll_area = QWidget(self.scroll_area)
        self.widget_in_scroll_area.setObjectName('settings_area')
        self.widget_in_scroll_area.setStyleSheet('#settings_area {background: transparent;}')
        self.scroll_area.setWidget(self.widget_in_scroll_area)
        self.layout_ = QVBoxLayout(self.widget_in_scroll_area)

        self.setMinimumWidth(375)
        self.setWindowTitle('设置')
        self.setWindowIcon(QIcon(ICON))
        apply_style(self)

        self.layout_.addWidget(TokenManager(self.widget_in_scroll_area))
        self.layout_.addWidget(AutoLoginControl(self.widget_in_scroll_area))
        self.layout_.addWidget(FunctionSettings(self.widget_in_scroll_area))

        self.status_bar = self.statusBar()
        self.status_bar.addWidget(QLabel(f'当前登录账号：{client.account.get()["username"]}，此页面的设置项都是重启后生效'))

class GeneratorToListDialog(QProgressDialog):
    def __init__(self,generator:Generator,parent:QWidget|None=None):
        super().__init__(
            '当前生成器正在处理信息中，请等候',
            '取消',
            0,
            0,
            parent,
        )

        self.setWindowTitle('进程执行中')
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowCloseButtonHint)
        self.canceled.connect(self.cancel_event)

        self.worker_thread = QThread()
        self.worker = GeneratorToListWorker(generator)
        
        self.worker.moveToThread(self.worker_thread)
        self.worker.send_list.connect(self.receive_list)
        
        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.on_thread_end)
        self.worker_thread.start()

    def receive_list(self,final_list:list):self.final_list = final_list
    def get_list(self):return self.final_list

    def on_thread_end(self):
        self.worker_thread.deleteLater()
        self.accept()

    def stop_thread(self):
        if self.worker_thread.isRunning():
            self.worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()

    def closeEvent(self,event:QCloseEvent):
        self.stop_thread()
        super().closeEvent(event)

    def cancel_event(self):
        self.stop_thread()
        self.reject()