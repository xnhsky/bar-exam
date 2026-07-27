# locks/ — 二台同時 TJR の予約（claim）置き場

`locks/claims/{問題ID}.json` は **TJR の生成予約**。OWNER PC / xnrg2 PC が同時に TJR を
回しても同じ問題を二重生成しないため、各問の生成開始前にこのファイルを commit→push して
番号を原子的に予約する（push の直列化＝分散ロック）。仕組みの正典は
`docs/run-patterns.md`「二台同時 TJR の衝突対策」、実装は `scripts/tjr-claim.ps1`。

- 中身：`problemId` / `pc`（マシン名）/ `stream`（T/J/R/F）/ `createdAt`（UTC）/ `ttlMinutes`
- 解放：TX は完成 commit に削除を同梱・JX は ⑦ finalize で削除
- 失効：TTL 超過 claim は他 PC が引き継ぎ可。TJR が毎バッチ先頭で掃除（`Clear-TjrStaleClaims`）
- **手で消してよいか**：残骸が邪魔なら消してよい（生成が走っていない claim は TTL で自然消滅
  するので通常は放置でよい）。生成中の相手 PC の claim を消すと二重生成に戻るので注意。
