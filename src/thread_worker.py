from PyQt6.QtCore import *
from typing import *
from berserk.types.common import *
from berserk import Client

class GameViewerWorker(QObject):
    send_dict = pyqtSignal(dict)

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