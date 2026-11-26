// Hand-written notes for the Stats by MR page, read from the band numbers for ranked sets (the page's default) as of
// the date below. The tables under them are live; when a note stops matching the table, rewrite the note (and its
// date) rather than the data.
export const NOTES_AS_OF = '2026-11-26';
export const NOTES_SAMPLE = 'ranked sets only: 382 player-sets with a known band. There are no ranked Under Master sets yet and only 5 below 1400, so those columns are hints at most. 2000+ is 49 player-sets but only 7 players, most from two of them. Custom room and casual sets (the Other filter) are left out of the notes because training sets can be lopsided: Cammy wins 78% of her non-ranked games, against 66% overall.';

export type Note = { topic: string; title: string; body: string };
export const NOTES: Note[] = [
  {
    topic: 'Button economy',
    title: 'Higher bands don\'t press more; each press earns more',
    body: 'Decision presses (new attacks started while nobody is in hitstun, blockstun or a knockdown) stay at 12.5 to 14 a round in every ranked band from 1400 up. What climbs is what each press earns: about 580-595 damage per press from 1400 to 1799, 640 at 1800-1999 and 660 at 2000+. Damage dealt per round rises from about 6,800-7,200 to 8,750, and damage taken falls from about 7,900 to 5,700. Getting better is less about taking more turns than about getting more from the turns you take.'
  },
  {
    topic: 'Drive economy',
    title: 'More Drive spent, less of it on OD, more of it on hits',
    body: 'Drive spent per round rises from about 6.3 bars at 1400-1599 to 7.5 at 2000+, while OD falls from 2.1 bars a round to 1.5. The clearest Drive change is the combo Drive Rush cancel: 0.6 a game at 1400-1599, 1.2-1.4 at 1600-1799, 1.5 at 1800-1999 and 1.8 at 2000+. Pressure cancels on block level off at about 1 a game from 1600 up. Raw Drive Rush is about 3 a game until 2000+ (4.5). Super spent per round rises from 0.5 to 0.85 bars, but a third or more of lost rounds still end with a full super in every band.'
  },
  {
    topic: 'Offense, pressure and oki',
    title: 'Throws grow with rank; oki is steady from 1400 up',
    body: 'Throws landed sit at about 1.4-1.6 a game below 1800, then rise to 1.8 at 1800-1999 and 2.7 at 2000+, the biggest jump between any two neighbouring bands. About 12-14% of damage comes from oki in every ranked band from 1400 up, and counter hits stay near 5 a game. Higher bands don\'t get more knockdowns; they get more from the throw.'
  },
  {
    topic: 'Defense',
    title: 'Higher bands block more and press less on wake-up',
    body: 'Holding block after a blocked string sits at 17-19.5% below 1800 and 24% from 1800 up. Holding block on wake-up goes from 18.5-21% to 23% at 1800-1999 and 27% at 2000+. Pressing a button on wake-up falls from about 31% at 1400-1599 to 25-27% from 1800 up. Perfect parries climb from 0.3 a game to 0.55 at 1800-1999 and 0.74 at 2000+. Anti-airs and throw techs barely change. Damage taken by lens (reviewed players only): higher bands lose a larger share of their smaller damage total to mid-range counter hits, walk-in throws and being opened up while blocking. Their losses come from honest guesses, not from punished unsafe moves.'
  },
  {
    topic: 'Spectra',
    title: 'Mindful offense and defense, and spending, rise at 1800',
    body: 'The spectra change most between 1700-1799 and 1800-1999. Temperament (defense) moves from about 2.6-2.9 below 1800 to 3.5 at 1800-1999 and 3.8 at 2000+ (mindful). Temperament (offense) goes from 2.6-2.9 to about 3.4-3.5. Resource use rises from 2.85 at 1400-1599 to 3.8 at 2000+ (spendthrift, matching the Drive numbers). Risk tolerance eases from 3.1-3.4 to 2.9-3.0. Composure, Variety and Adaptability barely change across bands, so they describe the player more than the level.'
  },
  {
    topic: 'Archetypes',
    title: 'Aggressive is the common read; Balanced only pays off from 1800',
    body: 'In ranked, Aggressive is the most common read in every band from 1400 to 1999 (44-65% of player-sets); at 2000+ Balanced takes over (65%). Below 1800 neither archetype wins most of its sets: Aggressive wins 31-41%, Balanced 19-37%. From 1800 up both win more, Aggressive 59% and Balanced 61% (89% at 2000+). Custom room sets had made Balanced look strong at 1700-1799 (70% with them, 37% ranked only).'
  },
];
