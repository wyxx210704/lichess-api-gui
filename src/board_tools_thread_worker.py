from PyQt6.QtCore import *
from berserk import Client
from time import sleep
from berserk.types.common import *

class ChallengeListen(QObject):
    challenge_update = pyqtSignal(dict)

    def __init__(self,client:Client):
        super().__init__()
        self.client = client
        self.is_running = True

    def stop(self):self.is_running = False

    def run_event(self):
        while True:
            if self.is_running:
                self.challenge_update.emit(self.client.challenges.get_mine())
                sleep(5)
            else:break

class CreateGameWorker(QObject):
    end_event = pyqtSignal()

    def __init__(self,client:Client,time: int,increment: int,rated: bool = False,variant: VariantKey = "standard",color: Color | Literal['random'] = "random",rating_range: str | tuple[int, int] | list[int] | None = None):
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