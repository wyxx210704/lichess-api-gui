from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from berserk import *

from widgets import *
from events import *

app = QApplication([])
while True:
    token,success = QInputDialog.getText(
        None,
        '登录',
        '请输入token',
    )

    if success:
        try:Client(TokenSession(token)).account.get()
        except Exception as error:QMessageBox.critical(
            None,
            '错误',
            f'登录发生错误：{error}')
        else:
            QMessageBox.information(
                None,
                '提示',
                '登录成功，接下来将检查账号类型')
            break
    else:exit(0)

user_info = Client(TokenSession(token)).account.get()
if ('title' in user_info) and (user_info['title'] == 'BOT'):
    is_bot = True
    QMessageBox.information(
        None,
        '检查结果',
        '这是一个bot账号，下棋板块会调用client.bot'
    )
else:
    is_bot = False
    QMessageBox.information(
        None,
        '检查结果',
        '这不是一个bot账号，下棋板块会调用client.board'
    )

client = Client(TokenSession(token))
window = QMainWindow()
window.setMinimumSize(700,400)
menu_bar = window.menuBar()

status_bar = window.statusBar()
status_bar.addWidget(QLabel('lichess-api-gui 版本1.2\n如果进度条是满的那么就没有API操作，否则其他情况都是有API操作'))

progress_bar = QProgressBar()
progress_bar.setRange(0,100)
progress_bar.setValue(100)
progress_bar.setFormat('')
status_bar.addWidget(progress_bar)

tree = JsonTreeWidget(window)
window.setCentralWidget(tree)

window.setWindowTitle('lichess api')
window.setWindowIcon(QIcon('./lichess_icon.ico'))

account_menu = menu_bar.addMenu('账号')
users_menu = menu_bar.addMenu('查询用户')
more_menu = menu_bar.addMenu('更多功能还在开发中，敬请期待')

get_account = QAction('账号全部信息')
get_account.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.account.get())))
account_menu.addAction(get_account)

get_email = QAction('账号邮箱')
get_email.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_string(client.account.get_email())))
account_menu.addAction(get_email)

get_preferences = QAction('个人偏好设置')
get_preferences.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.account.get_preferences())))
account_menu.addAction(get_preferences)

get_activity_feed = QAction('用户最近活动动态')
get_activity_feed.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_activity_feed(get_user_name(window)))))
users_menu.addAction(get_activity_feed)

get_all_top_10 = QAction('全部排行榜前十名')
get_all_top_10.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_all_top_10())))
users_menu.addAction(get_all_top_10)

get_crosstable = QAction('两个用户之间的对战数据')
get_crosstable.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_crosstable(get_user_name(window,'输入第一个用户'),get_user_name(window,'输入第二个用户')))))
users_menu.addAction(get_crosstable)

get_leaderboard = QAction('某个特定种类的排行榜')
get_leaderboard.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_leaderboard(get_item(window,'选择棋的种类',PERFS),get_int(window,'输入要获取的排名数量')))))
users_menu.addAction(get_leaderboard)

get_live_streamers = QAction('直播流')
get_live_streamers.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_live_streamers())))
users_menu.addAction(get_live_streamers)

get_public_data = QAction('用户公开资料')
get_public_data.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_public_data(get_user_name(window)))))
users_menu.addAction(get_public_data)

get_rating_history = QAction('用户等级分变化历史')
get_rating_history.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_rating_history(get_user_name(window)))))
users_menu.addAction(get_rating_history)

get_user_performance = QAction('用户某个特定种类的表现情况')
get_user_performance.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_user_performance(get_user_name(window),get_item(window,'选择棋的种类',PERFS)))))
users_menu.addAction(get_user_performance)

window.show()
app.exec()