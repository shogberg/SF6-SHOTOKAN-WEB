// Hand-written notes for the MR bands page, read from the band numbers as of the date below. The tables under them
// are live; when a note stops matching the table, rewrite the note (and its date) rather than the data.
export const NOTES_AS_OF = '2026-11-26';
export const NOTES_SAMPLE = '432 player-sets with a known band (22 more had no MR and are left out). Under Master (6 player-sets) and Below 1400 (9) are hints only; 2000+ is 49 player-sets but only 7 players, most from two of them.';

export type Note = { topic: string; title: string; body: string };
export const NOTES: Note[] = [
  {
    topic: 'Button economy',
    title: 'Higher bands don\'t press more; each press earns more',
    body: 'Decision presses (new attacks started while nobody is in hitstun, blockstun or a knockdown) stay at 12 to 14 a round in every band. What climbs is what each press earns: about 560 damage per press at 1400-1599, 590-600 at 1600-1799, 630 at 1800-1999 and 660 at 2000+. Damage dealt per round rises from about 6,600 to 8,750, and damage taken falls from about 8,000 to 5,700. The share of a set\'s presses stays near 50% for everyone. Getting better is less about taking more turns than about getting more from the turns you take.'
  },
  {
    topic: 'Drive economy',
    title: 'More Drive spent, less of it on OD, more of it on hits',
    body: 'Drive spent per round rises from about 6.2 bars at 1400-1599 to 7.5 at 2000+, but the OD share falls (1.9 bars a round to 1.5). The clearest Drive change is the combo Drive Rush cancel, which triples from 0.6 a game to 1.7-1.8 between 1400 and 1800. Pressure cancels on block level off at about 1 a game from 1600 up. Raw Drive Rush is flat at about 3 a game until 2000+ (4.5). Drive Reversals and burnouts fall slowly. Super spent per round rises from 0.5 to 0.85 bars, but about a third of lost rounds still end with a full super in every band.'
  },
  {
    topic: 'Offense, pressure and oki',
    title: 'Throws and oki grow with rank',
    body: 'Throws landed go from about 1.5 a game below 1800 to 1.8 at 1800-1999 and 2.7 at 2000+, the biggest jump between any two neighbouring bands. Damage from oki goes from about 3-5% of a player\'s damage under 1400 to 11-14% from 1400 up: lower-band players rarely turn a knockdown into more damage. Counter hits rise a little (4.8 to 5.4 a game). Damage from pressure and from punishes stays at about 13-15% and 12-13% in every band from 1400 up.'
  },
  {
    topic: 'Defense',
    title: 'Higher bands block more and press less on wake-up',
    body: 'Holding block after a blocked string goes from about 17.5% at 1400-1599 to 24% from 1800 up, and holding block on wake-up from 20% to 27% at 2000+. Pressing a button on wake-up falls from 44% Under Master and about 31% at 1400-1599 to 25-27% from 1800 up. Perfect parries climb from 0.3 to 0.7 a game. Anti-airs and throw techs barely change. Damage taken by lens (reviewed players only): higher bands lose a larger share of their smaller damage total to mid-range counter hits, walk-in throws and being opened up while blocking. Their losses come from the honest guesses, not from punished unsafe moves.'
  },
  {
    topic: 'Spectra',
    title: 'Mindful defense and spending rise; risk falls a little',
    body: 'Temperament (defense) moves from impulsive toward mindful, 2.7 at 1400-1599 to 3.5 at 1800-1999 and 3.8 at 2000+, and Temperament (offense) from 2.7 to about 3.4-3.5 above 1800. Resource use rises from 2.8 to 3.8 (spendthrift, matching the Drive numbers). Risk tolerance eases from about 3.3 to 2.9-3.0. Composure, Variety and Adaptability barely change across bands, so they describe the player more than the level.'
  },
  {
    topic: 'Archetypes',
    title: 'Aggressive is the common read; Balanced wins more as rank rises',
    body: 'Aggressive is the most common read in every band up to 1999 (42-66% of player-sets). At 2000+ Balanced takes over (65%). Balanced players win only about a quarter of their sets below 1700 but 61-89% from 1800 up. Aggressive players win 58-59% of theirs from 1800 up, against 28-38% below. A plan that keeps both offense and defense pays off more the higher the band.'
  },
];
