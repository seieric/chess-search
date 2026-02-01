#include "minimax.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_POSITIONS 256
#define MAX_DEPTH_FOR_SYMMETRY 3

// ヒューリスティクス用: 中心からの距離でソート
static int compare_positions_heuristic(const void *a, const void *b, void *board_ptr) {
    const Position *pos_a = (const Position *)a;
    const Position *pos_b = (const Position *)b;
    const Board *board = (const Board *)board_ptr;
    
    double dist_a = fabs(pos_a->row - board->center_row) + fabs(pos_a->col - board->center_col);
    double dist_b = fabs(pos_b->row - board->center_row) + fabs(pos_b->col - board->center_col);
    
    // 降順（遠い方が優先）
    if (dist_b > dist_a) return 1;
    if (dist_b < dist_a) return -1;
    return 0;
}

// qsort用のラッパー（グローバル変数を使わない実装）
static Board *g_board_for_sort = NULL;
static int compare_positions_wrapper(const void *a, const void *b) {
    return compare_positions_heuristic(a, b, g_board_for_sort);
}

static void sort_moves_by_heuristic(Board *board, Position *positions, int count) {
    g_board_for_sort = board;
    qsort(positions, count, sizeof(Position), compare_positions_wrapper);
    g_board_for_sort = NULL;
}

// 対称性チェック（簡易版）
static bool check_horizontal_symmetry(const Board *board) {
    if (board->pos.col * 2 != board->cols - 1) {
        return false;
    }
    
    int half_cols = (board->cols + 1) / 2;
    for (int r = 0; r < board->rows; r++) {
        for (int c = 0; c < half_cols; c++) {
            if (board_get(board, r, c) != board_get(board, r, board->cols - 1 - c)) {
                return false;
            }
        }
    }
    return true;
}

static bool check_vertical_symmetry(const Board *board) {
    if (board->pos.row * 2 != board->rows - 1) {
        return false;
    }
    
    int half_rows = (board->rows + 1) / 2;
    for (int r = 0; r < half_rows; r++) {
        for (int c = 0; c < board->cols; c++) {
            if (board_get(board, r, c) != board_get(board, board->rows - 1 - r, c)) {
                return false;
            }
        }
    }
    return true;
}

static Position get_canonical_position(Position pos, int rows, int cols,
                                       bool is_h_sym, bool is_v_sym) {
    Position canonical = pos;
    Position candidates[4];
    int count = 1;
    candidates[0] = pos;
    
    if (is_h_sym) {
        candidates[count].row = pos.row;
        candidates[count].col = cols - 1 - pos.col;
        count++;
    }
    if (is_v_sym) {
        candidates[count].row = rows - 1 - pos.row;
        candidates[count].col = pos.col;
        count++;
    }
    if (is_h_sym && is_v_sym) {
        candidates[count].row = rows - 1 - pos.row;
        candidates[count].col = cols - 1 - pos.col;
        count++;
    }
    
    // 最小の位置を返す
    for (int i = 1; i < count; i++) {
        if (candidates[i].row < canonical.row || 
            (candidates[i].row == canonical.row && candidates[i].col < canonical.col)) {
            canonical = candidates[i];
        }
    }
    return canonical;
}

static int filter_symmetric_moves(Board *board, Position *positions, int count) {
    bool is_h_sym = check_horizontal_symmetry(board);
    bool is_v_sym = check_vertical_symmetry(board);
    
    if (!is_h_sym && !is_v_sym) {
        return count;
    }
    
    // 重複除去
    Position filtered[MAX_POSITIONS];
    bool seen[MAX_POSITIONS * 2] = {false};  // 簡易的なハッシュテーブル
    int filtered_count = 0;
    
    for (int i = 0; i < count; i++) {
        Position canonical = get_canonical_position(positions[i], board->rows, board->cols,
                                                    is_h_sym, is_v_sym);
        int hash = (canonical.row * board->cols + canonical.col) % (MAX_POSITIONS * 2);
        
        if (!seen[hash]) {
            seen[hash] = true;
            filtered[filtered_count++] = positions[i];
        }
    }
    
    memcpy(positions, filtered, filtered_count * sizeof(Position));
    return filtered_count;
}

MinimaxResult minimax(Board *board, int depth, bool player, 
                     bool verbose, bool heuristic, bool symmetry) {
    MinimaxResult result;
    result.node_count = 1;
    
    Position available_positions[MAX_POSITIONS];
    int count = board_get_available_positions(board, available_positions, MAX_POSITIONS);
    
    if (count == 0) {
        result.winner = !player;
        return result;
    }
    
    // 対称性フィルタ
    if (symmetry && depth <= MAX_DEPTH_FOR_SYMMETRY) {
        count = filter_symmetric_moves(board, available_positions, count);
    }
    
    // ヒューリスティクス
    if (heuristic) {
        sort_moves_by_heuristic(board, available_positions, count);
    }
    
    if (verbose) {
        for (int i = 0; i < depth * 2; i++) printf(" ");
        printf("depth=%d, player=%s, available=%d\n", depth, 
               player ? "先手" : "後手", count);
    }
    
    for (int i = 0; i < count; i++) {
        if (verbose) {
            for (int j = 0; j < (depth * 2 + 2); j++) printf(" ");
            printf("%s chose (%d, %d)\n", player ? "先手" : "後手",
                   available_positions[i].row, available_positions[i].col);
        }
        
        Position old_pos = board_make_move(board, available_positions[i]);
        MinimaxResult child_result = minimax(board, depth + 1, !player, verbose, heuristic, symmetry);
        result.node_count += child_result.node_count;
        board_undo_move(board, available_positions[i], old_pos);
        
        if (child_result.winner == player) {
            result.winner = player;
            return result;
        }
    }
    
    result.winner = !player;
    return result;
}
