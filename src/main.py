from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from berserk import *
from widgets import *

app = QApplication([])
dialog = LoginDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    client = Client(TokenSession(dialog.get_token()))
    window = QMainWindow()
    menu_bar = window.menuBar()

    tree = JsonTreeWidget(window)
    window.setCentralWidget(tree)

    window.setWindowTitle('lichess api')
    window.setWindowIcon(QIcon('./lichess_icon.ico'))

    account_menu = menu_bar.addMenu('账号')
    more_menu = menu_bar.addMenu('更多功能还在开发中，敬请期待')

    get_account = QAction('获取账号全部信息')
    get_account.triggered.connect(lambda:tree.set_dict(client.account.get()))
    account_menu.addAction(get_account)

    get_email = QAction('获取账号邮箱')
    get_email.triggered.connect(lambda:tree.set_string(client.account.get_email()))
    account_menu.addAction(get_email)

    get_preferences = QAction('获取个人偏好设置')
    get_preferences.triggered.connect(lambda:tree.set_dict(client.account.get_preferences()))
    account_menu.addAction(get_preferences)

    window.show()
    app.exec()