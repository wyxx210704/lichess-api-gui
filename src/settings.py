from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from json import load,dump
import os

from config_format import ConfigFormat

class BaseSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def load_config_with_format(self) -> ConfigFormat:
        return load(open(
            '../configuration_and_resources/config.json',
            'r',
            encoding='utf-8',
            errors='ignore',
        ))
    
    def save_config(self,config:ConfigFormat):
        dump(
            config,
            open(
                '../configuration_and_resources/config.json',
                'w',
                encoding='utf-8',
                errors='ignore',
            ),
            ensure_ascii=False,
            indent=4,
        )

class TokenManager(BaseSettingsWidget):
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
        self.btn_save.clicked.connect(self.save_config_)
        button_layout.addWidget(self.btn_save)
        
        self.layout_.addLayout(button_layout)
    
    def load_config(self):
        """加载配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            if os.path.exists(self.config_path):
                self.full_config = self.load_config_with_format()
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
                self.save_config_()
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置文件失败: {str(e)}")
            self.full_config = {'tokens': {}}
            self.tokens_data = {}
    
    def save_config_(self):
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
            self.save_config(self.full_config)
            
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

class AutoLoginControl(BaseSettingsWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.layout_ = QVBoxLayout(self)
        self.config = self.load_config_with_format()

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

        self.save_config(self.config)
        QMessageBox.information(
            self,
            '提示',
            '保存成功',
        )