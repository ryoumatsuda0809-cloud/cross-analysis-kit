# クロス分析キット（診断エンジン）

外の事実（A軸）と現場の現実（B軸）を、**別々に取って突き合わせ、食い違いから真因の仮説を出す**ための道具一式です。
Claude Code のスキル4段（①market-recon → ②genba-ops → ③shinin-hansho → ④tougou-report）と、
それを正しい順序と隔離で回す `cross-run`、顧客情報を守る `client-data-firewall`、機械の検査とテストが入っています。

## はじめかた

```bash
git clone https://github.com/ryoumatsuda0809-cloud/cross-analysis-kit.git
cd cross-analysis-kit
git config core.hooksPath .githooks   # コミット前の検査（社名・案件の混入を止める）を有効にする
pip install pytest
python -m pytest -q                   # Python 3.9 以上。すべてオフラインで動く
```

そのフォルダで Claude Code を開く（スキルは `.claude/skills/`、フックは `.claude/settings.json` から読まれる）。

**最初の一回だけ**
1. `対外資料/_ブランド定義.md` の `{…}` を埋める。埋めるまで PDF は作られない。
   実在の住所・連絡先を書いたら、そのファイルを公開リポジトリに push しない。
2. `STATUS.md` を自分の状況に書き換える（`CLAUDE.md` が毎回最初に読ませる）。
3. 架空の案件 `案件/_TEST_{名前}/` で ①〜④ を1回通す（`cross-run` スキル）。

## 案件と守秘

- 案件は `案件/{コードネーム}/` に置く。**`案件/` と `診断結果/` は git に入らない**（`.gitignore`）。
- 実名は `案件/_社名対応表_ローカル専用.md` にだけ書き、禁止語は `案件/_禁止語_ローカル専用.txt` に並べる。
  コミット前の検査がこの禁止語でも止める。
- 非公開リポジトリでも、一度 push したものは履歴から消えない。顧客の情報は最初から入れない。

## 出力の見本

`対外資料/デモ_20260919/見本_課題仮説レポート.md` … 架空の会社を例にした ④ の出力（課題仮説レポート）。
PDF にするなら `cd 対外資料/_report_build && ./build.sh ../デモ_20260919/見本_課題仮説レポート.md`。

## 読む順

1. `CLAUDE.md` … 憲法。なぜそうするか（パイプライン・封・守秘）
2. `STATUS.md` … 今どこにいるか（テンプレート）
3. `CHECK.md` … 場面別チェックリスト。何を確認するか
4. `質の検証.md` … 分析の質をどう測るか

## Windows で使うとき

- Claude Code のフックは `python3` が無ければ `python` を使う。Python 3.9 以上を入れておく。
- 封（`03_仮説_封.md`）の受け渡しはクリップボードを使う（Windows は PowerShell、Mac は pbpaste）。
- `対外資料/_report_build/build.sh`（PDF作成）は Git Bash で動かす。pandoc と Chrome（または Edge）が要る。
- 文字化けを避けるため、環境変数 `PYTHONUTF8=1` を設定しておくと安全。

## 公開版について

元は非公開で運用していたもの。公開にあたり、実在の会社名・地名・個人名・アカウント情報・営業資料・
実走ログ（作業の全記録）を取り除き、事務所名などは `{事務所名}` のような差し込み欄にした。
文中の「実走ログ #番号」「移行台帳 §番号」は、その決定が生まれた経緯への参照で、公開版には含まれない。
自分の記録を残すなら、同じ名前の `実走ログ.md` を作って追記していけばよい。
