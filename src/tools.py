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
from costants import ICON,CONFIG

class GameViewer(QWidget):
    def __init__(self,generator:Generator):
        # 第一部分：初始化窗口
        super().__init__()
        self.splitter = QSplitter(Qt.Orientation.Horizontal,self)
        QVBoxLayout(self).addWidget(self.splitter)
        self.generator = generator
        
        self.setWindowTitle('对局查看器')
        self.setWindowIcon(QIcon(ICON))

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
        self.fen = StringDisplay(self.real_time_info_panel)
        self.info_panel_layout.addRow('当前局面FEN',self.fen)

        self.white_clock = StringDisplay(self.real_time_info_panel)
        self.info_panel_layout.addRow('白方剩余时间（秒）',self.white_clock)

        self.black_clock = StringDisplay(self.real_time_info_panel)
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

    def receive_dict(self,dct:dict):
        # 这里由于有判断逻辑，所以请大家使用下方的example函数进行查看，证明为什么要这样子设计

        if 'winner' in dct:#证明这是最后一个
            self.tree.set_dict(dct)
        else:
            self.fen.setText(dct['fen'])
            self.white_clock.setText(str(dct['wc']))
            self.black_clock.setText(str(dct['bc']))
            self.move_record.addItem(dct['lm'])
            self.svg_widget.load(self.fen_to_svg(dct['fen']))
        
    def example(self):
        {'id': 'ek0k9QzF', 'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 'speed': 'rapid', 'perf': 'rapid', 'rated': True, 'source': 'pool', 'createdAt': 1782554334440, 'players': {'white': {'user': {'name': 'KoT_Tropical', 'id': 'kot_tropical'}, 'rating': 2445}, 'black': {'user': {'name': 'Krishnadas16_2004', 'id': 'krishnadas16_2004'}, 'rating': 2537}}}
        {'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'wc': 600, 'bc': 600}
        {'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1', 'lm': 'e2e4', 'wc': 600, 'bc': 600}
        {'fen': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2', 'lm': 'c7c5', 'wc': 600, 'bc': 600}
        {'fen': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2', 'lm': 'g1f3', 'wc': 599, 'bc': 600}
        {'fen': 'rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3', 'lm': 'd7d6', 'wc': 599, 'bc': 600}
        {'fen': 'rnbqkbnr/pp2pppp/3p4/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3', 'lm': 'f1b5', 'wc': 596, 'bc': 600}
        {'fen': 'rn1qkbnr/pp1bpppp/3p4/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4', 'lm': 'c8d7', 'wc': 596, 'bc': 598}
        {'fen': 'rn1qkbnr/pp1bpppp/3p4/1Bp5/4P3/5N2/PPPPQPPP/RNB1K2R b KQkq - 3 4', 'lm': 'd1e2', 'wc': 595, 'bc': 598}
        {'fen': 'rn1qkb1r/pp1bpppp/3p1n2/1Bp5/4P3/5N2/PPPPQPPP/RNB1K2R w KQkq - 4 5', 'lm': 'g8f6', 'wc': 595, 'bc': 595}
        {'fen': 'rn1qkb1r/pp1bpppp/3p1n2/1Bp5/4P3/2N2N2/PPPPQPPP/R1B1K2R b KQkq - 5 5', 'lm': 'b1c3', 'wc': 591, 'bc': 595}
        {'fen': 'rn1qkb1r/1p1bpppp/p2p1n2/1Bp5/4P3/2N2N2/PPPPQPPP/R1B1K2R w KQkq - 0 6', 'lm': 'a7a6', 'wc': 591, 'bc': 594}
        {'fen': 'rn1qkb1r/1p1Bpppp/p2p1n2/2p5/4P3/2N2N2/PPPPQPPP/R1B1K2R b KQkq - 0 6', 'lm': 'b5d7', 'wc': 589, 'bc': 594}
        {'fen': 'r2qkb1r/1p1npppp/p2p1n2/2p5/4P3/2N2N2/PPPPQPPP/R1B1K2R w KQkq - 0 7', 'lm': 'b8d7', 'wc': 589, 'bc': 591}
        {'fen': 'r2qkb1r/1p1npppp/p2p1n2/2p5/4P3/2NP1N2/PPP1QPPP/R1B1K2R b KQkq - 0 7', 'lm': 'd2d3', 'wc': 588, 'bc': 591}
        {'fen': 'r2qkb1r/1p1n1ppp/p2ppn2/2p5/4P3/2NP1N2/PPP1QPPP/R1B1K2R w KQkq - 0 8', 'lm': 'e7e6', 'wc': 588, 'bc': 589}
        {'fen': 'r2qkb1r/1p1n1ppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B1K2R b KQkq - 0 8', 'lm': 'a2a4', 'wc': 588, 'bc': 589}
        {'fen': 'r2qk2r/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B1K2R w KQkq - 1 9', 'lm': 'f8e7', 'wc': 588, 'bc': 587}
        {'fen': 'r2qk2r/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B2RK1 b kq - 2 9', 'lm': 'e1g1', 'wc': 585, 'bc': 587}
        {'fen': 'r2q1rk1/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B2RK1 w - - 3 10', 'lm': 'e8g8', 'wc': 585, 'bc': 585}
        {'fen': 'r2q1rk1/1p1nbppp/p2ppn2/2p5/P3PB2/2NP1N2/1PP1QPPP/R4RK1 b - - 4 10', 'lm': 'c1f4', 'wc': 585, 'bc': 585}
        {'fen': 'r2qr1k1/1p1nbppp/p2ppn2/2p5/P3PB2/2NP1N2/1PP1QPPP/R4RK1 w - - 5 11', 'lm': 'f8e8', 'wc': 585, 'bc': 579}
        {'fen': 'r2qr1k1/1p1nbppp/p2ppn2/P1p5/4PB2/2NP1N2/1PP1QPPP/R4RK1 b - - 0 11', 'lm': 'a4a5', 'wc': 583, 'bc': 579}
        {'fen': 'r2qr1k1/1p1nbppp/p2p1n2/P1p1p3/4PB2/2NP1N2/1PP1QPPP/R4RK1 w - - 0 12', 'lm': 'e6e5', 'wc': 583, 'bc': 575}
        {'fen': 'r2qr1k1/1p1nbppp/p2p1n2/P1p1p3/4P3/2NP1NB1/1PP1QPPP/R4RK1 b - - 1 12', 'lm': 'f4g3', 'wc': 582, 'bc': 575}
        {'fen': 'r2qrnk1/1p2bppp/p2p1n2/P1p1p3/4P3/2NP1NB1/1PP1QPPP/R4RK1 w - - 2 13', 'lm': 'd7f8', 'wc': 582, 'bc': 575}
        {'fen': 'r2qrnk1/1p2bppp/p2p1n2/P1p1p3/4P3/2NP2B1/1PPNQPPP/R4RK1 b - - 3 13', 'lm': 'f3d2', 'wc': 578, 'bc': 575}
        {'fen': 'r2qr1k1/1p2bppp/p2pnn2/P1p1p3/4P3/2NP2B1/1PPNQPPP/R4RK1 w - - 4 14', 'lm': 'f8e6', 'wc': 578, 'bc': 574}
        {'fen': 'r2qr1k1/1p2bppp/p2pnn2/P1p1p3/2N1P3/2NP2B1/1PP1QPPP/R4RK1 b - - 5 14', 'lm': 'd2c4', 'wc': 574, 'bc': 574}
        {'fen': 'r2qr1k1/1p2bppp/p2p1n2/P1p1p3/2NnP3/2NP2B1/1PP1QPPP/R4RK1 w - - 6 15', 'lm': 'e6d4', 'wc': 574, 'bc': 573}
        {'fen': 'r2qr1k1/1p2bppp/p2p1n2/P1p1p3/2NnP3/2NP2B1/1PPQ1PPP/R4RK1 b - - 7 15', 'lm': 'e2d2', 'wc': 572, 'bc': 573}
        {'fen': 'r2qr1k1/1p2bppp/p2p4/P1p1p2n/2NnP3/2NP2B1/1PPQ1PPP/R4RK1 w - - 8 16', 'lm': 'f6h5', 'wc': 572, 'bc': 570}
        {'fen': 'r2qr1k1/1p2bppp/p2p4/P1pNp2n/2NnP3/3P2B1/1PPQ1PPP/R4RK1 b - - 9 16', 'lm': 'c3d5', 'wc': 566, 'bc': 570}
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1bn/2NnP3/3P2B1/1PPQ1PPP/R4RK1 w - - 10 17', 'lm': 'e7g5', 'wc': 566, 'bc': 567}
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1bn/2NnP3/3P2B1/1PP2PPP/R2Q1RK1 b - - 11 17', 'lm': 'd2d1', 'wc': 564, 'bc': 567}
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1b1/2NnP3/3P2n1/1PP2PPP/R2Q1RK1 w - - 0 18', 'lm': 'h5g3', 'wc': 564, 'bc': 562}
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1b1/2NnP3/3P2P1/1PP2PP1/R2Q1RK1 b - - 0 18', 'lm': 'h2g3', 'wc': 562, 'bc': 562}
        {'fen': 'r2qr1k1/1p3ppp/p2p3b/P1pNp3/2NnP3/3P2P1/1PP2PP1/R2Q1RK1 w - - 1 19', 'lm': 'g5h6', 'wc': 562, 'bc': 553}
        {'fen': 'r2qr1k1/1p3ppp/p2p3b/P1pNp3/2NnP3/2PP2P1/1P3PP1/R2Q1RK1 b - - 0 19', 'lm': 'c2c3', 'wc': 531, 'bc': 553}
        {'fen': 'r2qr1k1/1p3ppp/p1np3b/P1pNp3/2N1P3/2PP2P1/1P3PP1/R2Q1RK1 w - - 1 20', 'lm': 'd4c6', 'wc': 531, 'bc': 534}
        {'fen': 'r2qr1k1/1p3ppp/p1np3b/P1pNp3/2N1P1Q1/2PP2P1/1P3PP1/R4RK1 b - - 2 20', 'lm': 'd1g4', 'wc': 530, 'bc': 534}
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P1pNp3/2N1P1Q1/2PP2P1/1P3PP1/R4RK1 w - - 3 21', 'lm': 'e8e6', 'wc': 530, 'bc': 531}
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P1pNp3/1PN1P1Q1/2PP2P1/5PP1/R4RK1 b - - 0 21', 'lm': 'b2b4', 'wc': 472, 'bc': 531}
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P2Np3/1pN1P1Q1/2PP2P1/5PP1/R4RK1 w - - 0 22', 'lm': 'c5b4', 'wc': 472, 'bc': 524}
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P2Np3/1PN1P1Q1/3P2P1/5PP1/R4RK1 b - - 0 22', 'lm': 'c3b4', 'wc': 472, 'bc': 524}
        {'fen': 'r2q2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/R4RK1 w - - 1 23', 'lm': 'c6d4', 'wc': 472, 'bc': 522}
        {'fen': 'r2q2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/4RRK1 b - - 2 23', 'lm': 'a1e1', 'wc': 460, 'bc': 522}
        {'fen': '2rq2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/4RRK1 w - - 3 24', 'lm': 'a8c8', 'wc': 460, 'bc': 518}
        {'fen': '2rq2k1/1p3ppp/p2pr2b/P2Np3/1PNnP3/3P2PQ/5PP1/4RRK1 b - - 4 24', 'lm': 'g4h3', 'wc': 454, 'bc': 518}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnP3/3P2PQ/5PP1/4RRK1 w - - 5 25', 'lm': 'c8c6', 'wc': 454, 'bc': 460}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/6P1/4RRK1 b - - 0 25', 'lm': 'f2f4', 'wc': 438, 'bc': 460}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PN1PP2/3P2PQ/2n3P1/4RRK1 w - - 1 26', 'lm': 'd4c2', 'wc': 438, 'bc': 424}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PN1PP2/3P2PQ/2n1R1P1/5RK1 b - - 2 26', 'lm': 'e1e2', 'wc': 429, 'bc': 424}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/4R1P1/5RK1 w - - 3 27', 'lm': 'c2d4', 'wc': 429, 'bc': 424}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/5RP1/5RK1 b - - 4 27', 'lm': 'e2f2', 'wc': 427, 'bc': 424}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2N4/1PNnPp2/3P2PQ/5RP1/5RK1 w - - 0 28', 'lm': 'e5f4', 'wc': 427, 'bc': 312}
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2N4/1PNnPP2/3P3Q/5RP1/5RK1 b - - 0 28', 'lm': 'g3f4', 'wc': 426, 'bc': 312}
        {'fen': '3q2k1/1p3ppp/p2pr2b/P2N4/1PrnPP2/3P3Q/5RP1/5RK1 w - - 0 29', 'lm': 'c6c4', 'wc': 426, 'bc': 303}
        {'fen': '3q2k1/1p3ppp/p2pr2b/P2N4/1PPnPP2/7Q/5RP1/5RK1 b - - 0 29', 'lm': 'd3c4', 'wc': 425, 'bc': 303}
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPnrP2/7Q/5RP1/5RK1 w - - 0 30', 'lm': 'e6e4', 'wc': 425, 'bc': 302}
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPnrP2/6PQ/5R2/5RK1 b - - 0 30', 'lm': 'g2g3', 'wc': 400, 'bc': 302}
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPn1P2/4r1PQ/5R2/5RK1 w - - 1 31', 'lm': 'e4e3', 'wc': 400, 'bc': 285}
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPn1P2/4r1PQ/5RK1/5R2 b - - 2 31', 'lm': 'g1g2', 'wc': 396, 'bc': 285}
        {'fen': '3qr1k1/1p3ppp/p2p3b/P2N4/1PPn1P2/6PQ/5RK1/5R2 w - - 3 32', 'lm': 'e3e8', 'wc': 396, 'bc': 275}
        {'fen': '3qr1k1/1p3ppp/p2p3b/P2N4/1PPn1PQ1/6P1/5RK1/5R2 b - - 4 32', 'lm': 'h3g4', 'wc': 392, 'bc': 275}
        {'fen': '3qr1k1/1p3p1p/p2p2pb/P2N4/1PPn1PQ1/6P1/5RK1/5R2 w - - 0 33', 'lm': 'g7g6', 'wc': 392, 'bc': 240}
        {'fen': '3qr1k1/1p3p1p/p2p2pb/P2N4/1PPn1PQ1/6P1/5RK1/7R b - - 1 33', 'lm': 'f1h1', 'wc': 380, 'bc': 240}
        {'fen': '3qr1k1/1p3pbp/p2p2p1/P2N4/1PPn1PQ1/6P1/5RK1/7R w - - 2 34', 'lm': 'h6g7', 'wc': 380, 'bc': 234}
        {'fen': '3qr1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1Q/6P1/5RK1/7R b - - 3 34', 'lm': 'g4h4', 'wc': 379, 'bc': 234}
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1q/6P1/5RK1/7R w - - 0 35', 'lm': 'd8h4', 'wc': 379, 'bc': 229}
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1R/6P1/5RK1/8 b - - 0 35', 'lm': 'h1h4', 'wc': 379, 'bc': 229}
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N1n2/1PP2P1R/6P1/5RK1/8 w - - 1 36', 'lm': 'd4f5', 'wc': 379, 'bc': 227}
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N1n2/1PP2P2/6P1/5RK1/7R b - - 2 36', 'lm': 'h4h1', 'wc': 377, 'bc': 227}
        {'fen': '6k1/1p3pbp/p2p2p1/P2N1n2/1PP1rP2/6P1/5RK1/7R w - - 3 37', 'lm': 'e8e4', 'wc': 377, 'bc': 226}
        {'fen': '6k1/1p3pbp/p2p2p1/P2N1n2/1PP1rP2/6P1/5RK1/6R1 b - - 4 37', 'lm': 'h1g1', 'wc': 373, 'bc': 226}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPbrP2/6P1/5RK1/6R1 w - - 5 38', 'lm': 'g7d4', 'wc': 373, 'bc': 223}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPbrP2/6P1/5RK1/2R5 b - - 6 38', 'lm': 'g1c1', 'wc': 346, 'bc': 223}
        {'fen': '6k1/1p3p1p/p2pr1p1/P2N1n2/1PPb1P2/6P1/5RK1/2R5 w - - 7 39', 'lm': 'e4e6', 'wc': 346, 'bc': 199}
        {'fen': '6k1/1p3p1p/p2pr1p1/P2N1n2/1PPb1P2/6P1/6K1/2R2R2 b - - 8 39', 'lm': 'f2f1', 'wc': 338, 'bc': 199}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/6P1/4r1K1/2R2R2 w - - 9 40', 'lm': 'e6e2', 'wc': 338, 'bc': 193}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/4r3/2R2R2 b - - 10 40', 'lm': 'g2f3', 'wc': 337, 'bc': 193}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/7r/2R2R2 w - - 11 41', 'lm': 'e2h2', 'wc': 337, 'bc': 182}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/7r/4RR2 b - - 12 41', 'lm': 'c1e1', 'wc': 325, 'bc': 182}
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KPr/8/4RR2 w - - 13 42', 'lm': 'h2h3', 'wc': 325, 'bc': 169}
        {'fen': '6k1/1p2Np1p/p2p2p1/P4n2/1PPb1P2/5KPr/8/4RR2 b - - 14 42', 'lm': 'd5e7', 'wc': 320, 'bc': 169}
        {'fen': '6k1/1p2np1p/p2p2p1/P7/1PPb1P2/5KPr/8/4RR2 w - - 0 43', 'lm': 'f5e7', 'wc': 320, 'bc': 157}
        {'fen': '6k1/1p2Rp1p/p2p2p1/P7/1PPb1P2/5KPr/8/5R2 b - - 0 43', 'lm': 'e1e7', 'wc': 320, 'bc': 157}
        {'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/5KPr/8/5R2 w - - 0 44', 'lm': 'h7h5', 'wc': 320, 'bc': 156}
        {'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/6Pr/6K1/5R2 b - - 1 44', 'lm': 'f3g2', 'wc': 316, 'bc': 156}
        {'id': 'ek0k9QzF', 'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 'speed': 'rapid', 'perf': 'rapid', 'rated': True, 'source': 'pool', 'createdAt': 1782554334440, 'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/6Pr/6K1/5R2 b - - 1 44', 'turns': 87, 'status': {'id': 31, 'name': 'resign'}, 'winner': 'white', 'players': {'white': {'user': {'name': 'KoT_Tropical', 'id': 'kot_tropical'}, 'rating': 2445, 'ratingDiff': 29}, 'black': {'user': {'name': 'Krishnadas16_2004', 'id': 'krishnadas16_2004'}, 'rating': 2537, 'ratingDiff': -24}}}

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
        self.setWindowIcon(QIcon(ICON))

        self.layout_.addWidget(TokenManager(self.widget_in_scroll_area))
        self.layout_.addWidget(AutoLoginControl(self.widget_in_scroll_area))

        account_info = client.account.get()
        self.status_bar = self.statusBar()
        self.status_bar.addWidget(QLabel(f'当前登录账号：{account_info["username"]}'))
        self.status_bar.addWidget(QLabel(f'下棋客户端模式：{'bot' if ('title' in account_info) and (account_info["title"] == 'BOT') else '人类'}模式'))