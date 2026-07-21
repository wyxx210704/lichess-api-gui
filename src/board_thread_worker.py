from PyQt6.QtCore import *
from berserk import Client
from berserk.types.bots import *#board的数据结构是一样的，不信就看board.py里面的example

from board_format import *

class PlayChessStream(QObject):
    send_dict = pyqtSignal(dict)

    def __init__(self,client:Client,game_id:str):
        super().__init__()
        self.client = client
        self.game_id = game_id

    def run_event(self):
        generator = self.client.board.stream_game_state(self.game_id)
        for value in generator:
            self.send_dict.emit(value)

class EventListen(QObject):
    ongoing_game_update = pyqtSignal(
        dict,                   
        str,                 
    )

    challenge_update = pyqtSignal(   
        dict,                 
        str,               
    )

    state_update = pyqtSignal(
        str,
        list,
        list,
    )
    
    def __init__(self,client:Client):
        super().__init__()
        self.client = client

        self.challenge_type = {
            "challenge":'challenge',
            "challengeCanceled":'cancel',
            "challengeDeclined":'decline',
        }

        self.game_type = {
            'gameStart':'start',
            'gameFinish':'finish',
        }

    def run_event(self):
        for value in self.client.board.stream_incoming_events():
            #当有事件变化时更新，省资源
            challenge_in = self.client.challenges.get_mine()['in']
            ongoing_game = self.client.games.get_ongoing()

            #以下这两个变量直接存储条件，后面直接判断
            challenge_in_not_empty = len(challenge_in) != 0
            ongoing_game_not_empty = len(ongoing_game) != 0

            if challenge_in_not_empty and ongoing_game_not_empty:state = 'both'
            elif challenge_in_not_empty:state = 'challenge'
            elif ongoing_game_not_empty:state = 'game'
            else:state = 'both_not'

            self.state_update.emit(
                state,
                challenge_in,
                ongoing_game,
            )

            if value['type'] == 'challenge' or value['type'] == 'challengeCanceled' or value['type'] == 'challengeDeclined':
                self.challenge_update.emit(
                    value['challenge'],
                    self.challenge_type[value['type']],
                )
            elif value['type'] == 'gameStart' or value['type'] == 'gameFinish':
                self.ongoing_game_update.emit(
                    value['game'],
                    self.game_type[value['type']],
                )