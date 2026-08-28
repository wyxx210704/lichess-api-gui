GENERAL_PATH = 'configuration_and_resources/'
CONFIG = GENERAL_PATH + 'config.json'
ICON = GENERAL_PATH + 'lichess_icon.ico'

PERFS = [
    #标准
    "ultraBullet", 
    "bullet", 
    "blitz", 
    "rapid", 
    "classical", 
    "correspondence",
    #变体
    "chess960",
    "kingOfTheHill",
    "threeCheck",
    "antichess",
    "atomic",
    "horde",
    "racingKings",
    "crazyhouse",
]

CREATE_TOKEN_TUTORIAL = '''.
1. 先进入[此页面](https://lichess.org/account/oauth/token)，点右上角+按钮，然后就会进入以下页面
![页面内容展示](https://api.keepwork.com/ts-storage/siteFiles/49798/raw#1782219326915image.png)
2. 填好令牌（token）描述，只要能让自己记住就行
3. 按需要勾选令牌（token）可执行的功能
4. 滑到底部，点右下角创建按钮，即可创建
'''