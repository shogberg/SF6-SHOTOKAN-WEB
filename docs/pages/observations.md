# Observations (`/analysis/observations`)

Notes on what makes a winning player, what makes a struggling player, and how the model's view changes over time.
- Each observation has a date, a topic (Winning / Struggling / Model change / Other), a title, the body (markdown), and evidence links (sets, players, analysis pages).
- **Revisions are kept:** a new note can supersede an older one; both stay visible, linked, so the change of view is part of the record.
- **Timeline** view and **by topic** view.
- Written locally (markdown files with front matter), shipped in the snapshot; nothing is edited on the server.

As of 25 Nov 2026 there are 25 notes (obs-0001 to obs-0025), for 154 compared sets. obs-0019 to obs-0022 (25 Nov) cover unspent super in lost rounds, Drive Parry, pressing after blocking and mid-range punish windows; obs-0023 revises obs-0016 (blind predictions now edge out MR: 74% vs 70%), obs-0024 notes that a punished reversal comes back, and obs-0025 counts a day of rounds lost with super. As of 26 Nov 2026 there are 28: obs-0026 (high-level A.K.I. wins on the throw loop), obs-0027 (fireball Drive Rush value and its follow-up) and obs-0028 (A.K.I., Jamie, Alex and Elena moves renamed from the wiki; old A.K.I. "Snake Step" = Sinister Slide). obs-0010 revises obs-0004 ("winners are more patient on defense"); revised notes stay visible as the earlier view.

Front matter example:
```
---
id: obs-0007
date: 2026-11-19
topic: Model change
title: Drive discipline matters more than counter-hit volume
supersedes: obs-0003
evidence: [set:JSHO2G1_JSHO2G2_JSHO2G3, player:jon]
---
```
