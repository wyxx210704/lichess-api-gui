from typing import *
from berserk.types.challenges import Variant
from datetime import datetime,timedelta

Perf = TypedDict('Perf',{'name':str})
OptionalBoolItem:TypeAlias = Optional[Literal[True]]
Time:TypeAlias = int|timedelta#如果是整数那就是毫秒单位

Player = TypedDict('Player',{
    'id':str,
    'name':str,
    'title':str|None,
    'rating':int,
    'provisional':OptionalBoolItem,

    #以下条目只会在对手是网站内置ai的时候出现
    'aiLevel':Optional[int],
})

Clock = TypedDict('Clock',{#单位毫秒
    'initial':int,
    'increment':int,
})

GameStste = TypedDict('GameState',{
    'type':Literal['gameState'],
    'moves':str,
    'wtime':Time,
    'btime':Time,
    'winc':Time,
    'binc':Time,
    'status':str,

    #以下条目只在部分情况出现
    'wtakeback':OptionalBoolItem,
    'btakeback':OptionalBoolItem,
    'wdraw':OptionalBoolItem,
    'bdraw':OptionalBoolItem,
    'winner':Optional[str],
})

GameFull = TypedDict('GameFull',{
    'id':str,
    'variant':Variant,
    'rated':bool,
    'speed':str,
    'perf':Perf,
    'createdAt':datetime,
    'white':Player,
    'black':Player,
    'initialFen':str,
    'clock':Optional[Clock],
    'type':Literal['gameFull'],
    'state':GameStste
})

ChatLine = TypedDict('ChatLine',{
    'type':Literal['chatLine'],
    'room':Literal['player','spectator'],
    'username':str,
    'text':str
})

OpponentGone = TypedDict('OpponentGone',{
    'type':Literal['opponentGone'],
    'gone':bool,
    'claimWinInSeconds':int,
})

EventInGame:TypeAlias = (
    GameFull |
    GameStste |
    ChatLine |
    OpponentGone
)