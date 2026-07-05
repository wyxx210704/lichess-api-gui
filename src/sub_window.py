from input_dialogs import *
from business_logic import *
from tools import *
from thread_worker import CreateGameWorker

sub_window_list = []
thread_list = []

def start_sittings(client:Client):
    try:
        window = SettingsWindow(client)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动设置窗口报错')

def create_game(client:Client,parent:QWidget|None=None):
    time = get_int(parent,'输入基础时间（分钟）',0,180)
    incr = get_int(parent,'输入每步增加时间（秒）',0,180)

    variant = (get_item(parent,'选择变体',[
        "chess960",
        "kingOfTheHill",
        "threeCheck",
        "antichess",
        "atomic",
        "horde",
        "racingKings",
        "crazyhouse",
    ]) if get_bool(
        parent,
        '是否为变体',
    ) else 'standard')

    if variant == 'standard':
        # 这里时间分配用的逻辑跟官方一致
        minute = (time + (incr + 40)) // 60

        if minute < 3:perf = 'bullet'
        elif (minute >= 3) and (minute < 8):perf = 'blitz'
        elif (minute >= 8) and (minute < 25):perf = 'rapid'
        elif minute >= 25:perf = 'classical'
    else:perf = variant

    worker_thread = QThread()
    thread_list.append(worker_thread)
    worker = CreateGameWorker(
        client,
        time,
        incr,
        get_bool(parent,'是否排位'),
        variant,
        get_item(parent,'选择自己执棋颜色',["white", "black",'random']),
        (
            get_int(parent,'期待匹配到等级分最低的对手是多少分',400,client.account.get()['perfs'][perf]['rating']),
            get_int(parent,'期待匹配到等级分最高的对手是多少分',client.account.get()['perfs'][perf]['rating'],3000),
        )
    )

    window = NoCloseProgressDialog('正在匹配对手',parent)
    sub_window_list.append(window)
    window.destroyed.connect(lambda:sub_window_list.remove(window))

    worker.moveToThread(worker_thread)
    worker.end_event.connect(window.close)

    worker_thread.started.connect(worker.run_event)
    worker_thread.finished.connect(worker_thread.deleteLater)
    worker_thread.start()

def start_game_viewer(generator:Generator):
    try:
        window = GameViewer(generator)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动对局查看器报错')

def start_puzzle_viewer(client:Client,parent:QWidget|None=None):
    mode = get_item(parent,'选择获取谜题的模式',[
        '特定编号',
        '每日谜题',
        '根据难度选择',
    ])

    if mode == '特定编号':puzzle_deta = client.puzzles.get(get_id(parent,True))
    elif mode == '每日谜题':puzzle_deta = client.puzzles.get_daily()
    elif mode == '根据难度选择':puzzle_deta = client.puzzles.get_next(None,get_item(parent,'选择难度',[
        "easiest", 
        "easier", 
        "normal", 
        "harder", 
        "hardest"
    ]))
        
    try:
        window = ChessPuzzleViewer(puzzle_deta)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动谜题查看器报错',parent)