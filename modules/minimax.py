"""minimax法の実装"""

from .board import Board

# 対称性を考慮する最大探索深さ
MAX_DEPTH_FOR_SYMMETRY = 3

# 探索の最大深さ
MAX_DEPTH = 40


def minimax(
    board: Board,
    depth: int,
    player: bool,
    verbose: bool,
    heuristic: bool,
    symmetry: bool,
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
        symmetry (bool): 対称性を考慮して探索を削減するかどうか

    Returns:
        tuple[float, int]: (先手の勝利確率, 探索した局面数)
    """
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
        return (0.0 if player else 1.0), node_count

    # 対称性を考慮
    if symmetry and depth <= MAX_DEPTH_FOR_SYMMETRY:
        available_positions = _filter_symmetric_moves(board, available_positions)

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
            symmetry,
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


def _filter_symmetric_moves(board: Board, positions: list[int]) -> list[int]:
    """左右上下対称となる手を除外し、探索候補を削減したリストを返す

    Args:
        board (Board): 現在のチェスボードの状態
        positions (list[int]): 移動候補のリスト

    Returns:
        list[int]: 対称性を考慮して削減された移動候補のリスト
    """
    unique_moves = []
    seen_states = set()

    for pos in positions:
        # 試しに移動してみる
        original_pos = board.make_move(pos)

        # 移動後の盤面の正規形を取得
        canonical_state = board.get_canonical_state()

        if canonical_state not in seen_states:
            seen_states.add(canonical_state)
            unique_moves.append(pos)

        # 元に戻す
        board.undo_move(pos, original_pos)

    return unique_moves
