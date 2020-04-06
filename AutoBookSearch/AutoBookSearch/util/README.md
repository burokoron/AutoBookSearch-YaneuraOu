# 定跡作成に役立つかもしれないスクリプト集

### 動作保証環境
- python：3.7.4
- tqdm：4.31.1
- python-shogi：1.0.8

### reducing_book.py
肥大化してしまった定跡を削減する。
最悪応手を調べ、実戦で現れそうにない局面を削除していく。

実行コマンド例  
`python reducing_book.py -yane Base.db -tera TeraBase.db -o _Base.db -theme Theme.sfen -r 0.1`

- -yane：やねうら定跡
- -tera：テラショック定跡
- -o：出力される削減やねうら定跡
- -theme：課題局面までの手順をsfenで記述したファイル
- -r：登録手数を基準とした削減率(0.0～1.0)
