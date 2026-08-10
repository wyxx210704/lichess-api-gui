from PyQt6.QtWidgets import *
from typing import cast

from base import BaseCRUDWidget
from format import AlternativeTimeItem

class AlternativeTimeEdit(BaseCRUDWidget):
    def __init__(self, config:list[AlternativeTimeItem], parent = None):
        super().__init__('自动匹配时间控制', '自动匹配的时候，会从这个列表时间里面随机选择', parent)
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setColumnCount(2)

        self.tree_widget.setHeaderLabels([
            '基本时间',
            '每步增加时间',
        ])

        for time in config:
            item = QTreeWidgetItem(self.tree_widget)
            item.setText(0,str(time['limit']))
            item.setText(1,str(time['increment']))

        self.init_ui(
            self.tree_widget,
            {
                '基本时间（分钟）':'int',
                '每步增加时间（秒）':'int',
            },
            self.add,
            self.delete,
            (lambda:(yield from [
                (0,180),
                (0,180),
            ]))()
        )

    def add(self, value:list[int]):
        if (value[0] == 0) and (value[1] == 0):
            QMessageBox.information(
                self,
                '提示',
                '无效时间',
            )
        else:
            item = QTreeWidgetItem(self.tree_widget)
            for index,number in enumerate(value):
                item.setText(index,str(number))

    def delete(self):
        if self.tree_widget.currentItem() != None:
            self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(self.tree_widget.currentItem()))
        else:QMessageBox.critical(
            self,
            '错误',
            '请先选中一个选项',
        )

    def get_config(self):
        return cast(
            list[AlternativeTimeItem],
            [{'limit':int(item.text(0)),'increment':int(item.text(1))} 
            for item in [self.tree_widget.topLevelItem(index)
            for index in range(self.tree_widget.topLevelItemCount())]]
        )