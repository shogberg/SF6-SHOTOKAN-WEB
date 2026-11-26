// Hand-written notes for the Archetypes page, from the archetype reads in reviewed sets (as of the date below, all
// MR bands). The tables on the page are live; rewrite a note (and its date) when it stops matching them.
export const ARCH_NOTES_AS_OF = '2026-11-26';

export type ArchNote = { archetype: string; body: string; why: string };
export const ARCH_NOTES: ArchNote[] = [
  {
    archetype: 'Aggressive',
    body: 'The most common read: 56% of player-sets, winning 45% of them. These players press early after blocking and on wake-up, run raw and pressure Drive Rushes, and take the turn whenever they can. On the spectra they lean high-risk (3.3) and spendthrift (3.4). They beat Defensive players (7 of 9 sets) and split mirror matches (65 of 130), but lose to Balanced players (34 of 92).',
    why: 'Characters with fast Drive Rushes, dive kicks or strong pressure (Cammy, A.K.I., Juri) are read as Aggressive most often, because the kit rewards taking turns. It is also the default below 1800: most players at 1400-1799 are read this way. A player who is behind in a set tends to lean further in.'
  },
  {
    archetype: 'Balanced',
    body: 'About a third of reads (36%), and the best record: 61% of sets won, 63% against Aggressive players (58 of 92). They block first, attack on purpose, and change what they do between games. They are the most mindful on defense (3.6) and offense (3.4) and take less risk (2.9). At 2000+ Balanced is the majority read (65%) and wins 89% of its sets.',
    why: 'A Balanced read usually means a player who knows when the matchup and the score call for offense and when for defense. That makes it the archetype that grows with MR. Characters with good tools for both, such as Cammy, Mai and Luke, show up often here.'
  },
  {
    archetype: 'Defensive',
    body: 'Rare (5% of reads) and the worst record: 15% of sets won, 2 of 9 against Aggressive and 1 of 11 against Balanced. They anti-air and punish first and spend very little (Resource use 1.5, the lowest of any archetype).',
    why: 'Usually not a chosen style: it shows up when a player is being run over and stops taking turns, or on characters whose plan waits for the opponent (Arjun, some Juri and A.K.I. sets). In Economy of Buttons terms they hand over the initiative. Waiting works when it ends in a punish or an anti-air, not when it ends in blocking more pressure.'
  },
  {
    archetype: 'Fundamentalist',
    body: 'Also rare (3% of reads, 54% won): spacing, pokes, anti-airs and whiff punishes, with the least Variety of any archetype (2.4: they stick to one plan). They do well against Balanced players (5 of 11) but the sample is small.',
    why: 'This leans with the character: zoners and long-poke characters (Dhalsim, Ryu, Sagat, A.K.I.\'s fireball game) are read this way when the player sticks to range control. A Fundamentalist read is less a level than a plan, and it often turns into Balanced when the player adds a knockdown game.'
  },
];

export const ARCH_GENERAL = [
  'An archetype is a read on one player in one set, not a label on the player: the same player can be Aggressive against a zoner and Balanced against a rushdown. Profiles show each player\'s usual read and how often they leave it.',
  'Reads lean for four reasons. The character\'s kit suggests a style. The matchup pushes one player to take turns. The score changes risk (losing game 1 often makes a player press more). And MR: Aggressive dominates below 1800, Balanced grows above it.',
  'Small bands (Under Master, Below 1400, 2000+) have few players, so their mixes are hints; the counts are shown next to every number.'
];
