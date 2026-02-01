import argparse

from modules import Board, minimax


def main(args: argparse.Namespace):
    # 引数からチェスボードの初期設定を取得する
    board_size = (args.height, args.width)
    initial_position = (args.initial_row, args.initial_col)
    piece_type = args.piece_type
    verbose = args.verbose
    heuristic = args.heuristic

    # チェスボードを初期化する
    board = Board(board_size, initial_position, piece_type)
    board.print_board()

    first_player_wins = minimax(board, 0, True, verbose, heuristic)
    if first_player_wins:
        print("先手必勝")
    else:
        print("後手必勝")


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
        "--verbose",
        action="store_true",
        help="探索の詳細なログを表示する",
    )
    parser.add_argument(
        "--heuristic",
        action="store_true",
        help="ヒューリスティクスの利用",
    )
    args = parser.parse_args()
    main(args)
