from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import *
from berserk import *

class LoginWorker(QObject):
    thread_state = pyqtSignal(bool)
    error = pyqtSignal(str)
    success = pyqtSignal()

    def __init__(self,token:str):
        super().__init__()
        self.token = token

    def run_event(self):
        self.thread_state.emit(True)
        try:
            Client(TokenSession(self.token)).account.get()
        except Exception as error:
            self.error.emit(str(error))
        else:
            self.success.emit()

    def finish_event(self):
        self.thread_state.emit(False)

class LoginDialog(QDialog):
    def __init__(self,parent:QWidget|None = None,):
        super().__init__(parent)
        self.layout_ = QVBoxLayout(self)
        self.setWindowTitle('登录')
        self.setWindowIcon(QIcon('./lichess_icon.ico'))

        self.layout_.addWidget(QLabel(
            '请用token进行登录，没有token请到\nhttps://lichess.org/account/oauth/token 创建',
            self,
        ))

        self.input_token = QLineEdit(self)
        self.input_token.setPlaceholderText('输入token')
        self.layout_.addWidget(self.input_token)

        self.button = QPushButton(
            '登录',
            self,
        )

        self.button.clicked.connect(self.login)
        self.layout_.addWidget(self.button)

        self.layout_.addWidget(QLabel(
            'lichess-api-gui 版本1.1',
            self,
        ))
    def get_token(self):return self.input_token.text()

    def login(self):
        # 禁用登录按钮，防止重复点击
        self.button.setEnabled(False)
        
        def show_and_hide_progress_dialog(state:bool):
            if state:
                self.progress_dialog.show()
            else:
                self.progress_dialog.hide()
                # 恢复登录按钮
                self.button.setEnabled(True)

        def show_error(info:str):
            QMessageBox.critical(
                None,
                '报错',
                f'登录发生错误：{info}'
            )
            self.button.setEnabled(True)  # 错误时恢复按钮

        def success():
            QMessageBox.information(
                None,
                '登录成功',
                '登录成功，准备跳转'
            )
            self.accept()

        # 保存为实例变量，防止被垃圾回收
        self.worker_thread = QThread()
        self.worker = LoginWorker(self.input_token.text())  # 保存worker引用
        self.progress_dialog = QProgressDialog(  # 保存progress_dialog引用
            '正在登录中',
            None,
            0,
            0,
        )

        cancel_btn = QPushButton("不能取消")
        cancel_btn.setEnabled(False)
        self.progress_dialog.setCancelButton(cancel_btn)
        self.progress_dialog.hide()

        self.worker.moveToThread(self.worker_thread)
        self.worker.thread_state.connect(show_and_hide_progress_dialog)
        self.worker.error.connect(show_error)
        self.worker.success.connect(success)

        self.worker_thread.started.connect(self.worker.run_event)
        self.worker_thread.finished.connect(self.worker.finish_event)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

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
                item.setText(1, "null")
            elif isinstance(item_data, str) and '\n' in item_data:
                # 多行字符串：展开为子项
                item.setText(1, f"({item_data.count(chr(10)) + 1}行)")
                lines = item_data.split('\n')
                for i, line in enumerate(lines, 1):
                    line_item = QTreeWidgetItem(item)
                    line_item.setText(0, f"第{i}行")
                    line_item.setText(1, line)
            else:
                item.setText(1, str(item_data))

    def _add_dict_items(self, parent, data):
        """递归添加字典项"""
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, str(key))
            
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
            elif isinstance(value, str) and '\n' in value:
                # 多行字符串：展开为子项
                item.setText(1, f"({value.count(chr(10)) + 1}行)")
                lines = value.split('\n')
                for i, line in enumerate(lines, 1):
                    line_item = QTreeWidgetItem(item)
                    line_item.setText(0, f"第{i}行")
                    line_item.setText(1, line)
            else:
                item.setText(1, str(value))

