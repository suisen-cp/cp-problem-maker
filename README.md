# cp-problem-maker

競技プログラミングの問題作成を補助するツール。

仕様は https://github.com/yosupo06/library-checker-problems を大きく参考にしているが、異なる部分もあるので注意。

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

`/path/to/problem` で指定したパスを作業フォルダとして新しい問題のテンプレートを作成する。既に存在するフォルダを指定してもよいが、空である必要がある。

パスの指定を省略した場合はカレントディレクトリを作業フォルダとして新しい問題のテンプレートを作成する。この場合もカレントディレクトリは空である必要がある。

作成されるテンプレートの中身は次の通り。

```
problem
 |- gen/               # 入力生成器を配置するフォルダ
 |- in/                # 入力データが配置されるフォルダ
 |- include/           # 後述の params.hpp など、共通で用いるファイルを配置するフォルダ
 |- out/               # 出力データが配置されるフォルダ
 |- sol/               # 解法を配置するフォルダ
 |   |- correct.cpp    # 想定解コード
 |- checker.cpp        # ジャッジコード
 |- compile_info.toml  # C++ コードのコンパイルに関する設定ファイル
 |- info.toml          # 問題に関する設定ファイル
 |- task.md            # 問題文を書くファイル (optional)
 |- verifier.cpp       # 入力のフォーマットや制約を検証するコード
```

問題完成時の例は [サンプル](sample) を参照。`in/`, `out/` 配下の入出力データや `include/params.hpp` は自動で生成される。それ以外のファイルを追加したり編集したりする必要がある。

### `cp-problem-maker gen-params`

```bash
cp-problem-maker gen-params [-p /path/to/problem] [--allow-replace]
```

`info.toml` に書いた定数を `include/params.hpp` に書き込む。

`include/params.hpp` が既に存在していればエラーとなる。ただし、明示的に `--allow-replace` を指定した場合は既存のファイルを置き換える。

### `cp-problem-maker gen-case`

```bash
cp-problem-maker gen-case [-p /path/to/problem] [--allow-replace]
```

同じ引数で `cp-problem-maker gen-params` を実行して設定ファイルの変更を反映してから入出力を生成する。

`in/` および `out/` が空ではないか、あるいは `include/params.hpp` が既に存在していればエラーとなる。ただし、明示的に `--allow-replace` を指定した場合は既存のファイルを置き換える。

### `cp-problem-maker check`

```bash
cp-problem-maker check [-p /path/to/problem] [-s [solution_1 [solution_2 ...]]] 
```

`-s` で指定した解法 (`sol/` からの相対パスで指定) を走らせ、`info.toml` で指定した通りの挙動をしているかをチェックする。

解法を何も指定しなかった場合は全ての解法を走らせる。

### `cp-problem-maker test`

```bash
cp-problem-maker test [-p /path/to/problem] [--allow-replace]
```

これは以下と等価。

```bash
cp-problem-maker gen-case [-p /path/to/problem] [--allow-replace]
cp-problem-maker check [-p /path/to/problem]
```

### 入力生成器の書き方

入力生成器は `gen/` 配下に配置する。

#### 生の入力データを置く場合

サンプルなど、生の入力データは `.in` または `.txt` の拡張子を付けて配置する。

`info.toml` にも作成したデータの情報を反映する必要がある。`info.toml` の書き方は [デフォルトの info.toml](template/info.toml) のコメントを参照。

> [!NOTE]
> `info.toml` に次のように生成器を登録した場合、`gen/` 以下には `example_00.in`, `example_01.in`, `example_02.in` という名前で配置する必要がある。
> 番号は0埋めして2桁で書くこと。
>
> ```toml
> [[tests]]
>   name = 'example.in'
>   number = 3
> ```

#### C++ 入力生成器を置く場合

大きいケースなどは C++ で記述した生成器を `.cpp` または `.cc` の拡張子を付けて配置する。

`info.toml` にも作成した生成器の情報を反映する必要がある。`info.toml` の書き方は [デフォルトの info.toml](template/info.toml) のコメントを参照。

便利のため、実行時のコマンドライン引数 (`int main(int argc, char* argv[]) { ... }` の `argv`) に次の情報が与えられる。

- `argv[1]`: 同じ生成器から生成されるケースのうち何番目か (0-indexed) の情報。より具体的には、生成器 `random.cpp` に対して `random_00.in` を生成する実行時には `0` が、`random_06.in` を生成する実行時には `6` が与えられる。周期的に生成方法を切り替えたい場合などにこの情報を用いることを想定。
- `argv[2]`: 生成器の名前と `argv[1]` の組を元に生成した $`0`$ 以上 $`2^{31}`$ 未満のハッシュ値。乱数の seed として用いることを想定。

### `info.toml`

問題に関する設定ファイル。

書き方については `init` コマンドで生成される [デフォルトの info.toml](template/info.toml) のコメントを参照

### `compile_info.toml`

C++ コードのコンパイルに関する設定ファイル。

書き方については  `init` コマンドで生成される [デフォルトの compile_info.toml](template/compile_info.toml) のコメントを参照

### `verifier.cpp`

入力バリデータ。標準入力から入力が与えられる。

[testlib](https://github.com/MikeMirzayanov/testlib) を用いて書くことを想定しており、https://codeforces.com/blog/entry/18426 などを参考にして書くこと。

### `checker.cpp`

ジャッジコード。実行時のコマンドライン引数などの仕様は次の通り。

- `argv[1]`: 入力ファイル
- `argv[2]`: 想定解の出力ファイル
- `argv[3]`: ジャッジ対象の出力ファイル

[testlib](https://github.com/MikeMirzayanov/testlib) を用いて書くことを想定しており、スペシャルジャッジでない場合は https://github.com/MikeMirzayanov/testlib/blob/master/checkers/wcmp.cpp をコピーすれば十分。スペシャルジャッジの場合は https://codeforces.com/blog/entry/18426 などを参考にして書くこと。

インタラクティブジャッジは現時点で非対応。
