from json import load
from typing import TypedDict

class AutoLogin(TypedDict):
    enable:bool
    token:str

class ConfigFormat(TypedDict):
    tokens:dict[str,str]
    auto_login:AutoLogin
    # 3.0版本的时候会更新所有bot相关配置

def load_config_with_format() -> ConfigFormat:
    return load(open(
        '../configuration_and_resources/config.json',
        'r',
        encoding='utf-8',
        errors='ignore',
    ))