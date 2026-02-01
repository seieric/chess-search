#pragma once

#include "board.h"
#include <stdbool.h>

typedef struct {
    bool winner;       // true: 先手, false: 後手
    long node_count;   // 探索した局面数
} MinimaxResult;

MinimaxResult minimax(Board *board, int depth, bool player, 
                     bool verbose, bool heuristic, bool symmetry);
