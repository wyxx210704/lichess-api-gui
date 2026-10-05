from PyQt6.QtCore import *
from berserk import Client
from berserk.types.challenges import ChallengeJson
from berserk.exceptions import ResponseError
from time import sleep
from random import choice
from chess import Color
from typing import cast,Generator

from ..bot_settings.format import ConfigFormat,BasicSettings
from ..play_chess_general.game_formats import GameStste,EventInGame
from .bot_core import AutoReplyMessage,ChessAnalysis
from ..custom_api import ExtensionClient

class EventListen(QObject):
    ongoing_game_update = pyqtSignal(
        dict,                   
        str,                 
    )

    challenge_update = pyqtSignal(   
        dict,                 
        str,               
    )

    state_update = pyqtSignal(
        list,
        list,
    )
    
    def __init__(self,client:Client,config:ConfigFormat):
        super().__init__()
        self.client = client
        self.config = config
        self.my_name = client.account.get()['username']

    def run_event(self):
        for value in self.client.bots.stream_incoming_events():
            self.state_update.emit(
                self.client.challenges.get_mine()['in'],
                self.client.games.get_ongoing(),
            )

            if value['type'] == 'challenge' or value['type'] == 'challengeCanceled' or value['type'] == 'challengeDeclined':
                self.challenge_update.emit(
                    value['challenge'],
                    {
                        "challenge":'challenge',
                        "challengeCanceled":'cancel',
                        "challengeDeclined":'decline',
                    }[value['type']],
                )

                if value['type'] == 'challenge':
                    self.check_challenge(value['challenge'])
            elif value['type'] == 'gameStart' or value['type'] == 'gameFinish':
                self.ongoing_game_update.emit(
                    value['game'],
                    {
                        'gameStart':'start',
                        'gameFinish':'finish',
                    }[value['type']],
                )

    def check_challenge(self,challenge:ChallengeJson):
        if challenge['challenger']['name'] != self.my_name:#是进来的挑战
            if self.config['basic_settings']['more_settings']['challenge_no_bot'] and \
            (('title' in challenge['challenger']) and (challenge['challenger']['title'] == 'BOT')):
                self.client.challenges.decline(challenge['id'],'noBot')#我不接受来自机器人的挑战
            elif self.config['basic_settings']['more_settings']['challenge_only_bot'] and \
            (not (('title' in challenge['challenger']) and (challenge['challenger']['title'] == 'BOT'))):
                self.client.challenges.decline(challenge['id'],'onlyBot')#我只接受来自机器人的挑战
            elif challenge['challenger']['name'] in self.config['basic_settings']['block_list']:
                self.client.challenges.decline(challenge['id'],'generic')#我目前不接受挑战
            elif len(self.client.games.get_ongoing()) >= self.config['basic_settings']['more_settings']['max_game']:
                self.client.challenges.decline(challenge['id'],'later')#我现在不方便对弈，请稍后再邀请
            elif ((challenge['timeControl']['type'] == 'unlimited') or #因为这里暂时不支持无限时间对局
            (not self.config['challenge_in']['support_time'][challenge['speed']])):
                self.client.challenges.decline(challenge['id'],'timeControl')#我不接受此时限设置的挑战
            elif not self.config['challenge_in']['support_variants']['standard' if 
            challenge['variant']['key'] == 'fromPosition' else challenge['variant']['key']]:
                self.client.challenges.decline(challenge['id'],'variant')#我现在不愿意下这个变体
            else:
                if challenge['rated']:
                    if not self.config['challenge_in']['support_mode']['rated']:
                        self.client.challenges.decline(challenge['id'],'casual')#请向我发起休闲挑战
                    else:self.client.challenges.accept(challenge['id'])
                else:
                    if not self.config['challenge_in']['support_mode']['casual']:
                        self.client.challenges.decline(challenge['id'],'rated')#请向我发起排位挑战
                    else:self.client.challenges.accept(challenge['id'])

    def apply_settings(self,config:ConfigFormat):
        self.config = config

class ChallengeOutTimer(QObject):
    challenge_out = pyqtSignal(list)
    current_state = pyqtSignal(str)

    def __init__(self,client:Client,config:ConfigFormat):
        super().__init__()
        self.is_running = True
        self.client = client
        self.count = 0
        self.auto_match_config = config['auto_match']
        self.auto_match_interval = (
            config
            ['basic_settings']
            ['more_settings']
            ['auto_match_interval']
        )

    def stop(self):self.is_running = False

    def run_event(self):
        while self.is_running:
            sleep(1)
            self.count += 1

            #因为这里传进去分钟，所以需要乘60转换成秒
            if ((self.count % (self.auto_match_interval * 60)) == 0):
                self.create_an_auto_match()

            if (self.count % 5) == 0:
                #每5秒更新【出去的挑战】列表
                self.challenge_out.emit(self.client.challenges.get_mine()['out'])

    def create_an_auto_match(self):
        if len(self.client.games.get_ongoing()) != 0:return
        self.current_state.emit('正在查找在线机器人')
        online_bots = list(self.client.bots.get_online_bots(512))
        bot = choice(online_bots)['username']
        weight_expansion_list = []

        for key,weight in self.auto_match_config['variants_weight'].items():
            for _ in range(weight):weight_expansion_list.append(key)

        try:
            self.client.challenges.create(
                bot,
                choice(
                    [False] if self.auto_match_config['enable_mode']['casual'] else []
                    + [True] if self.auto_match_config['enable_mode']['rated'] else []
                ),
                choice(self.auto_match_config['alternative_time'])['limit'] * 60,#分钟要转换成秒
                choice(self.auto_match_config['alternative_time'])['increment'],
                None,#不是通讯棋
                None,#不提供此参数则颜色随机
                choice(weight_expansion_list),
            )
        except IndexError:
            #random.choice对一个空列表随机选择时会报错IndexError
            self.current_state.emit('自动匹配失败，请检查配置文件后再重试')
        except ResponseError as error:
            self.current_state.emit(f'发出挑战请求时报错：状态码【{error.status_code}：'
                                    f'{error.reason}】，报错原因{error.cause}')
        except Exception as error:
            self.current_state.emit('自动匹配时遇到未知报错：'
                                    f'【{error.__class__.__name__}：{error}】')
        else:self.current_state.emit(f'已成功在{len(online_bots)}个机器人里面选择{bot}发起挑战')

    def apply_settings(self,config:ConfigFormat):
        self.auto_match_config = config['auto_match']
        self.auto_match_interval = (
            config
            ['basic_settings']
            ['more_settings']
            ['auto_match_interval']
        )

class PlayChessStream(QObject):
    send_dict = pyqtSignal(dict)
    state_changed = pyqtSignal(str)
    engine_info_changed = pyqtSignal(dict)

    def __init__(self,client:Client,game_id:str,color:Color,config:BasicSettings):
        super().__init__()
        self.client = ExtensionClient.from_berserk(client)
        self.game_id = game_id
        self.color = color
        self.config = config

    def run_event(self):
        for value in cast(Generator[EventInGame],
        self.client.bots.stream_game_state(self.game_id)):
            self.send_dict.emit(value)

            match value['type']:
                case 'gameFull':
                    match value['variant']['key']:
                        case 'chess960' | 'fromPosition':
                            self.analyzer = ChessAnalysis(
                                self.config['engine_name'],
                                value['variant']['key'],
                                self.client,
                                value['initialFen'],
                            )
                        case 'standard':
                            self.analyzer = ChessAnalysis(
                                self.config['engine_name'],
                                value['variant']['key'],
                                self.client,
                            )
                        case _:
                            self.analyzer = ChessAnalysis(
                                self.config['engine_name'],
                                value['variant']['key'],
                                self.client,
                            )

                    if self.config['auto_reply_message']['enabled']:
                        self.auto_reply_message_ai = AutoReplyMessage(
                            self.config['auto_reply_message']['api_key'],
                            self.client.account.get()['username'],
                        )

                    self.client.bots.post_message(
                        self.game_id,
                        '欢迎和我下棋，下棋期间可以随时和我聊天' + \
                        ('，有ai实时接管聊天区' if self.config['auto_reply_message']['enabled'] else ''),
                        False,
                    )

                    self.client.bots.post_message(
                        self.game_id,
                        '欢迎来这里观战我的棋局，观战过程可以随时和我聊天' + \
                        ('，有ai实时接管聊天区' if self.config['auto_reply_message']['enabled'] else ''),
                        False,
                    )

                    self.receive_state(value['state'])
                case 'gameState':
                    self.receive_state(value)
                case 'chatLine' if self.config['auto_reply_message']['enabled'] \
                and ((value['username'] != 'lichess') and (value['username'] != \
                self.client.account.get()['username'])):#因为系统提示和自己不算
                    result = self.auto_reply_message_ai.make_a_chat(
                        value['room'],
                        value['text'],
                        value['username'],
                    )

                    if result['state'] == 'ok':
                        try:self.client.bots.post_message(
                                self.game_id,
                                result['text'],
                                (value['room'] == 'spectator'),#这直接就是个布尔值
                                #如果是观众来的那就发起观众那边
                            )
                        except Exception as error:
                            ok = False
                            error_reason = str(error)
                            error_type = error.__class__.__name__
                        else:
                            ok = True
                            text = result['text']
                    else:
                        ok = False
                        error_reason = result['text']#如果发生错误的时候那就是错误的文字
                        error_type = result['exception_type']

                    if ok:self.state_changed.emit(f'发送消息成功：{text}')
                    else:self.state_changed.emit(f'发送消息报错【{error_type}】：{error_reason}')
                case 'opponentGone' if value['gone'] and (value['claimWinInSeconds'] <= 0):
                    try:self.client.extension_bot.claim_victory(self.game_id)
                    except Exception as error:self.state_changed.emit(f'获得胜利报错【{error.__class__.__name__}】：{error}')
                    else:self.state_changed.emit('成功在此对局取得胜利')

    def receive_state(self,state:GameStste):
        moves_str:str = state['moves']
        moves_list = moves_str.split(' ')

        if state['status'] == 'started':
            match self.color:
                case True:#chess.WHITE
                    if ('btakeback' in state) and (state['btakeback'] == True):
                        self.client.extension_bot.accept_takeback(self.game_id)
                    elif (len(moves_list) % 2 == 0) or (moves_str == ''):#轮到白方走棋
                        result = self.analyzer.play_and_analysis(
                            state,
                            (('bdraw' in state) and (state['bdraw'] == True)),
                        )

                        try:
                            self.client.bots.make_move(self.game_id,result['move'])
                            self.engine_info_changed.emit(result['info'])
                            self.client.extension_bot.handle_draw(self.game_id,result['offer_draw'])#如果是false那么啥事也不发生
                            if result['resigned']:self.client.bots.resign_game(self.game_id)
                        except Exception as error:self.state_changed.emit(f'执行操作报错【{error.__class__.__name__}】：{error}')
                case False:#chess.BLACK
                    if ('wtakeback' in state) and (state['wtakeback'] == True):
                        self.client.extension_bot.accept_takeback(self.game_id)
                    elif len(moves_list) % 2 == 1 and (moves_str != ''):#轮到黑方走棋
                        result = self.analyzer.play_and_analysis(
                            state,
                            (('wdraw' in state) and (state['wdraw'] == True)),
                        )

                        try:
                            self.client.bots.make_move(self.game_id,result['move'])
                            self.engine_info_changed.emit(result['info'])
                            self.client.extension_bot.handle_draw(self.game_id,result['offer_draw'])#如果是false那么啥事也不发生
                            if result['resigned']:self.client.bots.resign_game(self.game_id)
                        except Exception as error:self.state_changed.emit(f'执行操作报错【{error.__class__.__name__}】：{error}')
        else:
            self.state_changed.emit(f'对局以{state["status"]}结束')
            self.analyzer.close_engine()