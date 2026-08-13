from PyQt6.QtWidgets import *
from typing import cast

from .base import BaseMultiCheckboxWidget
from .format import (
    SupportTime,
    SupportVariants,
)

class SupportTimeEdit(BaseMultiCheckboxWidget):
    def __init__(self, config:SupportTime, parent:QWidget|None = None):
        super().__init__(
            {
                'ultraBullet':{
                    'text':'超子弹棋',
                    'row':0,
                    'column':0,
                },
                'bullet':{
                    'text':'子弹棋',
                    'row':0,
                    'column':1,
                },
                'blitz':{
                    'text':'超快棋',
                    'row':0,
                    'column':2,
                },
                'rapid':{
                    'text':'快棋',
                    'row':1,
                    'column':0,
                },
                'classical':{
                    'text':'慢棋',
                    'row':1,
                    'column':1,
                },
                'correspondence':{
                    'text':'通讯棋',
                    'row':1,
                    'column':2,
                },
            },
            config,
            '支持的时间', 
            parent,
        )

    def get_config(self):
        return cast(
            SupportTime,
            super().get_config(),
        )

class SupportVariantsEdit(BaseMultiCheckboxWidget):
    def __init__(self, config:SupportVariants, parent:QWidget|None = None):
        super().__init__(
            {
                'standard':{
                    'text':'标准',
                    'row':0,
                    'column':0,
                },
                'chess960':{
                    'text':'菲舍尔随机象棋',
                    'row':0,
                    'column':1,
                },
                'kingOfTheHill':{
                    'text':'山丘之王',
                    'row':0,
                    'column':2,
                },
                'threeCheck':{
                    'text':'三次将军',
                    'row':1,
                    'column':0,
                },
                'antichess':{
                    'text':'弃子棋',
                    'row':1,
                    'column':1,
                },
                'atomic':{
                    'text':'原子棋',
                    'row':1,
                    'column':2,
                },
                'horde':{
                    'text':'部落棋',
                    'row':2,
                    'column':0,
                },
                'racingKings':{
                    'text':'竞速棋',
                    'row':2,
                    'column':1,
                },
                'crazyhouse':{
                    'text':'疯狂象棋',
                    'row':2,
                    'column':2,
                },
            },
            config,
            '支持的变体', 
            parent,
        )

    def get_config(self):
        return cast(
            SupportVariants,
            super().get_config(),
        )