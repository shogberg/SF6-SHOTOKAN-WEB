# Observations (`/analysis/observations`)

Notes on what makes a winning player, what makes a struggling player, and how the model's view changes over time.
- Each observation has a date, a topic (Winning / Struggling / Model change / Other), a title, the body (markdown), and evidence links (sets, players, analysis pages).
- **Revisions are kept:** a new note can supersede an older one; both stay visible, linked, so the change of view is part of the record.
- **Timeline** view and **by topic** view.
- Written locally (markdown files with front matter), shipped in the snapshot; nothing is edited on the server.

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
