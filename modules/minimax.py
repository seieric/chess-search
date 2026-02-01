"""minimax法の実装"""

from .board import Board


def minimax(
    board: Board,
    depth: int,
    player: bool,
    verbose: bool,
    heuristic: bool,
) -> bool:
    """minimax法を用いてゲーム木を探索する

    Args:
        board (Board): 現在のチェスボードの状態
        depth (int): 探索の深さ
        player (bool): 現在のプレイヤー（True: 先手, False: 後手）
        verbose (bool): ログ出力を行うかどうか
        heuristic (bool): 移動順序の最適化を行うかどうか

    Returns:
        bool: 先手が勝つ場合はTrue、後手が勝つ場合はFalse
    """
    # 移動できるマスを取得する
    available_positions = board.get_available_positions()

    # 移動できるマスがなければ現在のプレイヤーの負けとなり終了
    if not available_positions:
        # 現在のプレイヤーの負け、つまり、もう一方のプレイヤーの勝ち
        return not player

    # 移動順序を最適化
    if heuristic:
        available_positions = _sort_moves_by_heuristic(board, available_positions)

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
        result = minimax(board, depth + 1, not player, verbose, heuristic)
        board.undo_move(position, original_pos)

        if player:
            # 先手のターン
            if result:
                # 先手の勝ち
                return True
        else:
            # 後手のターン
            if not result:
                # 後手の勝ち
                return False

    # 現在のプレイヤーが勝てる移動がなかった場合、現在のプレイヤーの負け
    return not player


def _sort_moves_by_heuristic(
    board: Board, positions: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """ヒューリスティクスに基づき移動候補を並べ替える

    移動後に相手の選択肢が少なくなる手や、盤面の端や隅に近く詰みやすそうな手を先に探索できるようにする。

    Args:
        board (Board): 現在のチェスボードの状態
        positions (list[tuple[int, int]]): 移動候補のリスト

    Returns:
        list[tuple[int, int]]: ソート済みの移動候補のリスト
    """

    def evaluate_move(pos: tuple[int, int]) -> tuple[int, int]:
        """手の評価値を計算する（小さいほど優先度が高い）"""
        # 移動後の相手の選択肢数
        original_pos = board.make_move(pos)
        opponent_moves = len(board.get_available_positions())
        board.undo_move(pos, original_pos)

        # 盤面の端からの距離
        center_row = board.size[0] / 2
        center_col = board.size[1] / 2
        distance_from_center = abs(pos[0] - center_row) + abs(pos[1] - center_col)

        return (opponent_moves, -int(distance_from_center * 10))

    return sorted(positions, key=evaluate_move)
