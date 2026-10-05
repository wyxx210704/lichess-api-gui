from typing import *
from chess import Move

class ChatHistory(TypedDict):
    role:Literal[
        'system',
        'user',
        'assistant',
    ]
    content:str

class Answer(TypedDict):
    state:Literal['ok','error']
    text:str
    exception_type:NotRequired[str]

class BotPlayResult(TypedDict):
    move:str
    info:dict
    offer_draw:bool
    resigned:bool