"""Derived-table builders, run in this order by publish.py. Each module has build(con, cfg)."""
from . import player_set, set_summary, player_profile, player_character, observations

ORDER = [player_set, set_summary, player_profile, player_character, observations]
