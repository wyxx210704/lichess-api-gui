from berserk import Client
from chess import STARTING_FEN
from datetime import timedelta
from chess.engine import *
from zai import ZhipuAiClient
from typing import cast
from berserk.types.common import VariantKey

from ..bot_settings.format import EngineName
from ..play_chess_general.game_formats import GameStste
from .bot_format import *
from ..chess_general_logic import get_board

class ChessAnalysis:
    def __init__(self,engine_names:EngineName,variant:VariantKey,client:Client,start_fen:str=STARTING_FEN):
        self.client = client
        self.variant = variant

        match variant:
            #horde和racingKings的起始局面很特殊
            case 'horde':self.start_fen = "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPPPPPP w kq - 0 1"
            case 'racingKings':self.start_fen = "8/8/8/8/8/8/krbnNBRK/qrbnNBRQ w - - 0 1"

            case 'fromPosition' | 'chess960':self.start_fen = start_fen
            #lichess里面fromPosition代表自定义起始局面，chess960本来就是需要起始局面的
            case _:self.start_fen = STARTING_FEN#标准国际象棋跟其他任何变体都是用普通起始局面

        try:self.engine = SimpleEngine.popen_uci((
                'engines/' + (engine_names['standard'] if 
                (variant == 'standard') or (variant == 'chess960') or 
                (variant == 'fromPosition') else engine_names['variants'])
            ))#默认方案：直接使用引擎
        except:self.engine = None#找不到引擎或者引擎加载失败时就用云分析

    def play_and_analysis(self,state:GameStste,draw_offered:bool=False):
        board = get_board(self.variant,self.start_fen)
        if state['moves'] != '':
            for uci_move in state['moves'].split(' '):
                board.push_uci(uci_move)

        if self.engine != None:
            result = self.engine.play(
                board,
                Limit(
                    white_clock=(state['wtime'].total_seconds() if type(state['wtime']) == timedelta else state['wtime']),
                    black_clock=(state['btime'].total_seconds() if type(state['btime']) == timedelta else state['btime']),
                    white_inc=(state['winc'].total_seconds() if type(state['winc']) == timedelta else state['winc']),
                    black_inc=(state['binc'].total_seconds() if type(state['binc']) == timedelta else state['binc']),
                ),
                info=INFO_ALL,
                draw_offered=draw_offered,
            )

            move = result.move.uci()
            info = result.info
            offer_draw = result.draw_offered
            resign = result.resigned
        else:
            result = self.client.analysis.get_cloud_evaluation(
                board.fen(),
                1,
                self.variant,
            )

            move = result['pvs'][0]['moves'].split(' ')[0]
            info = result
            offer_draw = False
            resign = False

        return cast(
            BotPlayResult,{
                'move':move,
                'info':info,
                'offer_draw':offer_draw,
                'resigned':resign,
            }
        )

    def close_engine(self):
        if self.engine != None:self.engine.close()

class AutoReplyMessage:
    def __init__(self,token:str,lichess_user_name:str):
        self.client = ZhipuAiClient(api_key=token)
        self.chat_history:list[ChatHistory] = [{
            'role': 'system', 
            'content': f'你现在需要为lichess bot帐号{lichess_user_name}去接管一个对局的聊天区，'
            '向你发送消息有可能是这个bot的对手，也有可能是这个对局的观众，'
            '你可以与他们聊天',
        }]

        self.roles = {
            'player':'对手',
            'spectator':'观众'
        }

    def make_a_chat(self,role:Literal['player','spectator'],text:str,user:str=''):
        self.chat_history.append({'role':'user',
        'content':self.roles[role] + user + '：' + text})

        try:
            answer = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=self.chat_history,
            ).choices[0].message.content
        except Exception as error:
            return cast(
                Answer,
                {
                    'state':'error',
                    'text':str(error),
                    'exception_type':error.__class__.__name__,
                }
            )
        else:
            self.chat_history.append({'role':'assistant','content':answer})
            return cast(
                Answer,
                {
                    'state':'ok',
                    'text':answer,
                }
            )