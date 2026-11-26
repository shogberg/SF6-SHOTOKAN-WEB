// Hand-written notes for the Archetypes page, from the archetype reads in ranked sets (the page's default) as of the
// date below, all MR bands. The tables on the page are live; rewrite a note (and its date) when it stops matching them.
export const ARCH_NOTES_AS_OF = '2026-11-26';

export type ArchNote = { archetype: string; body: string; why: string };
export const ARCH_NOTES: ArchNote[] = [
  {
    archetype: 'Aggressive',
    body: 'The most common read in ranked: 59% of player-sets, winning 48% of them. These players press early after blocking and on wake-up, run raw and pressure Drive Rushes, and take the turn whenever they can. On the spectra they lean high-risk (3.3) and spendthrift (3.4). They beat every Defensive player they met (5 of 5 sets) and split mirror matches (62 of 124), but lose more than they win against Balanced players (33 of 78).',
    why: 'Characters with fast Drive Rushes, dive kicks or strong pressure (Cammy, A.K.I., Juri, Ken) are read as Aggressive most often, because the kit rewards taking turns. It is also the default below 1800: two thirds of ranked players at 1600-1799 are read this way. A player who is behind in a set tends to lean further in.'
  },
  {
    archetype: 'Balanced',
    body: 'About a third of ranked reads (35%), and a better record: 55% of sets won, 58% against Aggressive players (45 of 78). They block first, attack on purpose, and change what they do between games. They are the most mindful archetype on defense and offense (3.6 each) and take less risk than Aggressive players (2.8 against 3.3). It pays off with rank: Balanced players win only 19-37% of their ranked sets below 1800, 61% at 1800-1999 and 89% at 2000+, where Balanced is the majority read (65%).',
    why: 'A Balanced read usually means a player who knows when the matchup and the score call for offense and when for defense. That makes it the archetype that grows with MR. Characters with good tools for both, such as Cammy, A.K.I. and Mai, show up often here.'
  },
  {
    archetype: 'Defensive',
    body: 'Rare (3% of ranked reads) and the worst record: 1 of 9 sets won, 0 of 5 against Aggressive and 1 of 4 against Balanced. They anti-air and punish first and spend very little (Resource use 1.5, the lowest of any archetype).',
    why: 'Usually not a chosen style: it shows up when a player is being run over and stops taking turns, or on characters whose plan waits for the opponent (Arjun, some Dhalsim and A.K.I. sets). In Economy of Buttons terms they hand over the initiative. Waiting works when it ends in a punish or an anti-air, not when it ends in blocking more pressure.'
  },
  {
    archetype: 'Fundamentalist',
    body: 'Also rare (3% of ranked reads, 6 of 10 sets won): spacing, pokes, anti-airs and whiff punishes, with the least Variety of any archetype (2.2: they stick to one plan). They do well against Balanced players (5 of 9), but the sample is small.',
    why: 'This leans with the character: zoners and long-poke characters (Dhalsim, Ryu, A.K.I.\'s fireball game) are read this way when the player sticks to range control. A Fundamentalist read is less a level than a plan, and it often turns into Balanced when the player adds a knockdown game.'
  },
];

export const ARCH_GENERAL = [
  'An archetype is a read on one player in one set, not a label on the player: the same player can be Aggressive against a zoner and Balanced against a rushdown. Profiles show each player\'s usual read and how often they leave it.',
  'Reads lean for four reasons. The character\'s kit suggests a style. The matchup pushes one player to take turns. The score changes risk (losing game 1 often makes a player press more). And MR: in ranked, Aggressive is 45-66% of reads from 1400 to 1999, while Balanced is 65% at 2000+.',
  'Custom room and casual sets (the Other filter) are often training and can be lopsided; with them included, Balanced looks stronger (61% of sets won against 55% in ranked).',
  'Small bands (Under Master, Below 1400, 2000+) have few players, so their mixes are hints; the counts are shown next to every number.'
];
