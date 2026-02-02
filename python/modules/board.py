"""チェスボードの定義"""

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
        self, size: tuple[int, int], initial_position: tuple[int, int], piece_type: str
    ):
        """ゲーム状態を表すチェスボードを初期化する

        Args:
            size (tuple[int, int]): チェスボードのサイズ（縦, 横）
            initial_position (tuple[int, int]): 駒の初期位置（縦, 横）
            piece_type (str): 駒の種類（"rook", "king", "queen", "knight"）
        """
        if not (0 < size[0] <= 8 and 0 < size[1] <= 8):
            raise ValueError("ボードのサイズは1から8の範囲で指定してください")
        self.size = size
        self.center = (size[0] / 2, size[1] / 2)

        if piece_type not in ["rook", "king", "queen", "knight"]:
            raise ValueError("対応していない駒の種類です")
        self.piece_type = piece_type

        # 64bit整数でボードを表現
        self.board: int = 0  # bitの値が0なら未訪問、1なら訪問済み

        # 位置からbit-indexを、bit-indexから位置を引けるようにする
        self.index_map: dict[tuple[int, int], int] = {}
        self.position_map: dict[int, tuple[int, int]] = {}
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.index_map[(i, j)] = i * self.size[1] + j
        for position, index in self.index_map.items():
            self.position_map[index] = position

        if not (
            0 <= initial_position[0] < size[0] and 0 <= initial_position[1] < size[1]
        ):
            raise ValueError("初期位置がボードの範囲外です")
        self.pos: int = self.index_map[initial_position]

        # 初期位置を訪問済みとしてマーク
        self.board |= 1 << self.index_map[initial_position]

        # 各位置ごとに、その位置からの移動可能な位置を計算する
        self._create_available_positions_map()

        # 対称変換用の関数群を定義
        rows, cols = self.size
        self.ops = [
            (lambda r, c: r, lambda r, c: c),  # Identity
            (lambda r, c: r, lambda r, c: cols - 1 - c),  # Horizontal Mirror
            (lambda r, c: rows - 1 - r, lambda r, c: c),  # Vertical Mirror
            (lambda r, c: rows - 1 - r, lambda r, c: cols - 1 - c),  # 180 Rotate
        ]

        # 正方形の場合は対角系も追加
        if rows == cols:
            self.ops.extend(
                [
                    (lambda r, c: c, lambda r, c: r),  # Transpose (Diagonal)
                    (
                        lambda r, c: cols - 1 - c,
                        lambda r, c: rows - 1 - r,
                    ),  # Anti-transpose
                    (lambda r, c: c, lambda r, c: rows - 1 - r),  # 90 Rotate
                    (lambda r, c: cols - 1 - c, lambda r, c: r),  # 270 Rotate
                ]
            )

    def make_move(self, position: tuple[int, int]) -> tuple[int, int]:
        """駒を新しい位置に移動し、その位置を訪問済みとしてマークする

        Args:
            position (tuple[int, int]): 駒の移動先の位置（縦, 横）

        Returns:
            tuple[int, int]: 移動前の位置
        """
        old_position = self.position_map[self.pos]
        self.pos = self.index_map[position]
        # 新しい位置を訪問済みとしてマーク
        self.board |= 1 << self.index_map[position]
        return old_position

    def undo_move(
        self, unmark_position: tuple[int, int], restore_position: tuple[int, int]
    ):
        """移動を取り消し、ゲーム状態を元に戻す

        Args:
            unmark_position (tuple[int, int]): 訪問マークを解除する位置
            restore_position (tuple[int, int]): 駒を戻す位置
        """
        # 訪問マークを解除
        self.board &= ~(1 << self.index_map[unmark_position])
        self.pos = self.index_map[restore_position]

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

    def get_available_positions(self) -> list[tuple[int, int]]:
        """現在の位置から移動可能で未訪問の位置のリストを取得する

        Returns:
            list[tuple[int, int]]: 移動可能な位置のリスト
        """
        # 移動可能かつ未訪問
        available_positions = ~self.board & self.available_positions_map[self.pos]

        if available_positions == 0:
            return []

        # 位置リストを生成
        positions = []
        for i in range(self.size[0] * self.size[1]):
            if (available_positions >> i) & 1:
                positions.append(self.position_map[i])
        return positions

    def _create_available_positions_map(self):
        """ボード上の各位置に対して移動可能な位置を格納した辞書を作成する"""
        self.available_positions_map: dict[int, int] = {}

        # 駒の移動設定を取得
        directions, is_unlimited = PIECE_MOVE_CONFIG[self.piece_type]

        # 各位置から移動可能な位置を計算する
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                start_position = (i, j)
                bitmask = 0
                for direction in directions:
                    # 各方向について、開始位置から移動先を計算
                    new_pos = (
                        start_position[0] + direction[0],
                        start_position[1] + direction[1],
                    )
                    while (
                        0 <= new_pos[0] < self.size[0]
                        and 0 <= new_pos[1] < self.size[1]
                    ):
                        bitmask |= 1 << self.index_map[new_pos]
                        if not is_unlimited:
                            # 無制限に移動できない場合はここで終了
                            break

                        # 与えられた方向上の次の位置をチェックする
                        new_pos = (
                            new_pos[0] + direction[0],
                            new_pos[1] + direction[1],
                        )

                self.available_positions_map[self.index_map[start_position]] = bitmask

    def get_canonical_state(self) -> tuple[int, int]:
        """現在の盤面状態の正規形（対称変換の中で最小の値）を返す

        Returns:
            tuple[int, int]: (駒の位置インデックス, 盤面)
        """
        rows, cols = self.size
        r_pos, c_pos = self.position_map[self.pos]

        def get_state(r_map, c_map):
            # 駒の位置を変換
            new_r, new_c = r_map(r_pos, c_pos), c_map(r_pos, c_pos)
            new_pos_idx = new_r * cols + new_c

            # 盤面のビットを変換
            new_board = 0
            # 訪問済みのビットだけループさせる
            # ただしビット操作だけでやるのは複雑なので、全マス走査する
            # ボードサイズは最大8x8なので64回ループは許容範囲
            for i in range(rows * cols):
                if (self.board >> i) & 1:
                    curr_r, curr_c = i // cols, i % cols
                    tr, tc = r_map(curr_r, curr_c), c_map(curr_r, curr_c)
                    new_board |= 1 << (tr * cols + tc)
            return (new_pos_idx, new_board)

        candidates = [get_state(r_op, c_op) for r_op, c_op in self.ops]
        return min(candidates)
