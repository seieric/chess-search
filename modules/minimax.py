"""minimax法の実装"""

from .board import Board


def minimax(board: Board, depth: int, player: bool, verbose: bool = False) -> bool:
    """minimax法を用いてゲーム木を探索する

    Args:
        board (Board): 現在のチェスボードの状態
        depth (int): 探索の深さ
        player (bool): 現在のプレイヤー（True: 先手, False: 後手）
        verbose (bool): ログ出力を行うかどうか

    Returns:
        bool: 先手が勝つ場合はTrue、後手が勝つ場合はFalse
    """
    # 移動できるマスを取得する
    available_positions = board.get_available_positions()

    # 移動できるマスがなければ現在のプレイヤーの負けとなり終了
    if not available_positions:
        # 現在のプレイヤーの負け、つまり、もう一方のプレイヤーの勝ち
        return not player

    if verbose:
        print(" " * depth * 2, end="")
        print(
            f"depth={depth}, player={'先手' if player else '後手'}, available={available_positions}"
        )

    # 可能な移動を順番に試していく
    for position in available_positions:
        if verbose:
            print(" " * (depth * 2 + 2), end="")
            print(f"{'先手' if player else '後手'} chose {position}")

        # 駒を移動する
        original_pos = board.make_move(position)

        # 移動結果を再帰的に評価する
        if player:
            # 先手のターン
            result = minimax(board, depth + 1, False, verbose)
            # 元に戻す
            board.undo_move(position, original_pos)
            if result:
                # 先手の勝ち
                return True
        else:
            # 後手のターン
            result = minimax(board, depth + 1, True, verbose)
            # 元に戻す
            board.undo_move(position, original_pos)
            if not result:
                # 後手の勝ち
                return False

    # 現在のプレイヤーが勝てる移動がなかった場合、現在のプレイヤーの負け
    return not player
