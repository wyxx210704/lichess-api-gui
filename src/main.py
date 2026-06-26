from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from berserk import *

from widgets import *
from events import *

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
    users_menu = menu_bar.addMenu('查询用户')
    more_menu = menu_bar.addMenu('更多功能还在开发中，敬请期待')

    get_account = QAction('账号全部信息')
    get_account.triggered.connect(lambda:tree.set_dict(client.account.get()))
    account_menu.addAction(get_account)

    get_email = QAction('账号邮箱')
    get_email.triggered.connect(lambda:tree.set_string(client.account.get_email()))
    account_menu.addAction(get_email)

    get_preferences = QAction('个人偏好设置')
    get_preferences.triggered.connect(lambda:tree.set_dict(client.account.get_preferences()))
    account_menu.addAction(get_preferences)

    get_activity_feed = QAction('用户最近活动动态')
    get_activity_feed.triggered.connect(lambda:tree.set_list(client.users.get_activity_feed(get_user_name(window))))
    users_menu.addAction(get_activity_feed)

    get_all_top_10 = QAction('全部排行榜前十名')
    get_all_top_10.triggered.connect(lambda:tree.set_dict(client.users.get_all_top_10()))
    users_menu.addAction(get_all_top_10)

    get_crosstable = QAction('两个用户之间的对战数据')
    get_crosstable.triggered.connect(lambda:tree.set_dict(client.users.get_crosstable(get_user_name(window,'输入第一个用户'),get_user_name(window,'输入第二个用户'))))
    users_menu.addAction(get_crosstable)

    get_leaderboard = QAction('某个特定种类的排行榜')
    get_leaderboard.triggered.connect(lambda:tree.set_list(client.users.get_leaderboard(get_item(window,'选择棋的种类',PERFS),get_int(window,'输入要获取的排名数量'))))
    users_menu.addAction(get_leaderboard)

    get_live_streamers = QAction('直播流')
    get_live_streamers.triggered.connect(lambda:tree.set_list(client.users.get_live_streamers()))
    users_menu.addAction(get_live_streamers)

    get_public_data = QAction('用户公开资料')
    get_public_data.triggered.connect(lambda:tree.set_dict(client.users.get_public_data(get_user_name(window))))
    users_menu.addAction(get_public_data)

    get_rating_history = QAction('用户等级分变化历史')
    get_rating_history.triggered.connect(lambda:tree.set_list(client.users.get_rating_history(get_user_name(window))))
    users_menu.addAction(get_rating_history)

    get_leaderboard = QAction('用户某个特定种类的表现情况')
    get_leaderboard.triggered.connect(lambda:tree.set_list(client.users.get_leaderboard(get_user_name(window),get_item(window,'选择棋的种类',PERFS))))
    users_menu.addAction(get_leaderboard)

    window.show()
    app.exec()