// Hand-written notes for the Archetypes page, from the archetype reads in ranked sets (the page's default) as of the
// date below, all MR bands. The tables on the page are live; rewrite a note (and its date) when it stops matching them.
// 2026-11-27: generated reads recalibrated against the pool (obs-0038), so these notes were rewritten.
export const ARCH_NOTES_AS_OF = '2026-11-27';

export type ArchNote = { archetype: string; body: string; why: string };
export const ARCH_NOTES: ArchNote[] = [
  {
    archetype: 'Aggressive',
    body: 'Still the most common ranked read, but no longer the default: 38% of player-sets (it was 59% before the recalibration), winning 46% of them. These players press early after blocking and on wake-up, use Drive Rush to take the turn, and jump more than their character usually does. They lean high-risk (3.5) and spendthrift (3.5) but only middling on Cash-in (3.1): they spend a lot, and a fair share of it goes into rushes and parries that don\'t land. They beat Defensive players (15 of 20) and split mirror matches (33 of 66), but lose to Balanced (29 of 66) and especially Fundamentalist players (6 of 26).',
    why: 'Characters with fast Drive Rushes or strong pressure (Cammy, A.K.I., Juri, Ken) show up here most. Jumps are now judged against the character\'s norm, so a Cammy is no longer Aggressive just for dive kicking. Being behind in a set still pushes players this way.'
  },
  {
    archetype: 'Balanced',
    body: 'A third of ranked reads (32%), winning 49%. They block first, attack on purpose, and change what they do between games; they are a little more mindful than Aggressive players on defense and offense, take less risk (3.1 against 3.5), and take more ground (Space 3.6). They beat Aggressive (37 of 66) and Defensive players (12 of 19) but lose to Fundamentalists (7 of 29). Balanced is the most common read at 2000+ (39% of reads there), where Balanced players won 28 of 41 sets.',
    why: 'A Balanced read usually means a player who knows when the matchup and the score call for offense and when for defense, which is why it grows with MR. Cammy, A.K.I. and Mai players show up here most.'
  },
  {
    archetype: 'Fundamentalist',
    body: 'Now a real group: 18% of ranked reads, with the best record by far, 61 of 81 sets won (75%), including 20 of 26 against Aggressive and 22 of 29 against Balanced players. They win exchanges with counter hits and punish counters without pressing more than most, take the least risk of the common reads (2.6), and score highest on Cash-in (4.1) and Space (3.8): their Drive and super go into hits that landed, and they keep the opponent cornered.',
    why: 'Read the record with care: landing counter hits is part of the definition and also comes with winning, and many of these reads are one strong Mai player (ll Moke ll) and high-MR sets (31 of 33 won at 1800-1999). It describes how strong ground players win: poke, whiff punish, punish everything, and spend only on confirmed hits.'
  },
  {
    archetype: 'Defensive',
    body: '13% of ranked reads and the worst record: 16 of 59 sets won (27%), 1 of 14 against Fundamentalists and 5 of 20 against Aggressive players. They press little, rarely Drive Rush, and spend the least (Resource use 2.1); they also give up the most ground (Space 2.5, the only archetype below the middle).',
    why: 'Usually not a chosen style: it shows up when a player is being run over and stops taking turns, or on characters whose plan waits for the opponent. Many Defensive reads are Mai players at high MR (they still won 9 of 21 at 2000+). Waiting works when it ends in a punish or an anti-air, which is the Fundamentalist read; when it ends in blocking more pressure in the corner, it reads Defensive.'
  },
];

export const ARCH_GENERAL = [
  'An archetype is a read on one player in one set, not a label on the player: the same player can be Aggressive against a zoner and Fundamentalist against a rushdown. Profiles show each player\'s usual read and how often they leave it.',
  'How a read is made (since 27 November 2026): per round, how often the player presses after blocking or on wake-up, how much Drive Rush pressure they use, and how often they jump compared with their character\'s average, against every other player in the database. The top 30% on that are Aggressive and the bottom 30% Defensive; players in the top 30% on counter hits and punish counters who aren\'t aggressive are Fundamentalist; the rest are Balanced. Full reviews are read by hand with the same meanings.',
  'Reads lean for four reasons: the character\'s kit, the matchup, the score (losing game 1 often makes a player press more), and MR. In ranked, Aggressive is the most common read from 1600 to 1999; at 2000+ Balanced leads and Fundamentalist and Defensive are a fifth each.',
  'Custom room and casual sets (the Other filter) are often training and can be lopsided. Small bands (Under Master, Below 1400) have few players, so their mixes are hints; the counts are shown next to every number.'
];
