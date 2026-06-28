from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import *
from typing import Generator
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