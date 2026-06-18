#!/bin/bash

# 保存先の lib/ フォルダを作成
mkdir -p lib

# URL一覧を1行ずつ読み込んでダウンロード
while IFS= read -r url; do
  # 空行や "null" が混ざっていたらスキップ
  if [ -z "$url" ] || [ "$url" == "null" ]; then
    continue
  fi
  
  echo "[DL] $url"
  
  # URLの末尾（ファイル名）を自動抽出して lib/ に保存（リトライ付き）
  curl --connect-timeout 10 --retry 3 --retry-delay 5 \
    -L "$url" \
    -o "lib/$(basename "$url")"
    
done < lib_url.txt
