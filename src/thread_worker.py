from PyQt6.QtCore import *
from typing import Generator
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

class GeneratorToListWorker(QObject):
    send_list = pyqtSignal(list)
    
    def __init__(self,generator:Generator):
        super().__init__()
        self.generator = generator
        self.list_result = []
        self.is_running = True

    def stop(self):self.is_running = False
    
    def run_event(self):
        for value in self.generator:
            if self.is_running:
                self.list_result.append(value)
            else:break
        else:
            self.send_list.emit(self.list_result)
            self.thread().quit()