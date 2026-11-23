-- SHOTOKAN Web snapshot schema. Source tables are copied from sf6.db (see copy_source in publish.py);
-- this file defines the derived tables. Version lives in snapshot_meta.schema_version.

CREATE TABLE snapshot_meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE player_set (            -- one row per player per set: the base for every player view
  set_key TEXT, player_id INTEGER, opp_id INTEGER, played_date TEXT, context TEXT, format TEXT, review TEXT,
  character TEXT, opp_character TEXT, games_won INTEGER, games_lost INTEGER, won INTEGER,
  mr INTEGER, league TEXT, band TEXT, band_label TEXT, weight REAL,
  archetype TEXT, lean TEXT, read_confidence TEXT, opp_archetype TEXT,
  lost_game1 INTEGER, is_deviation INTEGER,
  PRIMARY KEY (set_key, player_id));

CREATE TABLE player_profile (
  player_id INTEGER PRIMARY KEY, name TEXT, cfn_id TEXT, region TEXT, characters TEXT,
  sets INTEGER, sets_won INTEGER, games_won INTEGER, games_lost INTEGER, first_date TEXT, last_date TEXT,
  latest_mr INTEGER, latest_league TEXT, latest_band TEXT, latest_band_label TEXT,
  reviews_json TEXT,                -- {"Quick": n, "Full": n, "Tournament": n}
  archetype TEXT, archetype_n INTEGER, lean TEXT, confidence TEXT, deviation_rate REAL, deviation_n INTEGER,
  summary TEXT, strengths TEXT, leaks TEXT, patterns TEXT, how_to_beat TEXT,
  spectra_json TEXT, per_game_json TEXT, opp_did_json TEXT);

CREATE TABLE player_character (       -- per player per character: record, per-game stats and spectra on that character
  player_id INTEGER, character TEXT, sets INTEGER, sets_won INTEGER, games INTEGER, games_won INTEGER, games_lost INTEGER,
  per_game_json TEXT, spectra_json TEXT, stats_source TEXT,  -- stats_source: 'games' (per-game stats) or 'sets' (older sets: whole-set stats)
  PRIMARY KEY (player_id, character));

CREATE TABLE player_archetype_summary (  -- per player per archetype read
  player_id INTEGER, archetype TEXT, sets INTEGER, wins INTEGER, losses INTEGER, PRIMARY KEY (player_id, archetype));

CREATE TABLE player_spectra_by_result (  -- per player per axis: mean score in won vs lost sets
  player_id INTEGER, axis TEXT, mean_win REAL, n_win INTEGER, mean_loss REAL, n_loss INTEGER, mean_all REAL, sd_all REAL,
  PRIMARY KEY (player_id, axis));

CREATE TABLE player_deviation (          -- archetype moves away from the player's modal archetype, by context
  player_id INTEGER, from_archetype TEXT, to_archetype TEXT, context TEXT, n INTEGER,
  PRIMARY KEY (player_id, from_archetype, to_archetype, context));

CREATE TABLE set_summary (
  set_key TEXT PRIMARY KEY, played_date TEXT, context TEXT, format TEXT, review TEXT, note TEXT,
  p1_id INTEGER, p2_id INTEGER, p1_char TEXT, p2_char TEXT, p1_games INTEGER, p2_games INTEGER, winner_id INTEGER,
  game_scores TEXT, game_scores_p2 TEXT, progression TEXT, n_games INTEGER,
  p1_mr INTEGER, p2_mr INTEGER, p1_league TEXT, p2_league TEXT, p1_band_label TEXT, p2_band_label TEXT,
  p1_archetype TEXT, p2_archetype TEXT,
  has_prediction INTEGER, prediction_verdict TEXT, prediction_correct INTEGER);

CREATE TABLE predictions (
  set_key TEXT, idx INTEGER, written_at TEXT, predicted TEXT, actual TEXT, verdict TEXT, correct INTEGER, body_json TEXT,
  PRIMARY KEY (set_key, idx));

CREATE TABLE observations (
  obs_id TEXT PRIMARY KEY, written_at TEXT, topic TEXT, title TEXT, body TEXT, evidence_json TEXT, supersedes TEXT);
