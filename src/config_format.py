from typing import TypedDict

class AutoLogin(TypedDict):
    enable:bool
    token:str

class CopyIndent(TypedDict):
    enable:bool
    indent:int

class FunctionSettings(TypedDict):
    translate:bool
    copy_indent:CopyIndent

class ConfigFormat(TypedDict):
    tokens:dict[str,str]
    auto_login:AutoLogin
    function_settings:FunctionSettings