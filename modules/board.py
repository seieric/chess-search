"""チェスボードの定義"""

import random

# (directions, is_unlimited) の形式で駒の移動設定を定義
PIECE_MOVE_CONFIG = {
    "rook": (
        [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ],
        True,
    ),
    "king": (
        [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ],
        False,
    ),
    "queen": (
        [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ],
        True,
    ),
    "knight": (
        [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ],
        False,
    ),
}


class Board:
    def __init__(
        self,
        size: tuple[int, int],
        initial_position: tuple[int, int],
        piece_type: str,
        num_playout: int,
    ):
        """ゲーム状態を表すチェスボードを初期化する

        Args:
            size (tuple[int, int]): チェスボードのサイズ（縦, 横）
            initial_position (tuple[int, int]): 駒の初期位置（縦, 横）
            piece_type (str): 駒の種類（"rook", "king", "queen", "knight"）
            num_playout (int): プレイアウトの試行回数
        """
        if not (0 < size[0] <= 8 and 0 < size[1] <= 8):
            raise ValueError("ボードのサイズは1から8の範囲で指定してください")
        self.size = size
        self.center = (size[0] / 2, size[1] / 2)
        self.len = size[0] * size[1]

        if piece_type not in ["rook", "king", "queen", "knight"]:
            raise ValueError("対応していない駒の種類です")
        self.piece_type = piece_type

        # 64bit整数でボードを表現
        self.board: int = 0  # bitの値が0なら未訪問、1なら訪問済み

        # 位置からbit-indexを引けるようにする
        self.index_map = self._create_position_index_map(size)

        if not (
            0 <= initial_position[0] < size[0] and 0 <= initial_position[1] < size[1]
        ):
            raise ValueError("初期位置がボードの範囲外です")
        self.pos: int = self.index_map[initial_position]

        # 初期位置を訪問済みとしてマーク
        self.board |= 1 << self.index_map[initial_position]

        # 各位置からの移動可能な位置を格納したマップ
        self.available_positions_map = self._create_available_positions_map(
            piece_type, size
        )

        # 対称変換用のマップ群
        self.op_maps = self._create_op_maps(size)

        # ヒューリスティクス用の中心からの距離マップ (index -> distance)
        self.dist_from_center_map = [
            abs((i // size[1]) - self.center[0]) + abs((i % size[1]) - self.center[1])
            for i in range(self.len)
        ]

        self.num_playout = num_playout

    def get_state(self) -> tuple[int, int]:
        """現在のボードの状態を取得する

        Returns:
            tuple[int, int]: (盤面のビット表現, 駒の位置のインデックス)
        """
        return self.board, self.pos

    def set_state(self, board: int, position: int):
        """ボードの状態を設定する

        Args:
            board (int): 盤面のビット表現
            position (int): 駒の位置のインデックス
        """
        self.board = board
        self.pos = position

    def make_move(self, position: int) -> int:
        """駒を新しい位置に移動し、その位置を訪問済みとしてマークする

        Args:
            position (int): 駒の移動先の位置インデックス

        Returns:
            int: 移動前の位置インデックス
        """
        old_position = self.pos
        self.pos = position
        # 新しい位置を訪問済みとしてマーク
        self.board |= 1 << position
        return old_position

    def undo_move(self, unmark_position: int, restore_position: int):
        """移動を取り消し、ゲーム状態を元に戻す

        Args:
            unmark_position (int): 訪問マークを解除する位置インデックス
            restore_position (int): 駒を戻す位置インデックス
        """
        # 訪問マークを解除
        self.board &= ~(1 << unmark_position)
        self.pos = restore_position

    def print_board(self):
        """チェスボードの状態を表示する"""
        # 列番号を表示
        print("  ", end="")
        for j in range(self.size[1]):
            print(j, end=" ")
        print()
        for i in range(self.size[0]):
            row = [str(i)]  # 行番号を追加
            for j in range(self.size[1]):
                current_index = self.index_map[(i, j)]
                if current_index == self.pos:
                    row.append("P")  # 駒の位置
                elif (self.board >> current_index) & 1:
                    row.append("x")  # 訪問済みのマス
                else:
                    row.append("-")  # 未訪問のマス
            print(" ".join(row))
        print()

    def get_available_positions(self) -> list[int]:
        """現在の位置から移動可能で未訪問の位置のリストを取得する

        Returns:
            list[int]: 移動可能な位置インデックスのリスト
        """
        # 移動可能かつ未訪問
        available_positions = ~self.board & self.available_positions_map[self.pos]

        if available_positions == 0:
            return []

        # 位置リストを生成
        positions: list[int] = []
        while available_positions:
            # 最下位の1の位置を取得
            i = (available_positions & -available_positions).bit_length() - 1
            positions.append(i)
            # 最下位の1を消す
            available_positions &= available_positions - 1
        return positions

    def get_playout_result(self, current_player: bool) -> float:
        """ランダムに手を選んでゲームを進めた場合に先手が勝つ確率を返す

        Args:
            current_player (bool): 現在の手番（True: 先手, False: 後手）

        Returns:
            float: 先手の勝利確率
        """
        first_player_wins = 0
        current_board, current_pos = self.get_state()
        for _ in range(self.num_playout):
            player = current_player  # True: 先手, False: 後手
            while True:
                available_positions = self.get_available_positions()
                if not available_positions:
                    if not player:
                        # 後手が動けないなら先手の勝ち
                        first_player_wins += 1
                    break

                # ランダムに移動を選択
                chosen_position = random.choice(available_positions)
                self.make_move(chosen_position)

                # プレイヤー交代
                player = not player
            # ゲーム終了後、ボード状態を元に戻す
            self.set_state(current_board, current_pos)

        return first_player_wins / self.num_playout

    def get_canonical_state(self) -> tuple[int, int]:
        """現在の盤面状態の正規形（対称変換の中で最小の値）を返す

        Returns:
            tuple[int, int]: (駒の位置インデックス, 盤面)
        """
        candidates: list[tuple[int, int]] = []
        for op_map in self.op_maps:
            # 駒の位置を変換
            new_pos = op_map[self.pos]

            # 盤面のビットを変換
            new_board = 0
            # ビット操作だけでやるのは複雑なので、全マス走査する
            # ボードサイズは最大8x8なので64回ループは許容範囲
            for i in range(self.len):
                if (self.board >> i) & 1:
                    new_board |= 1 << op_map[i]
            candidates.append((new_pos, new_board))

        return min(candidates)

    def get_state_key(self) -> int:
        """現在の盤面状態の一意なキーを生成する

        Returns:
            int: 盤面状態のキー
        """
        canonical_pos, canonical_board = self.get_canonical_state()
        # 駒の位置を上位ビットに、盤面を下位ビットに結合してキーを生成
        return (canonical_pos << 64) | canonical_board

    @staticmethod
    def _create_position_index_map(size: tuple[int, int]) -> dict[tuple[int, int], int]:
        """位置からインデックスへのマッピングを作成する

        Args:
            size (tuple[int, int]): ボードのサイズ（縦, 横）

        Returns:
            dict[tuple[int, int], int]: 位置からインデックスへのマッピング
        """
        index_map: dict[tuple[int, int], int] = {}
        for i in range(size[0]):
            for j in range(size[1]):
                index_map[(i, j)] = i * size[1] + j
        return index_map

    @staticmethod
    def _create_available_positions_map(
        piece_type: str, size: tuple[int, int]
    ) -> list[int]:
        """ボード上の各位置に対して移動可能な位置を格納したリストを作成する

        Args:
            piece_type (str): 駒の種類（"rook", "king", "queen", "knight"）
            size (tuple[int, int]): ボードのサイズ（縦, 横）

        Returns:
            list: 各位置インデックスに対応する移動可能な位置のビットマスクのリスト
        """
        available_positions_map = [0] * (size[0] * size[1])

        # 駒の移動設定を取得
        directions, is_unlimited = PIECE_MOVE_CONFIG[piece_type]

        # 各位置から移動可能な位置を計算する
        for i in range(size[0] * size[1]):
            start_pos = (i // size[1], i % size[1])
            bitmask = 0
            for direction in directions:
                # 各方向について、開始位置から移動先を計算
                new_pos = (
                    start_pos[0] + direction[0],
                    start_pos[1] + direction[1],
                )
                while 0 <= new_pos[0] < size[0] and 0 <= new_pos[1] < size[1]:
                    bitmask |= 1 << (new_pos[0] * size[1] + new_pos[1])
                    if not is_unlimited:
                        # 無制限に移動できない場合はここで終了
                        break

                    # 与えられた方向上の次の位置をチェックする
                    new_pos = (
                        new_pos[0] + direction[0],
                        new_pos[1] + direction[1],
                    )

            available_positions_map[i] = bitmask

        return available_positions_map

    @staticmethod
    def _create_op_maps(size: tuple[int, int]) -> list[list[int]]:
        """対称変換用のマッピングを作成する

        Args:
            size (tuple[int, int]): ボードのサイズ（縦, 横）

        Returns:
            list[list[int]]: 各対称変換に対応するインデックスマッピングのリスト
        """
        board_len = size[0] * size[1]
        ops = [
            (lambda r, c: r, lambda r, c: c),  # Identity
            (lambda r, c: r, lambda r, c: size[1] - 1 - c),  # Horizontal Mirror
            (lambda r, c: size[0] - 1 - r, lambda r, c: c),  # Vertical Mirror
            (lambda r, c: size[0] - 1 - r, lambda r, c: size[1] - 1 - c),  # 180 Rotate
        ]

        # 正方形の場合は対角系も追加
        if size[0] == size[1]:
            ops.extend(
                [
                    (lambda r, c: c, lambda r, c: r),  # Transpose (Diagonal)
                    (
                        lambda r, c: size[1] - 1 - c,
                        lambda r, c: size[0] - 1 - r,
                    ),  # Anti-transpose
                    (lambda r, c: c, lambda r, c: size[0] - 1 - r),  # 90 Rotate
                    (lambda r, c: size[1] - 1 - c, lambda r, c: r),  # 270 Rotate
                ]
            )

        op_maps: list[list[int]] = []
        for r_op, c_op in ops:
            op_map: list[int] = [0] * board_len
            for r in range(size[0]):
                for c in range(size[1]):
                    new_r, new_c = r_op(r, c), c_op(r, c)
                    op_map[r * size[1] + c] = new_r * size[1] + new_c
            op_maps.append(op_map)

        return op_maps
