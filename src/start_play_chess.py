from bot import BotMain
from board import BoardMain

window_list = []
def turn_from_main(is_bot:bool):
    if is_bot:
        window = BotMain()
    else:
        window = BoardMain()

    window_list.append(window)
    window.destroyed.connect(lambda:window_list.remove(window))
    window.show()