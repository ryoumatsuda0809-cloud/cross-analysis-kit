# クロス分析キット（診断エンジン）

外の事実（A軸）と現場の現実（B軸）を、**別々に取って突き合わせ、食い違いから真因の仮説を出す**ための道具一式です。
Claude Code のスキル4段（①market-recon → ②genba-ops → ③shinin-hansho → ④tougou-report）と、
それを正しい順序と隔離で回す `cross-run`、顧客情報を守る `client-data-firewall`、機械の検査とテストが入っています。

## 使い方

1. このフォルダ（`cross-analysis-kit/`）を**単独のフォルダとして**取り出し、そこで Claude Code を開く
   （スキルは `.claude/skills/`、フックは `.claude/settings.json` から読まれる）。
2. 案件は `案件/{コードネーム}/` に置く。**`案件/` は git に入らない**（`.gitignore`）。実名は
   `案件/_社名対応表_ローカル専用.md` にだけ書き、禁止語は `案件/_禁止語_ローカル専用.txt` に並べる。
3. 単独のリポジトリにしたら、コミット前の検査を有効にする：`git config core.hooksPath .githooks`
4. テスト：`python -m pytest -q`（必要なのは Python 3.9 以上と pytest だけ）

## 読む順

1. `CLAUDE.md` … 憲法。なぜそうするか（パイプライン・封・守秘）
2. `CHECK.md` … 場面別チェックリスト。何を確認するか
3. `質の検証.md` … 分析の質をどう測るか

## Windows で使うとき

- Claude Code のフックは `python3` が無ければ `python` を使う。Python 3.9 以上を入れておく。
- 封（`03_仮説_封.md`）の受け渡しはクリップボードを使う（Windows は PowerShell、Mac は pbpaste）。
- `対外資料/_report_build/build.sh`（PDF作成）は Git Bash で動かす。pandoc と Chrome（または Edge）が要る。
- 文字化けを避けるため、環境変数 `PYTHONUTF8=1` を設定しておくと安全。

## 公開版について

元は非公開で運用していたもの。公開にあたり、実在の会社名・地名・個人名・アカウント情報・営業資料・
実走ログ（作業の全記録）を取り除き、事務所名などは `{事務所名}` のような差し込み欄にした。
