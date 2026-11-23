# Players (`/players`)

Every player with a reviewed set, next to Sets in the navigation.
- A **Player** picker (name, characters, number of sets): choosing one opens that player's overview (`/players/{id}`).
- A filter box (name, character or CFN ID) and a table: sets and games won-lost, latest rank (per the rank rules: MR, league name, or "MR unknown"), archetype and last set date.
- API: `GET /api/v1/players` returns every `player_profile` row, sorted by name.
