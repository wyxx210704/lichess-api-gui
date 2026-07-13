from PyQt6.QtCore import *
from berserk import Client

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