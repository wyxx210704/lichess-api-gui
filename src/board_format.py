from typing import TypeAlias,Literal

ChallengeType:TypeAlias = Literal[                   
    'challenge',            
    'cancel',               
    'decline',              
]

GameType:TypeAlias = Literal[
    'start',
    'finish',
]

State:TypeAlias = Literal[
    'challenge',
    'game',
    'both',
    'both_not',
]