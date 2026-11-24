# Observations (`/analysis/observations`)

Notes on what makes a winning player, what makes a struggling player, and how the model's view changes over time.
- Each observation has a date, a topic (Winning / Struggling / Model change / Other), a title, the body (markdown), and evidence links (sets, players, analysis pages).
- **Revisions are kept:** a new note can supersede an older one; both stay visible, linked, so the change of view is part of the record.
- **Timeline** view and **by topic** view.
- Written locally (markdown files with front matter), shipped in the snapshot; nothing is edited on the server.

As of 24 Nov 2026 there are 18 notes (obs-0001 to obs-0018), updated for 130 compared sets; obs-0014 to obs-0017 add the button economy (damage per decision press), the average game, blind MR-based predictions and how lessons hold up under pressure, and obs-0018 notes that predictions pick the winner but undersell the margin. obs-0010 revises obs-0004 ("winners are more patient on defense"), which stopped holding as sets were added; obs-0004 stays visible as the earlier view.

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
