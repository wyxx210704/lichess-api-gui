from PyQt6.QtCore import *
from typing import *
from berserk.types.common import *
from berserk import Client

class GameViewerWorker(QObject):
    send_dict = pyqtSignal(dict)
    _example = [
        {'id': 'ek0k9QzF', 'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 'speed': 'rapid', 'perf': 'rapid', 'rated': True, 'source': 'pool', 'createdAt': 1782554334440, 'players': {'white': {'user': {'name': 'KoT_Tropical', 'id': 'kot_tropical'}, 'rating': 2445}, 'black': {'user': {'name': 'Krishnadas16_2004', 'id': 'krishnadas16_2004'}, 'rating': 2537}}},
        {'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'wc': 600, 'bc': 600},
        {'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1', 'lm': 'e2e4', 'wc': 600, 'bc': 600},
        {'fen': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2', 'lm': 'c7c5', 'wc': 600, 'bc': 600},
        {'fen': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2', 'lm': 'g1f3', 'wc': 599, 'bc': 600},
        {'fen': 'rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3', 'lm': 'd7d6', 'wc': 599, 'bc': 600},
        {'fen': 'rnbqkbnr/pp2pppp/3p4/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3', 'lm': 'f1b5', 'wc': 596, 'bc': 600},
        {'fen': 'rn1qkbnr/pp1bpppp/3p4/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4', 'lm': 'c8d7', 'wc': 596, 'bc': 598},
        {'fen': 'rn1qkbnr/pp1bpppp/3p4/1Bp5/4P3/5N2/PPPPQPPP/RNB1K2R b KQkq - 3 4', 'lm': 'd1e2', 'wc': 595, 'bc': 598},
        {'fen': 'rn1qkb1r/pp1bpppp/3p1n2/1Bp5/4P3/5N2/PPPPQPPP/RNB1K2R w KQkq - 4 5', 'lm': 'g8f6', 'wc': 595, 'bc': 595},
        {'fen': 'rn1qkb1r/pp1bpppp/3p1n2/1Bp5/4P3/2N2N2/PPPPQPPP/R1B1K2R b KQkq - 5 5', 'lm': 'b1c3', 'wc': 591, 'bc': 595},
        {'fen': 'rn1qkb1r/1p1bpppp/p2p1n2/1Bp5/4P3/2N2N2/PPPPQPPP/R1B1K2R w KQkq - 0 6', 'lm': 'a7a6', 'wc': 591, 'bc': 594},
        {'fen': 'rn1qkb1r/1p1Bpppp/p2p1n2/2p5/4P3/2N2N2/PPPPQPPP/R1B1K2R b KQkq - 0 6', 'lm': 'b5d7', 'wc': 589, 'bc': 594},
        {'fen': 'r2qkb1r/1p1npppp/p2p1n2/2p5/4P3/2N2N2/PPPPQPPP/R1B1K2R w KQkq - 0 7', 'lm': 'b8d7', 'wc': 589, 'bc': 591},
        {'fen': 'r2qkb1r/1p1npppp/p2p1n2/2p5/4P3/2NP1N2/PPP1QPPP/R1B1K2R b KQkq - 0 7', 'lm': 'd2d3', 'wc': 588, 'bc': 591},
        {'fen': 'r2qkb1r/1p1n1ppp/p2ppn2/2p5/4P3/2NP1N2/PPP1QPPP/R1B1K2R w KQkq - 0 8', 'lm': 'e7e6', 'wc': 588, 'bc': 589},
        {'fen': 'r2qkb1r/1p1n1ppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B1K2R b KQkq - 0 8', 'lm': 'a2a4', 'wc': 588, 'bc': 589},
        {'fen': 'r2qk2r/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B1K2R w KQkq - 1 9', 'lm': 'f8e7', 'wc': 588, 'bc': 587},
        {'fen': 'r2qk2r/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B2RK1 b kq - 2 9', 'lm': 'e1g1', 'wc': 585, 'bc': 587},
        {'fen': 'r2q1rk1/1p1nbppp/p2ppn2/2p5/P3P3/2NP1N2/1PP1QPPP/R1B2RK1 w - - 3 10', 'lm': 'e8g8', 'wc': 585, 'bc': 585},
        {'fen': 'r2q1rk1/1p1nbppp/p2ppn2/2p5/P3PB2/2NP1N2/1PP1QPPP/R4RK1 b - - 4 10', 'lm': 'c1f4', 'wc': 585, 'bc': 585},
        {'fen': 'r2qr1k1/1p1nbppp/p2ppn2/2p5/P3PB2/2NP1N2/1PP1QPPP/R4RK1 w - - 5 11', 'lm': 'f8e8', 'wc': 585, 'bc': 579},
        {'fen': 'r2qr1k1/1p1nbppp/p2ppn2/P1p5/4PB2/2NP1N2/1PP1QPPP/R4RK1 b - - 0 11', 'lm': 'a4a5', 'wc': 583, 'bc': 579},
        {'fen': 'r2qr1k1/1p1nbppp/p2p1n2/P1p1p3/4PB2/2NP1N2/1PP1QPPP/R4RK1 w - - 0 12', 'lm': 'e6e5', 'wc': 583, 'bc': 575},
        {'fen': 'r2qr1k1/1p1nbppp/p2p1n2/P1p1p3/4P3/2NP1NB1/1PP1QPPP/R4RK1 b - - 1 12', 'lm': 'f4g3', 'wc': 582, 'bc': 575},
        {'fen': 'r2qrnk1/1p2bppp/p2p1n2/P1p1p3/4P3/2NP1NB1/1PP1QPPP/R4RK1 w - - 2 13', 'lm': 'd7f8', 'wc': 582, 'bc': 575},
        {'fen': 'r2qrnk1/1p2bppp/p2p1n2/P1p1p3/4P3/2NP2B1/1PPNQPPP/R4RK1 b - - 3 13', 'lm': 'f3d2', 'wc': 578, 'bc': 575},
        {'fen': 'r2qr1k1/1p2bppp/p2pnn2/P1p1p3/4P3/2NP2B1/1PPNQPPP/R4RK1 w - - 4 14', 'lm': 'f8e6', 'wc': 578, 'bc': 574},
        {'fen': 'r2qr1k1/1p2bppp/p2pnn2/P1p1p3/2N1P3/2NP2B1/1PP1QPPP/R4RK1 b - - 5 14', 'lm': 'd2c4', 'wc': 574, 'bc': 574},
        {'fen': 'r2qr1k1/1p2bppp/p2p1n2/P1p1p3/2NnP3/2NP2B1/1PP1QPPP/R4RK1 w - - 6 15', 'lm': 'e6d4', 'wc': 574, 'bc': 573},
        {'fen': 'r2qr1k1/1p2bppp/p2p1n2/P1p1p3/2NnP3/2NP2B1/1PPQ1PPP/R4RK1 b - - 7 15', 'lm': 'e2d2', 'wc': 572, 'bc': 573},
        {'fen': 'r2qr1k1/1p2bppp/p2p4/P1p1p2n/2NnP3/2NP2B1/1PPQ1PPP/R4RK1 w - - 8 16', 'lm': 'f6h5', 'wc': 572, 'bc': 570},
        {'fen': 'r2qr1k1/1p2bppp/p2p4/P1pNp2n/2NnP3/3P2B1/1PPQ1PPP/R4RK1 b - - 9 16', 'lm': 'c3d5', 'wc': 566, 'bc': 570},
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1bn/2NnP3/3P2B1/1PPQ1PPP/R4RK1 w - - 10 17', 'lm': 'e7g5', 'wc': 566, 'bc': 567},
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1bn/2NnP3/3P2B1/1PP2PPP/R2Q1RK1 b - - 11 17', 'lm': 'd2d1', 'wc': 564, 'bc': 567},
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1b1/2NnP3/3P2n1/1PP2PPP/R2Q1RK1 w - - 0 18', 'lm': 'h5g3', 'wc': 564, 'bc': 562},
        {'fen': 'r2qr1k1/1p3ppp/p2p4/P1pNp1b1/2NnP3/3P2P1/1PP2PP1/R2Q1RK1 b - - 0 18', 'lm': 'h2g3', 'wc': 562, 'bc': 562},
        {'fen': 'r2qr1k1/1p3ppp/p2p3b/P1pNp3/2NnP3/3P2P1/1PP2PP1/R2Q1RK1 w - - 1 19', 'lm': 'g5h6', 'wc': 562, 'bc': 553},
        {'fen': 'r2qr1k1/1p3ppp/p2p3b/P1pNp3/2NnP3/2PP2P1/1P3PP1/R2Q1RK1 b - - 0 19', 'lm': 'c2c3', 'wc': 531, 'bc': 553},
        {'fen': 'r2qr1k1/1p3ppp/p1np3b/P1pNp3/2N1P3/2PP2P1/1P3PP1/R2Q1RK1 w - - 1 20', 'lm': 'd4c6', 'wc': 531, 'bc': 534},
        {'fen': 'r2qr1k1/1p3ppp/p1np3b/P1pNp3/2N1P1Q1/2PP2P1/1P3PP1/R4RK1 b - - 2 20', 'lm': 'd1g4', 'wc': 530, 'bc': 534},
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P1pNp3/2N1P1Q1/2PP2P1/1P3PP1/R4RK1 w - - 3 21', 'lm': 'e8e6', 'wc': 530, 'bc': 531},
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P1pNp3/1PN1P1Q1/2PP2P1/5PP1/R4RK1 b - - 0 21', 'lm': 'b2b4', 'wc': 472, 'bc': 531},
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P2Np3/1pN1P1Q1/2PP2P1/5PP1/R4RK1 w - - 0 22', 'lm': 'c5b4', 'wc': 472, 'bc': 524},
        {'fen': 'r2q2k1/1p3ppp/p1npr2b/P2Np3/1PN1P1Q1/3P2P1/5PP1/R4RK1 b - - 0 22', 'lm': 'c3b4', 'wc': 472, 'bc': 524},
        {'fen': 'r2q2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/R4RK1 w - - 1 23', 'lm': 'c6d4', 'wc': 472, 'bc': 522},
        {'fen': 'r2q2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/4RRK1 b - - 2 23', 'lm': 'a1e1', 'wc': 460, 'bc': 522},
        {'fen': '2rq2k1/1p3ppp/p2pr2b/P2Np3/1PNnP1Q1/3P2P1/5PP1/4RRK1 w - - 3 24', 'lm': 'a8c8', 'wc': 460, 'bc': 518},
        {'fen': '2rq2k1/1p3ppp/p2pr2b/P2Np3/1PNnP3/3P2PQ/5PP1/4RRK1 b - - 4 24', 'lm': 'g4h3', 'wc': 454, 'bc': 518},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnP3/3P2PQ/5PP1/4RRK1 w - - 5 25', 'lm': 'c8c6', 'wc': 454, 'bc': 460},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/6P1/4RRK1 b - - 0 25', 'lm': 'f2f4', 'wc': 438, 'bc': 460},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PN1PP2/3P2PQ/2n3P1/4RRK1 w - - 1 26', 'lm': 'd4c2', 'wc': 438, 'bc': 424},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PN1PP2/3P2PQ/2n1R1P1/5RK1 b - - 2 26', 'lm': 'e1e2', 'wc': 429, 'bc': 424},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/4R1P1/5RK1 w - - 3 27', 'lm': 'c2d4', 'wc': 429, 'bc': 424},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2Np3/1PNnPP2/3P2PQ/5RP1/5RK1 b - - 4 27', 'lm': 'e2f2', 'wc': 427, 'bc': 424},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2N4/1PNnPp2/3P2PQ/5RP1/5RK1 w - - 0 28', 'lm': 'e5f4', 'wc': 427, 'bc': 312},
        {'fen': '3q2k1/1p3ppp/p1rpr2b/P2N4/1PNnPP2/3P3Q/5RP1/5RK1 b - - 0 28', 'lm': 'g3f4', 'wc': 426, 'bc': 312},
        {'fen': '3q2k1/1p3ppp/p2pr2b/P2N4/1PrnPP2/3P3Q/5RP1/5RK1 w - - 0 29', 'lm': 'c6c4', 'wc': 426, 'bc': 303},
        {'fen': '3q2k1/1p3ppp/p2pr2b/P2N4/1PPnPP2/7Q/5RP1/5RK1 b - - 0 29', 'lm': 'd3c4', 'wc': 425, 'bc': 303},
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPnrP2/7Q/5RP1/5RK1 w - - 0 30', 'lm': 'e6e4', 'wc': 425, 'bc': 302},
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPnrP2/6PQ/5R2/5RK1 b - - 0 30', 'lm': 'g2g3', 'wc': 400, 'bc': 302},
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPn1P2/4r1PQ/5R2/5RK1 w - - 1 31', 'lm': 'e4e3', 'wc': 400, 'bc': 285},
        {'fen': '3q2k1/1p3ppp/p2p3b/P2N4/1PPn1P2/4r1PQ/5RK1/5R2 b - - 2 31', 'lm': 'g1g2', 'wc': 396, 'bc': 285},
        {'fen': '3qr1k1/1p3ppp/p2p3b/P2N4/1PPn1P2/6PQ/5RK1/5R2 w - - 3 32', 'lm': 'e3e8', 'wc': 396, 'bc': 275},
        {'fen': '3qr1k1/1p3ppp/p2p3b/P2N4/1PPn1PQ1/6P1/5RK1/5R2 b - - 4 32', 'lm': 'h3g4', 'wc': 392, 'bc': 275},
        {'fen': '3qr1k1/1p3p1p/p2p2pb/P2N4/1PPn1PQ1/6P1/5RK1/5R2 w - - 0 33', 'lm': 'g7g6', 'wc': 392, 'bc': 240},
        {'fen': '3qr1k1/1p3p1p/p2p2pb/P2N4/1PPn1PQ1/6P1/5RK1/7R b - - 1 33', 'lm': 'f1h1', 'wc': 380, 'bc': 240},
        {'fen': '3qr1k1/1p3pbp/p2p2p1/P2N4/1PPn1PQ1/6P1/5RK1/7R w - - 2 34', 'lm': 'h6g7', 'wc': 380, 'bc': 234},
        {'fen': '3qr1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1Q/6P1/5RK1/7R b - - 3 34', 'lm': 'g4h4', 'wc': 379, 'bc': 234},
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1q/6P1/5RK1/7R w - - 0 35', 'lm': 'd8h4', 'wc': 379, 'bc': 229},
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N4/1PPn1P1R/6P1/5RK1/8 b - - 0 35', 'lm': 'h1h4', 'wc': 379, 'bc': 229},
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N1n2/1PP2P1R/6P1/5RK1/8 w - - 1 36', 'lm': 'd4f5', 'wc': 379, 'bc': 227},
        {'fen': '4r1k1/1p3pbp/p2p2p1/P2N1n2/1PP2P2/6P1/5RK1/7R b - - 2 36', 'lm': 'h4h1', 'wc': 377, 'bc': 227},
        {'fen': '6k1/1p3pbp/p2p2p1/P2N1n2/1PP1rP2/6P1/5RK1/7R w - - 3 37', 'lm': 'e8e4', 'wc': 377, 'bc': 226},
        {'fen': '6k1/1p3pbp/p2p2p1/P2N1n2/1PP1rP2/6P1/5RK1/6R1 b - - 4 37', 'lm': 'h1g1', 'wc': 373, 'bc': 226},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPbrP2/6P1/5RK1/6R1 w - - 5 38', 'lm': 'g7d4', 'wc': 373, 'bc': 223},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPbrP2/6P1/5RK1/2R5 b - - 6 38', 'lm': 'g1c1', 'wc': 346, 'bc': 223},
        {'fen': '6k1/1p3p1p/p2pr1p1/P2N1n2/1PPb1P2/6P1/5RK1/2R5 w - - 7 39', 'lm': 'e4e6', 'wc': 346, 'bc': 199},
        {'fen': '6k1/1p3p1p/p2pr1p1/P2N1n2/1PPb1P2/6P1/6K1/2R2R2 b - - 8 39', 'lm': 'f2f1', 'wc': 338, 'bc': 199},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/6P1/4r1K1/2R2R2 w - - 9 40', 'lm': 'e6e2', 'wc': 338, 'bc': 193},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/4r3/2R2R2 b - - 10 40', 'lm': 'g2f3', 'wc': 337, 'bc': 193},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/7r/2R2R2 w - - 11 41', 'lm': 'e2h2', 'wc': 337, 'bc': 182},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KP1/7r/4RR2 b - - 12 41', 'lm': 'c1e1', 'wc': 325, 'bc': 182},
        {'fen': '6k1/1p3p1p/p2p2p1/P2N1n2/1PPb1P2/5KPr/8/4RR2 w - - 13 42', 'lm': 'h2h3', 'wc': 325, 'bc': 169},
        {'fen': '6k1/1p2Np1p/p2p2p1/P4n2/1PPb1P2/5KPr/8/4RR2 b - - 14 42', 'lm': 'd5e7', 'wc': 320, 'bc': 169},
        {'fen': '6k1/1p2np1p/p2p2p1/P7/1PPb1P2/5KPr/8/4RR2 w - - 0 43', 'lm': 'f5e7', 'wc': 320, 'bc': 157},
        {'fen': '6k1/1p2Rp1p/p2p2p1/P7/1PPb1P2/5KPr/8/5R2 b - - 0 43', 'lm': 'e1e7', 'wc': 320, 'bc': 157},
        {'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/5KPr/8/5R2 w - - 0 44', 'lm': 'h7h5', 'wc': 320, 'bc': 156},
        {'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/6Pr/6K1/5R2 b - - 1 44', 'lm': 'f3g2', 'wc': 316, 'bc': 156},
        {'id': 'ek0k9QzF', 'variant': {'key': 'standard', 'name': 'Standard', 'short': 'Std'}, 'speed': 'rapid', 'perf': 'rapid', 'rated': True, 'source': 'pool', 'createdAt': 1782554334440, 'fen': '6k1/1p2Rp2/p2p2p1/P6p/1PPb1P2/6Pr/6K1/5R2 b - - 1 44', 'turns': 87, 'status': {'id': 31, 'name': 'resign'}, 'winner': 'white', 'players': {'white': {'user': {'name': 'KoT_Tropical', 'id': 'kot_tropical'}, 'rating': 2445, 'ratingDiff': 29}, 'black': {'user': {'name': 'Krishnadas16_2004', 'id': 'krishnadas16_2004'}, 'rating': 2537, 'ratingDiff': -24}}},
    ]# 也就是说需要分离出第一项、第二项和最后一项，第一项、第二项已经在下方GameViewer分离

    def __init__(self,generator:Generator):
        super().__init__()
        self.generator = generator

    def run_event(self):
        for value in self.generator:
            self.send_dict.emit(value)

class CreateGameWorker(QObject):
    end_event = pyqtSignal()

    def __init__(self,client:Client,time: int,increment: int,rated: bool = False,variant: VariantKey = "standard",color: Color | Literal['random'] = "random",rating_range: str | Tuple[int, int] | List[int] | None = None):
        super().__init__()
        self.client = client
        self.configs = [
            time,
            increment,
            rated,
            variant,
            color,
            rating_range,
        ]

    def run_event(self):
        self.client.board.seek(*self.configs)
        self.end_event.emit()