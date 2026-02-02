"""minimax法の実装"""

from .board import Board

# 対称性を考慮する最大探索深さ
MAX_DEPTH_FOR_SYMMETRY = 3


def minimax(
    board: Board,
    depth: int,
    player: bool,
    verbose: bool = False,
    heuristic: bool = False,
    symmetry: bool = False,
) -> tuple[bool, int]:
    """minimax法を用いてゲーム木を探索する

    Args:
        board (Board): 現在のチェスボードの状態
        depth (int): 探索の深さ
        player (bool): 現在のプレイヤー（True: 先手, False: 後手）
        verbose (bool): ログ出力を行うかどうか
        heuristic (bool): 移動順序の最適化を行うかどうか
        symmetry (bool): 対称性を考慮して探索を削減するかどうか

    Returns:
        tuple[bool, int]: (勝者（True: 先手, False: 後手）, 探索した局面数)
    """
    # 局面数をカウント（この関数が呼ばれるたびに1局面）
    node_count = 1

    # 移動できるマスを取得する
    available_positions = board.get_available_positions()

    # 移動できるマスがなければ現在のプレイヤーの負けとなり終了
    if not available_positions:
        # 現在のプレイヤーの負け、つまり、もう一方のプレイヤーの勝ち
        return not player, node_count

    # 対称性を考慮
    if symmetry and depth <= MAX_DEPTH_FOR_SYMMETRY:
        available_positions = _filter_symmetric_moves(board, available_positions)

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
        result, child_nodes = minimax(
            board, depth + 1, not player, verbose, heuristic, symmetry
        )
        node_count += child_nodes
        board.undo_move(position, original_pos)

        # 得られた勝者が現在のプレイヤーであれば、その手を選ぶ
        if result == player:
            # 勝者は現在のプレイヤーとなる
            return player, node_count

    # 現在のプレイヤーが勝てる移動がなかった場合、現在のプレイヤーの負け
    return not player, node_count


def _sort_moves_by_heuristic(
    board: Board, positions: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """ヒューリスティクスに基づき移動候補を並べ替える

    盤面の端や隅に近く詰みやすそうな手を先に探索できるようにする。
    （純粋に選択肢の少ない手を調べようとするとこの処理自体が重くなってしまう。）

    Args:
        board (Board): 現在のチェスボードの状態
        positions (list[tuple[int, int]]): 移動候補のリスト

    Returns:
        list[tuple[int, int]]: ソート済みの移動候補のリスト
    """
    # 端に近い位置を優先
    return sorted(
        positions,
        key=lambda pos: -(
            abs(pos[0] - board.center[0]) + abs(pos[1] - board.center[1])
        ),
    )


def _filter_symmetric_moves(
    board: Board, positions: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """左右上下対称となる手を除外し、探索候補を削減したリストを返す

    Args:
        board (Board): 現在のチェスボードの状態
        positions (list[tuple[int, int]]): 移動候補のリスト

    Returns:
        list[tuple[int, int]]: 対称性を考慮して削減された移動候補のリスト
    """
    rows, cols = board.size

    # 左右対称性
    is_horizontal_symmetric = board.is_horizontal_symmetric
    # 上下対称性
    is_vertical_symmetric = board.is_vertical_symmetric

    if not is_horizontal_symmetric and not is_vertical_symmetric:
        # 対称性がない場合は削減できない
        return positions

    # 対称性に基づいて候補を削減
    result = []
    seen_canonical = set()

    for pos in positions:
        canonical = _get_canonical_position(
            pos, rows, cols, is_horizontal_symmetric, is_vertical_symmetric
        )
        if canonical not in seen_canonical:
            result.append(pos)
            seen_canonical.add(canonical)

    return result


def _get_canonical_position(
    pos: tuple[int, int],
    rows: int,
    cols: int,
    is_horizontal_symmetric: bool,
    is_vertical_symmetric: bool,
) -> tuple[int, int]:
    """位置の正規形を返す"""
    r, c = pos
    candidates = [(r, c)]

    if is_horizontal_symmetric:
        candidates.append((r, cols - 1 - c))

    if is_vertical_symmetric:
        candidates.append((rows - 1 - r, c))

    if is_horizontal_symmetric and is_vertical_symmetric:
        candidates.append((rows - 1 - r, cols - 1 - c))

    return min(candidates)
