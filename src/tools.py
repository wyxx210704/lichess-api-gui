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

class LoginWizard(QWizard):
    '''
    页面功能如下
    1. 创建token指引
    2. 使用token登录
    3. 将token添加到常用列表或者从常用列表删除
    '''

    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.login_success = False
        self.token = ''
        self.is_bot = False

        self.currentIdChanged.connect(self.check_login_state)
        self.setOptions(
            QWizard.WizardOption.NoDefaultButton|
            QWizard.WizardOption.HaveNextButtonOnLastPage|
            QWizard.WizardOption.HaveFinishButtonOnEarlyPages
        )

        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setWindowTitle('登录向导')
        self.setWindowIcon(QIcon(ICON))

        self.token_creation_guidelines()
        self.login_page()
        self.token_manager_page()

    def check_login_state(self,id_:int):
        if (id_ == 1):
            #登录页面是第二页，login_success变量会在login函数处理
            #该条件代表在登录页面并且还没登录成功，下一步按钮就不会亮
            self.page_2.change_state(self.login_success)

    def login(self):
        try:user_info = Client(TokenSession(self.token_input.text())).account.get()
        except Exception as error:
            self.state_display.setText(f'登录报错：{error}')
        else:
            if ('title' in user_info) and (user_info['title'] == 'BOT'):
                self.is_bot = True
            else:
                self.is_bot = False

            self.login_success = True
            self.token = self.token_input.text()
            self.page_2.change_state(True)
            self.state_display.setText(f'登录成功，这个账号{'是' if self.is_bot else '不是'}bot账号，下棋时用的API是{'bot' if self.is_bot else 'board'}')

    def load_config_with_format(self) -> ConfigFormat:
        return load(open(
            CONFIG,
            'r',
            encoding='utf-8',
            errors='ignore',
        ))

    def select_from_the_list(self,item:QListWidgetItem):self.token_input.setText(self.tokens[item.text()])
    def get_info(self):return Client(TokenSession(self.token)),self.is_bot

    def token_creation_guidelines(self):
        self.page_1 = QWizardPage(self)
        self.page_1.setTitle('登录lichess，创建当前登录状态token')
        self.page_1.setSubTitle('在此处登录lichess，拿到token来登录此程序')
        self.addPage(self.page_1)

        scroll_area = QScrollArea(self.page_1)
        scroll_area.setWidgetResizable(True)
        browser = QWebEngineView(self.page_1)
        browser.setFixedHeight(2300)
        browser.load(QUrl('https://wyxx210704.github.io/lichess-login'))
        scroll_area.setWidget(browser)
        QVBoxLayout(self.page_1).addWidget(scroll_area)

    def login_page(self):
        self.page_2 = ControllableWizardPage(self)
        self.page_2.setTitle('登录')
        self.page_2.setSubTitle('必须先在这里登录才能过得去')
        self.addPage(self.page_2)

        self.page_2_layout = QVBoxLayout(self.page_2)
        self.page_2_layout.addWidget(QLabel('请在下方输入token，或者从列表中选择'))

        self.tokens = self.load_config_with_format()['tokens']

        self.tokens_list = QListWidget(self.page_2)
        self.tokens_list.addItems([name for name in self.tokens.keys()])
        self.tokens_list.itemClicked.connect(self.select_from_the_list)
        self.page_2_layout.addWidget(self.tokens_list)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('输入token')
        self.page_2_layout.addWidget(self.token_input)

        self.login_button = QPushButton(
            '登录',
            self.page_2,
        )

        self.login_button.clicked.connect(self.login)
        self.page_2_layout.addWidget(self.login_button)

        self.state_display = StringDisplay(self.page_2)
        self.state_display.setPlaceholderText('登录的状态会显示在这里')
        self.page_2_layout.addWidget(self.state_display)

    def token_manager_page(self):
        self.page_3 = QWizardPage(self)
        self.page_3.setTitle('管理token')
        self.page_3.setSubTitle('如果有常用token的话，那就可以在这里管理，如果不需要就点完成按钮')
        self.addPage(self.page_3)

        token_manager = TokenManager(self.page_3)
        QVBoxLayout(self.page_3).addWidget(token_manager)

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