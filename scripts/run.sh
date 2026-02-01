#!/bin.sh
PROGRAM=./c/chess_search ./scripts/search1.sh --heuristic --symmetry > logs/c_search1.log 2>&1
PROGRAM=./c/chess_search ./scripts/search2.sh --heuristic --symmetry > logs/c_search2.log 2>&1
PROGRAM=./c/chess_search ./scripts/search3.sh --heuristic --symmetry > logs/c_search3.log 2>&1
./scripts/search1.sh > logs/search1.log --heuristic --symmetry 2>&1
./scripts/search2.sh > logs/search2.log --heuristic --symmetry 2>&1
./scripts/search3.sh > logs/search3.log --heuristic --symmetry 2>&1