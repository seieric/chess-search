import argparse

from modules import Board, minimax


def main(args: argparse.Namespace):
    # 引数からチェスボードの初期設定を取得する
    board_size = (args.height, args.width)
    initial_position = (args.initial_row, args.initial_col)
    piece_type = args.piece_type
    verbose = args.verbose
    heuristic = args.heuristic
    symmetry = args.symmetry
    num_playout = args.num_playout

    # チェスボードを初期化する
    board = Board(board_size, initial_position, piece_type, num_playout)
    board.print_board()

    first_player_win_prob, node_count = minimax(
        board, 0, True, verbose, heuristic, symmetry, 0.0, 1.0
    )
    if first_player_win_prob > 0.5:
        print(f"先手必勝(先手勝率: {first_player_win_prob:.2%})")
    else:
        print(f"後手必勝(先手勝率: {first_player_win_prob:.2%})")
    print(f"探索局面数: {node_count:,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="チェスの駒を動かすゲームの探索")
    parser.add_argument(
        "height",
        type=int,
        help="チェスボードの縦のサイズ",
    )
    parser.add_argument(
        "width",
        type=int,
        help="チェスボードの横のサイズ",
    )
    parser.add_argument(
        "initial_row",
        type=int,
        help="駒の初期位置（縦）",
    )
    parser.add_argument(
        "initial_col",
        type=int,
        help="駒の初期位置（横）",
    )
    parser.add_argument(
        "piece_type",
        type=str,
        help="駒の種類（rook, king, queen, knight）",
    )
    parser.add_argument(
        "num_playout",
        type=int,
        help="プレイアウトの試行回数",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="探索の詳細なログを表示する",
    )
    parser.add_argument(
        "--heuristic",
        action="store_true",
        help="ヒューリスティクスの利用",
    )
    parser.add_argument(
        "--symmetry",
        action="store_true",
        help="対称性の利用",
    )
    args = parser.parse_args()
    main(args)
