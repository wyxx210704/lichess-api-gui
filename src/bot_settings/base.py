from PyQt6.QtWidgets import *
from typing import *

CONFIG_PATH = '../../configuration_and_resources/bot_config.json'
AUTO_REPLY_MESSAGE_TUTORIAL = '''
## 步骤一：注册/登录智谱AI开放平台

1. 访问[智谱AI开放平台官网](https://open.bigmodel.cn/)
2. 点击右上角的“登录/注册”按钮
3. 使用手机号或邮箱完成注册并登录

---

## 步骤二：进入API密钥管理页面

登录后，有两种方式进入密钥管理：

- **方式一**：点击右上角头像 → 选择“API Keys”
- **方式二**：在控制台首页左侧菜单栏，点击“API Keys”

---

## 步骤三：创建新的API Key

1. 在API Keys页面，点击 **“创建新密钥”** 或 **“创建API Key”** 按钮
2. 系统会弹出对话框，要求输入密钥名称（用于备注识别，如“我的第一个应用”）
3. 点击确认后，系统会生成一串密钥

> ⚠️ **重要提示**：生成的API Key只会完整显示**一次**！请务必立即**复制保存**到安全的地方。如果丢失，只能删除后重新创建。

---

## 步骤四：获取和使用API Key

API Key的格式通常为：

```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

这是一个由点号分隔的两段式字符串。
'''

class BaseBotSettingsWidget(QGroupBox):
    def __init__(self, title:str, description:str,parent:QWidget|None=None):
        super().__init__(title, parent)
        self.description = description

    def get_description(self):return QLabel(self.description)
    #此为工具函数，因为各个子类所用的布局不同
    #所以这个类就负责保存描述

    def get_config(self) -> dict|list:...
    #此为类型注解，具体逻辑专靠子类

class BaseOneWidgetTwoConfigs(BaseBotSettingsWidget):
    def get_config(self) -> tuple[dict,dict]:...
    #此为类型注解，具体逻辑专靠子类

class CRUDInput(QWidget):
    def __init__(self, deta_format:dict[str,Literal['int','str']],parent:QWidget|None = None,
                 ranges:Generator[tuple[int,int]]=(lambda: (yield (0,100)))()):
        super().__init__(parent)
        self.layout_ = QFormLayout(self)
        self.input_widgets = cast(
            list[QSpinBox|QLineEdit],
            [],
        )

        for name,type_ in deta_format.items():
            if type_ == 'int':
                input_widget = QSpinBox(self)
                input_widget.setRange(*next(ranges,(0,100)))
            elif type_ == 'str':input_widget = QLineEdit(self)

            self.input_widgets.append(input_widget)
            self.layout_.addRow(
                name,
                input_widget,
            )

    def get_value(self):
        value_list = []

        for widget in self.input_widgets:
            if type(widget) == QSpinBox:value_list.append(widget.value())
            elif type(widget) == QLineEdit:value_list.append(widget.text())

        return cast(
            list[int|str],
            value_list,
        )

class BaseCRUDWidget(BaseBotSettingsWidget):
    def __init__(self, title:str, description:str, parent:QWidget|None = None):
        super().__init__(title, description, parent)
        self.layout_ = QVBoxLayout(self)

    def init_ui(self,deta_widget:QAbstractItemView,deta_format:dict[str,Literal['int','str']],
                add_func:Callable[[list[int|str]],None],delete_func:Callable[[],None],
                ranges:Generator[tuple[int,int]]=(lambda: (yield (0,100)))()):
        self.layout_.addWidget(self.get_description())
        self.layout_.addWidget(deta_widget)
        
        self.input_widget = CRUDInput(deta_format,self,ranges)
        self.layout_.addWidget(self.input_widget)
        self.button_layout = QHBoxLayout()
        self.layout_.addLayout(self.button_layout)

        self.add_button = QPushButton('添加',self)
        self.add_button.clicked.connect(lambda:add_func(self.input_widget.get_value()))
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton('删除',self)
        self.delete_button.clicked.connect(delete_func)
        self.button_layout.addWidget(self.delete_button)

    def add(self,value:list[int|str]):...
    def delete(self):...
    def get_config(self) -> list:...
    #此为类型注解，具体逻辑专靠子类

class ButtonFormat(TypedDict):
    text:str
    row:int
    column:int

class BaseMultiCheckboxWidget(BaseBotSettingsWidget):
    def __init__(self, config_format:dict[str,ButtonFormat],config:dict[str,bool],
                 title:str, parent:QWidget|None = None,description_column_span:int=3):
        super().__init__(title, '只有这其中勾选的才会接受挑战，没有被勾选的就会自动拒绝', parent)
        self.buttons = cast(dict[str,QCheckBox],{})
        self.layout_ = QGridLayout(self)

        self.layout_.addWidget(
            self.get_description(),
            0,
            0,
            1,
            description_column_span,
        )

        for key,value in config_format.items():
            button = QCheckBox(value['text'],self)
            button.setChecked(config[key])
            self.buttons[key] = button

            self.layout_.addWidget(
                button,
                value['row']+1,
                value['column'],
            )

    def get_config(self):
        return {key:button.isChecked() for key,button in self.buttons.items()}