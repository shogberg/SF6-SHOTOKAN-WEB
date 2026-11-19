# Set search (`/sets`)

Find all sets for a player by name, past name or CFN ID, as a paged list.

- **Search box:** a name, part of a name, or a CFN ID.
  - One match (or an exact name or CFN ID match) opens that player's sets straight away.
  - Several matches show a **selectable list of players** (name, main character, band, number of sets, CFN ID, other names). Picking one opens their sets.
  - No search: every set, newest first.
- **List:** 25 sets per page with page controls above and below (Prev, page numbers, Next, "26-40 of 40"). For a player, the list is from their side (result, games, opponent, archetype); for all sets, both players are shown.
- **Filters:** result (for a player), review level, context. Changing a filter goes back to page 1.
- **URL state:** `?q=`, `?player=`, `?page=`, `?result=`, `?review=`, `?context=`, so a list can be bookmarked or shared.

API: `GET /api/v1/sets?q=&player=&page=&per_page=&result=&review=&context=` returns `data` (the page), `page` (`{page, per_page, total, pages}`), `totals`, `player` (when one is selected) and `candidates` (when the search matched several players). `per_page` defaults to 25, max 100. `GET /api/v1/players/{id}/sets` takes the same `page` / `per_page`.
