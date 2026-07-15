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

