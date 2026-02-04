#!/bin/sh
: ${PROGRAM:=python3 main.py}
# 駒がクイーンのとき5x5と6x6の盤面で先手必勝となる場所を探索する
# 対称性があるため、左上の一部のみを調べる
echo "[盤面1:5x5]"
for row in 0 1 2; do
  for col in `seq 0 $row`; do
    echo "初期位置: ($row, $col)"
    time $PROGRAM 5 5 $row $col queen 1000 0 $@
    echo ""
  done
done

echo "[盤面2:6x6]"
for row in 0 1 2; do
  for col in `seq 0 $row`; do
    echo "初期位置: ($row, $col)"
    time $PROGRAM 6 6 $row $col queen 1000 0 $@
    echo ""
  done
done