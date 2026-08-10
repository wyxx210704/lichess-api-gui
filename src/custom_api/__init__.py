from berserk import Client
from requests import Session

from .tools import *

class ExtensionClient(Client):
    def __init__(self, session:Session | None = None, base_url:str | None = None, pgn_as_default:bool = False, *, tablebase_url:str | None = None, explorer_url:str | None = None):
        super().__init__(session, base_url, pgn_as_default, tablebase_url=tablebase_url, explorer_url=explorer_url)
        self.lobby = Lobby(session, base_url)
        self.more = More(session, base_url)
    
    @classmethod
    def from_berserk(cls,client:Client):
        return cls(client._r.session,client._r.base_url)