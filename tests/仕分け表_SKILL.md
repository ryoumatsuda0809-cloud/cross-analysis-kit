# 仕分け表（SKILL.md）｜ 各 SKILL.md の規則を M／G／H に分ける（段9・移行台帳 §10）

> **分母は `tests/skill_units.py` が決める**（箇条書き・表の本文の行・指示の言い回しを含む地の文）。
> SKILL.md の文章が変わって抽出が変わると、`tests/test_rtm.py` が落ちる。行を足す・消す・照合を直す。
> 分類・状態・検査の意味は `tests/仕分け表.md`（CHECK.md 版）と同じ。**`?` は未仕分け。**
> 拾った行が規則でなければ **N**。規則の中身は変えない（ここは仕分けるだけ）。
>
> **数え方（09-27 本人決定・移行台帳 §10）**
> - 1行に規則が2つ以上あれば `12a`・`12b`…に分ける（a から連続・2行以上）。`12a` の照合は本文の頭、`12b` 以降は本文のどこかの語
> - 理由・例・背景は **N**。ほかの行の繰り返しは **R**：メモ欄に `参照：原本 #n`（n は M・G・H の行。別スキルでもよい）
> - **N・R は分母に入らない。**達成率は「済の M ÷ 全 M」。形は `test_rtm.py` の `skill_table_errors` が見る

| # | スキル | 分類 | 状態 | 検査 | 照合 | メモ |
|---|---|---|---|---|---|---|
| 1 | client-data-firewall | N |  |  | 自分の手法・ノウハウ（共有したい | text |
| 2 | client-data-firewall | H |  |  | 「顧客データが混ざっていないか確 | text |
| 3 | client-data-firewall | N |  |  | フォルダ除外だけでは守れない。顧 | text |
| 4 | client-data-firewall | N |  |  | 顧客の診断結果が 案件/ 配下に | list |
| 5 | client-data-firewall | N |  |  | .gitignore に 案件/ | list |
| 6 | client-data-firewall | N |  |  | 確かめたら、まだ漏れていた。 顧 | list |
| 7 | client-data-firewall | N |  |  | 人間の注意力に依存する層は、必ず | text |
| 8 | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a7_anken_is_gitignored` | 1. 場所 ／ .gitigno | table |
| 9 | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a8_2_blocks_banned_word_in_diff` `test_engine_consistency.py::test_a8_3_blocks_leak_in_already_tracked_file` | 2. 内容 ／ コードネーム化＋ | table／禁止語リストにある語だけ |
| 10 | client-data-firewall | M | 済 | `test_check_anken.py::test_repo_check_passes_on_this_repo` `test_engine_consistency.py::test_a8_1_blocks_anken_path` | 3. 機械検査 ／ pre-co | table／配線は check_anken --repo |
| 11 | client-data-firewall | M | 済 | `test_lint_01.py::test_leak_ng_on_tracked_file` | ③を飛ばさない。 ①だけ見て「案 | text／全追跡ファイルを走査（pre-commit 項目3） |
| 12 | client-data-firewall | R |  |  | 細かい線引きをしない。線が細いほ | text／参照：原本 #8 |
| 13 | client-data-firewall | R |  |  | 「private だから追跡して | text／参照：原本 #8 |
| 14 | client-data-firewall | H |  |  | 同期の都合で守秘を緩めない。同期 | text |
| 15 | client-data-firewall | N |  |  | ローカルには顧客情報を全部置いて | text |
| 16 | client-data-firewall | H |  |  | だから消さずに移す。知識を失わな | text |
| 17 | client-data-firewall | G |  |  | ✅「従業員数と厚生年金被保険者数 | table |
| 18 | client-data-firewall | G |  |  | ✅「指定管理者の議事録を当てろ」 | table |
| 19 | client-data-firewall | G |  |  | ✅「DXの空白＝ツールが無い、と | table |
| 20 | client-data-firewall | M | 済 | `test_lint_01.py::test_leak_ng_on_tracked_file` | フック本体は commit され | text／フックも追跡ファイルなので項目3が走査する |
| 21a | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a7_anken_is_gitignored` | 禁止語リストは .gitigno | text／置き場が gitignore 済み |
| 21b | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a8_2_blocks_banned_word_in_diff` | フックがそれを読む | text／フックがリストを読んで止める |
| 22 | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a8_clean_commit_passes` `test_engine_consistency.py::test_a8_2_blocks_banned_word_in_diff` | ガードレールもテストしないと動か | text／Stage 5 のテストA＝A7・B＝clean・C＝A8-2 |
| 23 | client-data-firewall | N |  |  | .gitignore は過去の | text |
| 24 | client-data-firewall | H |  |  | A. 履歴を書き換える ／ gi | table |
| 25 | client-data-firewall | H |  |  | B. リポジトリを作り直す ／ | table |
| 26 | client-data-firewall | H |  |  | C. 何もしない ／ priva | table |
| 27 | client-data-firewall | R |  |  | 守秘と利便を天秤にかけない。 「 | list／参照：原本 #14 |
| 28 | client-data-firewall | R |  |  | 目視を信用しない。 3-15 も | list／参照：原本 #10 |
| 29 | client-data-firewall | R |  |  | 線は太く引く。 細かい例外を作る | list／参照：原本 #8 |
| 30 | client-data-firewall | R |  |  | 消すより移す。 ローカルには全部 | list／参照：原本 #16 |
| 31 | client-data-firewall | H |  |  | --no-verify で迂回し | list |
| 32 | client-data-firewall | M | 済 | `test_engine_consistency.py::test_a7_anken_is_gitignored` | [ ] 案件フォルダは .git | list |
| 33 | client-data-firewall | M | 済 | `test_check_md.py::test_firewall_ng_case_folder_not_in_table` | [ ] 対応表にコードネームを登 | list／候補：案件/ 直下のフォルダ名が対応表のコードネームにあるか（ローカル）／【09-28】案件フォルダ（_ で始まらず 01〜06 のどれかがある）が対応表のフォルダ名にあるか。実物は test_real_firewall_registration（ローカル） |
| 34 | client-data-firewall | M | 済 | `test_check_md.py::test_firewall_ng_real_name_not_banned` `test_check_md.py::test_firewall_ng_number_not_banned` | [ ] 禁止語リストに実名・法人 | list／候補：対応表の実名が禁止語リストにあるか（ローカル）／【09-28】対応表の実名（「架空」の行を除く）に禁止語が1つ以上含まれるか・法人番号・電話番号の値が禁止語リストにあるか。出すのはコード名だけ |
| 35 | client-data-firewall | M | 済 | `test_check_anken.py::test_repo_check_passes_on_this_repo` `test_check_anken.py::test_ng_when_hooks_path_not_set` | [ ] このマシンで core. | list |
| 36 | cross-run | H |  |  | 「診断を最後まで通して」と言われ | text／使いどき |
| 37 | cross-run | N |  |  | 1本の会話では成立しない。 | text |
| 38 | cross-run | N |  |  | 「読まない」は運用ルール。「知ら | text |
| 39 | cross-run | G |  |  | ① 違う盲点 ／ 同じ盲点の2つ | table |
| 40a | cross-run | M | 済 | `test_seal_security.py::test_deny_blocks_seal_paths` | ② 独立に取る ／ 先に見た答え | table／03 の封は deny |
| 40b | cross-run | R |  |  | サブエージェント隔離 | table／参照：原本 #102 |
| 41 | cross-run | R |  |  | ③ 食い違いを潰さない ／ どち | table／参照：原本 #381 |
| 42 | cross-run | R |  |  | ④ 意味は人間が決める ／ 矛盾 | table／参照：原本 #192 |
| 43 | cross-run | N |  |  | AIの仮説を読んでから現場に行っ | text |
| 44 | cross-run | G |  |  | ① market-recon ／ | table／①が作るもの |
| 45 | cross-run | R |  |  | ② genba-ops ／ ✅ | table／参照：原本 #149。★表は 02b 分離前・01i 以前のまま（01 ✅・「02 末尾」）→ 台帳 §4 Z2 |
| 46 | cross-run | R |  |  | ③ shinin-hansho | table／参照：原本 #359 |
| 47 | cross-run | R |  |  | ④ tougou-report | table／参照：原本 #106 |
| 48 | cross-run | H |  |  | 人間 ／ ✅ ／ ✅ ／ 自分で | table／人が現場前に 03 を見ないか |
| 49 | cross-run | N |  |  | settings.json の | text |
| 50 | cross-run | N |  |  | 「③・司令塔だけ読める」という区 | text |
| 51 | cross-run | R |  |  | （実際に起きた。deny を一時 | text／参照：原本 #112 |
| 52 | cross-run | N |  |  | 封（.claude/settin | text |
| 53 | cross-run | N |  |  | 別のフォルダで開くと、何の警告も | text |
| 54 | cross-run | H |  |  | 確認用のファイルは作らない。 存在 | list |
| 55 | cross-run | H |  |  | 「denied by your | list |
| 56 | cross-run | H |  |  | 「存在しない（does not exi | list |
| 57 | cross-run | H |  |  | 案件フォルダの中身を ls して | text／どこから始めるかの判断。足りないものは #53〜#57 の WARN |
| 58 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 何も無い ／ Stage 1（① | table／どの段がまだ回せないかを WARN で出す。次に何をするかは人 |
| 59 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 01〜03 あり、現場メモ無し | table／現場メモが無ければ ② の WARN。止まったかは人 |
| 60 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 現場メモあり、04 無し ／ S | table／04 が無ければ ③ の WARN |
| 61 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 04 あり、05 無し ／ St | table／05 が無ければ ④ の WARN |
| 62 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 05 あり、06 無し ／ St | table／06 の有無は READERS に無い。05 があれば ④ の WARN が消える |
| 63 | cross-run | R |  |  | 現場メモが無いのに②以降を回さな | text／参照：原本 #59 |
| 64 | cross-run | H |  |  | NG が1件でも出たら、どの段も | text／起動したかは痕跡が残らない。NG の検出は #60 |
| 65 | cross-run | M | 済 | `test_check_anken.py::test_duplicate_number_is_ng` `test_check_anken.py::test_banned_vocabulary_is_ng` `test_check_anken.py::test_quarantine_folder_inside_anken_is_ng` `test_check_anken.py::test_missing_reader_file_is_warn` | 同一案件内の番号重複／禁止語彙（ | text／4つとも check_anken |
| 66 | cross-run | N |  |  | 文章のルールは読まれなければ効か | text |
| 67 | cross-run | M | 済 | `test_check_anken.py::test_duplicate_detected_through_any_prefix` `test_check_anken.py::test_chained_prefix` `test_check_anken.py::test_chained_prefix_duplicate_is_ng` | 番号重複の検査は接頭辞の一覧に依 | text／既知の穴 Z7：_a_b_ のように連なる接頭辞は剥がせない（xfail）／【09-29 Z7 を直した → 済】連なる接頭辞も剥がす。実案件の check_anken の出力は直す前と1字も変わらない |
| 68 | cross-run | N |  |  | ③を起動する前に、必ず次の2つを | text／前置き |
| 69 | cross-run | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | ls 案件/{社名}/04_現場 | list／③ の WARN（CHECK #55） |
| 70a | cross-run | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_row_missing` `test_check_genba_mark.py::test_ng_when_filled_but_shapeless` `test_anken_outputs.py::test_real_anken_scripts` | python3 check_ge | list／CHECK #56 |
| 70b | cross-run | M | 済 | `test_check_genba_ref.py::test_ng_when_cited_line_missing_or_untagged` `test_check_genba_ref.py::test_ng_when_role_differs_from_memo` `test_check_genba_ref.py::test_ng_when_role_count_differs` `test_anken_outputs.py::test_real_anken_scripts` | ②の後は python3 check_genba_ref | list／【09-29 追加】実走 #58 の対策 (b)。NG なら③を起動しないは #66（R→#59） |
| 71 | cross-run | R |  |  | NG が出たら③を起動しない。出 | text／参照：原本 #64 |
| 72 | cross-run | H |  |  | ①だけあれば②を起動してよい、と | text／出所の妥当性は人。4印の形は #65 |
| 73 | cross-run | N |  |  | （②はメモの中身を分析するだけで | text |
| 74 | cross-run | M | 済 | `test_check_anken.py::test_quarantine_folder_inside_anken_is_ng` `test_check_md.py::test_archive_rules` `test_check_md.py::test_real_archive_state` | 案件/_使わない/{案件名}_{ | list／中に作らないは check_anken、名前の形は R115 |
| 75 | cross-run | M | 済 | `test_check_anken.py::test_quarantine_folder_inside_anken_is_ng` | 案件フォルダの中に隔離フォルダを | text |
| 76 | cross-run | N |  |  | 同じ案件の中に2つできる。人もA | text |
| 77 | cross-run | M | 済 | `test_check_md.py::test_archive_rules` `test_check_md.py::test_real_archive_state` | 中は平らにする。 _材料/B_現 | list／R116 |
| 78 | cross-run | M | 済 | `test_check_anken.py::test_banned_vocabulary_is_ng` `test_check_md.py::test_archive_rules` | 接頭辞は付けない。 _保留_ _ | list／案件の中は check_anken、_使わない/ の中は R117 |
| 79 | cross-run | N |  |  | 場所で表す。名前で表さない。 名 | text |
| 80 | cross-run | M | 済 | `test_check_md.py::test_archive_rules` `test_check_md.py::test_real_archive_state` | _なぜ使わないか.md に、何を | list／R118。有無だけ。何を書いたかは人 |
| 81 | cross-run | H |  |  | その場でチャットに全件報告する。 | list／チャットは機械から見えない |
| 82 | cross-run | H |  |  | 捨てない。 比較すると直すべき箇 | text／消したかは痕跡が残らない |
| 83 | cross-run | M | 済 | `test_check_anken.py::test_duplicate_number_is_ng` `test_check_anken.py::test_banned_vocabulary_is_ng` | 更新したら上書きする。前と今を両 | text／同じ番号が2つ・_旧_ などの語だけ |
| 84 | cross-run | H |  |  | 上書きしない例外は3つだけ： 0 | text／案件は git の外で上書きの履歴が無い。seal_guard は封への書き込みは止めない |
| 85 | cross-run | M | 済 | `test_engine_consistency.py::test_no_backup_files_in_engine` | エンジン側（.claude/ 等 | text／候補：追跡ファイルに .bak が無い／【09-28】リポジトリ（案件/・診断結果/・.git/ を除く）に .bak・.orig・.old・~ が無いか |
| 86 | cross-run | N |  |  | ①は最初の段なので、汚染される先 | text |
| 87 | cross-run | N |  |  | 終わったら必ず2つやる： | text／前置き |
| 88 | cross-run | M | 済 | `test_check_md.py::test_r15_ng_without_source_log` `test_check_md.py::test_real_case_state` | _材料/A_公開/取得ログ_{日 | list／R15。有無だけ（CHECK #15） |
| 89 | cross-run | M | 済 | `test_check_md.py::test_r31_ng_when_not_frozen_after_site` `test_check_md.py::test_real_case_state` | 01 に凍結宣言を書く | list／R31。現場の後なら（CHECK #31） |
| 90 | cross-run | N |  |  | もうA軸ではない。01 に追記し | text |
| 91 | cross-run | N |  |  | 03 を作った直後の報告で、ほぼ | text |
| 92 | cross-run | H |  |  | 01 の要点（事実のみ） | list／報告してよいもの。チャットは機械から見えない |
| 93 | cross-run | H |  |  | 02 の問いの本数と分野 | list |
| 94 | cross-run | H |  |  | 取れなかったもの・埋まらなかった | list |
| 95 | cross-run | H |  |  | 03 は「n件作成した（未開封） | list |
| 96 | cross-run | H |  |  | 報告を読む本人（＝ほとんどの場合 | table／チャットは機械から見えない |
| 97 | cross-run | H |  |  | 報告を読まない別人 ／ 件数＋タ | table |
| 98 | cross-run | N |  |  | ❌ 禁止例（実際に起きたもの） | text |
| 99 | cross-run | N |  |  | ❌「DXの空白という見立てを否定 | list／例 |
| 100 | cross-run | N |  |  | ❌「1件否定、2件削除、1件強化 | list／例 |
| 101 | cross-run | N |  |  | ❌「◯◯比率◯◯%という実数で根 | list／例 |
| 102 | cross-run | H |  |  | 自分で 04/05/06 を書か | text／誰が書いたかは成果物に残らない |
| 103 | cross-run | N |  |  | 渡すときは以下を必ず守る： | text／前置き |
| 104 | cross-run | M | 済 | `test_engine_consistency.py::test_a1_readers_match_cross_run_table` `test_seal_security.py::test_deny_blocks_seal_paths` | ② genba-ops ／ 01 | table／表と READERS の一致（A1）・03/02b は deny。実際に渡したかは人 |
| 105 | cross-run | M | 済 | `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | ③ shinin-hansho | table／表と READERS の一致（A1）。埋め込みは #109 |
| 106 | cross-run | M | 済 | `test_engine_consistency.py::test_a1_readers_match_cross_run_table` `test_seal_security.py::test_deny_blocks_seal_paths` | ④ tougou-report | table／表と READERS の一致（A1）・03 は deny |
| 107 | cross-run | N |  |  | 01 は現場で相手に見せる紙であ | text |
| 108 | cross-run | N |  |  | 「公式サイトには記載がありません | text |
| 109a | cross-run | H |  |  | 各段が終わったら、報告に含まれる | text／受け取ったかは痕跡が残らない |
| 109b | cross-run | H |  |  | ②の後は、③の前に毎回 B-1 | text／【09-29 追加】照合は意味の判断（LLM の検証役）でコードでは決まらない（実走 58-3）。表は 08 に残るが、③の前に走らせたかはファイルから決まらない |
| 109c | cross-run | H |  |  | 1件でもあれば③を起動せず | text／【09-29 追加】起動したかは痕跡が残らない（#59 と同じ） |
| 110 | cross-run | N |  |  | をファイルパスで渡して「読んでく | text |
| 111 | cross-run | N |  |  | この deny はエージェントの | text |
| 112 | cross-run | H |  |  | settings.json は本 | text／誰が編集したかは残らない（check_seal が書かないことは #137） |
| 113 | cross-run | R |  |  | ②が完了していることを必ず確認し | list／参照：原本 #69 |
| 114 | cross-run | H |  |  | 受け取った中身の見出しの案件名が、今回の案件と一 | list／プロンプトは成果物に残らない |
| 115 | cross-run | H |  |  | ③のサブエージェントには、03/ | list／プロンプトは成果物に残らない |
| 116 | cross-run | R |  |  | 埋め込まれたテキストとして受け取 | text／参照：原本 #115 |
| 117 | cross-run | H |  |  | 司令塔（あなた）が 03/02b | text |
| 118 | cross-run | R |  |  | ③に渡した後、必要以上にその内容 | text／参照：原本 #117 |
| 119 | cross-run | G |  |  | うまくいった話は要らない。詰まっ | list |
| 120 | cross-run | M | 済 | `test_engine_consistency.py::test_log_categories_are_the_seven` | 分類を付ける：スキルの穴／テンプ | list／候補：実走ログの各項目に7分類のどれかがある／【09-28】実走ログの詰まりの表（# ｜分類）で分類が7つのどれかを含むか。2列の「分類｜内容」表と箇条書きは分類の欄が無いので見ない。7分類の外を使った過去の6件（#27・#28・#52・#53・#56・#57）は KNOWN_LOG（追記専用のため書き換えない） |
| 121 | cross-run | G |  |  | 直さないと決めたものも書く。 ❌ | list |
| 122 | cross-run | G |  |  | 配管として正しく動いたことも短く | list |
| 123 | cross-run | N |  |  | 出力を読んで、以下を実際に確かめ | text／前置き |
| 124 | cross-run | R |  |  | [ ] 04 §0 に独立性の宣 | list／参照：原本 #189 |
| 125 | cross-run | R |  |  | [ ] 05 §0 に開封記録が | list／参照：原本 #364 |
| 126 | cross-run | M | 済 | `test_check_report.py::test_ng_on_each_internal_word` `test_anken_outputs.py::test_b35_ng_when_rejected_hypothesis_in_06` | [ ] 06 に棄却された仮説が | list／棄却の特徴語（内部語）だけ（CHECK #103）。言い換えは人／【09-28 再点検】「棄却の特徴語」＝棄却した仮説の語。05 で棄却した仮説の文言が 06 にそのまま載っていないかは見ていない（CHECK #75）／【09-28 B35】05 §3 で棄却した仮説の文言が 06 本文にそのまま無いか（B7 と同じ下限。言い換えは人） |
| 127 | cross-run | G |  |  | [ ] 06 の「要検証」が結論 | list／問いに回っているかは意味を読む |
| 128 | cross-run | H |  |  | [ ] ①だけでも②だけでも出な | list／クロスが成立したかは人の判断 |
| 129 | cross-run | H |  |  | 各段の検査だけでは捕まらない。 | text／③の申告が④でどう扱われたかは意味を読む |
| 130 | cross-run | R |  |  | ④でどう扱われているかを、必ず目 | text／参照：原本 #129 |
| 131 | cross-run | G |  |  | 不明は「不明」と書く。 推測で埋 | list |
| 132 | cross-run | M | 一部 | `test_check_report.py::test_ng_on_each_assertive_word` | 断定しない。「〜の可能性」「〜と | list／06 の断定語だけ。04・05 は見ていない |
| 133 | cross-run | R |  |  | 一般論を証拠にしない。 業界パッ | list／参照：原本 #184 |
| 134 | cross-run | R |  |  | 最終判断はAIがしない。 ③は格 | list／参照：原本 #346 |
| 135 | cross-run | R |  |  | 食い違いは方向とは限らない。 実 | list／参照：原本 #371 |
| 136 | cross-run | N |  |  | （実走ログ 3-28）。「①がX | text |
| 137 | cross-run | R |  |  | 現場メモを外部検索・外部モデルに | list／参照：原本 #197 |
| 138 | cross-run | R |  |  | 04 に生の逐語・個人名を書かな | list／参照：原本 #201 |
| 139 | cross-run | G |  |  | 顧客の実数を、スキル・業界パック | list／禁止語リストは実数を止めない |
| 140 | cross-run | R |  |  | 案件フォルダを git で追跡し | list／参照：原本 #8 |
| 141 | cross-run | N |  |  | assets/subagent- | table／案内 |
| 142 | cross-run | M | 済 | `test_seal_security.py::test_check_seal_does_not_write_settings` `test_seal_security.py::test_check_seal_is_wired_into_pre_commit` | check_seal.py（リポ | table／外す／戻すをしない・毎回（pre-commit） |
| 143 | cross-run | R |  |  | check_genba_mark | table／参照：原本 #70a。★#65 は「③の前」、ここは「②の前」→ 台帳 §4 Z3 |
| 144 | cross-run | N |  |  | client-data-fire | table／案内 |
| 145 | cross-run | N |  |  | 実走ログ.md ／ 詰まりの記録 | table／案内 |
| 146 | cross-run | N |  |  | CLAUDE.md §3-1 ／ | table／案内 |
| 147 | genba-ops | H |  |  | 「現場メモを分析して」「なぜこう | text／使いどき |
| 148a | genba-ops | H |  |  | 市場調査・公開情報スキャンはこの | text／market-recon の仕事をしない |
| 148b | genba-ops | R |  |  | 現場でしか分からないことをAIが断定せず | text／参照：原本 #161 |
| 148c | genba-ops | R |  |  | 現場で確認すべき点を必ず分ける | text／参照：原本 #192 |
| 149 | genba-ops | M | 済 | `test_seal_security.py::test_deny_blocks_seal_paths` `test_hooks.py::test_seal_guard_blocks` | 03_仮説_封.md は絶対に読 | text／deny と seal_guard が開かせない（CHECK #47） |
| 150 | genba-ops | N |  |  | ②は、①とは独立した2つ目の情報 | text |
| 151 | genba-ops | N |  |  | 2つあるように見えて実は1つにな | text |
| 152 | genba-ops | G |  |  | だから②は、①の仮説を裏付けも反 | text |
| 153 | genba-ops | N |  |  | 見てよいものと、見てはいけないも | text |
| 154 | genba-ops | N |  |  | 01i（事実・建前・市場＝定規） | list／★#159 と食い違い（01 は読まない）→ 台帳 §8 |
| 155 | genba-ops | N |  |  | AIの推論ではない。事実を共有し | text |
| 156 | genba-ops | N |  |  | 02（問い）＝見てよい。 問いは | list |
| 157 | genba-ops | R |  |  | 03（AIの仮説）＝絶対に見ない | list／参照：原本 #149 |
| 158 | genba-ops | M | 済 | `test_seal_security.py::test_deny_blocks_seal_paths` `test_hooks.py::test_seal_guard_blocks` | 02b_主任診断士の見立て_封. | list／02b も同じ deny |
| 159 | genba-ops | N |  |  | 以前は 02 の末尾に見立てが同 | text |
| 160 | genba-ops | R |  |  | → 02b として分離済み。02 | text／参照：原本 #158 |
| 161 | genba-ops | G |  |  | 最重要：現場でしか分からないこと | text |
| 162 | genba-ops | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 必須①：現場メモ（ヒアリングシー | list／置き場所だけ（CHECK #35） |
| 163 | genba-ops | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 必須②：案件/{会社名}/01i | list／読む先の一覧は cross-run と一致 |
| 164 | genba-ops | H |  |  | 01_外形カード_事実編.md（ | text／deny は 01 を止めない。読んだかは痕跡が残らない |
| 165 | genba-ops | N |  |  | 任意：案件/{会社名}/02_現 | list |
| 166 | genba-ops | N |  |  | 任意：対象業界の業界パック .. | list |
| 167 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_row_missing` `test_check_genba_mark.py::test_ng_when_mark_empty` | 話者 ／ 分かる範囲の役職・氏名 | table／話者は空でないかだけ |
| 168 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_row_missing` `test_check_genba_mark.py::test_ng_when_filled_but_shapeless` | いつ ／ 日時 ／ 2026-0 | table |
| 169 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_row_missing` `test_check_genba_mark.py::test_ng_when_filled_but_shapeless` | どこで ／ 現地に入ったか、遠隔 | table |
| 170 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_row_missing` `test_check_genba_mark.py::test_ng_when_filled_but_shapeless` | 誰から ／ 誰を経由して聞いたか | table |
| 171 | genba-ops | N |  |  | Zoom通話は「現地か遠隔か」＝ | text |
| 172a | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_empty` `test_anken_outputs.py::test_real_anken_scripts` | 4つとも埋まっていなければ、_材 | list |
| 172b | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_body_line_has_no_role` `test_check_genba_mark.py::test_ng_when_plain_answer_line_has_no_role` | 本文の各行の頭に【役割】 | list／【09-29 追加】実走 #58 の対策 (b)。役割が名前でないかは人が見る |
| 173 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_filled_but_shapeless` | この検査は「欄が空でないか」では | list |
| 174 | genba-ops | M | 済 | `test_check_genba_mark.py::test_ng_when_mark_empty` `test_check_genba_mark.py::test_unknown_without_reason_is_note_not_ng` | 分からない場合は空欄にせず「不明 | list／理由なしの「不明」は NOTE（止めない） |
| 175 | genba-ops | R |  |  | 「不明」と明記すること自体はよい | text／参照：原本 #174 |
| 176 | genba-ops | N |  |  | この4印は現場メモの出所を確認す | list |
| 177 | genba-ops | R |  |  | 案件/{会社名}/03_仮説_封 | text／参照：原本 #149 |
| 178 | genba-ops | M | 済 | `test_seal_security.py::test_every_seal_file_on_disk_is_denied` `test_seal_security.py::test_deny_blocks_seal_paths` | 存在しても開かない。_封 で終わ | text |
| 179 | genba-ops | M | 済 | `test_anken_outputs.py::test_b30_ng_when_no_02_and_not_stated` `test_anken_outputs.py::test_b30_ok_when_no_02_stated` `test_anken_outputs.py::test_b30_not_applied_when_02_exists` `test_anken_outputs.py::test_b30_stated_only_in_comment_is_missing` | 02 が無い（飛び込み・紹介・既 | table／B30：02 が無い案件の 04 カバレッジ節に「02 なし」（内部メモの中だけは書いたことにならない） |
| 180 | genba-ops | M | 済 | `test_check_anken.py::test_01i_falls_back_to_01_with_note` | 01i が無い（#14〈定規化〉 | table |
| 181 | genba-ops | M | 済 | `test_check_md.py::test_r111_ng_when_fallback_not_declared` `test_check_md.py::test_real_case_state` | ただし 04 の冒頭に「定規は | text／R111。「代用」の語だけ |
| 182 | genba-ops | M | 済 | `test_anken_outputs.py::test_b31_ok_when_stated_and_no_rows` `test_anken_outputs.py::test_b31_ng_when_not_stated` `test_anken_outputs.py::test_b31_ng_when_diff_rows_exist` `test_anken_outputs.py::test_b31_quote_is_not_a_statement` `test_anken_outputs.py::test_b31_applied_only_when_both_missing` | 01 も 01i も無い ／ 進 | table／B31：01 も 01i も無い案件の 04 に「01 … 無い／なし」の本文行があり、建前のズレ表に行が無い（「### 市場ベンチマークとのズレ」の表は見ない＝狭い方の読み）。実物が無いので合成でだけ確認 |
| 183 | genba-ops | G |  |  | 業界パックが無い業種 ／ パック | table／パックの有無は業種の判断が要る（CHECK #49） |
| 184 | genba-ops | G |  |  | パックは"勘所"であって"正解" | text |
| 185 | genba-ops | G |  |  | 「対外的にこう言っている」と「現 | list |
| 186 | genba-ops | M | 済 | `test_anken_outputs.py::test_b2_ng` | 市場平均とのズレ（現場の数字が業 | list／ベンチマーク表の「状態」欄の形だけ（B2） |
| 187 | genba-ops | M | 済 | `test_anken_outputs.py::test_b10_ng_on_new_tag` `test_engine_consistency.py::test_a3_fixed_tags_same_everywhere` `test_anken_outputs.py::test_b38_ng_when_tag_cell_empty` | 各項目に固定タグを付ける：#市場 | list／B10・A3／【09-28 再点検】「各項目に付ける」＝タグ列が空の行が無いかは見ていない（B10 は付いたタグが固定の5つかだけ）／【09-28 B38】タグ列のある表で、中身のある行のタグ列が空でないか |
| 188 | genba-ops | R |  |  | ①のAI仮説とは突き合わせない。 | text／参照：原本 #152 |
| 189 | genba-ops | M | 済 | `test_anken_outputs.py::test_b1_ng` | テンプレの §0「独立性の宣言」 | text／形だけ（CHECK #48） |
| 190a | genba-ops | M | 済 | `test_anken_outputs.py::test_b3_ng` `test_anken_outputs.py::test_b38_ng_when_tag_cell_empty` | 真因の芽リスト（各項目に根拠＝現 | list／強度と役割数の形だけ（B3）。根拠の中身は人／【09-28 再点検】「タグ付き」（各行のタグ列が空でない）は見ていない（#182）／【09-28 B38】各行のタグ列が空でないか |
| 190b | genba-ops | R |  |  | タグ付き | list／参照：原本 #187 |
| 190c | genba-ops | M | 済 | `test_check_genba_ref.py::test_ng_when_cited_line_missing_or_untagged` `test_check_genba_ref.py::test_ng_when_role_differs_from_memo` `test_check_genba_ref.py::test_ng_when_role_count_differs` | 根拠は 【役割】L行番号 | list／【09-29 追加】実走 #58 の対策 (b)。「推測で補わない」は引いた行の印と合うかまで。意味の広げ方は B-1（cross-run #104b） |
| 191a | genba-ops | M | 済 | `test_anken_outputs.py::test_b2_ng` | 建前と現場のズレ一覧（01i§2の | list／ズレ表の「同じものを測っているか」の形だけ（B2） |
| 191b | genba-ops | M | 済 | `test_check_genba_ref.py::test_ng_when_sec2_fact_has_no_line_number` `test_check_genba_ref.py::test_ng_when_cited_line_missing_or_untagged` `test_check_genba_ref.py::test_ng_when_role_differs_from_memo` `test_check_genba_ref.py::test_ng_when_role_count_differs` | 現場の事実にも 【役割】L行番号 | list／【09-29 追加】実走 #58 の対策 (b) |
| 192 | genba-ops | M | 済 | `test_anken_outputs.py::test_b15_ng` | 人間が現場で確認すべき点（現場メ | list／B15：04 に節があり、本文か表に中身がある |
| 193 | genba-ops | M | 済 | `test_anken_outputs.py::test_b15_ng` `test_anken_outputs.py::test_b15_ok_when_no_02` | カバレッジ（02 の問いのうち、 | list／B15：問い番号が1つでもあるか「02 なし」 |
| 194 | genba-ops | N |  |  | 開封して突き合わせるのは③の仕事 | text |
| 195 | genba-ops | R |  |  | 現場を最優先。AIは断定しない。 | list／参照：原本 #161 |
| 196 | genba-ops | G |  |  | 事実（誰がいつ言ったか）と仮説を | list |
| 197 | genba-ops | H |  |  | 守秘①：外に出さない。 現場メモ | list／外部に流したかは成果物に残らない |
| 198 | genba-ops | G |  |  | 守秘②：04 に生の文言をそのま | list／逐語かは読まないと分からない（CHECK #54） |
| 199 | genba-ops | N |  |  | private は「漏れない」保 | text |
| 200 | genba-ops | G |  |  | 書いてよい：要約・一般化した事実 | list |
| 201 | genba-ops | G |  |  | 書かない：個人名、生の愚痴の逐語 | list |
| 202 | genba-ops | M | 済 | `test_engine_consistency.py::test_a7_anken_is_gitignored` | 現場メモの原本（音声・逐語）は | list／★置き場が CLAUDE.md §3（_材料/B_現場/）と違う → 台帳 §8 |
| 203 | genba-ops | R |  |  | 重みづけに必要なのは「誰が」では | list／参照：原本 #201 |
| 204 | genba-ops | R |  |  | 業界パックを盲信しない。 現場が | list／参照：原本 #184 |
| 205 | genba-ops | R |  |  | 03_仮説_封.md を開かない | list／参照：原本 #149 |
| 206 | genba-ops | N |  |  | ここを破ると、AIの見立てを確認 | text |
| 207 | genba-ops | R |  |  | ①の仮説を裏付けも反証もしない。 | list／参照：原本 #152 |
| 208 | market-recon | H |  |  | 「○○社を調べて／診断して」「こ | text／使いどき |
| 209 | market-recon | R |  |  | 現場の声・気持ち・暗黙のルールは | text／参照：原本 #338 |
| 210 | market-recon | R |  |  | 現場の生々しい現実（愚痴・属人化 | text／参照：原本 #338 |
| 211 | market-recon | N |  |  | つまり——AIが立てた「真因仮説 | text |
| 212 | market-recon | N |  |  | AIの見立てを確認しに行くだけの | text |
| 213 | market-recon | M | 済 | `test_check_md.py::test_r18_ng_on_empty_mark_cell` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 01i_外形カード_内部用.md | table／3印の空欄（R18-01i）と読む先の一覧。食い違いを生のまま残したかは人 |
| 214 | market-recon | G |  |  | 01_外形カード_事実編.md | table |
| 215 | market-recon | G |  |  | 02_現場で確認すべき問い.md | table |
| 216 | market-recon | R |  |  | 03_仮説_封.md ／ ギャッ | table／参照：原本 #48 |
| 217 | market-recon | N |  |  | 問いを先に渡してよい理由：問いは | text |
| 218 | market-recon | N |  |  | むしろ何を聞けばいいかが分かって | text |
| 219 | market-recon | G |  |  | この分割を「1枚にまとめた方が親 | text |
| 220 | market-recon | H |  |  | 必須：対象企業の正式名称（あれば | list／入力 |
| 221 | market-recon | N |  |  | 任意：業種・所在地・業界パックの | list |
| 222 | market-recon | R |  |  | 現場メモ・ヒアリング内容は入力と | text／参照：原本 #338 |
| 223 | market-recon | H |  |  | 公式サイト・会社概要 ／ 事業内 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 224 | market-recon | H |  |  | 法人情報（gBizINFO／法人 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 225 | market-recon | H |  |  | 行政の委員会・審議会の議事録／公 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 226 | market-recon | H |  |  | 採用ページ・求人サイト ／ 募集 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 227 | market-recon | H |  |  | 口コミ（転職会議・Googleレ | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 228 | market-recon | H |  |  | プレスリリース・ニュース ／ 直 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 229 | market-recon | H |  |  | SNS・ブログ ／ 発信のトーン | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 230 | market-recon | H |  |  | 業界統計・団体（e-Stat／R | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 231 | market-recon | H |  |  | 競合 ／ 同業上位・近隣競合の打 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 232 | market-recon | H |  |  | それでも確定できなければ憶測で1 | text |
| 233 | market-recon | H |  |  | 法人運営の対象は公的法人DBを必 | text／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 234 | market-recon | H |  |  | 対象が行政と契約関係にあるなら、 | text／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 235 | market-recon | N |  |  | 地方の中小企業では該当することが | text |
| 236 | market-recon | H |  |  | 選定結果 ／ {自治体名} {施 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 237 | market-recon | H |  |  | 議事録 ／ {自治体名} {施設 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 238 | market-recon | H |  |  | 事業計画 ／ {自治体名} {施 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 239 | market-recon | H |  |  | 監査 ／ {自治体名} 指定管理 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 240 | market-recon | H |  |  | 委員の質問と、経営者の回答が噛み | list／着眼点 |
| 241 | market-recon | H |  |  | 経営者が「課題」として自ら口にし | list／着眼点 |
| 242 | market-recon | H |  |  | 数字（来場者・従業員・離職率・収 | list／着眼点 |
| 243 | market-recon | H |  |  | 会計の建て付け（按分・区分経理） | list／着眼点 |
| 244 | market-recon | N |  |  | 注意：議事録は「その人がそう述べ | text |
| 245 | market-recon | G |  |  | 01 に書くときは 「〜と述べて | text |
| 246 | market-recon | H |  |  | 順序を逆にしない（2026-09 | text／作った順は痕跡が残らない（上書きで更新日時が変わる） |
| 247 | market-recon | N |  |  | 以下の「定規」の基準は 01i | text |
| 248 | market-recon | N |  |  | 法人番号は絶対に正しいが、現場の | text |
| 249 | market-recon | N |  |  | 最重要の読者は ② genba- | text |
| 250 | market-recon | N |  |  | カードが弱ければ、②はズレを見つ | text |
| 251 | market-recon | N |  |  | 「入場券になる」「現場の30分を | text |
| 252 | market-recon | N |  |  | 定規の品質基準が入っているのはこ | text |
| 253 | market-recon | G |  |  | A｜同定 ／ 誰の話か確定させる | table |
| 254 | market-recon | M | 済 | `test_check_md.py::test_r21_ng_when_other_section_thicker` `test_check_md.py::test_real_case_state` | B｜定規 ／ 会社が外に向かって | table／R21（CHECK #21） |
| 255 | market-recon | G |  |  | C｜文脈 ／ 市場・競合・業界の | table |
| 256 | market-recon | R |  |  | D｜見立て ／ 「〜の可能性があ | table／参照：原本 #258 |
| 257 | market-recon | G |  |  | 「〜である」〔出典〕　2. 「〜 | list |
| 258 | market-recon | M | 済 | `test_lint_01.py::test_ng_on_each_judgement_word` | 禁止：「可能性がある」「〜と思わ | text／ここに並ぶ語形は lint_01 の一覧に全部ある |
| 259 | market-recon | M | 済 | `test_lint_01.py::test_ng_on_each_internal_word` | 「実態」という語を 01 で使わ | text／CHECK #17 |
| 260 | market-recon | G |  |  | 議事録の節の見出しは 「逃げられ | text／「実態」の語は #254 |
| 261 | market-recon | M | 済 | `test_lint_01.py::test_template_01_has_no_work_notes_above_split` | だからテンプレ本体に作業説明を書 | text／候補：01-facts-template.md の切り離し線から上に lint_01 の内部語が無い／【09-28】01 テンプレの切り離し線から上に、SKILL の「載せない」語（定規・3分類・文末・自己チェック・判定）・lint_01 の語・内部メモが無いか |
| 262 | market-recon | R |  |  | 相手に見せる4つの節と、参考にし | table／参照：原本 #261 |
| 263 | market-recon | R |  |  | 社内メモ（切り離し線の下） ／ | table／参照：原本 #287 |
| 264 | market-recon | M | 済 | `test_lint_01.py::test_ng_on_each_internal_word` | 言葉も相手が読む前提で選ぶ。「自 | text／「自己申告」 |
| 265 | market-recon | H |  |  | 口コミ・元社員の投稿は会社の発信 | text |
| 266 | market-recon | M | 済 | `test_lint_01.py::test_ng_when_three_column_header_missing` `test_check_md.py::test_r18_ng_on_empty_mark_cell` | 出典 ／ どこに書いてあったか | table／見出しは lint_01、各行のセルは R18（CHECK #18） |
| 267 | market-recon | M | 済 | `test_check_md.py::test_r18_ng_on_empty_mark_cell` `test_check_md.py::test_r18k_ng_on_kind_outside_five` | 種類 ／ 種類 ／ 貴社の発信／ | table／空欄だけ。値が5つのどれかは見ていない／【09-28 R18k】01 の種類が5つの1つか「不明」（値が不明の行は「—」も可） |
| 268 | market-recon | M | 済 | `test_check_md.py::test_r18_ng_on_empty_mark_cell` `test_check_md.py::test_r18_fumei_is_filled` `test_check_md.py::test_r18t_ng_on_not_year_month` | 時点 ／ いつの情報か ／ 年月 | table／空欄だけ。年月の形は見ていない／【09-28 R18t】01 のいつが年月（西暦・和暦）か「不明」 |
| 269 | market-recon | N |  |  | ②③はこの順序で証拠の重さを読む | text |
| 270 | market-recon | N |  |  | 違うのは時点と申告先だけだった。 | text |
| 271 | market-recon | G |  |  | どれか1つに決めない。01i の | text／食い違いがあるかは読まないと分からない |
| 272 | market-recon | N |  |  | 気づかなければ、その会社の被保険 | text |
| 273 | market-recon | M | 済 | `test_check_md.py::test_s267_ng_on_empty_or_dash` `test_check_md.py::test_s267_ng_without_reason` `test_check_md.py::test_real_case_state` | 法人番号が特定できなければ 「不 | list／S267。13桁か「不明・未特定・特定できませんでした」（01 の敬語。表記の揺れは通す）。理由の行があるか（01 は社内メモ）まで。理由の中身は人 |
| 274 | market-recon | M | 済 | `test_check_md.py::test_r19_ng_when_gbiz_source_filled` `test_check_md.py::test_r19_ng_when_public_db_count_filled` `test_check_md.py::test_real_case_state` | 法人番号が未特定なら、gBizI | list／R19（CHECK #19 と同じ検査） |
| 275 | market-recon | M | 済 | `test_check_md.py::test_s269_ng_without_todo_or_without_address` `test_check_md.py::test_s269_todo_above_split_line_does_not_count` `test_check_md.py::test_real_case_state` | 社内メモの TODO に「法人番 | list／S269。「次にどこを見るか」の列がある表に、項目が法人番号で「所在地」を含む行（01 は社内メモ・01i は §5-2） |
| 276 | market-recon | H |  |  | 質疑のある場 ／ 委員会・審議会 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 277 | market-recon | H |  |  | 質疑のない届出 ／ 県・市の認定 | table／情報源・探し方。当てたかは取得ログを読まないと分からない |
| 278 | market-recon | N |  |  | 理念・製品一覧からは定規が1行も | text |
| 279 | market-recon | N |  |  | 母集団の選び方が §2 の厚さを | text |
| 280 | market-recon | M | 一部 | `test_lint_01.py::test_ng_on_each_judgement_word` | [ ] 見立てが1行も入っていな | list／CHECK #16 と同じ。「課題」「弱い」単体は見ない |
| 281 | market-recon | R |  |  | [ ] 「実態」「自己申告」とい | list／参照：原本 #259 |
| 282 | market-recon | R |  |  | [ ] 全ての行に どこに／種類 | list／参照：原本 #266 |
| 283 | market-recon | R |  |  | [ ] 法人番号が未特定なら、g | list／参照：原本 #274 |
| 284 | market-recon | R |  |  | [ ] 数字が食い違ったとき、ど | list／参照：原本 #271 |
| 285 | market-recon | R |  |  | [ ] §2 が一番厚いか | list／参照：原本 #254 |
| 286 | market-recon | M | 済 | `test_lint_01.py::test_warn_when_section4_nearly_empty` | [ ] §4（分からなかったこと | list／CHECK #23 |
| 287 | market-recon | M | 済 | `test_lint_01.py::test_ng_on_code_name` `test_lint_01.py::test_ng_on_each_internal_word` | [ ] 切り離し線から上だけを読 | list／コード名・内部語だけ。評価・狙いは人（CHECK #25） |
| 288 | market-recon | H |  |  | [ ] 各行を1つずつ見て「これ | list |
| 289 | market-recon | R |  |  | 事実／仮説の弁別は「出典が付くか | list／参照：原本 #266 |
| 290 | market-recon | G |  |  | 埋まらない項目は 2つに割る（1 | list |
| 291 | market-recon | G |  |  | 「不明（非公開）」を 02 の問 | list |
| 292 | market-recon | N |  |  | 流し込むと 02 が穴埋めリスト | text |
| 293 | market-recon | G |  |  | 「建前」はその会社がそう発信して | list |
| 294 | market-recon | R |  |  | ## ここはC（文脈）。ズレの根 | text／参照：原本 #255 |
| 295 | market-recon | N |  |  | 一般論を定規にすると、出てくるの | text |
| 296 | market-recon | N |  |  | CLAUDE.md §4-3「一 | text |
| 297 | market-recon | G |  |  | 市場規模・成長/縮小トレンド（出 | list |
| 298 | market-recon | G |  |  | この会社の市場内ポジション（事実 | list |
| 299 | market-recon | G |  |  | 同一商圏・同一自治体内の競合（実 | list |
| 300 | market-recon | N |  |  | ズレの根拠に使わないものを、相手 | text |
| 301 | market-recon | H |  |  | 「答えを示唆する問い」になってし | text／02 を 03 より先に書いたかは痕跡が残らない |
| 302 | market-recon | G |  |  | 答えを書かない。 ○「月別の来場 | list |
| 303 | market-recon | G |  |  | 実際に口に出して聞ける言葉にする | list／使えるかは現場でしか測れない（STATUS §4） |
| 304 | market-recon | G |  |  | 数字で答えが返る問いを優先する（ | list |
| 305 | market-recon | M | 済 | `test_check_md.py::test_s299_ng` | 全問を1回で聞くことはできない。 | text／候補：02 の冒頭の表に初回訪問の10問（規則は L281。網に掛かっていない）／【09-28 S299】02 の「10問」の節の表に、問いと元番号の埋まった行がちょうど10行。選び方は人（CHECK #28 は H） |
| 306 | market-recon | H |  |  | 選ぶ基準に「どの仮説を決着させる | text／選んだ理由は残らない |
| 307 | market-recon | H |  |  | その場でしか手に入らないか — | list |
| 308 | market-recon | H |  |  | 相手が答えやすいか — 最初に答 | list |
| 309 | market-recon | H |  |  | 次の問いを開くか — 1つ答える | list |
| 310 | market-recon | G |  |  | 順番の型：業務の実態 → 数字 | text |
| 311 | market-recon | G |  |  | 根拠にしてよいのは 建前の内部矛 | text |
| 312 | market-recon | G |  |  | 当て木（業界パック・出典つきの市 | list |
| 313 | market-recon | R |  |  | 「この業種なら通常〜」「一般的に | text／参照：原本 #312 |
| 314 | market-recon | G |  |  | 断定しない。「〜の可能性」「〜と | list／03 は封なので機械も読まない |
| 315a | market-recon | G |  |  | 各仮説に根拠と出典を付ける | list |
| 315b | market-recon | G |  |  | 事前の基準 | list／03 は封なので機械も読まない（10-01 本人決定） |
| 316 | market-recon | M | 済 | `test_engine_consistency.py::test_a3_fixed_tags_same_everywhere` | 各仮説に 担当専門家タグ を付け | list／一覧の一致（A3）。03 は封なので中のタグは見ない |
| 317 | market-recon | R |  |  | 報告時に 03 の中身をチャット | text／参照：原本 #95 |
| 318 | market-recon | N |  |  | 自由に書くと必ず漏れる。 202 | text |
| 319 | market-recon | R |  |  | 01 の要点（事実のみ） | list／参照：原本 #92 |
| 320 | market-recon | R |  |  | 02 の問いの本数と分野 | list／参照：原本 #93 |
| 321 | market-recon | R |  |  | 埋まらなかった項目・取得できなか | list／参照：原本 #94 |
| 322 | market-recon | R |  |  | 03 は「n件作成した（未開封） | list／参照：原本 #96 |
| 323 | market-recon | N |  |  | ❌ 禁止例（実際に起きたもの） | text |
| 324 | market-recon | N |  |  | ❌「DXの空白という見立てを否定 | list／例 |
| 325 | market-recon | N |  |  | ❌「v1の仮説を1件否定、2件削 | list／例 |
| 326 | market-recon | N |  |  | ❌「◯◯比率◯◯%という実数で根 | list／例 |
| 327 | market-recon | N |  |  | ❌ 仮説の見出し・方向性・「どこ | list／例 |
| 328 | market-recon | N |  |  | ❌「タグ内訳：#DX 2／#財務 | list／例 |
| 329 | market-recon | N |  |  | ✅「03 を7件作成した（未開封 | list／例 |
| 330 | market-recon | R |  |  | 公開情報のみ・出典必須。 出典の | list／参照：原本 #266 |
| 331 | market-recon | R |  |  | 事実と仮説を絶対に混ぜない。 別 | list／参照：原本 #258 |
| 332 | market-recon | R |  |  | 不明は「不明」と書く。 推測で埋 | list／参照：原本 #131 |
| 333 | market-recon | R |  |  | 01 は定規である。 品質基準は | list／参照：原本 #288 |
| 334 | market-recon | R |  |  | 01 に「可能性がある」「実態」 | list／参照：原本 #258 |
| 335 | market-recon | R |  |  | 仮説は断定形にしない。 条件③（ | list／参照：原本 #314 |
| 336 | market-recon | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` | 「人間が現場で確認すべき点」を必 | list／02 の有無だけ |
| 337 | market-recon | N |  |  | AIが万能のふりをしないことが、 | text |
| 338 | market-recon | H |  |  | 現場の声・気持ち・暗黙のルールは | list／入力を無視したかは痕跡が残らない |
| 339 | market-recon | R |  |  | 守秘。顧客の機密情報をWeb検索 | list／参照：原本 #197 |
| 340 | market-recon | R |  |  | その文言を検索窓に打ち込まない。 | text／参照：原本 #197 |
| 341 | market-recon | H |  |  | 広く浅く→狭く深く。 まず全情報 | list |
| 342 | market-recon | N |  |  | assets/01-facts- | list／案内。★01i のテンプレが一覧に無い → 台帳 §8 |
| 343 | market-recon | N |  |  | assets/02-questi | list／案内 |
| 344 | market-recon | N |  |  | assets/03-hypoth | list／案内 |
| 345 | shinin-hansho | H |  |  | 「この結論は根拠が弱くないか」「 | text／使いどき |
| 346 | shinin-hansho | G |  |  | 最終判断はしない（判断は人間）。 | text |
| 347 | shinin-hansho | N |  |  | 両者は互いを見ていない。 だから | text |
| 348 | shinin-hansho | N |  |  | このスキルが、採用／要検証／棄却 | text |
| 349 | shinin-hansho | N |  |  | 責任がここに集約されていることで | text |
| 350 | shinin-hansho | R |  |  | 原則：このスキルは判断しない。 | text／参照：原本 #346 |
| 351 | shinin-hansho | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 必須①：案件/{会社名}/04_ | list／有無だけ |
| 352 | shinin-hansho | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 必須②：案件/{会社名}/03_ | list／有無だけ |
| 353 | shinin-hansho | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 参照：案件/{会社名}/01i_ | list／有無だけ。01 を読まないかは人 |
| 354 | shinin-hansho | M | 済 | `test_check_anken.py::test_01i_falls_back_to_01_with_note` | 01i が無い案件（#14以前） | list |
| 355 | shinin-hansho | G |  |  | その場合、05 の格付けで 「定 | text |
| 356 | shinin-hansho | H |  |  | 3つ目の視点：案件/{会社名}/ | list／読んだかは §0 の記録（#358）で形だけ見える |
| 357 | shinin-hansho | N |  |  | 任意：対象業界の業界パック .. | list |
| 358 | shinin-hansho | G |  |  | ただし——これは見立てであって現 | text |
| 359 | shinin-hansho | H |  |  | 必ず 04 を先に読み、03 を | text／CHECK #58 と同じ。記録の形は #358 |
| 360 | shinin-hansho | R |  |  | 04_現場分析.md を読み、現 | list／参照：原本 #359 |
| 361 | shinin-hansho | H |  |  | 01i（事実＝定規。無ければ 0 | list／★#347（01i。01 ではない）と食い違い → 台帳 §8 |
| 362 | shinin-hansho | R |  |  | 02b_主任診断士の見立て_封. | list／参照：原本 #359 |
| 363 | shinin-hansho | R |  |  | そのうえで 03_仮説_封.md | list／参照：原本 #359 |
| 364 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b4_ng` `test_anken_outputs.py::test_b39_ng_when_02b_not_stated` | 開封したことを出力に明記する（い | list／形だけ（B4・CHECK #59）／【09-28 再点検】「02b の有無」は 05 テンプレ §0 に行が無く、見ていない（テンプレと SKILL のずれ → 台帳 §8）／【09-28 B39】§0 に「02b」の語があるか（有無の書き方は問わない）。テンプレ §0 に行が無いずれは台帳 §8 のまま |
| 365 | shinin-hansho | H |  |  | ✅ 03 を読む → 05_反証 | list |
| 366 | shinin-hansho | H |  |  | ❌ 03 の仮説をチャットに列挙 | list／チャットは機械から見えない（CHECK #60） |
| 367 | shinin-hansho | R |  |  | ✅ チャットに報告してよいのは： | list／参照：原本 #366 |
| 368 | shinin-hansho | N |  |  | なぜ：03 を封じているのは「② | text |
| 369 | shinin-hansho | R |  |  | だから注意ではなく、手順で切る— | text／参照：原本 #366 |
| 370 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b26_ng_when_not_stated` `test_anken_outputs.py::test_b26_ok_when_selected_in_sec0` `test_anken_outputs.py::test_b26_ng_when_template_choice_left` `test_anken_outputs.py::test_b26_ok_when_stated_in_text` `test_anken_outputs.py::test_b26_stated_only_in_comment_is_missing` | 「現場側が無い状態での格付け」で | text／B26：04 が無い案件の 05 に「現場側が無い」の語があるか、§0 の「04 の有無」で「なし」を選んでいる（09-28 本人了承：どちらでも明記とみなす）。内部メモの中だけは明記にならない |
| 371 | shinin-hansho | G |  |  | 食い違いは「方向の対立」だけでは | text |
| 372 | shinin-hansho | N |  |  | 「①がXと言い②がnot-X」だ | text |
| 373 | shinin-hansho | G |  |  | 一致 ／ 一致 ／ 両方が同じ道 | table |
| 374 | shinin-hansho | G |  |  | 一致 ／ 食い違い ／ 実走で最 | table |
| 375 | shinin-hansho | G |  |  | 食い違い ／ — ／ 外からの見 | table |
| 376 | shinin-hansho | G |  |  | 値の食い違い ／ — ／ 同じ項 | table |
| 377 | shinin-hansho | G |  |  | A軸のみ ／ — ／ 03 にし | table |
| 378 | shinin-hansho | G |  |  | B軸のみ ／ — ／ 04 にし | table |
| 379a | shinin-hansho | G |  |  | 比較不能 ／ — ／ 層が違うの | table |
| 379b | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b13_ng_when_empty` `test_anken_outputs.py::test_b14_ng_when_limits_empty` `test_anken_outputs.py::test_b36_ng_when_sec9_says_none` `test_anken_outputs.py::test_b36_ng_when_fewer_rows_than_04` | 「まだ比べていない」と書き 06 へ渡す | table／B13・B14。何を書いたかは人／【09-28 再点検】04 §2 に比較不能の行があるのに 05 §9 が「なし」の場合を見逃す（B13 は空欄だけ）／【09-28 B36】04 §2 の比較不能・片側欠測の件数 ≤ 05 §9 の行数（「なし」で済ませていないか）。どの行に対応するかは人 |
| 380 | shinin-hansho | G |  |  | 「A軸のみ」と「B軸のみ」は扱い | text |
| 381 | shinin-hansho | G |  |  | 食い違いを潰さない（条件③）。 | text |
| 382 | shinin-hansho | G |  |  | 04 の芽と 03 の仮説は1対 | list |
| 383 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b29_ok` `test_anken_outputs.py::test_b29_ng` | ただし 元の番号を必ず残す（例： | text／B29：§1 の各行で中身のある側に数字がある（09-28 本人了承）。H・芽の頭の文字は問わない：実物に 04 §2 の「#3」を指す行がある。B軸のみの 03・A軸のみの 04・③が作成・02b のみ・②に該当なし は見ない |
| 384 | shinin-hansho | G |  |  | 04 にしか無い項目（B軸のみ） | list |
| 385 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b27_ng_b_axis_not_marked` `test_anken_outputs.py::test_b27_ng_when_03_blank` `test_anken_outputs.py::test_b27_ok_b_axis_marked` | 03 列に「（①には無い）」と書 | text／B27：§1 の 03 列が空でない・B軸のみの行は「①」と「には無い」がある（表記の揺れは通す。案件D は「①の〜には無い」形） |
| 386 | shinin-hansho | H |  |  | 04 の「強度」欄を必ず見る。 | list |
| 387 | shinin-hansho | G |  |  | 04 に「業界パックなし」と書か | list |
| 388 | shinin-hansho | G |  |  | 前提テスト：その仮説が乗っている | list |
| 389 | shinin-hansho | N |  |  | 理由：証拠テストは「根拠が何か」 | text |
| 390 | shinin-hansho | N |  |  | 03 の仮説が「従業員13名だか | list／例 |
| 391 | shinin-hansho | G |  |  | 複数の仮説が同じ前提に乗っている | list |
| 392 | shinin-hansho | N |  |  | 前提が崩れても、結論まで捨てると | list |
| 393 | shinin-hansho | G |  |  | 前提が崩れ、結論も観測と合わない | table |
| 394 | shinin-hansho | G |  |  | 前提は崩れたが、結論は 04 か | table |
| 395 | shinin-hansho | G |  |  | 証拠テスト：根拠は何か？「出典デ | list |
| 396 | shinin-hansho | G |  |  | 一般論は仮説の"外"だけでなく" | list |
| 397 | shinin-hansho | R |  |  | 組み込まれていることがある（「独 | text／参照：原本 #396 |
| 398 | shinin-hansho | G |  |  | 代表性テスト：現場の声は何人・ど | list |
| 399 | shinin-hansho | G |  |  | 因果テスト：相関を因果と取り違え | list |
| 400 | shinin-hansho | G |  |  | 対抗仮説テスト：同じ事実を説明す | list |
| 401 | shinin-hansho | G |  |  | 反証条件テスト：何が観測されれば | list |
| 402 | shinin-hansho | G |  |  | AI依存テスト：この結論はデータ | list |
| 403 | shinin-hansho | H |  |  | 第二の意見（任意・Phase 2 | text／外部に何を渡したかは成果物に残らない |
| 404 | shinin-hansho | G |  |  | 採用：出典 or 現場の一次情報 | list |
| 405 | shinin-hansho | G |  |  | 要検証：筋は良いが証拠が足りない | list |
| 406a | shinin-hansho | G |  |  | 棄却：一般論のみ／代表性なし／対 | list |
| 406b | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b12_ng_when_rejection_has_no_reason` | 理由を残す（消さない） | list／B12。理由の中身は人 |
| 407 | shinin-hansho | G |  |  | 判定不能：材料が足りず、判定その | list |
| 408 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b4_ng` | テンプレの §0「開封記録」を必 | text／形だけ |
| 409a | shinin-hansho | M | 一部 | `test_anken_outputs.py::test_b4_ng` `test_anken_outputs.py::test_b34_ng_when_03_before_04` | §0 開封記録：04 を読んだ後 | list／【09-28 再点検】§0 の「04 を読んだ日時」と「03 を開封した日時」の前後を比べていない（B4 は空欄とテンプレの文言だけ）／【09-28 B34】§0 の2つの日時の前後を比べる（日付、両方に時刻があれば時刻まで。同じ日で時刻が片方だけは比べられないので通す）／【09-29 済 → 一部（本人決定 c）】同じ日で時刻が片方しか無いと「04 の後に 03」を確かめられないのに通す。記録の欠け＝05 の書き方の問題なので検査では埋めない。直しは移行後：05 §0 のテンプレで両方の時刻を必須に（③が読むファイル＝修正。台帳 §8）／【10-01 実走 #76】テンプレ §0 の2行に「時刻まで書く」と書いた（75-9 と一緒に）。TEST の③2回とも両方に時刻あり（#75 は3回中1回）。検査は本人決定 c のまま片方だけでも通すので「一部」のまま |
| 409b | shinin-hansho | R |  |  | 04 が無い場合はその旨と、暫定判定であること | list／参照：原本 #370 |
| 410 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b16_ng_when_section_missing` `test_anken_outputs.py::test_b16_rigor_ng` | §1 クロス表：03の仮説 ｜ | list／B16：節と §1 の列（03・04・結論・機序・解釈） |
| 411 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b17_ng_when_counts_differ` `test_anken_outputs.py::test_b17_ng_when_summary_blank` `test_anken_outputs.py::test_b17_premise_table_is_not_counted_twice` `test_anken_outputs.py::test_b17_ng_when_a_judgement_row_is_missing` | §2 反証サマリー（採用 n／要 | list／B17：4つの判定が全部並び、§3 の最初の判定表と件数が合う |
| 412 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b16_ng_when_section_missing` `test_anken_outputs.py::test_b16_rigor_ng` `test_anken_outputs.py::test_b16_premise_heading_by_stage_name` | §3 仮説ごとの判定表（＋前提が | list／B16：§3 と「前提が崩れた仮説」の専用表（### の名前は「前提が崩れた」か「Stage 2-0」） |
| 413 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b5_ng_when_questions_are_a_list` | §4 現場で確認すべき決定的な問 | list／表の形だけ。優先度の順は人 |
| 414 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b5_ng` `test_anken_outputs.py::test_b5_ng_when_no_destination_column` | → 各問いに「顧客可／社内のみ」 | text／B5 |
| 415 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b16_ng_when_section_missing` `test_anken_outputs.py::test_b16_rigor_ng` | §5 AIに頼りすぎ注意：データ | list／B16：節があり空でない（「データでなくモデル依存」かどうかの中身は H） |
| 416 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b6_ng_when_empty` `test_anken_outputs.py::test_b6_ng_when_section_missing` | §6 ③が新しく作った仮説の申告 | list／B6 |
| 417 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b16_ng_when_section_missing` `test_anken_outputs.py::test_b16_rigor_ng` | §7 02b（主任診断士の見立て | list／B16：節があり空でない |
| 418 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b11_ng_when_human_section_missing` | §8 人間の判断が必要な論点（下 | list／B11 |
| 419 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b13_ng_when_empty` `test_anken_outputs.py::test_b13_ng_when_section_missing` `test_anken_outputs.py::test_b36_ng_when_sec9_says_none` | §9 比べていないもの（04§2 | list／B13／【09-28 再点検】#373b と同じ（04 §2 の比較不能 → §9 の引き継ぎ）／【09-28 B36】#373b と同じ |
| 420 | shinin-hansho | N |  |  | ③の格付けで「値の食い違い」か「 | text |
| 421 | shinin-hansho | N |  |  | ③は通過点ではない。受け取って、 | text |
| 422 | shinin-hansho | R |  |  | \| 比較不能（§9） \| 材料は | text／参照：原本 #379a |
| 423 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b28_ng_rejected_to_customer` `test_anken_outputs.py::test_b28_ng_when_id_in_hypothesis_column` `test_anken_outputs.py::test_b28_ng_when_rejected_branch_cited` `test_anken_outputs.py::test_b28_split_parent_is_judgement` `test_anken_outputs.py::test_b28_mixed_sources_is_judgement` | 棄却した仮説から出た「決定的な問 | text／B28：§4 の出所の番号が全部 §3 で棄却の行にしか出ないのに顧客可、を止める。分割（H4a 要検証・H4b 棄却で出所が H4）と番号の混在は「なぜ聞くのか」の判断（H）＝機械では決まらない |
| 424 | shinin-hansho | G |  |  | 顧客可 ／ 顧客に見せてよい。採 | table |
| 425 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b7_ng_when_internal_question_copied_to_06` `test_anken_outputs.py::test_b22_ng_when_internal_question_not_transferred` | 社内のみ ／ 棄却した仮説から出 | table／06 に載っていないか（B7）＋ 07 §4 の転記数（B22） |
| 426 | shinin-hansho | R |  |  | 答えが棄却済みの仮説になるなら、 | text／参照：原本 #423 |
| 427 | shinin-hansho | G |  |  | 「訪問を前提にしない」＝訪問でき | text／F-1 と関わる |
| 428 | shinin-hansho | N |  |  | 03 にも 04 にも書かれてい | text |
| 429 | shinin-hansho | R |  |  | だが黙って混ぜてはいけない。 ④ | text／参照：原本 #430 |
| 430 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b6_ng_when_empty` | 「これは①にも②にも無く、③が突 | list／節があり空でないかだけ（B6） |
| 431 | shinin-hansho | G |  |  | 対抗仮説を必ず併記する | list |
| 432 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b18_ng_when_self_approved` `test_anken_outputs.py::test_b18_ok_when_to_be_verified` | 格付けは原則 要検証。③が作った | list／B18：③が作った仮説を「採用」にしていない（「原則」なので要検証以外の判定は止めない） |
| 433 | shinin-hansho | G |  |  | 「AIが決める領域ではない」と判 | text |
| 434 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b9_ng_when_07_has_fewer_items` | 「これらは 07_主任診断士への | text／転記された結果（07 の件数）で見る（B9） |
| 435 | shinin-hansho | G |  |  | 建設的に叩く。 目的は確度を上げ | list |
| 436 | shinin-hansho | R |  |  | 一般論・業界パックを"証拠"にし | list／参照：原本 #395 |
| 437a | shinin-hansho | R |  |  | 対抗仮説と反証条件を必ず付ける。 | list／参照：原本 #400 |
| 437b | shinin-hansho | R |  |  | 反証条件 | list／参照：原本 #401 |
| 438 | shinin-hansho | R |  |  | 判断しない。 採用/要検証/棄却 | list／参照：原本 #346 |
| 439 | shinin-hansho | R |  |  | 04 を先に、03 を後に読む。 | list／参照：原本 #359 |
| 440 | shinin-hansho | R |  |  | 自分が作った解釈は、自分で承認し | list／参照：原本 #432 |
| 441 | shinin-hansho | R |  |  | 食い違いを消さない。 どちらが正 | list／参照：原本 #381 |
| 442 | shinin-hansho | M | 済 | `test_anken_outputs.py::test_b26_ng_when_adopted_without_04` `test_anken_outputs.py::test_b26_not_applied_when_04_exists` `test_anken_outputs.py::test_b26_ok_without_adoption` | 04 が無いときは 採用 を出さ | list／B26：04 が無い案件の 05 §3 で採用 0（§2 との一致は B17）。実案件に 04 の無い 05 は無い＝合成でだけ確認 |
| 443 | shinin-hansho | R |  |  | 守秘。 第二の意見で外部モデルを | list／参照：原本 #403 |
| 444 | tougou-report | R |  |  | 経営者がハッとする言葉に翻訳し、 | text／参照：原本 #459 |
| 445 | tougou-report | H |  |  | 「レポートにまとめて」「提出用に | text／使いどき |
| 446 | tougou-report | R |  |  | これは貼り合わせではなく編集。棄 | text／参照：原本 #459 |
| 447 | tougou-report | G |  |  | 編集であって貼り合わせではない。 | text |
| 448 | tougou-report | G |  |  | 確度で取捨し、経営者の言葉に翻訳 | text／トーン |
| 449 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_structural_leaks` | 採番（H1 X5 H3a・判定表 | list／採番の形（B-6） |
| 450 | tougou-report | M | 済 | `test_check_report.py::test_draft_tolerates_comments_with_internal_words` `test_check_report.py::test_ng_on_structural_leaks` | 「どの判定をどこに束ねたか」の対 | list／本文に出れば採番・内部語で捕まる |
| 451 | tougou-report | M | 済 | `test_build_sh.py::test_internal_memo_is_stripped_before_check` | 内部メモは build.sh が | list／build.sh を偽の pandoc の手前まで走らせて見る |
| 452 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_each_internal_word` `test_check_report.py::test_ng_on_structural_leaks` | check_report.py | list |
| 453 | tougou-report | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 案件/{会社名}/01i_外形カ | list／有無だけ |
| 454a | tougou-report | M | 済 | `test_check_anken.py::test_01i_falls_back_to_01_with_note` | 01i が無い案件（#14以前） | list／代用の NOTE |
| 454b | tougou-report | M | 済 | `test_anken_outputs.py::test_b32_ng_when_substitute_not_recorded` `test_anken_outputs.py::test_b32_ok_when_recorded` `test_anken_outputs.py::test_b32_not_applied_when_01i_exists` | 07（社内申し送り）に残リスク | list／B32：01 はあり 01i が無い案件の 07 に「01i」と「代用／無い／なし」が同じ行にある。_TEST_案件C は規則（09-20）より前の 07（08-19）＝KNOWN |
| 455 | tougou-report | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 案件/{会社名}/05_反証レポ | list／有無だけ。尊重したかは人 |
| 456 | tougou-report | M | 済 | `test_check_anken.py::test_missing_reader_file_is_warn` `test_engine_consistency.py::test_a1_readers_match_cross_run_table` | 案件/{会社名}/04_現場分析 | list／有無だけ |
| 457 | tougou-report | H |  |  | 案件/{会社名}/02_現場で確 | list／★④の入力に 02 とあるが、READERS と cross-run #101 の ④ に 02 が無い → 台帳 §8 |
| 458 | tougou-report | R |  |  | 03_仮説_封.md を直接読ま | text／参照：原本 #106 |
| 459 | tougou-report | G |  |  | 反証の格付けを尊重する：棄却は載 | list／棄却の語の検査は cross-run #121 |
| 460 | tougou-report | G |  |  | 事実と仮説を分ける：出典・現場の | list |
| 461 | tougou-report | G |  |  | 経営者の言葉に翻訳：専門用語を避 | list |
| 462 | tougou-report | M | 済 | `test_anken_outputs.py::test_b20_ng_when_four_issues` `test_anken_outputs.py::test_b20_ok_with_three` | 主要課題は3つの"見出し"に絞る | list／B20：課題の節の ### が3つ以下 |
| 463 | tougou-report | G |  |  | ただし「採用」を3件に間引かない | text |
| 464 | tougou-report | G |  |  | 束ねる軸は「機序」（なぜそうなっ | text |
| 465 | tougou-report | M | 済 | `test_anken_outputs.py::test_b33_ng_when_bundling_not_left_to_human` `test_anken_outputs.py::test_b33_ok_when_left_to_human` `test_anken_outputs.py::test_b33_not_applied_up_to_three` `test_anken_outputs.py::test_b33_line_outside_sec6_is_not_enough` | 本人が決める前：④は束ねて出して | list／B33：05 §3 の採用が3件を超えた案件の 07 §6 に「束ね」と「本人」が同じ行にある（本人が決めた後の記録も同じ形）。「決める前か後か」は機械では分からないので区別しない。_TEST_案件C は規則（09-25）より前＝KNOWN |
| 466 | tougou-report | G |  |  | 本人が決めた後に④をやり直すとき | list／07 の記録と見出しの一致は意味を読む |
| 467 | tougou-report | N |  |  | 問いにも棄却が混ざる： | list／前置き |
| 468 | tougou-report | M | 済 | `test_anken_outputs.py::test_b7_ng_when_internal_question_copied_to_06` | 05§4「現場で確認すべき決定的 | text／B7。文言が一致したときだけ（CHECK #85） |
| 469 | tougou-report | G |  |  | 「社内のみ」の存在は書く。件数と | list |
| 470 | tougou-report | N |  |  | 何も書かない ／ 06 が全件掲 | table |
| 471 | tougou-report | N |  |  | 件数を書く（「6件伏せた」） ／ | table |
| 472 | tougou-report | H |  |  | 前提：その1文が事実であること。 | text／07§4 で確かめたかは痕跡が残らない |
| 473 | tougou-report | M | 済 | `test_anken_outputs.py::test_b21_ng_when_two_issues_without_table` `test_anken_outputs.py::test_b21_ok_with_table_and_single_issue_needs_none` `test_anken_outputs.py::test_b21_ng_when_table_after_first_heading` | 課題を同じ重さに見せない（→ C | list／B21：課題が2つ以上なら表があり、最初の課題の見出しより前にある |
| 474 | tougou-report | M | 済 | `test_anken_outputs.py::test_b21_ng_when_two_issues_without_table` | 列は ①御社の発信とお話が異なっ | text／B21：3列の見出し（異なっていた／数字／決めていない） |
| 475 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_each_internal_word` `test_anken_outputs.py::test_b41_ng` | 格付け（強・中・弱）は書かない。 | text／「格付け」の語だけ。強・中・弱を書いたかは見ていない／【09-28 B41】06 に「強度」「格付け」の語・強／中／弱だけのセルが無いか。「強い根拠」のような地の文の格付けは人 |
| 476 | tougou-report | G |  |  | 「根拠だけ棄却」型は、載せないだ | list |
| 477 | tougou-report | G |  |  | ③が「自分で新しく作った」と申告 | list |
| 478 | tougou-report | G |  |  | 理由：見出しにすると、誰も決めて | text |
| 479 | tougou-report | M | 済 | `test_anken_outputs.py::test_b14_ng_when_limits_empty` `test_anken_outputs.py::test_b14_ng_when_limits_only_in_comment` `test_anken_outputs.py::test_b37_ng_on_ijou_nashi` `test_anken_outputs.py::test_b37_ng_on_polite_forms` | 比較不能を「異常なし」と書かない | list／B14（CHECK #83）。書き方は人／【09-28 再点検】06 に「異常なし」の語があるかは見ていない（B14 は限界の節の空欄だけ）／【09-28 B37】06 本文（内部メモを除く）に「異常なし」が無いか／【09-29】敬体の形（異常はありません・見られません・ございません・異常がない）も見る。「異常がないか」（問い）は通す。言い換え（問題ありません等）は人 |
| 480 | tougou-report | H |  |  | 出所は 05§9「比べていないも | text／04§2 を見ないかは痕跡が残らない |
| 481 | tougou-report | G |  |  | 9-1（材料が足りない）：「両側 | list |
| 482 | tougou-report | G |  |  | 9-2（層が違う）：「この2つは | list |
| 483 | tougou-report | G |  |  | 資格の独占業務に踏み込まない：法 | list |
| 484 | tougou-report | G |  |  | 「〜すべき」と断定しない。「〜を | text／法務・税務などの文脈か読まないと分からない |
| 485 | tougou-report | N |  |  | 社労士法27条・行政書士法1条の | text |
| 486 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` | → 06 に「本レポートで踏み込 | text／必須節（CHECK #86） |
| 487 | tougou-report | G |  |  | 法令・補助金・許認可の適正性に触 | list |
| 488 | tougou-report | G |  |  | 第三者認証（ISO等）の「有効性 | list |
| 489 | tougou-report | M | 済 | `test_anken_outputs.py::test_b19_ng_when_section_missing` `test_anken_outputs.py::test_b19_ng_when_sources_empty` | 出典を残す：AIの作文でないこと | list／B19：節があり空でない（内部メモだけは空とみなす） |
| 490 | tougou-report | R |  |  | 守秘：現場メモの生の文言はそのま | list／参照：原本 #198 |
| 491 | tougou-report | N |  |  | 06_課題仮説レポート.md ／ | table／案内 |
| 492 | tougou-report | M | 済 | `test_anken_outputs.py::test_b9_ng_when_07_missing` | 07_主任診断士への申し送り.m | table／B9。06 があれば 07 もある（CHECK #87） |
| 493 | tougou-report | M | 済 | `test_anken_outputs.py::test_b19_ng_when_section_missing` `test_anken_outputs.py::test_b19_ng_when_summary_over_three_lines` `test_anken_outputs.py::test_b19_three_lines_ok` | エグゼクティブサマリー（3行で" | list／B19：節があり、本文が1〜3行（「本質的な病巣を突く」かは H） |
| 494 | tougou-report | M | 済 | `test_anken_outputs.py::test_b19_ng_when_section_missing` | 御社の現状（外から見えること）（ | list／B19 |
| 495 | tougou-report | M | 済 | `test_anken_outputs.py::test_b19_ng_when_section_missing` `test_anken_outputs.py::test_b23_ok_with_four_items` `test_anken_outputs.py::test_b23_ng_when_item_missing` `test_anken_outputs.py::test_b20_ng_when_four_issues` | 見えてきた本質的な課題（確度順に | list／B19・B20・B23：課題の節があり、見出しが3つ以下、各課題に4項目（何が起きているか／なぜか／根拠／放置すると）。「確度順」は 05 の判定との意味の対応が要るので H |
| 496 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` | 一緒に確かめたい問い（05§4 | list／必須節 |
| 497 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` | この診断の限界：伺えた範囲（ | list／必須節 |
| 498 | tougou-report | R |  |  | 限界を先に言う相手の方が、言わな | text／参照：原本 #497 |
| 499 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` | 本レポートで踏み込んでいない領域 | list／必須節 |
| 500 | tougou-report | G |  |  | 相手が規制業種なら業界規制名を一 | text／規制業種かは人の判断 |
| 501 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` | 次の一歩（すり合わせへの案内。押 | list／必須節 |
| 502 | tougou-report | R |  |  | 出典 | list／参照：原本 #489 |
| 503 | tougou-report | M | 済 | `test_check_report.py::test_submission_ng_when_comment_left` | 内部メモ（どの格付けをどう反映し | list／提出版にコメントが残れば NG |
| 504 | tougou-report | G |  |  | 中身は1件も落とさない。書き方だ | text |
| 505 | tougou-report | G |  |  | 観察あり（どこで に 現地 があ | table／観察ありは通常の型。B8 は観察ゼロだけ見る |
| 506 | tougou-report | M | 済 | `test_anken_outputs.py::test_b8_ng_on_observation_zero` `test_anken_outputs.py::test_b8_applies_to_template_format_memo` `test_anken_outputs.py::test_b8_ng_on_missing_stock_phrases` | 観察ゼロ（遠隔・伝聞・書面のみ） | table／文書名・見出し・「課題である」だけ（CHECK #77）／【09-28 B8 拡張】課題の節の冒頭2行に「断定ではなく」・「拝見していない／見て確かめたもの」・訪問に触れるなら「機会をいただける」。問いの並べ順（書面で確かめられるものを先に）は人 |
| 507 | tougou-report | M | 済 | `test_anken_outputs.py::test_b8_ng_on_observation_zero` `test_anken_outputs.py::test_b8_negated_kadai_is_allowed` | 観察ゼロなら「これが課題である」 | list／「課題である」の語だけ |
| 508 | tougou-report | M | 済 | `test_anken_outputs.py::test_b19_ng_when_section_missing` | 全項目が単一ソースでも 06 は | list／B19：課題の節に本文がある。「単一ソースであることを本文に書く」は言い回しが自由で形にならない（H） |
| 509 | tougou-report | N |  |  | なぜ (b)「観察が入るまで出さ | list |
| 510 | tougou-report | H |  |  | 型を変えたら、紐づく記述を全部見 | list |
| 511 | tougou-report | M | 済 | `test_check_report.py::test_ng_when_required_section_missing` `test_engine_consistency.py::test_a4_required_sections_exist_in_report_template` `test_anken_outputs.py::test_b25_ng_when_template_section_missing` `test_anken_outputs.py::test_b25_template_heads_are_read_from_template` | 理由：古い 06 を土台にすると | text／B25：テンプレの「## 」見出しを毎回読み、06 が全部持つか（課題の節は観察の有無で2通り）。_TEST_案件C で実際に1節の欠落を捕まえた |
| 512 | tougou-report | R |  |  | 本レポートで踏み込んでいない領域 | table／参照：原本 #486 |
| 513 | tougou-report | R |  |  | この診断の限界 ／ 「AIに頼り | table／参照：原本 #497 |
| 514 | tougou-report | G |  |  | ページ数の上限は置かない（→ C | list |
| 515 | tougou-report | G |  |  | 長さを理由に削ってよいのは「重複 | list |
| 516 | tougou-report | N |  |  | 理由：長さで削ると真っ先に落ちる | list |
| 517 | tougou-report | N |  |  | 重複の例：「この診断の限界」と課 | list／例 |
| 518 | tougou-report | R |  |  | 課題の見出しは最大3つ（束ねる。 | list／参照：原本 #462 |
| 519 | tougou-report | M | 済 | `test_anken_outputs.py::test_b40_ng_when_customer_question_dropped` | 「一緒に確かめたい問い」は全件を | list／候補：05 §4 の顧客可の問いが 06 にある（④が言い換えるので文言一致では下限）／【09-28 B40】05 §4 の顧客可の件数 ≤ 06「一緒に確かめたい問い」の件数（④は言い換えるので文言は照合しない＝件数の下限） |
| 520 | tougou-report | G |  |  | 営業に効くからという理由で、診断 | text |
| 521 | tougou-report | N |  |  | 理由：06 は診断の成果物であっ | text |
| 522 | tougou-report | R |  |  | 重複（同じ説明が2か所にある）・ | table／参照：原本 #515 |
| 523 | tougou-report | R |  |  |  ／ 印象が悪い／煽りに読まれる | table／参照：原本 #520 |
| 524 | tougou-report | R |  |  |  ／ 相手が読みたがらなさそう | table／参照：原本 #520 |
| 525 | tougou-report | G |  |  | 削ったら、紙に「削った」と書く。 | text |
| 526 | tougou-report | G |  |  | 見本（デモ）は抜粋してよい。ただ | text |
| 527 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_each_sincerity_word` | 1 ／ 誠実さを宣言する ／ 「 | table／語の一覧だけ |
| 528 | tougou-report | G |  |  | 2 ／ 3つの課題を同じ形で書く | table |
| 529 | tougou-report | G |  |  | 3 ／ 人がいない紙にする ／ | table |
| 530 | tougou-report | R |  |  | 4 ／ 太字を撒く ／ 全部が強 | table／参照：原本 #534 |
| 531a | tougou-report | M | 済 | `test_anken_outputs.py::test_b25_ng_when_template_section_missing` `test_anken_outputs.py::test_b25_ng_when_hajimeni_not_first` | → 冒頭に「はじめに」を置き、主 | text／B25：テンプレの「はじめに」の節があり、最初の ## 節。空欄のまま出すかは CHECK #96（波括弧） |
| 531b | tougou-report | H |  |  | 主任診断士本人が一人称で書く | text／誰が書いたかは残らない（09-28：テンプレに欄を足した → 台帳 §8） |
| 532 | tougou-report | H |  |  | 空欄に戻したり、言い回しを整えた | text／前の 06 と比べれば機械でも見られるが、前の版を残さない運用 |
| 533 | tougou-report | N |  |  | 太字の決まり（check_rep | text／前置き |
| 534 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_two_inline_bolds_in_one_section` `test_check_report.py::test_one_inline_bold_per_section_ok` | 文中の太字は 1節に1か所まで。 | list |
| 535 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_long_bold` `test_check_report.py::test_bold_sentence_on_own_line_is_counted` | 太字は 20字まで。文ごと太くし | list |
| 536 | tougou-report | M | 済 | `test_check_report.py::test_label_only_bold_lines_not_counted` `test_check_report.py::test_label_followed_by_colon_inline_not_counted` | 項目名（「何が起きているか：」の | list |
| 537 | tougou-report | G |  |  | 迷ったら太字にしない。強調が1つ | list |
| 538 | tougou-report | N |  |  | ※このスキルやテンプレの指示文は | list |
| 539 | tougou-report | M | 済 | `test_check_report.py::test_ng_on_each_assertive_word` `test_anken_outputs.py::test_b42_ng` | 敬体。相手は「御社」。断定しない | list／断定語の一覧だけ。敬体・「可能性」の連続は見ていない／【09-28 B42】常体の文末（である。だ。など）が無い・「可能性」が3文続かない・表の外で「貴社」と呼ばない（表・見出し・引用・内部メモは見ない）。「1ページ」は連続3文で近似。言い切れる事実を言い切ったかは人／【09-29】常体の文末に「る。う。」（〜ている。〜と考える。〜と思う。）を足した。「」の中（相手の言葉）は見ない。案件D の「はじめに」の1文は KNOWN |
| 540 | tougou-report | R |  |  | 現場の生の言葉は載せない（頻度・ | list／参照：原本 #198 |
| 541 | tougou-report | R |  |  | 専門用語を避ける。「何が起きて・ | list／参照：原本 #461 |
| 542 | tougou-report | M | 未 |  | 色・字体・余白は 対外資料/_ブ | list／候補：ブランド定義に空欄があれば build.sh が止まる。★STATUS §5 は字体が未定のまま、PDF は作られている → 台帳 §8 |
| 543 | tougou-report | H |  |  | PDF化は 対外資料/_repo | list |
| 544 | tougou-report | M | 済 | `test_build_sh.py::test_ng_stops_before_pdf` `test_build_sh.py::test_internal_word_outside_memo_stops` | check_report.py | text／NG なら pandoc まで行かず PDF も無い |
| 545 | tougou-report | H |  |  | 見た目の反復は VS Code | list |
| 546 | tougou-report | G |  |  | 本文の Markdown と体裁 | list |
| 547 | tougou-report | H |  |  | デモは「実物と同じ作り」でなけれ | text／手で書いたかは残らない |
| 548 | tougou-report | H |  |  | 1 ／ _TEST_ の架空案件 | table |
| 549 | tougou-report | G |  |  | 2 ／ 見本にするときの差分は3 | table |
| 550 | tougou-report | R |  |  | 3 ／ 節は1つも落とさない。( | table／参照：原本 #511 |
| 551 | tougou-report | R |  |  | 4 ／ style.css を当 | table／参照：原本 #543 |
| 552 | tougou-report | R |  |  | 案件/{会社名}/06_課題仮説 | table／参照：原本 #503 |
| 553 | tougou-report | R |  |  | 案件/{会社名}/07_主任診断 | table／参照：原本 #492 |
| 554 | tougou-report | N |  |  | これを 06 の内部メモに書いて | text |
| 555 | tougou-report | M | 済 | `test_anken_outputs.py::test_b9_ng_when_07_has_fewer_items` | 05§8「人間の判断が必要な論点 | list／B9。件数だけ |
| 556 | tougou-report | M | 済 | `test_anken_outputs.py::test_b22_ng_when_new_hypothesis_not_transferred` `test_anken_outputs.py::test_b24_ng_when_counter_hypothesis_blank` `test_anken_outputs.py::test_b24_ok_with_counter_hypothesis` | ③が「自分で新しく作った」と申告 | list／B22：05 §6 の件数 ≤ 07 §3 の転記数／B24：各行に対抗仮説 |
| 557 | tougou-report | G |  |  | 06 で書くか書かないか④が迷っ | list |
| 558 | tougou-report | G |  |  | 事実の食い違い（値の不一致）で、 | list |
| 559 | tougou-report | G |  |  | 06 は顧客のもの、07 は診断 | text |
| 560 | tougou-report | R |  |  | 棄却は載せない・要検証は仮説と明 | list／参照：原本 #459 |
| 561 | tougou-report | R |  |  | 事実と仮説を分け、出典を残す。 | list／参照：原本 #460 |
| 562 | tougou-report | R |  |  | 3つに絞る。経営者の言葉に翻訳。 | list／参照：原本 #462 |
| 563 | tougou-report | R |  |  | 「一緒に確かめたい問い」を隠さな | list／参照：原本 #519 |
| 564 | tougou-report | R |  |  | 急かさない・決めつけない・依存さ | list／参照：原本 #448 |
