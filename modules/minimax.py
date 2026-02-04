"""minimax法の実装"""

from .board import Board

# 探索の最大深さ
MAX_DEPTH = 40

_transposition_table: dict[int, float] = {}


def minimax(
    board: Board,
    depth: int,
    player: bool,
    verbose: bool,
    heuristic: bool,
    alpha: float,
    beta: float,
) -> tuple[float, int]:
    """minimax法を用いてゲーム木を探索する

    Args:
        board (Board): 現在のチェスボードの状態
        depth (int): 探索の深さ
        player (bool): 現在のプレイヤー（True: 先手, False: 後手）
        verbose (bool): ログ出力を行うかどうか
        heuristic (bool): 移動順序の最適化を行うかどうか

    Returns:
        tuple[float, int]: (先手の勝利確率, 探索した局面数)
    """
    # transposition tableのキーを生成
    state_key = board.get_state_key()
    if state_key in _transposition_table:
        return _transposition_table[state_key], 0
    # 局面数をカウント（この関数が呼ばれるたびに1局面）
    node_count = 1

    # 一定深さではプレイアウトの結果を返す
    if depth >= MAX_DEPTH:
        # 先手の勝率を取得
        first_player_win_prob = board.get_playout_result(player)
        return first_player_win_prob, node_count

    # 移動できるマスを取得する
    available_positions = board.get_available_positions()

    # 移動できるマスがなければ現在のプレイヤーの負けとなり終了
    if not available_positions:
        # 現在のプレイヤーの負け、つまり、もう一方のプレイヤーの勝ち
        _transposition_table[state_key] = 0.0 if player else 1.0
        return (0.0 if player else 1.0), node_count

    # 移動順序を最適化
    if heuristic:
        _sort_moves_by_heuristic(board, available_positions)

    if verbose:
        print(" " * depth * 2, end="")
        print(
            f"depth={depth}, player={'先手' if player else '後手'}, available={available_positions}"
        )

    # 先手(True)なら最大値を、後手(False)なら最小値を初期値に設定
    best_value = 0.0 if player else 1.0

    # 可能な移動を順番に試していく
    for position in available_positions:
        if verbose:
            print(" " * (depth * 2 + 2), end="")
            print(f"{'先手' if player else '後手'} chose {position}")

        # 駒を移動する
        original_pos = board.make_move(position)

        # 移動結果を再帰的に評価する
        result, child_nodes = minimax(
            board,
            depth + 1,
            not player,
            verbose,
            heuristic,
            alpha,
            beta,
        )
        node_count += child_nodes
        board.undo_move(position, original_pos)

        # Alpha-Beta枝刈り
        if player:
            # 先手は先手勝率を最大化したい
            best_value = max(best_value, result)
            alpha = max(alpha, best_value)
            # beta値を上回ったら枝刈り
            if alpha >= beta:
                break
        else:
            # 後手は先手勝率を最小化したい
            best_value = min(best_value, result)
            beta = min(beta, best_value)
            # alpha値を下回ったら枝刈り
            if alpha >= beta:
                break

    _transposition_table[state_key] = best_value
    return best_value, node_count


def _sort_moves_by_heuristic(board: Board, positions: list[int]):
    """ヒューリスティクスに基づき移動候補を並べ替える

    盤面の端や隅に近く詰みやすそうな手を先に探索できるようにする。
    （純粋に選択肢の少ない手を調べようとするとこの処理自体が重くなってしまう。）

    Args:
        board (Board): 現在のチェスボードの状態
        positions (list[int]): 移動候補のリスト
    """
    # 端に近い位置を優先
    positions.sort(key=lambda pos: -board.dist_from_center_map[pos])
