#pragma once

#include <stdbool.h>

typedef enum {
    PIECE_ROOK,
    PIECE_KING,
    PIECE_QUEEN,
    PIECE_KNIGHT
} PieceType;

typedef struct {
    int row;
    int col;
} Position;

typedef struct {
    int rows;
    int cols;
    unsigned char *board;  // 1D array: board[row * cols + col]
    Position pos;
    PieceType piece_type;
    double center_row;
    double center_col;
} Board;

// Board関数
Board *board_create(int rows, int cols, Position initial_pos, PieceType piece_type);
void board_destroy(Board *board);
void board_print(const Board *board);
Position board_make_move(Board *board, Position position);
void board_undo_move(Board *board, Position unmark_pos, Position restore_pos);
int board_get_available_positions(const Board *board, Position *positions, int max_positions);

// インライン関数: ボードアクセス
static inline unsigned char board_get(const Board *board, int row, int col) {
    return board->board[row * board->cols + col];
}

static inline void board_set(Board *board, int row, int col, unsigned char value) {
    board->board[row * board->cols + col] = value;
}
