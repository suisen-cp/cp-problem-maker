# cp-problem-maker

競技プログラミングの問題作成を補助するツール。

## インストール

```bash
cd インストールしたい場所
git clone git@github.com:suisen-cp/cp-problem-maker.git
cd cp-problem-maker
pip install .
```

## アンインストール

```bash
pip uninstall /path/to/repository
```

入れた場所を忘れた場合は以下のコマンドを打って `Location` の部分を見ればよい。

```bash
pip show cp-problem-maker
```

## 使い方

### `cp-problem-maker init`

```bash
cp-problem-maker init [-p /path/to/problem]
```

`/path/to/problem` で指定したパスを作業フォルダとして新しい問題のテンプレートを作成する。既に存在するフォルダを指定してもよいが、空である必要がある。`/path/to/problem` として絶対パスを指定しても相対パスを指定してもよい。

パスの指定を省略した場合はカレントディレクトリを作業フォルダとして新しい問題のテンプレートを作成する。この場合もカレントディレクトリは空である必要がある。

作成されるテンプレートの中身は次の通り (https://github.com/yosupo06/library-checker-problems で用いられている形式とほぼ同様)。

```
problem
 |- gen/               # 入力のジェネレータを置くフォルダ
 |   |- example_00.in  # サンプルケースなど、手動で作成する入力
 |   |- random.cpp     # 入力生成器
 |- in/                # 入力データが出力されるフォルダ
 |- include/
 |   |- params.h       # 設定ファイルに書いた定数が定義されるファイル
 |- out/               # 出力データが出力されるフォルダ
 |- sol/               # 解法を置くフォルダ
 |   |- correct.cpp    # 想定解
 |- checker.cpp        # ジャッジ
 |- info.toml          # 設定ファイル
 |- task.md            # 問題文を書くファイル
 |- verifier.cpp       # 入力のバリデータ
```

問題完成時のイメージは次の通り。

```
problem
 |- gen/
 |   |- example_00.in  # サンプル1
 |   |- example_01.in  # サンプル2
 |   :
 |   |- random.cpp
 |   |- handmade.cpp
 |   :
 |- include/
 |   |- params.h    # 設定ファイルに書いた定数が書き込まれるファイル
 |   |- utility.hpp # その他用いたいファイル
 |- in/
 |   |- example_00.in
 |   |- example_01.in
 |   :
 |   |- random_00.in
 |   |- random_01.in
 |   :
 |   |- handmade_00.in
 |   |- handmade_01.in
 |   :
 |- out/
 |   |- example_00.out
 |   |- example_01.out
 |   :
 |   |- random_00.out
 |   |- random_01.out
 |   :
 |   |- handmade_00.out
 |   |- handmade_01.out
 |   :
 |- sol/
 |   |- correct.cpp
 |   |- wa.cpp         # 想定WA解法
 |   |- tle.cpp        # 想定TLE解法
 |   :
 |- checker.cpp
 |- info.toml
 |- task.md
 |- verifier.cpp
```

### `cp-problem-maker gen-case`

```bash
cp-problem-maker gen-case [-p /path/to/problem] [--allow-replace]
```

入出力を生成する。`problem/in/` および `problem/out/` が空でなければエラーとなる。ただし、明示的に `--allow-replace` を指定した場合はこの限りではない。

### `cp-problem-maker check`

```bash
cp-problem-maker check [-p /path/to/problem] [-s [solution_1 [solution_2 ...]]] 
```

`-s` で指定した解法 (`problem/sol/` からの相対パスで指定) をジャッジする。何も指定しなかった場合は全ての解法をジャッジする。

### `cp-problem-maker test`

```bash
cp-problem-maker test [-p /path/to/problem] [--allow-replace]
```

これは以下と等価。

```bash
cp-problem-maker gen-case [-p /path/to/problem] [--allow-replace]
cp-problem-maker check [-p /path/to/problem]
```

## 設定ファイルの書き方

```toml
title = "title" # 問題のタイトル
timelimit = 2.0 # Time Limit。単位は秒

# テストケースに関する設定
[[tests]]
  name = "example.in" # .in はケースを直接記したファイルを指す 
  number = 3          # 生成するケース数。この場合はexample_00.in, example_01.in, example_02.inの3つ

[[tests]]
  name = "random.cpp" # 入力生成器 (problem/gen/ 配下においたファイル)
  number = 2          # 生成するケース数。この場合はrandom_00.in, random_01.inの2つ

# 解法に関する設定
[[solutions]]
  name = "wa.cpp"     # 解法ファイル (problem/sol/ 配下においたファイル)
  allow_tle = false   # TLEすることを許すか (デフォルトでは false)
  wrong = true        # WAとなることを想定するか (デフォルトではfalse)

[[solutions]]
  name = "tle.cpp"
  allow_tle = true

[[solutions]]
  name = "another_correct.cpp"  # 別解

# 制約など、各種ファイル (checkerやverifierなど) で用いるパラメータ。ここで定義した値が problem/include/params.h 内で定義される。
[params]
  N_MIN = 1
  N_MAX = 100000
  Q_MIN = 1
  Q_MAX = 100000
```

## `verifier.cpp` や `checker.cpp` の書き方

`testlib` を用いて書くことを想定。

### 参考

- https://github.com/MikeMirzayanov/testlib (`testlib` の GitHub リポジトリ)
- https://codeforces.com/blog/entry/18426 (スペシャルジャッジの書き方)

