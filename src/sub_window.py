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