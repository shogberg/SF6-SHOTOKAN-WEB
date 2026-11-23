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
  "body": "It measures exactly: damage, hit types, counter hits, anti-airs, throws, techs, Drive spent and lost, timings after blocking and on wake-up. It can't see intent. When the review says why something happened, that's a read on the data, and it says how confident it is."
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
  "body": "Drive decides who gets to act. Spending it on things that don't buy damage or position, or losing it while blocking, gives the opponent turns for free. Burnout is often the real turning point of a round."
 },
 {
  "section": "How I evaluate players",
  "title": "Spectra, not labels",
  "body": "Each player gets eight 1-5 scores between two opposite ends: temperament (impulsive to mindful), adaptability (inelastic to elastic), risk tolerance, initiative (reactive to proactive), composure, variety, and resource use. They describe how someone played in this set, not who they are, and they move from set to set."
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
  "title": "Block first, then decide",
  "body": "Strong players treat blocking as the default and spend actions only when they have a reason. Most damage at every level comes from pressing at the wrong time, not from failing to press."
 },
 {
  "section": "Top player habits",
  "title": "Punish everything that is punishable",
  "body": "Consistent players take every free punish and every anti-air. It's the cheapest damage in the game and it changes what the opponent dares to do."
 },
 {
  "section": "Top player habits",
  "title": "Make one adjustment at a time",
  "body": "The best players notice one pattern, change one thing, and check whether it worked. Elastic beats clever."
 },
 {
  "section": "Top player habits",
  "title": "Manage Drive and the clock",
  "body": "Keep enough Drive to defend, spend it when it buys damage or position, and make the opponent burn out first."
 },
 {
  "section": "Top player habits",
  "title": "Keep the reads cheap",
  "body": "When they gamble, it's a low-cost gamble with a big payoff, and only after the opponent has shown the habit at least twice."
 }
];
