// About SHOTOKAN: the same text as the review dashboards' About tab (without "Which character I would play").
export type AboutItem = { section: string; title: string; body: string };
export const ABOUT: AboutItem[] = [
 {
  "section": "SHOTOKAN as a model",
  "title": "What SHOTOKAN is",
  "body": "SHOTOKAN is .shog's replay-review system. A REFramework script records both players' game state on every frame of a replay (moves, HP, Drive, super, positions, inputs, hitstun and blockstun). An analyzer turns that into hits, situations, timings, Drive economy and parries; a SQLite database keeps every reviewed set; and reviews like this one read it through a set of coaching lenses."
 },
 {
  "section": "SHOTOKAN as a model",
  "title": "What it measures, and what it can't",
  "body": "It measures exactly: damage, hit types, counter hits, anti-airs, throws, techs, Drive spent and lost, timings after blocking and on wake-up. Damage is the permanent life a hit takes, so when a hit cashes in white (recoverable) health, such as after Arjun's blocked pressure or a Drive Reversal, that counts too. It can't see intent. When the review says why something happened, that's a read on the data, and it says how confident it is."
 },
 {
  "section": "SHOTOKAN as a model",
  "title": "The lenses",
  "body": "E.X. Dojo's seminars for structure, Coach DoctaAfrikan's sessions for player types and matchup knowledge, Coach Juzzy and Coach Coosco for practical habits, Maj's Footsies Handbook for neutral, character notes for what is normal for each character, and .shog's own coaching rules and theories on top (Plant and Harvest, the Economy of Buttons, read or react)."
 },
 {
  "section": "How I view the game",
  "title": "Read or react",
  "body": "Most of SF6 is decided by reads, not reactions. Oki and pressure are almost always reads, because things happen faster than the 12-15 frames a human needs to react. Reactions belong to moments when you aren't committed yet: a shimmy, a wait at mid range, blocking."
 },
 {
  "section": "How I view the game",
  "title": "Risk should match the skill gap",
  "body": "If you can win without risk, don't take it: that's what consistency is. Even matches turn into more reads. The underdog has to take risks, but in the right spots: after a shown habit, or when one hit swings the round."
 },
 {
  "section": "How I view the game",
  "title": "Drive is a second health bar",
  "body": "Drive decides who gets to act. What matters is what it buys: winners spend more Drive than losers, but they spend it after a hit (combo Drive Rush cancels) or cheaply from neutral (raw Drive Rush), not on 3-bar cancels into a blocked string. Burning out on its own doesn't separate winners from losers, and a burnout spent on a combo that kills isn't counted at all."
 },
 {
  "section": "How I evaluate players",
  "title": "Spectra, not labels",
  "body": "Each player gets eight 1-5 scores between two opposite ends: temperament on defense and on offense (impulsive to mindful), adaptability (inelastic to elastic), risk tolerance, initiative (reactive to proactive), composure, variety, and resource use. They describe how someone played in this set, not who they are, and they move from set to set. Adaptability only counts a reused move against a player while it was losing them the game: keeping a winning plan isn't inelastic."
 },
 {
  "section": "How I evaluate players",
  "title": "Where damage comes from",
  "body": "Every hit taken is tagged by what the player was doing (pressing at mid range, walking in, blocking and getting opened up, jumping, an unsafe move punished). The biggest bucket is usually the most useful thing to fix, because it's a habit rather than one bad moment."
 },
 {
  "section": "How I evaluate players",
  "title": "Chess or poker?",
  "body": "Each decision is judged by its type. A chess decision has a right answer (a punish, an anti-air): did they find it? A poker decision is a read: did it fit what the opponent had shown? Losing a good read isn't a mistake; winning a bad one isn't a plan."
 },
 {
  "section": "Top player habits",
  "title": "Don't get opened up on wake-up",
  "body": "Blocking is still the default, but across the reviewed sets winners don't hold block more often than losers. The difference is what happens on wake-up: winners take less of their damage there. Pick a wake-up option that fits what the attacker has shown (block, tech, a reversal you can afford) rather than the same one every time."
 },
 {
  "section": "Top player habits",
  "title": "Throw, and cash in your hits",
  "body": "The two clearest things winners do more of: they land more throws (2.0 a game to the loser's 1.3) and turn hits into damage with combo Drive Rush cancels (1.9 to 1.0). The throw is the one option that always gives a definite answer, so it belongs in the default offense."
 },
 {
  "section": "Top player habits",
  "title": "Punish everything that is punishable",
  "body": "Consistent players take every free punish and beat the opponent's buttons with their own: winners land more counter hits (5.9 a game to 4.7) and nearly twice the punish counters (0.8 to 0.4). It's the cheapest damage in the game and it changes what the opponent dares to do."
 },
 {
  "section": "Top player habits",
  "title": "Make one adjustment at a time",
  "body": "The best players notice one pattern, change one thing, and check whether it worked. Elastic beats clever."
 },
 {
  "section": "Top player habits",
  "title": "Manage Drive and the clock",
  "body": "Keep enough Drive to defend, and spend it when it turns a hit into damage, position or a kill. Drive Reversal is mostly a losing player's tool (losers use it about twice as often): it costs 2 bars, is -6 if blocked, and usually only resets the situation, so blocking, a tech or a parry is often the cheaper answer."
 },
 {
  "section": "Top player habits",
  "title": "Spend super before the round ends",
  "body": "Round winners spend about 1.1 bars of super a round; round losers 0.3, and most lost rounds end with 2 or more bars still in the gauge. A full gauge at the KO is damage that was never used. When a hit can carry into super and the round is close, cash it out."
 },
 {
  "section": "Top player habits",
  "title": "Keep the reads cheap",
  "body": "When they gamble, it's a low-cost gamble with a big payoff, and only after the opponent has shown the habit at least twice."
 },
 {
  "section": "What the data says",
  "title": "Winner vs loser, set by set",
  "body": "The traits page compares the winner and the loser of the same set, stat by stat, weighted by MR, so the opponent, matchup and day stay the same. As of 25 November 2026 that's 154 complete sets. The steadiest signals: resource use (winners are the bigger spender in 86% of sets, and they spend after hits), throws landed, combo Drive Rush cancels, counter hits and punish counters. Anti-airs, throw techs, burnouts and how often players hold block barely separate them; those track the matchup and the player more than winning."
 },
 {
  "section": "What the data says",
  "title": "Matchups can change the rules",
  "body": "Some characters change what defense costs. Against Arjun, blocked pressure leaves white health on your bar and his next hit cashes it all in: in every reviewed Arjun set, a quarter to a third of his damage came that way. Getting out of his turn is worth more than usual."
 },
 {
  "section": "What the data says",
  "title": "How well the reviews predict",
  "body": "Every review starts with a prediction written before the replay is analysed. Blind predictions picked the winner in 74% of 111 sets (86% at Medium confidence, 8 of 8 at High), a little better than simply picking the higher-MR player (70% of 133 sets). Low-confidence calls do no better than MR, so the predictions are still most useful for naming the factors that decide a set. In the 26 November batch of A.K.I. sets (two players, 32 complete sets) they picked 21 winners (66%): close-MR sets stayed coin flips."
 },
 {
  "section": "What the data says",
  "title": "Learning a character from a stronger player",
  "body": "Reviewing a high-level player of your character shows what to lab. Broski's A.K.I. (about 2,000 MR, 15 of 20 sets won) and Zastorial's (about 1,530 MR) won about as many neutral exchanges, but Broski threw twice as often and looped the throw after every knockdown: throws were a quarter of his damage and under a tenth of Zastorial's. Fireball Drive Rush paid for both, as long as the button after the first blocked one was a low or a throw (obs-0026, obs-0027). Move names come from the SuperCombo move lists, checked against each capture's inputs (obs-0028)."
 },
 {
  "section": "What the data says",
  "title": "Observations",
  "body": "Dated notes on what the data shows and how the model changed are on the Observations page. When a finding stops holding as sets are added, a new note revises the old one instead of rewriting history."
 }
];
