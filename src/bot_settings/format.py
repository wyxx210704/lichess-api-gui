from typing import TypedDict

class EngineName(TypedDict):
    standard:str
    variants:str

class GameBehavior(TypedDict):
    resign_score:int
    draw_piece_count:int
    draw_interval:int

class AutoReplyMessage(TypedDict):
    enabled:bool
    api_key:str

class MoreSettings(TypedDict):
    challenge_no_bot:bool
    challenge_only_bot:bool
    max_game:int
    auto_match_interval:int

class BasicSettings(TypedDict):
    engine_name:EngineName
    game_behavior:GameBehavior
    auto_reply_message:AutoReplyMessage
    block_list:list[str]
    more_settings:MoreSettings

class SupportTime(TypedDict):
    ultraBullet:bool
    bullet:bool
    blitz:bool
    rapid:bool
    classical:bool
    correspondence:bool

class SupportVariants(TypedDict):
    chess960:bool
    kingOfTheHill:bool
    threeCheck:bool
    antichess:bool
    atomic:bool
    horde:bool
    racingKings:bool
    crazyhouse:bool
    standard:bool

class GameMode(TypedDict):
    casual:bool
    rated:bool

class ChallengeIn(TypedDict):
    support_time:SupportTime
    support_variants:SupportVariants
    support_mode:GameMode

class AlternativeTimeItem(TypedDict):
    limit:int
    increment:int

class VariantsWeight(TypedDict):
    chess960:int
    kingOfTheHill:int
    threeCheck:int
    antichess:int
    atomic:int
    horde:int
    racingKings:int
    crazyhouse:int
    standard:int

class AutoMatch(TypedDict):
    alternative_time:list[AlternativeTimeItem]
    variants_weight:VariantsWeight
    enable_mode:GameMode

class ConfigFormat(TypedDict):
    basic_settings:BasicSettings
    challenge_in:ChallengeIn
    auto_match:AutoMatch