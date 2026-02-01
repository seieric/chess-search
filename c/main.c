#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "board.h"
#include "minimax.h"

static void print_usage(const char *prog_name) {
    fprintf(stderr, "Usage: %s <height> <width> <initial_row> <initial_col> <piece_type> [options]\n", prog_name);
    fprintf(stderr, "  piece_type: rook, king, queen, knight\n");
    fprintf(stderr, "Options:\n");
    fprintf(stderr, "  --verbose     探索の詳細なログを表示する\n");
    fprintf(stderr, "  --heuristic   ヒューリスティクスの利用\n");
    fprintf(stderr, "  --symmetry    対称性の利用\n");
    exit(1);
}

static PieceType parse_piece_type(const char *str) {
    if (strcmp(str, "rook") == 0) return PIECE_ROOK;
    if (strcmp(str, "king") == 0) return PIECE_KING;
    if (strcmp(str, "queen") == 0) return PIECE_QUEEN;
    if (strcmp(str, "knight") == 0) return PIECE_KNIGHT;
    fprintf(stderr, "Error: Invalid piece type '%s'\n", str);
    exit(1);
}

int main(int argc, char *argv[]) {
    if (argc < 6) {
        print_usage(argv[0]);
    }
    
    // 必須引数のパース
    int height = atoi(argv[1]);
    int width = atoi(argv[2]);
    int initial_row = atoi(argv[3]);
    int initial_col = atoi(argv[4]);
    PieceType piece_type = parse_piece_type(argv[5]);
    
    // オプション引数のパース
    bool verbose = false;
    bool heuristic = false;
    bool symmetry = false;
    
    for (int i = 6; i < argc; i++) {
        if (strcmp(argv[i], "--verbose") == 0) {
            verbose = true;
        } else if (strcmp(argv[i], "--heuristic") == 0) {
            heuristic = true;
        } else if (strcmp(argv[i], "--symmetry") == 0) {
            symmetry = true;
        } else {
            fprintf(stderr, "Unknown option: %s\n", argv[i]);
            print_usage(argv[0]);
        }
    }
    
    // バリデーション
    if (height <= 0 || width <= 0) {
        fprintf(stderr, "Error: Board size must be positive\n");
        return 1;
    }
    if (initial_row < 0 || initial_row >= height || 
        initial_col < 0 || initial_col >= width) {
        fprintf(stderr, "Error: Initial position out of bounds\n");
        return 1;
    }
    
    // ボード作成
    Position initial_pos = {initial_row, initial_col};
    Board *board = board_create(height, width, initial_pos, piece_type);
    if (!board) {
        fprintf(stderr, "Error: Failed to create board\n");
        return 1;
    }
    
    // ボード表示
    board_print(board);
    
    // 探索実行
    MinimaxResult result = minimax(board, 0, true, verbose, heuristic, symmetry);
    
    // 結果表示
    if (result.winner) {
        printf("先手必勝\n");
    } else {
        printf("後手必勝\n");
    }
    printf("探索局面数: %ld\n", result.node_count);
    
    // クリーンアップ
    board_destroy(board);
    
    return 0;
}
