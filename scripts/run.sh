#!/bin.sh
. python/.venv/bin/activate
./scripts/search1.sh > logs/search1.log --heuristic --symmetry 2>&1
./scripts/search2.sh > logs/search2.log --heuristic --symmetry 2>&1
./scripts/search3.sh > logs/search3.log --heuristic --symmetry 2>&1