#!/bin/sh
# 初期状態1・ルーク
echo "[初期状態1・ルーク]"
python3 main.py 3 3 2 2 rook $@
echo ""
# 初期状態1・キング
echo "[初期状態1・キング]"
python3 main.py 3 3 2 2 king $@
echo ""
# 初期状態2・ルーク
echo "[初期状態2・ルーク]"
python3 main.py 4 4 3 3 rook $@
echo ""
# 初期状態2・キング
echo "[初期状態2・キング]"
python3 main.py 4 4 3 3 king $@
echo ""
# 初期状態3・ルーク
echo "[初期状態3・ルーク]"
python3 main.py 5 4 3 3 rook $@
echo ""
# 初期状態3・キング
echo "[初期状態3・キング]"
python3 main.py 5 4 3 3 king $@