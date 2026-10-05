from PyQt6.QtWidgets import *
from PyQt6.QtGui import QDesktopServices
from typing import cast

from .base import (
    BaseBotSettingsWidget,
    BaseCRUDWidget,
    AUTO_REPLY_MESSAGE_TUTORIAL,
)

from .format import (
    EngineName,
    GameBehavior,
    AutoReplyMessage,
)

class EngineNameEdit(BaseBotSettingsWidget):
    def __init__(self, config:EngineName, parent:QWidget|None = None):
        super().__init__('引擎名称', '这里必须和真实文件一致，否则无法识别', parent)
        self.layout_ = QFormLayout(self)
        self.layout_.addRow(self.get_description())

        self.standard_engine_input = QLineEdit(self)
        self.standard_engine_input.setText(config['standard'])
        self.layout_.addRow(
            '标准',
            self.standard_engine_input,
        )

        self.variants_engine_input = QLineEdit(self)
        self.variants_engine_input.setText(config['variants'])
        self.layout_.addRow(
            '变体',
            self.variants_engine_input,
        )

    def get_config(self):
        return cast(
            EngineName,
            {
                'standard':self.standard_engine_input.text(),
                'variants':self.variants_engine_input.text(),
            }
        )

class GameBehaviorEdit(BaseBotSettingsWidget):
    def __init__(self, config:GameBehavior, parent:QWidget|None = None):
        super().__init__('对局行为控制', '控制对局时的行为（由于功能原因暂时停止使用）', parent)
        self.setEnabled(False)
        self.layout_ = QFormLayout(self)
        self.layout_.addRow(self.get_description())

        self.resign_score_spinbox = QSpinBox(self)
        self.resign_score_spinbox.setRange(-1000,-3)
        self.resign_score_spinbox.setValue(config['resign_score'])
        self.layout_.addRow(
            '评估分小于多少就认输',
            self.resign_score_spinbox,
        )

        self.draw_piece_count_spinbox = QSpinBox(self)
        self.draw_piece_count_spinbox.setRange(2,15)
        self.draw_piece_count_spinbox.setValue(config['draw_piece_count'])
        self.layout_.addRow(
            '棋子数量少于多少就和棋',
            self.draw_piece_count_spinbox,
        )

        self.draw_interval_spinbox = QSpinBox(self)
        self.draw_interval_spinbox.setRange(4,20)
        self.draw_interval_spinbox.setValue(config['draw_interval'])
        self.layout_.addRow(
            '两次提出和棋之间的间隔',
            self.draw_interval_spinbox,
        )

    def get_config(self):
        return cast(
            GameBehavior,
            {
                'resign_score':self.resign_score_spinbox.value(),
                'draw_piece_count':self.draw_piece_count_spinbox.value(),
                'draw_interval':self.draw_interval_spinbox.value(),
            }
        )

class AutoReplyMessageEdit(BaseBotSettingsWidget):
    def __init__(self, config:AutoReplyMessage, parent:QWidget|None = None):
        super().__init__('自动回复消息', '如果启用 ，则会在聊天中自动回复消息，通过智谱ai模型', parent)
        self.layout_ = QFormLayout(self)

        self.enabled = QCheckBox('启用',self)
        self.enabled.setChecked(config['enabled'])
        self.layout_.addRow(
            self.enabled,
            self.get_description()
        )

        self.tutorial = QTextBrowser(self)
        self.tutorial.setOpenLinks(False)
        self.tutorial.anchorClicked.connect(lambda url: QDesktopServices.openUrl(url))
        self.tutorial.setMarkdown(AUTO_REPLY_MESSAGE_TUTORIAL)
        self.layout_.addRow(self.tutorial)

        self.api_key_input = QLineEdit(self)
        self.api_key_input.setText(config['api_key'])
        self.layout_.addRow(
            '智谱ai api key',
            self.api_key_input,
        )

    def get_config(self):
        return cast(
            AutoReplyMessage,
            {
                'enabled':self.enabled.isChecked(),
                'api_key':self.api_key_input.text()
            }
        )

class BlockListEdit(BaseCRUDWidget):
    def __init__(self, config:list[str], parent:QWidget|None = None):
        super().__init__('黑名单','将某个用户添加或移除到黑名单，不接受他们的挑战，也不会去匹配他们',parent)
        self.list_widget = QListWidget(self)
        for user in config:self.list_widget.addItem(user)

        self.init_ui(
            self.list_widget,
            {'用户名':'str'},
            self.add,
            self.delete,
        )

    def add(self,value:list[str]):
        if value[0] == '':
            QMessageBox.information(
                self,
                '提示',
                '请先输入文字',
            )
        else:self.list_widget.addItem(value[0])

    def delete(self):
        if self.list_widget.currentItem() != None:
            self.list_widget.takeItem(self.list_widget.currentRow())
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一个选项',
        )

    def get_config(self):
        return [self.list_widget.item(index).text() for index in range(self.list_widget.count())]