from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from typing import Generator
from berserk import *
from json import load
import chess
import chess.svg

from widgets import *
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

        self.tokens = load(open(
            '../configuration_and_resources/config.json',
            'r',
            encoding='utf-8',
            errors='igmore',
        ))['tokens']

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

class ChessPuzzleViewer(QMainWindow):
    def __init__(self, puzzle_data):
        raise RuntimeError('该组件暂时不稳定，还属于内测阶段，暂时无法使用')

        super().__init__()
        self.puzzle_data = puzzle_data
        self.board = chess.Board()
        self.move_history = []
        self.solution_moves = []
        self.all_moves = []  # 所有走法（PGN + 解）
        self.current_move_index = -1
        
        # 解析数据
        self.parse_pgn()
        self.parse_solution()
        
        # 设置界面
        self.setWindowTitle("国际象棋谜题查看器")
        self.setMinimumSize(900, 700)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧：棋盘
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(500)
        
        self.board_widget = QSvgWidget()
        left_layout.addWidget(self.board_widget)
        
        # 添加走法计数标签
        self.move_label = QLabel("步数: 0/0")
        self.move_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.move_label.setFont(QFont("Arial", 12))
        left_layout.addWidget(self.move_label)
        
        main_layout.addWidget(left_widget)
        
        # 右侧：信息面板
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_widget.setMinimumWidth(350)
        
        # 右上角：谜题信息
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_widget.setLayout(info_layout)
        
        info_label = QLabel("谜题信息")
        info_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        info_layout.addWidget(info_label)
        
        # 显示谜题信息
        self.info_text = QLabel()
        self.info_text.setFont(QFont("Courier New", 10))
        self.info_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.update_info()
        info_layout.addWidget(self.info_text)
        
        right_layout.addWidget(info_widget)
        
        # 右下角：走法列表
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_widget.setLayout(list_layout)
        
        list_label = QLabel("走法列表")
        list_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        list_layout.addWidget(list_label)
        
        self.move_list = QListWidget()
        self.move_list.setFont(QFont("Courier New", 11))
        self.move_list.itemClicked.connect(self.on_move_selected)
        list_layout.addWidget(self.move_list)
        
        right_layout.addWidget(list_widget)
        
        # 设置右侧布局的比例
        right_layout.setStretch(0, 1)
        right_layout.setStretch(1, 2)
        
        self.build_all_moves()
        # 更新棋盘到初始位置（PGN结束/解开始的位置）
        self.jump_to_transition()
        
    def parse_pgn(self):
        """解析PGN走法"""
        pgn_str = self.puzzle_data['game']['pgn']
        moves = pgn_str.split()
        
        for move_str in moves:
            try:
                # 尝试解析走法
                move = self.board.parse_san(move_str)
                self.board.push(move)
                self.move_history.append(move_str)
            except ValueError:
                # 如果解析失败，可能是结果标记或其他内容
                pass
                
    def parse_solution(self):
        """解析谜题解"""
        self.board = chess.Board()
        # 重置棋盘并重新播放PGN到初始位置
        self.board.reset()
        pgn_str = self.puzzle_data['game']['pgn']
        moves = pgn_str.split()
        for move_str in moves:
            try:
                move = self.board.parse_san(move_str)
                self.board.push(move)
            except ValueError:
                pass
        
        # 现在应用解
        solution = self.puzzle_data['puzzle']['solution']
        for move_uci in solution:
            move = self.board.parse_uci(move_uci)
            san = self.board.san(move)
            self.board.push(move)
            self.solution_moves.append(san)
            
    def build_all_moves(self):
        """构建所有走法列表（PGN + 解）"""
        # 重置棋盘
        self.board = chess.Board()
        
        # 先添加PGN走法（使用SAN格式）
        pgn_str = self.puzzle_data['game']['pgn']
        pgn_moves = pgn_str.split()
        for move_str in pgn_moves:
            try:
                move = self.board.parse_san(move_str)
                san = self.board.san(move)
                self.board.push(move)
                self.all_moves.append({
                    'san': san,
                    'type': 'pgn',
                    'move': move
                })
            except ValueError:
                pass
        
        # 记录交界处的索引
        self.transition_index = len(self.all_moves) - 1
        
        # 添加解走法（使用SAN格式）
        self.board = chess.Board()
        # 重置并重播PGN
        pgn_str = self.puzzle_data['game']['pgn']
        pgn_moves = pgn_str.split()
        for move_str in pgn_moves:
            try:
                move = self.board.parse_san(move_str)
                self.board.push(move)
            except ValueError:
                pass
        
        for move_uci in self.puzzle_data['puzzle']['solution']:
            move = self.board.parse_uci(move_uci)
            san = self.board.san(move)
            self.board.push(move)
            self.all_moves.append({
                'san': san,
                'type': 'solution',
                'move': move
            })
        
        # 更新列表显示
        self.populate_list()
        
    def populate_list(self):
        """填充走法列表"""
        self.move_list.clear()
        
        for i, move_info in enumerate(self.all_moves):
            item = QListWidgetItem(move_info['san'])
            
            # 根据类型设置颜色
            if move_info['type'] == 'pgn':
                item.setForeground(QColor(40, 40, 200))  # 蓝色
                item.setBackground(QColor(240, 240, 255))
            else:
                item.setForeground(QColor(200, 40, 40))  # 红色
                item.setBackground(QColor(255, 240, 240))
            
            # 添加步数前缀
            move_number = (i // 2) + 1
            if i % 2 == 0:
                display_text = f"{move_number}. {move_info['san']}"
            else:
                display_text = f"{move_number}... {move_info['san']}"
            
            # 如果是解的开始，添加标记
            if i == self.transition_index + 1:
                display_text = "▶ " + display_text
            
            item.setText(display_text)
            self.move_list.addItem(item)
            
    def update_board(self, index):
        """更新棋盘到指定步数"""
        if index < 0 or index >= len(self.all_moves):
            return
            
        # 重置棋盘
        self.board = chess.Board()
        
        # 重播到指定步数
        for i in range(index + 1):
            move_info = self.all_moves[i]
            move = move_info['move']
            # 需要从UCI重新解析，因为move对象在reset后会失效
            self.board.push(move)
        
        self.current_move_index = index
        
        # 更新棋盘显示
        self.update_board_display()
        
        # 更新标签
        total = len(self.all_moves)
        self.move_label.setText(f"步数: {index + 1}/{total}")
        
    def update_board_display(self):
        """更新棋盘SVG显示"""
        try:
            svg_data = chess.svg.board(
                self.board,
                size=450,
                coordinates=True,
                style="margin: 0px;"
            )
            self.board_widget.load(QByteArray(svg_data.encode('utf-8')))
        except Exception as e:
            print(f"更新棋盘时出错: {e}")
            
    def jump_to_transition(self):
        """跳转到PGN和解的交界处"""
        if self.transition_index >= 0:
            self.update_board(self.transition_index)
            # 高亮列表中的对应项
            self.move_list.setCurrentRow(self.transition_index)
            self.move_list.scrollToItem(self.move_list.item(self.transition_index))
            
    def on_move_selected(self, item):
        """处理列表项选择事件"""
        row = self.move_list.row(item)
        self.update_board(row)
        
    def update_info(self):
        """更新谜题信息显示（中文标签）"""
        puzzle = self.puzzle_data['puzzle']
        game = self.puzzle_data['game']
        players = game['players']
        
        white = next(p for p in players if p['color'] == 'white')
        black = next(p for p in players if p['color'] == 'black')
        
        # 主题翻译映射
        theme_translation = {
            'veryLong': '非常长',
            'endgame': '残局',
            'crushing': '压倒性',
            'pawnEndgame': '兵残局',
            'defensiveMove': '防守走法',
            'advantage': '优势',
            'mate': '将杀',
            'mateIn1': '一步将杀',
            'mateIn2': '两步将杀',
            'mateIn3': '三步将杀',
            'mateIn4': '四步将杀',
            'mateIn5': '五步将杀',
            'mateIn6': '六步将杀',
            'mateIn7': '七步将杀',
            'mateIn8': '八步将杀',
            'mateIn9': '九步将杀',
            'mateIn10': '十步将杀',
            'middlegame': '中局',
            'opening': '开局',
            'queenEndgame': '后残局',
            'rookEndgame': '车残局',
            'knightEndgame': '马残局',
            'bishopEndgame': '象残局',
            'queenRookEndgame': '后车残局',
            'queenBishopEndgame': '后象残局',
            'queenKnightEndgame': '后马残局',
            'rookBishopEndgame': '车象残局',
            'rookKnightEndgame': '车马残局',
            'bishopKnightEndgame': '象马残局',
            'enPassant': '吃过路兵',
            'castling': '王车易位',
            'promotion': '兵升变',
            'underPromotion': '低升变',
        }
        
        # 翻译主题
        translated_themes = []
        for theme in puzzle['themes']:
            translated_themes.append(theme_translation.get(theme, theme))
        
        info = f"""
谜题 ID: {puzzle['id']}
评级: {puzzle['rating']}
对局次数: {puzzle['plays']}

对局信息:
  白方: {white['name']} ({white['rating']})
  黑方: {black['name']} ({black['rating']})
  对局类型: {game['perf']['name']}
  是否评级: {'是' if game['rated'] else '否'}

主题: {', '.join(translated_themes)}
PGN走法数: {len(self.move_history)}
解走法数: {len(self.solution_moves)}
        """
        self.info_text.setText(info.strip())

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