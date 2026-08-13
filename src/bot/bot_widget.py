from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from ..costants import GENERAL_PATH

class GameManager(QMdiArea):
    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent)
        self.image = QPixmap(GENERAL_PATH + 'no_current_game.jpg')
        self.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.setTabsClosable(False)
        self.setTabsMovable(True)

        self.setBackground(QBrush(self.image.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )))

    def resizeEvent(self, event:QResizeEvent):
        self.setBackground(QBrush(self.image.scaled(
            event.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )))

        super().resizeEvent(event)