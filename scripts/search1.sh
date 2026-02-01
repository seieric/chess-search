#!/bin/sh
: ${PROGRAM:=python3 python/main.py}
# 初期状態1・ルーク
echo "[初期状態1・ルーク]"
time $PROGRAM 3 3 2 2 rook $@
echo ""
# 初期状態1・キング
echo "[初期状態1・キング]"
time $PROGRAM 3 3 2 2 king $@
echo ""
# 初期状態2・ルーク
echo "[初期状態2・ルーク]"
time $PROGRAM 4 4 3 3 rook $@
echo ""
# 初期状態2・キング
echo "[初期状態2・キング]"
time $PROGRAM 4 4 3 3 king $@
echo ""
# 初期状態3・ルーク
echo "[初期状態3・ルーク]"
time $PROGRAM 5 4 3 3 rook $@
echo ""
# 初期状態3・キング
echo "[初期状態3・キング]"
time $PROGRAM 5 4 3 3 king $@