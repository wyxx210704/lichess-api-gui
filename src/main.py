from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from berserk import *
import os.path

from widgets import JsonTreeWidget
from start_play_chess import turn_from_main
from events import *
from costants import ICON

app = QApplication([])
translator = QTranslator()
qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
qm_file_path = os.path.join(qt_translations_path, "qt_zh_CN.qm")

if translator.load(qm_file_path):app.installTranslator(translator)
client,is_bot = login()

window = QMainWindow()
window.setMinimumWidth(400)
menu_bar = window.menuBar()

status_bar = window.statusBar()
status_bar.addWidget(QLabel('lichess-api-gui 版本2.10'))

progress_bar = QProgressBar()
progress_bar.setRange(0,100)
progress_bar.setValue(100)
progress_bar.setFormat('api工作状态')
status_bar.addWidget(progress_bar)

tree = JsonTreeWidget(window)
window.setCentralWidget(tree)

window.setWindowTitle('lichess api')
window.setWindowIcon(QIcon(ICON))
window.resize(
    750,
    500,
)

account_menu = menu_bar.addMenu('账号')
users_menu = menu_bar.addMenu('查询用户')
puzzles_menu = menu_bar.addMenu('谜题')
game_menu = menu_bar.addMenu('对局')
more_menu = menu_bar.addMenu('更多')

get_account = QAction('账号全部信息')
get_account.setShortcut('Ctrl+Shift+A, I')
get_account.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.account.get())))
account_menu.addAction(get_account)

get_email = QAction('账号邮箱')
get_email.setShortcut('Ctrl+Shift+A, E')
get_email.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_string(client.account.get_email())))
account_menu.addAction(get_email)

get_preferences = QAction('个人偏好设置')
get_preferences.setShortcut('Ctrl+Shift+A, P')
get_preferences.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.account.get_preferences())))
account_menu.addAction(get_preferences)

get_activity_feed = QAction('用户最近活动动态')
get_activity_feed.setShortcut('Ctrl+Shift+U, A')
get_activity_feed.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_activity_feed(get_user_name(window)))))
users_menu.addAction(get_activity_feed)

get_all_top_10 = QAction('全部排行榜前十名')
get_all_top_10.setShortcut('Ctrl+Shift+U, T')
get_all_top_10.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_all_top_10())))
users_menu.addAction(get_all_top_10)

get_crosstable = QAction('两个用户之间的对战数据')
get_crosstable.setShortcut('Ctrl+Shift+U, C')
get_crosstable.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_crosstable(get_user_name(window,'输入第一个用户'),get_user_name(window,'输入第二个用户'),get_bool(window,'是否获取当前比赛数据')))))
users_menu.addAction(get_crosstable)

get_leaderboard = QAction('某个特定种类的排行榜')
get_leaderboard.setShortcut('Ctrl+Shift+U, L')
get_leaderboard.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_leaderboard(get_item(window,'选择棋的种类',PERFS),get_int(window,'输入要获取的排名数量')))))
users_menu.addAction(get_leaderboard)

get_live_streamers = QAction('直播流')
get_live_streamers.setShortcut('Ctrl+Shift+U, S')
get_live_streamers.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_live_streamers())))
users_menu.addAction(get_live_streamers)

get_public_data = QAction('用户公开资料')
get_public_data.setShortcut('Ctrl+Shift+U, P')
get_public_data.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_public_data(get_user_name(window)))))
users_menu.addAction(get_public_data)

get_rating_history = QAction('用户等级分变化历史')
get_rating_history.setShortcut('Ctrl+Shift+U, R')
get_rating_history.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.users.get_rating_history(get_user_name(window)))))
users_menu.addAction(get_rating_history)

get_user_performance = QAction('用户在单个性能指标上的表现统计')
get_user_performance.setShortcut('Ctrl+Shift+U, U')
get_user_performance.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.users.get_user_performance(get_user_name(window),get_item(window,'选择棋的种类',PERFS)))))
users_menu.addAction(get_user_performance)

get_puzzle = QAction('获取特定编号的谜题')
get_puzzle.setShortcut('Ctrl+Shift+P, P')
get_puzzle.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get(get_id(window,True)))))
puzzles_menu.addAction(get_puzzle)

get_daily = QAction('今日谜题')
get_daily.setShortcut('Ctrl+Shift+P, D')
get_daily.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get_daily())))
puzzles_menu.addAction(get_daily)

get_difficulty = QAction('根据难度获取谜题')
get_difficulty.setShortcut('Ctrl+Shift+P, I')
get_difficulty.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get_next(None,get_item(window,'选择难度',["easiest", "easier", "normal", "harder", "hardest"])))))
puzzles_menu.addAction(get_difficulty)

puzzles_menu.addSeparator()

view_puzzle = QAction('在独立窗口中查看谜题')
view_puzzle.setShortcut('Ctrl+Shift+P, V')
view_puzzle.triggered.connect(lambda:start_puzzle_viewer(client,window))
puzzles_menu.addAction(view_puzzle)

export_json = QAction('导出单个对局（json）')
export_json.setShortcut('Ctrl+Shift+G, E, J')
export_json.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.games.export(
    get_id(window,False,'输入要导出的对局编号'),
    False,
    get_bool(window,'是否添加棋谱'),
    get_bool(window,'是否添加标签'),
    get_bool(window,'是否添加时钟'),
    get_bool(window,'是否添加分析'),
    get_bool(window,'是否添加开局'),
    get_bool(window,'是否添加注释'),
))))
game_menu.addAction(export_json)

export_pgn = QAction('导出单个对局（pgn）')
export_pgn.setShortcut('Ctrl+Shift+G, E, P')
export_pgn.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_string(client.games.export(
    get_id(window,False,'输入要导出的对局编号'),
    True,
    get_bool(window,'是否添加棋谱'),
    get_bool(window,'是否添加标签'),
    get_bool(window,'是否添加时钟'),
    get_bool(window,'是否添加分析'),
    get_bool(window,'是否添加开局'),
    get_bool(window,'是否添加注释'),
))))
game_menu.addAction(export_pgn)

export_by_player_json = QAction('批量导出用户对局（json）')
export_by_player_json.setShortcut('Ctrl+Shift+G, P, J')
export_by_player_json.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(list(client.games.export_by_player(
    get_user_name(window,'输入：要导出谁的对局'),
    False,
    None,
    None,
    get_int(window,'要导出多少对局'),
    None,
    get_screening(window,'排位对局'),
    get_item(window,'选择变体',PERFS),
    None,
    get_screening(window,'已分析的对局'),
    get_bool(window,'是否添加棋谱'),
    get_bool(window,'pgn是否在json里面'),
    get_bool(window,'是否添加标签'),
    get_bool(window,'是否添加时钟'),
    get_bool(window,'是否添加分析'),
    get_bool(window,'是否添加开局'),
    get_screening(window,'正在进行的对局'),
    get_screening(window,'已结束的对局'),
    None,
    None,
    get_bool(window,'是否添加注释'),
)))))
game_menu.addAction(export_by_player_json)

export_by_player_pgn = QAction('批量导出用户对局（pgn）')
export_by_player_pgn.setShortcut('Ctrl+Shift+G, P, P')
export_by_player_pgn.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(list(client.games.export_by_player(
    get_user_name(window,'输入：要导出谁的对局'),
    True,
    None,
    None,
    get_int(window,'要导出多少对局'),
    None,
    get_screening(window,'排位对局'),
    get_item(window,'选择变体',PERFS),
    None,
    get_screening(window,'已分析的对局'),
    get_bool(window,'是否添加棋谱'),
    None,
    get_bool(window,'是否添加标签'),
    get_bool(window,'是否添加时钟'),
    get_bool(window,'是否添加分析'),
    get_bool(window,'是否添加开局'),
    get_screening(window,'正在进行的对局'),
    get_screening(window,'已结束的对局'),
    None,
    None,
    get_bool(window,'是否添加注释'),
)))))
game_menu.addAction(export_by_player_pgn)

game_menu.addSeparator()

get_ongoing = QAction('正在进行的对局')
get_ongoing.setShortcut('Ctrl+Shift+G, O')
get_ongoing.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.games.get_ongoing())))
game_menu.addAction(get_ongoing)

view_game = QAction('观看对局')
view_game.setShortcut('Ctrl+Shift+G, V')
view_game.triggered.connect(lambda:start_game_viewer(client.games.stream_game_moves(get_id(window,False,'输入要观看的对局编号'))))
game_menu.addAction(view_game)

import_game = QAction('导入对局')
import_game.setShortcut('Ctrl+Shift+G, I')
import_game.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.games.import_game(get_pgn(window,'导入对局')))))
game_menu.addAction(import_game)

turn_to_play_chess = QAction('跳转到下棋')
turn_to_play_chess.setShortcut('Ctrl+Shift+M, T')
turn_to_play_chess.triggered.connect(lambda:turn_from_main(client,is_bot))
more_menu.addAction(turn_to_play_chess)

settings = QAction('设置')
settings.setShortcut('Ctrl+Shift+M, S')
settings.triggered.connect(lambda:start_sittings(client))
more_menu.addAction(settings)

window.show()
app.exec()