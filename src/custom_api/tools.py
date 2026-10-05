from berserk.formats import JSON_LIST
from berserk.clients.base import BaseClient
from berserk.types.common import VariantKey
from typing import cast

from .format import Seek

class More(BaseClient):
    def get_my_timeline(self):
        return self._r.get('/api/timeline')

class Lobby(BaseClient):
    def get_correspondence_lobby(self):
        return cast(
            list[Seek],
            self._r.get('/lobby/seeks',fmt=JSON_LIST)
        )

    def create_correspondence_seek(self,days:int,rated:bool=False,variant:VariantKey='standard',
                                   rating_range:list[int]|tuple[int,int]|str=''):
        if type(rating_range) == str:final_rating_range = rating_range
        else:final_rating_range = f'{rating_range[0]}-{rating_range[1]}'

        return self._r.post('/api/board/seek',data={
            'days':days,
            'rated':str(bool(rated)).lower(),
            'variant':variant,
            'ratingRange':final_rating_range,
        })

    #def enter_correspondence_seek(self,seek:Seek):
        #此函数暂时不确定，先暂时作为预留等后面找到办法

class ExtensionBot(BaseClient):
    def accept_takeback(self,game_id:str):self._r.post(f'/api/bot/game/{game_id}/takeback/yes')
    def claim_victory(self,game_id:str):self._r.post(f'/api/bot/game/{game_id}/claim-victory')
    def handle_draw(self,game_id:str,draw:bool):self._r.post(f'/api/bot/game/{game_id}/draw/{'yes' if draw else 'no'}')