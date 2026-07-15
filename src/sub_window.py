from input_dialogs import *
from business_logic import *
from tools import *

sub_window_list = []
thread_list = []

def start_sittings(client:Client):
    try:
        window = SettingsWindow(client)
        sub_window_list.append(window)#为了防止函数运行结束时窗口自动关闭
        window.destroyed.connect(lambda:sub_window_list.remove(window))
        window.show()
    except Exception as error:show_error_dialog(*get_error_details(error),'启动设置窗口报错')

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