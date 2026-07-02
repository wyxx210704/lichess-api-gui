'''
为berserk.types库所有TypedDict做翻译

berserk.types的作用
berserk在调用API的时候，为了方便让用户更明了的明白返回值里面会有啥，
所以调用API时会标上一些类型注解代表返回值会是什么格式

其中就有很多TypedDict
我会把它照抄下来并且一个一个的手工给它放上key_translates

还有很多Literal我会把它放在value_translates
'''
'berserk.types'

def get_key_translate(text:str):return key_translates.get(text,text)
key_translates = {

# 1. account
    # 1.1 Perf
    'games':'对局',
    'rating':'等级分',
    'rd':'等级分偏差值',
    'prog':'进步值',
    'prov':'是否为不确定分',

    # 1.2 Profile
    'flag':'国家',
    'location':'所在地',
    'bio':'简介',
    'realName':'真实姓名',
    'fideRating':'fide等级分',
    'uscfRating':'uscf等级分',
    'ecfRating':'ecf等级分',
    'cfcRating':'cfc等级分',
    'rcfRating':'rcf等级分',
    'dsbRating':'dsb等级分',
    'links':'链接',

    # 1.3 PlayTime
    'total':'总时长',
    'tv':'对局观看时长',

    # 1.4 StreamerInfo
    'channel':'频道',

    # 1.5 AccountInformation
    'id':'编号',
    'username':'用户名',
    'perfs':'棋的种类及具体数据',
    'flair':'徽章编号',
    'createdAt':'注册时间',
    'disabled':'是否被封号',
    'tosViolation':'是否违反规定',
    'profile':'个人信息',
    'seenAt':'最近登录',
    'parton':'部分',
    'verified':'是否验证',
    'playTime':'下棋时长',
    'title':'头衔',
    'url':'链接',
    'playing':'正在下棋',
    'count':'对局分类及计数',
    'streaming':'是否正在直播',
    'streamer':'直播流',
    'followable':'是否可以关注',
    'following':'是否正在关注',
    'blocking':'是否被列入黑名单',

    # 1.6 UserPreferences
    'dark':'深色模式',
    'transp':'透明模式',
    'bgImg':'背景图片',
    'is3d':'是否为3D模式',
    'theme':'棋盘主题',
    'pieceSet':'棋子样式',
    'theme3d':'3D棋盘主题',
    'pieceSet3d':'3D棋子样式',
    'soundSet':'提示音设置',
    'blindfold':'盲棋',
    'autoQueen':'自动升变为后',
    'autoThreefold':'三次重复局面和棋',
    'takeback':'悔棋',
    'moretime':'给对手增加时间',
    'clockTenths':'1/10秒',
    'clockBar':'显示进度条',
    'clockSound':'时间不足时提示音',
    'premove':'预走棋',
    'animation':'棋子动画',
    'captured':'吃子',
    'follow':'是否能被关注',
    'highlight':'高亮',
    'destination':'目的地',
    'coords':'坐标',
    'replay':'回放',
    'challenge':'挑战',
    'message':'谁能发消息过来',
    'coordColor':'坐标颜色',
    'submitMove':'确认走棋',
    'confirmResign':'允许认输',
    'insightShare':'分享对局洞察',
    'keyboardMove':'键盘走棋',
    'zen':'禅意模式',
    'moveEvent':'走棋事件',
    'rookCastle':'王车易位',

    # 1.7 Preferences
    'prefs':'偏好设置',
    'language':'语言',

# 2. analysis
    # 2.1 PrincipleVariation
    'moves':'走棋',
    'cp':'厘兵',

    # 2.2 PositionEvaluation
    'fen':'fen局面',
    'knodes':'节点',
    'depth':'深度',
    'pvs':'主要变化',

# 3. bots
    # 3.1 Opponent
    # id            在前面1.5章节已经有
    # username      在前面1.5章节已经有
    # rating        在前面1.1章节已经有

    # 3.2 GameEventInfo
    'fullId':'完整编号',
    'gameId':'对局编号',
    # fen           在前面2.2章节已经有
    'color':'颜色',
    'lastMove':'上一步棋',
    'source':'来源',
    'status':'状态',
    'variant':'变体',
    'speed':'速度',
    'perf':'种类',
    'rated':'是否排位',
    'hasMoved':'是否已走过棋',
    'opponent':'对手',
    'isMyTurn':'是否到我走棋',
    'secondsLeft':'剩余时间',
    'compat':'兼容',
    # id            在前面1.5章节已经有

    # 3.3 GameEvent
    'type':'类型',
    'game':'对局',

    # 3.4 ChallengeEvent
    # type          在前面3.3章节已经有
    # challenge     在前面1.6章节已经有

# 4. broadcast
    # 4.1 BroadcastPlayer
    'source_name':'来源名称',
    'display_name':'显示名称',
    # rating        在前面1.1章节已经有
    # title         在前面1.5章节已经有

# 5. bulk_pairings
    # 5.1 BulkPairingGame
    # id            在前面1.5章节已经有
    'black':'黑方',
    'white':'白方',

    # 5.2 BulkPairing
    # id            在前面1.5章节已经有
    # games         在前面1.1章节已经有
    # variant       在前面3.2章节已经有
    'clock':'时钟',
    'pairAt':'配对时间',
    'pairedAt':'已配对时间',
    # rated         在前面3.2章节已经有
    'startClocksAt':'启动时钟在',
    'scheduledAt':'计划在',

# 6. challenges
    # 6.1 Variant
    'key':'标识',
    'name':'名称',
    'short':'短名称',

    # 6.2 User
    # rating        在前面1.1章节已经有
    'provisional':'临时',

    # 6.3 Perf
    'icon':'图标',
    # name          在前面6.1章节已经有

    # 6.4 ChallengeJson
    # id            在前面1.5章节已经有
    # url           在前面1.5章节已经有
    # status        在前面3.2章节已经有
    'challenger':'挑战发起者',
    'destUser':'被挑战者',
    # variant       在前面3.2章节已经有
    # rated         在前面3.2章节已经有
    # speed         在前面3.2章节已经有
    'timeControl':'时间控制',
    # color         在前面3.2章节已经有
    'finalColor':'最终颜色',
    # perf          在前面3.2章节已经有
    'direction':'是发过来还是发出去',
    'initialFen':'初始局面FEN',
    'declineReason':'拒绝原因',
    'declineReasonKey':'拒绝原因标识',

# 7. common
    # 7.1 ClockConfig
    'limit':'基础时限',
    'increment':'每步增加时间',

    # 7.2 ExternalEngine
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有
    'clientSecret':'客户端密钥',
    'userId':'用户编号',
    'maxThreads':'最大线程数',
    'maxHash':'最大哈希值',
    'defaultDepth':'默认深度',
    'variants':'支持的变体',
    'providerData':'服务提供商数据',

    # 7.3 LightUser
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有
    # title         在前面1.5章节已经有
    # flair         在前面1.5章节已经有
    'patron':'赞助',

    # 7.4 OnlineLightUser
    'online':'在线状态',

# 8. fide
    # 8.1 FidePlayer
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有
    'federation':'联盟',
    'year':'年',
    # title         在前面1.5章节已经有
    # standard      在后面15.1章节已经有
    # rapid         在后面15.1章节已经有
    # blitz         在后面15.1章节已经有

# 9. opening_explorer
    # 9.1 Opening
    'eco':'开局ECO编号',
    # name          在前面6.1章节已经有

    # 9.2 Player
    # name          在前面6.1章节已经有
    # rating        在前面1.1章节已经有

    # 9.3 GameWithoutUci
    # id            在前面1.5章节已经有
    'winner':'胜利者',
    # speed         在前面3.2章节已经有
    'mode':'模式',
    # black         在前面5.1章节已经有
    # white         在前面5.1章节已经有
    # year          在前面8.1章节已经有
    'month':'月',

    # 9.4 Game
    'uci':'UCI棋谱',

    # 9.5 Move
    # uci           在前面9.4章节已经有
    'san':'SAN棋谱',
    'averageRating':'平均评分',
    # white         在前面5.1章节已经有
    # black         在前面5.1章节已经有
    'draws':'和棋',
    # game          在前面3.3章节已经有

    # 9.6 OpeningStatistic
    # white         在前面5.1章节已经有
    # draws         在前面9.5章节已经有
    # black         在前面5.1章节已经有

# 10. puzzles
    # 10.1 PuzzleUser
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有
    # color         在前面3.2章节已经有
    # rating        在前面1.1章节已经有

    # 10.2 PuzzlePerf
    # key           在前面6.1章节已经有
    # name          在前面6.1章节已经有

    # 10.3 PuzzleGame
    # id            在前面1.5章节已经有
    # perf          在前面3.2章节已经有
    # rated         在前面3.2章节已经有
    'players':'棋手',
    'pgn':'PGN棋谱',
    # clock         在前面5.2章节已经有

    # 10.4 PuzzleInfo
    # id            在前面1.5章节已经有
    # rating        在前面1.1章节已经有
    'plays':'做过这个谜题的人数',
    'solution':'解决方案',
    'themes':'主题',
    'initialPly':'初始层',

    # 10.5 PuzzleData
    # game          在前面3.3章节已经有
    'puzzle':'谜题',

    # 10.6 PuzzleRace
    # id            在前面1.5章节已经有
    # url           在前面1.5章节已经有

# 11. studies
    # 11.1 ChapterIdName
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有

# 12. team
    # 12.1 Team
    # id            在前面1.5章节已经有
    # name          在前面6.1章节已经有
    'description':'描述',
    'open':'公开',
    'leader':'团队领导',
    'leaders':'所有团队领导',
    'nbMembers':'成员数量',
    'joined':'是否加入',
    'requested':'是否请求',

    # 12.2 PaginatedTeams
    'currentPage':'当前页面',
    'maxPerPage':'每页最多团队数',
    'currentPageResults':'当前页面具体团队信息',
    'nbResults':'团队总数',
    'previousPage':'上一页',
    'nextPage':'下一页',
    'nbPages':'页码总数',

# 13. tournaments
    # 13.1 CurrentTournaments
    'created':'已创建',
    'started':'进行中',
    'finished':'已结束',

    # 13.2 Clock
    # limit         在前面7.1章节已经有
    # increment     在前面7.1章节已经有

    # 13.3 Stats
    'absences':'缺勤',
    # averageRating 在前面9.5章节已经有
    'blackWins':'黑方胜利数量',
    'byes':'中途退出',
    # draws         在前面9.5章节已经有
    # games         在前面1.1章节已经有
    'whiteWins':'白方胜利数量',

    # 13.4 SwissInfo
    # id            在前面1.5章节已经有
    'createdBy':'创建在',
    'startsAt':'开始在',
    # name          在前面6.1章节已经有
    # clock         在前面5.2章节已经有
    # variant       在前面3.2章节已经有
    'round':'轮次',
    'nbRounds':'轮次总数',
    'nbPlayers':'棋手总数',
    'nbOngoing':'正在进行对局总数',
    # status        在前面3.2章节已经有
    # rated         在前面3.2章节已经有
    'stats':'统计数据',

    # 13.5 TournamentResult
    'rank':'排名',
    # rating        在前面1.1章节已经有
    # username      在前面1.5章节已经有
    'performance':'表演',
    # title         在前面1.5章节已经有
    # flair         在前面1.5章节已经有

    # 13.6 ArenaSheet
    'scores':'分数',

    # 13.7 ArenaResult
    'score':'分数',
    'sheet':'表格',

    # 13.8 SwissResult
    'points':'积分',
    'tieBreak':'决胜局',

    # 13.9 PlayerTeamResult
    'user':'用户',
    # score         在前面13.7章节已经有

    # 13.10 TeamResult
    # rank          在前面13.5章节已经有
    # id            在前面1.5章节已经有
    # score         在前面13.7章节已经有
    # players       在前面10.3章节已经有

    # 13.11 TeamBattleResult
    # id            在前面1.5章节已经有
    'teams':'团队',

# 14. tv
    # 14.1 Player
    # color         在前面3.2章节已经有
    # user          在前面13.9章节已经有
    'ai':'AI用户',
    # rating        在前面1.1章节已经有
    'seconds':'秒数',

    # 14.2 FeaturedData
    # id            在前面1.5章节已经有
    'orientation':'目标',
    # players       在前面10.3章节已经有
    # fen           在前面2.2章节已经有

    # 14.3 MoveData
    # fen           在前面2.2章节已经有
    'lm':'最后一步棋',
    'wc':'白方时钟',
    'bc':'黑方时钟',

    # 14.4 TVFeed
    't':'类型',
    'd':'数据',

# 15. 附录
    # 15.1 棋的种类
    'standard':'标准',
    "ultraBullet":'超子弹棋', 
    "bullet":'子弹棋', 
    "blitz":'超快棋', 
    "rapid":'快棋', 
    "classical":'慢棋', 
    "correspondence":'通讯棋',
    "chess960":'菲舍尔随机象棋',
    "kingOfTheHill":'山丘之王',
    "threeCheck":'三次将军',
    "antichess":'弃子棋',
    "atomic":'原子棋',
    "horde":'部落棋',
    "racingKings":'竞速棋',
    "crazyhouse":'疯狂屋',
    "fromPosition":'自定义起始位置',

    # 15.2 谜题相关
    'storm':'谜题风暴',
    'racer':'谜题比赛',
    'streak':'谜题连胜',
    'runs':'进行次数',

    # 15.3 对局分类及计数
    'all':'全部',
    'draw':'和棋',
    'loss':'输',
    'win':'赢',
    'bookmark':'收藏',
    'import':'导入',
    'me':'与我下的棋',

    # 15.4 用户最近活动动态
    'interval':'时间段',
    'start':'开始时间',
    'end':'结束时间',
    'studies':'学习',
    'follows':'关注',
    'in':'进',
    'out':'出',
    'ids':'编号',
    'tournament':'锦标赛',
    'nb':'总数',
    'best':'最好',
    'nbGames':'总对局',
    'rankPercent':'排名百分比',
    'correspondenceEnds':'已结束的通讯棋',
    'rp':'等级分',
    'before':'下棋前',
    'after':'下棋后',
    'puzzles':'谜题',
    'correspondenceMoves':'在通讯棋中走的棋',

    # 15.5 有关排行榜
    'progress':'进步值',
    'patronColor':'赞助颜色',

    # 15.6 导出对局
    'lastMoveAt':'最后一步棋在',
    'ratingDiff':'等级分变化',
    'initial':'基础时间',
    'totalTime':'总时间',
    'division':'分开',
    'middle':'中间',
    'opening':'开局',
    'clocks':'具体时钟变化',
    'arenaTour':'来自竞技场',

    # 15.7 观看对局
    'tournamentId':'锦标赛编号',
    'turns':'转化',
}# 翻译内容结束

def get_value_translate(text:str):return value_translates.get(text,text)
value_translates = {

# 1. account
    # 1.1 SoundSet
    "silent":'安静',
    "standard":'标准',
    "piano":'钢琴',
    "nes":'任天堂娱乐系统',
    "sfx":'特效',
    "futuristic":'未来主义',
    "robot":'机器人',
    "music":'音乐',
    "speech":'言语',

# 2. analysis
# 没有Literal

# 3. bots
    # 3.1 GameSource
    "lobby":'游说',
    "friend":'朋友',
    "ai":'引擎',
    "api":'API',
    "tournament":'锦标赛',
    "position":'位置',
    "import":'导入',
    "importlive":'导入直播',
    "simul":'车轮战',
    "relay":'继电器',
    "pool":'泳池',
    "swiss":'瑞士轮',

    # 3.2 GameEvent.type
    "gameStart":'对局开始', 
    "gameFinish":'对局结束',

    # 3.3 ChallengeEvent.type
    "challenge":'挑战', 
    "challengeCanceled":'挑战取消', 
    "challengeDeclined":'挑战拒绝',

# 4. broadcast
# 没有Literal

# 5. bulk_pairing
# 没有Literal

# 6. challenges
    # 6.1 ChallengeStatus
    "created":'已创建',
    "offline":'离线',
    "canceled":'已取消',
    "declined":'已拒绝',
    "accepted":'已接受',

    # 6.2 ChallengeDeclineReason
    "generic":'通用',
    "later":'我现在不方便对弈，请稍后再邀请',
    "tooFast":'这个时限对我来说太快了，请发起一个更慢的对局挑战',
    "tooSlow":'这个时限对我来说太慢了，请发起一个更快的对局挑战',
    "timeControl":'我不接受此时限设置的挑战',
    "rated":'排位',
    "casual":'休闲',
    "standard":'我目前不接受变体挑战',
    "variant":'我现在不愿意下这个变体',
    "noBot":'我不接受来自机器人的挑战',
    "onlyBot":'我只接受来自机器人的挑战',

    # 6.3 ColorOrRandom
    'random':'随机',

    # 6.4 ChallengeDirection
    'in':'进',
    'out':'出',

# 7. common
    # 7.1 Color
    "white":'白方', 
    "black":'黑方',

    # 7.2 GameType
    "chess960":'菲舍尔随机象棋',
    "kingOfTheHill":'山丘之王',
    "threeCheck":'三次将军',
    "antichess":'弃子棋',
    "atomic":'原子棋',
    "horde":'部落棋',
    "racingKings":'竞速棋',
    "crazyhouse":'疯狂屋',
    "fromPosition":'自定义起始位置',

    # 7.3 Speed
    "ultraBullet":'超子弹棋', 
    "bullet":'子弹棋', 
    "blitz":'超快棋', 
    "rapid":'快棋', 
    "classical":'慢棋', 
    "correspondence":'通讯棋',

    # 7.4 Title
    "GM":'特级大师', 
    "WGM":'女子特级大师', 
    "IM":'国际大师', 
    "WIM":'女子国际大师', 
    "FM":'棋联大师', 
    "WFM":'女子棋联大师', 
    "NM":'国家大师', 
    "CM":'候选大师', 
    "WCM":'女子候选大师', 
    "WNM":'女子国家大师', 
    "LM":'lichess大师', 
    "BOT":'机器人',

    # 7.5 VariantKey
    'standard':'标准',

    # 7.6 PerfType
    # "bullet", "blitz", "rapid", "classical", "ultraBullet" 
    # 全部都在7.3章节有重复

    # 7.7 GameRule
    "noAbort":'不能终止对局', 
    "noRematch":'不能重赛', 
    "noGiveTime":'不能给对方时间',
    "noClaimWin":'无索赔赢', 
    "noEarlyDraw":'不能太早和棋',

# 8. fide
# 没有Literal

# 9. opening_explorer
    # 9.1 OpeningExplorerRating
    # "0", "1000", "1200", "1400", "1600", "1800", "2000", "2200", "2500"
    # 全都是数字无法提供翻译

    # 9.2 GameWithoutUci.winner
    # Literal["white"] | Literal["black"] | None
    # 全部都在7.1章节有重复

    # 9.3 GameWithoutUci.mode
    # Literal["rated"] | Literal["casual"]
    # 全部都在6.2章节有重复

# 10. puzzles
    # 10.1 DifficultyLevel
    "easiest":'最容易', 
    "easier":'比较容易', 
    "normal":'正常', 
    "harder":'比较难', 
    "hardest":'最难',

# 11. studies
# 没有Literal

# 12. team
# 没有Literal

# 13. tournaments
# 没有Literal

# 14. tv
    # 14.1 TVFeed.t
    "featured":'精选', 
    "fen":'fen局面',

}# 翻译内容结束