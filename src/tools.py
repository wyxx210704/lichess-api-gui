from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from typing import Generator
from berserk import *
import chess
import chess.svg

from widgets import *
from settings import *
from thread_worker import GameViewerWorker

class GameViewer(QWidget):
    def __init__(self,generator:Generator):
        # 第一部分：初始化窗口
        super().__init__()
        self.splitter = QSplitter(Qt.Orientation.Horizontal,self)
        QVBoxLayout(self).addWidget(self.splitter)
        self.generator = generator
        
        self.setWindowTitle('对局查看器')
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

        # 第二部分：窗口顶层部件
        self.svg_widget = NoStretchingSvgWidget(self)
        self.tab_widget = QTabWidget(self)
        self.splitter.addWidget(self.svg_widget)#在左边
        self.splitter.addWidget(self.tab_widget)#在右边

        # 第三部分：tab_widget里的部件
        self.tree = JsonTreeWidget(self.tab_widget)
        self.tab_widget.addTab(self.tree,'基本信息')

        self.real_time_info_panel = QWidget(self.tab_widget)
        self.tab_widget.addTab(self.real_time_info_panel,'对局状态')
        self.info_panel_layout = QFormLayout(self.real_time_info_panel)

        # 第四部分：实时信息面板里的部件
        self.fen = InformationDisplay(self.real_time_info_panel)
        self.info_panel_layout.addRow('当前局面FEN',self.fen)

        self.white_clock = InformationDisplay(self.real_time_info_panel)
        self.info_panel_layout.addRow('白方剩余时间（秒）',self.white_clock)

        self.black_clock = InformationDisplay(self.real_time_info_panel)
        self.info_panel_layout.addRow('黑方剩余时间（秒）',self.black_clock)

        self.move_record = QListWidget(self.real_time_info_panel)
        self.info_panel_layout.addRow(self.move_record)

        # 第五部分：初始化最前面两行的数据
        game_info = next(self.generator)#第一行
        self.tree.set_dict(game_info)

        start_pos = next(self.generator)
        self.fen.setText(start_pos['fen'])
        self.white_clock.setText(str(start_pos['wc']))
        self.black_clock.setText(str(start_pos['bc']))
        self.svg_widget.load(self.fen_to_svg(start_pos['fen']))

        # 第六部分：启动线程并监听对局
        self.worker_thread = QThread()
        self.worker = GameViewerWorker(self.generator)

        self.worker.moveToThread(self.worker_thread)
        self.worker.send_dict.connect(self.receive_dict)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def receive_dict(self,dct:dict):
        if 'winner' in dct:#证明这是最后一个
            self.tree.set_dict(dct)
        else:
            self.fen.setText(dct['fen'])
            self.white_clock.setText(str(dct['wc']))
            self.black_clock.setText(str(dct['bc']))
            self.move_record.addItem(dct['lm'])
            self.svg_widget.load(self.fen_to_svg(dct['fen']))

    def fen_to_svg(self,fen_string:str):
        """
        传入FEN字符串，生成棋盘SVG图片
        
        参数:
            fen_string (str): 标准的FEN字符串，例如 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        
        返回:
            str: SVG格式的棋盘图片字符串
        
        示例:
            fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
            svg = fen_to_svg(fen)
            with open('board.svg', 'w') as f:
                f.write(svg)
        """
        try:
            # 从FEN字符串创建棋盘对象
            board = chess.Board(fen_string)
            
            # 生成SVG图片
            svg_string = chess.svg.board(board=board)
            
            return svg_string.encode('utf-8')
        
        except ValueError as e:
            raise ValueError(f"无效的FEN字符串: {fen_string}") from e

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
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

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
            '../configuration_and_resources/config.json',
            'r',
            encoding='utf-8',
            errors='ignore',
        ))

    def select_from_the_list(self,item:QListWidgetItem):self.token_input.setText(self.tokens[item.text()])
    def get_info(self):return self.token,self.is_bot

    def token_creation_guidelines(self):
        self.page_1 = QWizardPage(self)
        self.page_1.setTitle('创建token')
        self.page_1.setSubTitle('如果还不懂创建token，就在此创建，如果创建好了，那就前往下一页')
        self.addPage(self.page_1)

        md_display = QTextBrowser(self.page_1)
        QVBoxLayout(self.page_1).addWidget(md_display)
        md_display.setMarkdown('''
        1. 先进入[此页面](https://lichess.org/account/oauth/token)，点右上角+按钮，然后就会进入以下页面
        ![页面内容展示](https://api.keepwork.com/ts-storage/siteFiles/49798/raw#1782219326915image.png)
        2. 填好令牌（token）描述，只要能让自己记住就行
        3. 按需要勾选令牌（token）可执行的功能
        4. 滑到底部，点右下角创建按钮，即可创建
        ''')

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

        self.state_display = InformationDisplay(self.page_2)
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
    """
    自定义错误信息展示消息框
    
    参数:
        file_name: 错误发生文件名 (str)
        line_number: 错误发生行号 (int)
        error_type: 错误类型 (str)
        error_message: 错误信息 (str)
        title: 窗口标题 (str, 默认: "错误")
    """
    
    def __init__(self, file_name:str, line_number:int, error_type:str, error_message:str, title:str="错误", parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QFormLayout(self)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

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

class NoCloseProgressDialog(QProgressDialog):
    def __init__(self, labelText:str,parent:QWidget|None=None):
        super().__init__(labelText,None, 0,0, parent)
        self.setWindowTitle('进程正在执行中')
        self.setCancelButton(None)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

class SettingsWindow(QMainWindow):
    def __init__(self,client:Client):
        super().__init__()
        self.scroll_area = QScrollArea(self)
        self.setCentralWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)

        self.widget_in_scroll_area = QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.widget_in_scroll_area)
        self.layout_ = QVBoxLayout(self.widget_in_scroll_area)

        self.setMinimumWidth(335)
        self.setWindowTitle('设置')
        self.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

        self.add_widget(TokenManager(self.widget_in_scroll_area))
        self.add_widget(AutoLoginControl(self.widget_in_scroll_area))

        account_info = client.account.get()
        self.status_bar = self.statusBar()
        self.status_bar.addWidget(QLabel(f'当前登录账号：{account_info["username"]}'))
        self.status_bar.addWidget(QLabel(f'下棋客户端模式：{'bot' if ('title' in account_info) and (account_info["title"] == 'BOT') else '人类'}模式'))

    def add_widget(self,widget:BaseSettingsWidget):
        self.layout_.addWidget(widget)
        self.layout_.addWidget(HorizontalLine(self.widget_in_scroll_area))

class ChessPuzzleViewer(QMainWindow):
    def __init__(self):
        raise RuntimeError('该组件暂时不稳定，还属于内测阶段，暂时无法使用')
    # 剩余内测代码暂时不公开展示