from PyQt6.QtCore import *
from berserk import Client
from time import sleep

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
    ongoing_game_update = pyqtSignal(list)
    challenge_update = pyqtSignal(dict)

    def __init__(self,client:Client):
        super().__init__()
        self.client = client

    def run_event(self):
        while True:
            self.ongoing_game_update.emit(self.client.games.get_ongoing())
            self.challenge_update.emit(self.client.challenges.get_mine())
            sleep(5)