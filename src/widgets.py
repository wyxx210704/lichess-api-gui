from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import *
from json import *
import os

from translates import *
from config_format import load_config_with_format

class JsonTreeWidget(QTreeWidget):
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["索引", "数据"])
        self.setIndentation(20)
        # 清空内容
        
    def clear_data(self):
        """清空所有数据"""
        self.clear()
    
    def set_integer(self, value:int):
        """显示整数"""
        self.clear_data()
        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, str(value))
        self.expandAll()
    
    def set_float(self, value:float):
        """显示小数"""
        self.clear_data()
        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, str(value))
        self.expandAll()
    
    def set_string(self, value:str):
        """显示字符串"""
        self.clear_data()
        if not isinstance(value, str):
            raise TypeError("参数必须是字符串类型")
        
        # 检查是否包含换行符
        if '\n' in value:
            # 多行字符串：按行分割
            lines = value.split('\n')
            for i, line in enumerate(lines, 1):
                item = QTreeWidgetItem(self)
                item.setText(0, f"第{i}行")
                item.setText(1, line)
        else:
            # 单行字符串：保持原样
            item = QTreeWidgetItem(self)
            item.setText(0, "返回结果")
            item.setText(1, value)
        
        self.expandAll()
    
    def set_bool(self, value:bool):
        """显示布尔值"""
        self.clear_data()
        item = QTreeWidgetItem(self)
        item.setText(0, "返回结果")
        item.setText(1, "True" if value else "False")
        self.expandAll()
    
    def set_list(self, value:list):
        """显示列表"""
        self.clear_data()
        if not isinstance(value, list):
            raise TypeError("参数必须是列表类型")
        self._add_list_items(self, value)
        self.expandAll()
    
    def set_dict(self, value:dict):
        """显示字典"""
        self.clear_data()
        if not isinstance(value, dict):
            raise TypeError("参数必须是字典类型")
        self._add_dict_items(self, value)
        self.expandAll()
    
    def _add_list_items(self, parent, data):
        """递归添加列表项"""
        for index, item_data in enumerate(data):
            item = QTreeWidgetItem(parent)
            item.setText(0, str(index))
            
            if isinstance(item_data, list):
                # 列表嵌套
                item.setText(1, "[]")
                self._add_list_items(item, item_data)
            elif isinstance(item_data, dict):
                # 字典嵌套
                item.setText(1, "{}")
                self._add_dict_items(item, item_data)
            elif isinstance(item_data, bool):
                item.setText(1, "True" if item_data else "False")
            elif item_data is None:
                item.setText(1, "None")
            elif isinstance(item_data, str):
                if '\n' in item_data:
                    # 多行字符串：展开为子项
                    item.setText(1, f"({item_data.count(chr(10)) + 1}行)")
                    lines = item_data.split('\n')
                    for i, line in enumerate(lines, 1):
                        line_item = QTreeWidgetItem(item)
                        line_item.setText(0, f"第{i}行")
                        line_item.setText(1, line)
                else:item.setText(1,get_value_translate(item_data))
            else:
                item.setText(1, str(item_data))

    def _add_dict_items(self, parent, data):
        """递归添加字典项"""
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, get_key_translate(str(key)))
            
            if isinstance(value, list):
                item.setText(1, "[]")
                self._add_list_items(item, value)
            elif isinstance(value, dict):
                item.setText(1, "{}")
                self._add_dict_items(item, value)
            elif isinstance(value, bool):
                item.setText(1, "True" if value else "False")
            elif value is None:
                item.setText(1, "null")
            elif isinstance(value, str):
                if '\n' in value:
                    # 多行字符串：展开为子项
                    item.setText(1, f"({value.count(chr(10)) + 1}行)")
                    lines = value.split('\n')
                    for i, line in enumerate(lines, 1):
                        line_item = QTreeWidgetItem(item)
                        line_item.setText(0, f"第{i}行")
                        line_item.setText(1, line)
                else:item.setText(1,get_value_translate(value))
            else:
                item.setText(1, str(value))

class NoStretchingSvgWidget(QSvgWidget):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)

    def load(self, contents:str):
        super().load(contents)
        self.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

class InformationDisplay(QLineEdit):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.setReadOnly(True)

class ControllableWizardPage(QWizardPage):
    def __init__(self,parent:QWidget|None=None):
        super().__init__(parent)
        self.state = True

    def change_state(self,state:bool):
        self.state = state
        self.completeChanged.emit()

    def isComplete(self):
        return self.state
    
class TokenManager(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        # 配置文件路径
        self.config_path = '../configuration_and_resources/config.json'
        
        # 存储token数据 {name: token}
        self.tokens_data = {}
        
        # 存储完整的配置数据（用于保留其他字段）
        self.full_config = {}
        
        # 初始化UI
        self.init_ui()
        
        # 加载配置
        self.load_config()
        
        # 刷新列表
        self.refresh_list()
    
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("Token管理器")
        self.setGeometry(0, 0, 455, 358)
        
        # 主布局
        self.layout_ = QVBoxLayout(self)
        
        # 列表控件
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.layout_.addWidget(self.list_widget)
        
        # 水平布局 - 输入区域
        input_layout = QHBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        
        self.label_name = QLabel("名称")
        self.line_edit_name = QLineEdit()
        form_layout.addRow(self.label_name, self.line_edit_name)
        
        self.label_token = QLabel("token")
        self.line_edit_token = QLineEdit()
        form_layout.addRow(self.label_token, self.line_edit_token)
        
        input_layout.addLayout(form_layout)
        
        # 添加按钮
        self.btn_add = QPushButton("添加")
        self.btn_add.clicked.connect(self.add_token)
        input_layout.addWidget(self.btn_add)
        
        self.layout_.addLayout(input_layout)
        
        # 水平布局 - 操作按钮
        button_layout = QHBoxLayout()
        
        self.btn_delete = QPushButton("删除")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_token)
        button_layout.addWidget(self.btn_delete)
        
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.save_config)
        button_layout.addWidget(self.btn_save)
        
        self.layout_.addLayout(button_layout)
    
    def load_config(self):
        """加载配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            if os.path.exists(self.config_path):
                self.full_config = load_config_with_format()
                # 提取 tokens 数据
                if 'tokens' in self.full_config:
                    self.tokens_data = self.full_config['tokens']
                else:
                    self.tokens_data = {}
                    self.full_config['tokens'] = self.tokens_data
            else:
                # 如果文件不存在，创建默认配置
                self.full_config = {'tokens': {}}
                self.tokens_data = {}
                self.save_config()
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置文件失败: {str(e)}")
            self.full_config = {'tokens': {}}
            self.tokens_data = {}
    
    def save_config(self):
        """保存配置到文件（只修改tokens字段，保留其他所有字段）"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 如果文件不存在，创建基础配置
            if not os.path.exists(self.config_path):
                self.full_config = {}
            
            # 只更新 tokens 字段，其他字段完全不动
            self.full_config['tokens'] = self.tokens_data
            
            # 写回文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                dump(self.full_config, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "提示", "保存成功！")
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")
            return False
    
    def refresh_list(self):
        """刷新列表显示"""
        self.list_widget.clear()
        
        # 按名称排序显示
        for name in sorted(self.tokens_data.keys()):
            item = QListWidgetItem(name)
            # 存储token数据到item中，方便获取
            item.setData(Qt.ItemDataRole.UserRole, self.tokens_data[name])
            self.list_widget.addItem(item)
    
    def add_token(self):
        """添加或更新token"""
        name = self.line_edit_name.text().strip()
        token = self.line_edit_token.text().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入名称！")
            return
        
        if not token:
            QMessageBox.warning(self, "警告", "请输入token！")
            return
        
        # 检查是否已存在
        if name in self.tokens_data:
            reply = QMessageBox.question(
                self, 
                "确认", 
                f"名称 '{name}' 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 添加/更新
        self.tokens_data[name] = token
        self.refresh_list()
        
        # 清空输入框
        self.line_edit_name.clear()
        self.line_edit_token.clear()
        
        # 自动选中刚添加的项目
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == name:
                self.list_widget.setCurrentRow(i)
                break
    
    def delete_token(self):
        """删除选中的token"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 '{name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.tokens_data[name]
            self.refresh_list()
            self.btn_delete.setEnabled(False)
            
            # 清空输入框
            self.line_edit_name.clear()
            self.line_edit_token.clear()
    
    def on_selection_changed(self):
        """选择变化时更新界面"""
        current_item = self.list_widget.currentItem()
        
        if current_item:
            self.btn_delete.setEnabled(True)
            name = current_item.text()
            token = current_item.data(Qt.ItemDataRole.UserRole)
            
            # 显示到输入框
            self.line_edit_name.setText(name)
            self.line_edit_token.setText(token)
        else:
            self.btn_delete.setEnabled(False)
            self.line_edit_name.clear()
            self.line_edit_token.clear()

class AutoLoginControl(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.layout_ = QVBoxLayout(self)
        self.config = load_config_with_format()

        self.group_box = QGroupBox(
            '是否自动登录',
            self,
        )

        self.group_box.setCheckable(True)
        self.layout_.addWidget(self.group_box)
        self.layout_in_group_box = QHBoxLayout(self.group_box)

        self.layout_in_group_box.addWidget(QLabel('token：'))
        self.token_input = QLineEdit(self.group_box)
        self.layout_in_group_box.addWidget(self.token_input)

        self.group_box.setChecked(self.config['auto_login']['enable'])
        self.token_input.setText(self.config['auto_login']['token'])

        self.save_button = QPushButton(
            '保存',
            self,
        )

        self.save_button.clicked.connect(self.save_file)
        self.layout_.addWidget(self.save_button)

    def save_file(self):
        self.config['auto_login']['enable'] = self.group_box.isChecked()
        self.config['auto_login']['token'] = self.token_input.text()

        dump(
            self.config,
            open(
                '../configuration_and_resources/config.json',
                'w',
                encoding='utf-8',
                errors='ignore',
            ),
            ensure_ascii=False,
            indent=4,
        )

        QMessageBox.information(
            None,
            '提示',
            '保存成功',
        )