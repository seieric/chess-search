#include "board.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 駒の移動設定
typedef struct {
    int dr;
    int dc;
} Direction;

static const Direction ROOK_DIRS[] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
static const int ROOK_DIRS_COUNT = 4;
static const bool ROOK_UNLIMITED = true;

static const Direction KING_DIRS[] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}, 
                                       {1, 1}, {1, -1}, {-1, 1}, {-1, -1}};
static const int KING_DIRS_COUNT = 8;
static const bool KING_UNLIMITED = false;

static const Direction QUEEN_DIRS[] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}, 
                                        {1, 1}, {1, -1}, {-1, 1}, {-1, -1}};
static const int QUEEN_DIRS_COUNT = 8;
static const bool QUEEN_UNLIMITED = true;

static const Direction KNIGHT_DIRS[] = {{2, 1}, {2, -1}, {-2, 1}, {-2, -1},
                                         {1, 2}, {1, -2}, {-1, 2}, {-1, -2}};
static const int KNIGHT_DIRS_COUNT = 8;
static const bool KNIGHT_UNLIMITED = false;

Board *board_create(int rows, int cols, Position initial_pos, PieceType piece_type) {
    Board *board = (Board *)malloc(sizeof(Board));
    if (!board) return NULL;
    
    board->rows = rows;
    board->cols = cols;
    board->board = (unsigned char *)calloc(rows * cols, sizeof(unsigned char));
    if (!board->board) {
        free(board);
        return NULL;
    }
    
    board->pos = initial_pos;
    board->piece_type = piece_type;
    board->center_row = rows / 2.0;
    board->center_col = cols / 2.0;
    
    board_set(board, initial_pos.row, initial_pos.col, 1);
    
    return board;
}

void board_destroy(Board *board) {
    if (board) {
        free(board->board);
        free(board);
    }
}

void board_print(const Board *board) {
    printf("  ");
    for (int j = 0; j < board->cols; j++) {
        printf("%d ", j);
    }
    printf("\n");
    
    for (int i = 0; i < board->rows; i++) {
        printf("%d ", i);
        for (int j = 0; j < board->cols; j++) {
            if (i == board->pos.row && j == board->pos.col) {
                printf("P ");
            } else if (board_get(board, i, j) == 1) {
                printf("x ");
            } else {
                printf("- ");
            }
        }
        printf("\n");
    }
    printf("\n");
}

Position board_make_move(Board *board, Position position) {
    Position old_pos = board->pos;
    board->pos = position;
    board_set(board, position.row, position.col, 1);
    return old_pos;
}

void board_undo_move(Board *board, Position unmark_pos, Position restore_pos) {
    board_set(board, unmark_pos.row, unmark_pos.col, 0);
    board->pos = restore_pos;
}

static int check_positions_in_directions(const Board *board, const Direction *dirs, 
                                        int dir_count, bool is_unlimited,
                                        Position *positions, int max_positions) {
    int count = 0;
    
    for (int d = 0; d < dir_count; d++) {
        int new_row = board->pos.row + dirs[d].dr;
        int new_col = board->pos.col + dirs[d].dc;
        
        while (new_row >= 0 && new_row < board->rows && 
               new_col >= 0 && new_col < board->cols) {
            if (board_get(board, new_row, new_col) == 0) {
                if (count < max_positions) {
                    positions[count].row = new_row;
                    positions[count].col = new_col;
                    count++;
                }
            }
            
            if (!is_unlimited) break;
            
            new_row += dirs[d].dr;
            new_col += dirs[d].dc;
        }
    }
    
    return count;
}

int board_get_available_positions(const Board *board, Position *positions, int max_positions) {
    switch (board->piece_type) {
        case PIECE_ROOK:
            return check_positions_in_directions(board, ROOK_DIRS, ROOK_DIRS_COUNT, 
                                                 ROOK_UNLIMITED, positions, max_positions);
        case PIECE_KING:
            return check_positions_in_directions(board, KING_DIRS, KING_DIRS_COUNT, 
                                                 KING_UNLIMITED, positions, max_positions);
        case PIECE_QUEEN:
            return check_positions_in_directions(board, QUEEN_DIRS, QUEEN_DIRS_COUNT, 
                                                 QUEEN_UNLIMITED, positions, max_positions);
        case PIECE_KNIGHT:
            return check_positions_in_directions(board, KNIGHT_DIRS, KNIGHT_DIRS_COUNT, 
                                                 KNIGHT_UNLIMITED, positions, max_positions);
        default:
            return 0;
    }
}
