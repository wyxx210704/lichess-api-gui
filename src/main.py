from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from berserk import *

from widgets import JsonTreeWidget
from events import *

app = QApplication([])
token,is_bot = login()

client = Client(TokenSession(token))
window = QMainWindow()
window.setMinimumSize(700,400)
menu_bar = window.menuBar()

status_bar = window.statusBar()
status_bar.addWidget(QLabel('lichess-api-gui 版本1.7'))

progress_bar = QProgressBar()
progress_bar.setRange(0,100)
progress_bar.setValue(100)
progress_bar.setFormat('api工作状态')
status_bar.addWidget(progress_bar)

tree = JsonTreeWidget(window)
window.setCentralWidget(tree)

window.setWindowTitle('lichess api')
window.setWindowIcon(QIcon('../configuration_and_resources/lichess_icon.ico'))

account_menu = menu_bar.addMenu('账号')
users_menu = menu_bar.addMenu('查询用户')
puzzles_menu = menu_bar.addMenu('谜题')
challenges_menu = menu_bar.addMenu('挑战')
game_menu = menu_bar.addMenu('对局')

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

get_puzzle = QAction('获取特定编号的谜题')
get_puzzle.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get(get_id(window,True)))))
puzzles_menu.addAction(get_puzzle)

get_daily = QAction('今日谜题')
get_daily.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get_daily())))
puzzles_menu.addAction(get_daily)

get_difficulty = QAction('根据难度获取谜题')
get_difficulty.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.puzzles.get_next(None,get_item(window,'选择难度',["easiest", "easier", "normal", "harder", "hardest"])))))
puzzles_menu.addAction(get_difficulty)

create_challenge = QAction('挑战特定用户')
create_challenge.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.challenges.create(
    get_user_name(window,'输入被挑战的用户'),
    get_bool(window,'是否排位'),
    get_int(window,'输入基础时间（秒）',1,10800),
    get_int(window,'输入每步增加时间（秒）',1,180),
    None,
    get_item(window,'选择自己执棋颜色',["white", "black"]),
    (get_item(window,'选择变体',[
        "chess960",
        "kingOfTheHill",
        "threeCheck",
        "antichess",
        "atomic",
        "horde",
        "racingKings",
        "crazyhouse",
    ]) if get_bool(
        window,
        '是否为变体',
    ) else None),
))))
challenges_menu.addAction(create_challenge)

challenge_ai = QAction('挑战ai')
challenge_ai.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.challenges.create_ai(
    get_int(window,'输入AI等级',1,8),
    get_int(window,'输入基础时间（秒）',1,10800),
    get_int(window,'输入每步增加时间（秒）',1,180),
    None,
    get_item(window,'选择自己执棋颜色',["white", "black"]),
    (get_item(window,'选择变体',[
        "chess960",
        "kingOfTheHill",
        "threeCheck",
        "antichess",
        "atomic",
        "horde",
        "racingKings",
        "crazyhouse",
    ]) if get_bool(
        window,
        '是否为变体',
    ) else None),
))))
challenges_menu.addAction(challenge_ai)

if not is_bot:
    open_challenge = QAction('在大厅中创建对局')
    open_challenge.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.board.seek(
        get_int(window,'输入基础时间（秒）',1,10800),
        get_int(window,'输入每步增加时间（秒）',1,180),
        get_bool(window,'是否排位'),
        (get_item(window,'选择变体',[
            "chess960",
            "kingOfTheHill",
            "threeCheck",
            "antichess",
            "atomic",
            "horde",
            "racingKings",
            "crazyhouse",
        ]) if get_bool(
            window,
            '是否为变体',
        ) else 'standard'),
        get_item(window,'选择自己执棋颜色',["white", "black",'random']),
        (
            -get_int(window,'期待匹配到等级分最低的对手比自己低多少',0,500),
            get_int(window,'期待匹配到等级分最高的对手比自己高多少',0,500),
        )
    ))))
    challenges_menu.addAction(open_challenge)

challenges_menu.addSeparator()

get_mine = QAction('查看我的挑战')
get_mine.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.challenges.get_mine())))
challenges_menu.addAction(get_mine)

cancel = QAction('取消挑战')
cancel.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.challenges.cancel(get_id(window,False,'输入要取消的挑战编号')))))
challenges_menu.addAction(cancel)

accept = QAction('接受挑战')
accept.triggered.connect(lambda:run_function(progress_bar,lambda:client.challenges.accept(get_id(window,False,'输入要接受的挑战编号'))))
challenges_menu.addAction(accept)

decline = QAction('拒绝挑战')
decline.triggered.connect(lambda:run_function(progress_bar,lambda:client.challenges.decline(get_id(window,False,'输入要拒绝的挑战编号'))))
challenges_menu.addAction(decline)

export = QAction('导出单个对局')
export.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.games.export(
    get_id(window,False,'输入要导出的对局编号'),
    False,
    get_bool(window,'是否添加棋谱'),
    get_bool(window,'是否添加标签'),
    get_bool(window,'是否添加时钟'),
    get_bool(window,'是否添加分析'),
    get_bool(window,'是否添加开局'),
    get_bool(window,'是否添加注释'),
))))
game_menu.addAction(export)

export_by_player_json = QAction('批量导出用户对局（json）')
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
get_ongoing.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_list(client.games.get_ongoing())))
game_menu.addAction(get_ongoing)

view_game = QAction('观看对局')
view_game.triggered.connect(lambda:start_game_viewer(client.games.stream_game_moves(get_id(window,False,'输入要观看的对局编号'))))
game_menu.addAction(view_game)

import_game = QAction('导入对局')
import_game.triggered.connect(lambda:run_function(progress_bar,lambda:tree.set_dict(client.games.import_game(get_pgn(window,'导入对局')))))
game_menu.addAction(import_game)

window.show()
app.exec()