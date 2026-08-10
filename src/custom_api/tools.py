from berserk.formats import JSON_LIST
from berserk.clients.base import BaseClient
from berserk.types.common import VariantKey
from berserk.clients.challenges import Challenges
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
                                   rating_range:list[int]|tuple[int]|str=''):
        if type(rating_range) == str:final_rating_range = rating_range
        else:final_rating_range = f'{rating_range[0]}-{rating_range[1]}'

        return self._r.post('/api/board/seek',data={
            'days':days,
            'rated':str(bool(rated)).lower(),
            'variant':variant,
            'ratingRange':final_rating_range,
        })

    def enter_correspondence_seek(self,seek:Seek):
        Challenges(self._r.session,self._r.base_url).accept(seek['id'])