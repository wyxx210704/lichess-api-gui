from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from typing import cast
from json import load,dump

from basic_settings import (
    EngineNameEdit,
    GameBehaviorEdit,
    AutoReplyMessageEdit,
    BlockListEdit
)

from challenge_in import (
    SupportTimeEdit,
    SupportVariantsEdit,
)

from one_widget_two_configs import (
    GameModeEdit,
    MoreSettingsAndVariantsWeightEdit,
)

from auto_match import AlternativeTimeEdit
from base import CONFIG_PATH
from format import ConfigFormat

class BotSettings(QWidget):
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.layout_ = QGridLayout(self)

        config = cast(
            ConfigFormat,
            load(open(
                CONFIG_PATH,
                'r',
                encoding='utf-8',
                errors='ignore',
            ))
        )

        basic_settings = config['basic_settings']
        challenge_in = config['challenge_in']
        auto_match = config['auto_match']

        self.engine_name = EngineNameEdit(basic_settings['engine_name'],self)
        self.layout_.addWidget(
            self.engine_name,
            0,
            0,
        )

        self.game_behavior = GameBehaviorEdit(basic_settings['game_behavior'],self)
        self.layout_.addWidget(
            self.game_behavior,
            4,
            0,
        )

        self.auto_reply_message = AutoReplyMessageEdit(basic_settings['auto_reply_message'],self)
        self.layout_.addWidget(
            self.auto_reply_message,
            0,
            1,
            3,
            1,
        )

        self.block_list = BlockListEdit(basic_settings['block_list'],self)
        self.layout_.addWidget(
            self.block_list,
            0,
            3,
            3,
            1,
        )

        self.support_time = SupportTimeEdit(challenge_in['support_time'],self)
        self.layout_.addWidget(
            self.support_time,
            1,
            0,
        )

        self.support_variants = SupportVariantsEdit(challenge_in['support_variants'],self)
        self.layout_.addWidget(
            self.support_variants,
            2,
            0,
        )

        self.alternative_time = AlternativeTimeEdit(auto_match['alternative_time'],self)
        self.layout_.addWidget(
            self.alternative_time,
            0,
            2,
            3,
            1,
        )

        self.game_mode = GameModeEdit(challenge_in['support_mode'],auto_match['enable_mode'],self)
        self.layout_.addWidget(
            self.game_mode,
            3,
            0,
        )

        self.more_settings_and_variants_weight = MoreSettingsAndVariantsWeightEdit(
            basic_settings['more_settings'],auto_match['variants_weight'],self)
        self.layout_.addWidget(
            self.more_settings_and_variants_weight,
            3,
            1,
            3,
            3,
        )

        self.save_button = QCommandLinkButton('保存',
        '这里整个配置页面的配置保存之后不需要重启，如果没有对局（除通讯棋外），那么这里的设置就会自动生效',self)
        self.save_button.clicked.connect(self.save)
        self.save_button.setIcon(QIcon.fromTheme('document-save'))
        self.layout_.addWidget(
            self.save_button,
            5,
            0,
        )

    def save(self):
        dump(
            {
                "basic_settings":{
                    "engine_name":self.engine_name.get_config(),
                    "game_behavior":self.game_behavior.get_config(),
                    "auto_reply_message":self.auto_reply_message.get_config(),
                    "block_list":self.block_list.get_config(),
                    "more_settings":self.more_settings_and_variants_weight.get_more_settings()
                },
                "challenge_in":{
                    "support_time":self.support_time.get_config(),
                    "support_variants":self.support_variants.get_config(),
                    "support_mode":self.game_mode.get_config()[0]
                },
                "auto_match":{
                    "alternative_time":self.alternative_time.get_config(),
                    "variants_weight":self.more_settings_and_variants_weight.get_variants_weight(),
                    "enable_mode":self.game_mode.get_config()[1]
                }
            },
            open(
                CONFIG_PATH,
                'w',
                encoding='utf-8',
                errors='ignore',
            ),
            ensure_ascii=False,
            indent=4,
        )
        QMessageBox.information(
            self,
            '提示',
            '保存成功',
        )

if __name__ == "__main__":
    app = QApplication([])
    window = BotSettings()
    window.show()
    app.exec()