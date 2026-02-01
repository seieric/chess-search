#!/bin/sh
# 駒がナイトのとき7x7と8x8の盤面で先手必勝となる場所を探索する

echo "[7x7盤面]"
for row in 0 1 2 3; do
  for col in `seq 0 $row`; do
    echo "初期位置: ($row, $col)"
    time python3 main.py 7 7 $row $col knight $@
    echo ""
  done
done

echo "[8x8盤面]"
for row in 0 1 2 3; do
  for col in `seq 0 $row`; do
    echo "初期位置: ($row, $col)"
    time python3 main.py 8 8 $row $col knight $@
    echo ""
  done
done