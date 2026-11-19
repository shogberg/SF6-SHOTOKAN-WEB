# Pages

One spec per view. Each maps to one API router (`api/app/routers/`) and one frontend route folder (`web/src/routes/`).

| Page | Route | API |
|---|---|---|
| [Search and home](search.md) | `/` | `/api/v1/search` |
| [Player profile](player-profile.md) | `/players/{id}` | `/api/v1/players/{id}`, `/archetypes` |
| [Player sets](player-sets.md) | `/players/{id}/sets` | `/api/v1/players/{id}/sets` |
| [Set search](set-search.md) | `/sets` | `/api/v1/sets` |
| [Set detail](set-detail.md) | `/sets/{set_key}` | `/api/v1/sets/{set_key}` |
| [Head to head](head-to-head.md) | `/h2h/{a}/{b}` | `/api/v1/h2h/{a}/{b}` |
| [Character matchups](character-matchups.md) *(placeholder)* | `/matchups` | `/api/v1/matchups/...` |
| [MR bands](mr-bands.md) | `/analysis/mr-bands` | `/api/v1/analysis/mr-bands` |
| [What winning players do](traits.md) | `/analysis/traits` | `/api/v1/analysis/traits` |
| [Observations](observations.md) | `/analysis/observations` | `/api/v1/analysis/observations` |
| [Archetype matchups](archetype-predictions.md) | `/analysis/archetype-predictions` | `/api/v1/analysis/archetype-predictions` |

Shared components: player search box, spectrum bar (five dots between two labels), archetype badge with confidence, set card, MR band picker, sample-size badge, "data as of" snapshot footer.
