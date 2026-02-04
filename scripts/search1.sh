#!/bin/sh
: ${PROGRAM:=python3 main.py}
# 初期状態1・ルーク
echo "[初期状態1・ルーク]"
time $PROGRAM 3 3 2 2 rook 1000 0 $@
echo ""
# 初期状態1・キング
echo "[初期状態1・キング]"
time $PROGRAM 3 3 2 2 king 1000 0 $@
echo ""
# 初期状態2・ルーク
echo "[初期状態2・ルーク]"
time $PROGRAM 4 4 3 3 rook 1000 0 $@
echo ""
# 初期状態2・キング
echo "[初期状態2・キング]"
time $PROGRAM 4 4 3 3 king 1000 0 $@
echo ""
# 初期状態3・ルーク
echo "[初期状態3・ルーク]"
time $PROGRAM 5 4 3 3 rook 1000 0 $@
echo ""
# 初期状態3・キング
echo "[初期状態3・キング]"
time $PROGRAM 5 4 3 3 king 1000 0 $@