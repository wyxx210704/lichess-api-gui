from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from typing import cast

from base import BaseOneWidgetTwoConfigs
from format import (
    GameMode,
    MoreSettings,
    VariantsWeight,
)

class GameModeEdit(BaseOneWidgetTwoConfigs):
    def __init__(self, challenge_in:GameMode,auto_match:GameMode,parent:QWidget|None = None):
        super().__init__('对局模式', '这里可以控制休闲或者排位在接收挑战或者自动匹配的支持性', parent)
        self.layout_ = QGridLayout(self)

        self.layout_.addWidget(self.get_description(),0,0,1,3)
        self.layout_.addWidget(QLabel('接受挑战'),1,0)
        self.layout_.addWidget(QLabel('自动匹配'),2,0)

        self.challenge_in_casual = QCheckBox('休闲',self)
        self.challenge_in_casual.setChecked(challenge_in['casual'])
        self.layout_.addWidget(
            self.challenge_in_casual,
            1,
            1,
        )

        self.challenge_in_rated = QCheckBox('排位',self)
        self.challenge_in_rated.setChecked(challenge_in['rated'])
        self.layout_.addWidget(
            self.challenge_in_rated,
            1,
            2,
        )

        self.auto_match_casual = QCheckBox('休闲',self)
        self.auto_match_casual.setChecked(auto_match['casual'])
        self.layout_.addWidget(
            self.auto_match_casual,
            2,
            1,
        )
        
        self.auto_match_rated = QCheckBox('排位',self)
        self.auto_match_rated.setChecked(auto_match['rated'])
        self.layout_.addWidget(
            self.auto_match_rated,
            2,
            2,
        )

    def get_config(self):
        return cast(
            GameMode,
            {
                'casual':self.challenge_in_casual.isChecked(),
                'rated':self.challenge_in_rated.isChecked(),
            },
        ),cast(
            GameMode,
            {
                'casual':self.auto_match_casual.isChecked(),
                'rated':self.auto_match_rated.isChecked(),
            },
        )

class MoreSettingsAndVariantsWeightEdit(BaseOneWidgetTwoConfigs):
    def __init__(self, more_settings:MoreSettings,variants_weight:VariantsWeight,parent:QWidget|None = None):
        super().__init__('自动匹配权重调节+更多设置', '这里可以调节自动匹配时使用各个种类的概率，更多设置：', parent)
        self.layout_ = QVBoxLayout(self)
        self.create_more_settings_widget(more_settings)
        self.create_variants_weight(variants_weight)

    def create_more_settings_widget(self,config:MoreSettings):
        self.more_settings_layout = QHBoxLayout()
        self.layout_.addLayout(self.more_settings_layout)
        self.more_settings_layout.addWidget(self.get_description())

        self.challenge_no_bot = QCheckBox('不接受机器人过来的挑战',self)
        self.challenge_no_bot.setChecked(config['challenge_no_bot'])
        self.more_settings_layout.addWidget(self.challenge_no_bot)

        self.challenge_only_bot = QCheckBox('只接受机器人过来的挑战',self)
        self.challenge_only_bot.setChecked(config['challenge_only_bot'])
        self.more_settings_layout.addWidget(self.challenge_only_bot)

        self.more_settings_layout.addWidget(QLabel('最大同时对局数'))
        self.max_game = QSpinBox(self)
        self.max_game.setRange(1,10)
        self.max_game.setValue(config['max_game'])
        self.more_settings_layout.addWidget(self.max_game)

        self.more_settings_layout.addWidget(QLabel('自动匹配间隔分钟'))
        self.auto_match_interval = QSpinBox(self)
        self.auto_match_interval.setRange(1,60)
        self.auto_match_interval.setValue(config['auto_match_interval'])
        self.more_settings_layout.addWidget(self.auto_match_interval)

    def get_more_settings(self):
        return cast(
            MoreSettings,
            {
                'challenge_no_bot':self.challenge_no_bot.isChecked(),
                'challenge_only_bot':self.challenge_only_bot.isChecked(),
                'max_game':self.max_game.value(),
                'auto_match_interval':self.auto_match_interval.value(),
            }
        )

    def create_variants_weight(self,config:VariantsWeight):
        self.variants_weight_layout = QGridLayout()
        self.layout_.addLayout(self.variants_weight_layout)
        rows = range(9)

        keys = [
            'standard',
            'chess960',
            'kingOfTheHill',
            'threeCheck',
            'antichess',
            'atomic',
            'horde',
            'racingKings',
            'crazyhouse',
        ]

        labels = [
            QLabel('标准'),
            QLabel('菲舍尔随机象棋'),
            QLabel('山丘之王'),
            QLabel('三次将军'),
            QLabel('弃子棋'),
            QLabel('原子棋'),
            QLabel('部落棋'),
            QLabel('竞速棋'),
            QLabel('疯狂象棋'),
        ]

        for index,label in enumerate(labels):
            self.variants_weight_layout.addWidget(
                label,
                index,
                0,
            )

        slider_generator = (lambda: (yield from rows))()
        self.sliders = dict(zip(keys,[QSlider(Qt.Orientation.Horizontal,self) for _ in rows]))

        for key,slider in self.sliders.items():
            slider.setRange(0,100)
            slider.setValue(config[key])
            slider.valueChanged.connect(self.update_value)
            self.variants_weight_layout.addWidget(
                slider,
                next(slider_generator),
                1,
            )

        progress_bar_generator = (lambda: (yield from rows))()
        self.progress_bars = dict(zip(keys,[QProgressBar(self) for _ in rows]))

        for key,progress_bar in self.progress_bars.items():
            progress_bar.setRange(0,100)
            progress_bar.setValue(0)
            progress_bar.setFormat('当前权重%v，占总量%m的%p%')
            self.variants_weight_layout.addWidget(
                progress_bar,
                next(progress_bar_generator),
                2,
            )

        self.update_value()

    def get_variants_weight(self):
        return cast(
            VariantsWeight,
            {key:slider.value() 
            for key,slider in 
            self.sliders.items()}
        )

    def update_value(self):
        total = 0
        for slider in self.sliders.values():
            total += slider.value()

        for key,progress_bar in self.progress_bars.items():
            progress_bar.setMaximum(total)
            progress_bar.setValue(self.sliders[key].value())