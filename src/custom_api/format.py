[
    {
        "id": "sprAizJN",
        "username": "SanuliYehensssa",
        "rating": 1500,
        "variant": {
            "key": "standard"
        },
        "perf": {
            "key": "correspondence"
        },
        "mode": 0,
        "days": 7,
        "provisional": True
    },
    {
        "id": "9BUnpTuy",
        "username": "spyrosboom",
        "rating": 1500,
        "variant": {
            "key": "kingOfTheHill"
        },
        "perf": {
            "key": "kingOfTheHill"
        },
        "mode": 0,
        "provisional": True
    },
    {
        "id": "f71HNW6F",
        "username": "quoctri28",
        "rating": 1698,
        "variant": {
            "key": "standard"
        },
        "perf": {
            "key": "correspondence"
        },
        "mode": 1,
        "days": 2,
        "provisional": True
    }
]

from typing import *
from berserk.types.common import VariantKey,PerfType

Variant = TypedDict('Variant',{'key':VariantKey})
Perf = TypedDict('Perf',{'key':PerfType})

class Seek(TypedDict):
    id:str
    username:str
    rating:int
    variant:Variant
    perf:Perf
    mode:Literal[0,1]
    days:NotRequired[int]
    provisional:NotRequired[bool]