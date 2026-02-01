#!/bin/sh
# 駒がクイーンのとき4x5と5x6の盤面で先手必勝となる場所を探索する
# 対称性があるため、左上の一部のみを調べる
echo "[盤面1:4x5]"
for row in 0 1; do
  for col in 0 1 2; do
    echo "初期位置: ($row, $col)"
    time python3 main.py 4 5 $row $col queen $@
    echo ""
  done
done

echo "[盤面2:5x6]"
for row in 0 1 2; do
  for col in 0 1 2; do
    echo "初期位置: ($row, $col)"
    time python3 main.py 5 6 $row $col queen $@
    echo ""
  done
done