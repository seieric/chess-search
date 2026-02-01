"""チェスボードの定義"""


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
        self.size = size
        self.center = (size[0] / 2, size[1] / 2)
        self.board = [0] * (size[0] * size[1])  # 0: not visited, 1: visited

        if not (
            0 <= initial_position[0] < size[0] and 0 <= initial_position[1] < size[1]
        ):
            raise ValueError("初期位置がボードの範囲外です")
        self.pos = initial_position
        self._mark_visited(initial_position)

        if piece_type not in ["rook", "king", "queen", "knight"]:
            raise ValueError("対応していない駒の種類です")
        self.piece_type = piece_type

    def make_move(self, position: tuple[int, int]) -> tuple[int, int]:
        """駒を新しい位置に移動し、その位置を訪問済みとしてマークする

        Args:
            position (tuple[int, int]): 駒の移動先の位置（縦, 横）

        Returns:
            tuple[int, int]: 移動前の位置
        """
        old_position = self.pos
        self.pos = position
        self._mark_visited(position)
        return old_position

    def undo_move(
        self, unmark_position: tuple[int, int], restore_position: tuple[int, int]
    ):
        """移動を取り消し、ゲーム状態を元に戻す

        Args:
            unmark_position (tuple[int, int]): 訪問マークを解除する位置
            restore_position (tuple[int, int]): 駒を戻す位置
        """
        self._unmark_visited(unmark_position)
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
                if (i, j) == self.pos:
                    row.append("P")  # 駒の位置
                elif self.board[i * self.size[1] + j] == 1:
                    row.append("x")  # 訪問済みのマス
                elif self.board[i * self.size[1] + j] == 0:
                    row.append("-")  # 未訪問のマス
            print(" ".join(row))
        print()

    def get_available_positions(self) -> list[tuple[int, int]]:
        """現在の位置から移動可能で未訪問の位置のリストを取得する

        Returns:
            list[tuple[int, int]]: 移動可能な位置のリスト
        """
        # コマの種類で場合分けして移動可能な位置を取得する
        match self.piece_type:
            case "rook":
                # 縦横に無制限に移動できる
                directions = [
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1),
                ]
                return self._check_positions_in_directions(
                    directions, is_unlimited=True
                )
            case "queen":
                # 縦横斜め全方向に無制限に移動できる
                directions = [
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1),
                    (1, 1),
                    (1, -1),
                    (-1, 1),
                    (-1, -1),
                ]
                return self._check_positions_in_directions(
                    directions, is_unlimited=True
                )
            case "king":
                # 周囲のいずれのマスに移動できる
                directions = [
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1),
                    (1, 1),
                    (1, -1),
                    (-1, 1),
                    (-1, -1),
                ]
                return self._check_positions_in_directions(directions)
            case "knight":
                # L字型に移動できる
                directions = [
                    (2, 1),
                    (2, -1),
                    (-2, 1),
                    (-2, -1),
                    (1, 2),
                    (1, -2),
                    (-1, 2),
                    (-1, -2),
                ]
                return self._check_positions_in_directions(directions)
            case _:
                # 対応していない駒の場合はエラーを投げる
                # 通常は初期化時にチェックしているため起こり得ないエラー
                raise RuntimeError("対応していない駒の種類です")

    def _check_positions_in_directions(
        self, directions: list[tuple[int, int]], is_unlimited: bool = False
    ) -> list[tuple[int, int]]:
        """現在の位置から指定された方向で移動可能な未訪問の位置を取得する

        Args:
            directions (list[tuple[int, int]]): チェックする方向のリスト
            is_unlimited (bool): 無制限に移動できるかどうか

        Returns:
            list[tuple[int, int]]: 移動可能な位置のリスト
        """
        available_positions = []
        for direction in directions:
            new_pos = (
                self.pos[0] + direction[0],
                self.pos[1] + direction[1],
            )
            while 0 <= new_pos[0] < self.size[0] and 0 <= new_pos[1] < self.size[1]:
                index = new_pos[0] * self.size[1] + new_pos[1]
                if self.board[index] == 0:
                    # 未訪問の位置なら移動可能
                    available_positions.append(new_pos)

                if not is_unlimited:
                    # 無制限に移動できない場合はここで終了
                    break

                # 与えられた方向上の次の位置をチェックする
                new_pos = (
                    new_pos[0] + direction[0],
                    new_pos[1] + direction[1],
                )

        return available_positions

    def _mark_visited(self, position: tuple[int, int]):
        """指定された位置を訪問済みにマークする

        Args:
            position (tuple[int, int]): 訪問済みにする位置
        """
        assert 0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1], (
            "位置がボードの範囲外です"
        )

        index = position[0] * self.size[1] + position[1]
        self.board[index] = 1

    def _unmark_visited(self, position: tuple[int, int]):
        """指定された位置の訪問済みマークを解除する

        Args:
            position (tuple[int, int]): 訪問済みマークを解除する位置
        """
        assert 0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1], (
            "位置がボードの範囲外です"
        )

        index = position[0] * self.size[1] + position[1]
        self.board[index] = 0
