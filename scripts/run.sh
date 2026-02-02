#!/bin/sh
. .venv/bin/activate
python3 --version
echo "executing search1"
./scripts/search1.sh > logs/search1.log --heuristic --symmetry 2>&1
echo "executing search2"
./scripts/search2.sh > logs/search2.log --heuristic --symmetry 2>&1
echo "executing search3"
./scripts/search3.sh > logs/search3.log --heuristic --symmetry 2>&1
