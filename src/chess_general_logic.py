import chess
import chess.svg
import chess.variant
from berserk.types.common import VariantKey

# VariantKey = Literal[
# 'chess960', 
# 'kingOfTheHill', 
# 'threeCheck', 
# 'antichess', 
# 'atomic', 
# 'horde', 
# 'racingKings', 
# 'crazyhouse', 
# 'fromPosition', 
# 'standard']

def get_board(variant: VariantKey, start_fen: str = chess.STARTING_FEN):
    # 根据变体类型创建对应的棋盘
    if variant == "standard" or variant == "fromPosition":
        # standard和fromPosition使用标准国际象棋
        return chess.Board(start_fen if variant == "fromPosition" else chess.STARTING_FEN)
    elif variant == "chess960":
        return chess.Board(start_fen, chess960=True)
    elif variant == "kingOfTheHill":
        return chess.variant.KingOfTheHillBoard()
    elif variant == "threeCheck":
        return chess.variant.ThreeCheckBoard()
    elif variant == "antichess":
        return chess.variant.AntichessBoard()
    elif variant == "atomic":
        return chess.variant.AtomicBoard()
    elif variant == "horde":
        return chess.variant.HordeBoard()
    elif variant == "racingKings":
        return chess.variant.RacingKingsBoard()
    elif variant == "crazyhouse":
        return chess.variant.CrazyhouseBoard()

def generate_svg_from_uci(move_list: list[str], orientation: chess.Color, variant: VariantKey, start_fen: str = chess.STARTING_FEN):
    # 验证variant参数
    valid_variants = [
        "standard", "chess960", "kingOfTheHill", "threeCheck", 
        "antichess", "atomic", "horde", "racingKings", 
        "crazyhouse", "fromPosition"
    ]
    if variant not in valid_variants:
        raise ValueError(f"不支持的变体类型: {variant}，支持的变体: {valid_variants}")

    board = get_board(variant,start_fen)
    last_move = None
    all_moves = []  # 用于存储所有走法

    for uci in move_list:
        try:
            move = chess.Move.from_uci(uci)
            if move in board.legal_moves:
                board.push(move)
                last_move = move
                all_moves.append(move)
            else:
                print(f"警告: 非法走法 '{uci}'，跳过")
        except ValueError:
            print(f"警告: 无效的UCI格式 '{uci}'，跳过")

    # 检测当前局面是否存在将军
    is_check = board.is_check()

    # 获取被将军的国王位置（如果有将军的话）
    check_square = None
    if is_check:
        # 获取当前轮到走棋的一方的国王位置
        king_color = board.turn
        king_square = board.king(king_color)
        if king_square is not None:
            check_square = king_square

    return chess.svg.board(
        board=board,
        lastmove=last_move,
        orientation=orientation,
        check=check_square,  # 标注被将军的国王位置
    ).encode()