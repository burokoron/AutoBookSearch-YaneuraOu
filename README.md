# AutoBookSearch-YaneuraOu
A tool for the book generation using YaneuraOu.

将棋ソフト「[やねうら王](https://github.com/yaneurao/YaneuraOu)」を使って特定局面から定跡を自動探索するツール

### 特徴
- 微有利な局面から有利な局面にもっていく手順を効率的に探索できる
- 特定の駒の禁止位置を設定することで任意の戦型探索ができる
  - 例：10～20手目に飛車が1～4筋にあることを禁止することで無理やり振り飛車にする

### 動作保証環境
- YaneuraOu：v4.86
- python：3.7.4
- numpy：1.16.5
- python-shogi：1.0.8

### 使い方
options.iniにパラメータを適切に設定しauto_book_search.pyを実行する。

#### options.ini
- YaneuraOu
  - EngineFile：やねうら王の実行ファイルのパス
  - EvalDir：評価関数があるフォルダのパス
  - BookDir:定跡ファイルのパス
  - Hash：置換表のサイズ
  - Threads：スレッド数
  - Depth：探索深さ
  - Nodes：1局面における最大探索局面数
  - BlackContempt：先手の千日手評価値(先手目線)
  - WhiteContempt：後手の千日手評価値(先手目線)
- Search
  - ThemeSfenFile：課題局面までの手順を記述したsfenファイル
    - 例：startpos moves 7g7f
    - 複数行指定可(効率が落ちるので非推奨)
  - ForbiddenFile：駒の位置の禁止条件を記述したファイル
    - 例：10 20 R A1 A2 A3 A4 B1 B2 B3 B4 C1 C2 C3 C4 D1 D2 D3 D4 E1 E2 E3 E4 F1 F2 F3 F4 G1 G2 G3 G4 H1 H2 H3 H4 I1 I2 I3 I4
      - 10～20手目、飛車、以下禁止位置
    - 複数行指定可
  - MaxMoves：課題局面からの思考対象となる最大手数
  - BestPVFile：最善応手群が一時保存されるファイル
  - CommandFile：やねうら王へのコマンドが一時保存されるファイル
  - YaneuraDBFile：局面ごとの探索結果から作成される定跡ファイル
  - TeraShockDBFile：YaneuraDBFileを探索して最善応手の評価値で更新された定跡ファイル
  - MaxLoops：定跡延長の回数
  - BlackResignValue：定跡探索を終了する先手の評価値(先手目線)
  - WhiteResignValue：定跡探索を終了する後手の評価値(先手目線)
  - CorrectionValue：探索深さに比例して評価値を補正するパラメータ(-log2(depth+1)*)
    - 数値を大きくするほど、評価値が悪くても探索の浅い手を調べるようになる
    - 0だと最善応手上位の手順を調べる
  - AutoMultiPV：探索候補手数を自動で決めるかどうか(yes/no)
  - MinMultiPV：最小候補手数
    - AutoMultiPVがnoの場合は常にこの値となる
  - MaxMultiPV：最大候補手数
    - AutoMultiPVがyesの場合のみ有効
