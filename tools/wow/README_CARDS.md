# Wow fact cards (free, no credits)

Run: `python3 tools/wow/card.py cards.json wowcards` -> one 1080x1350 PNG per card (Instagram 4:5 feed size), about 1 s each.
Copy an entry from `examples/cards.json` and change the fields. Look at every PNG before scheduling (Read it): nothing cut off,
numbers right, spelling right, picture matches the fact.

Text fields: `file`, `tag` (pill: SPACE FACT / BODY FACT / ANIMAL FACT / INDIA FACT / OCEAN FACT / EARTH FACT), `head1` (white,
ALL CAPS, about 18 chars or fewer), `head2` (gold, about 26 chars or fewer, may wrap to 2 lines; digits are drawn in Inter automatically),
`detail` (1-2 sentences, wrap ONE key phrase in [[double brackets]] to colour it gold), `handle`, `source` (small credit, may be ''), `seed`
(any integer; change it so two cards with the same scene look different).

Scenes (`scene`) and their options:
- `space`: starfield + nebula + one big planet. `planet` {preset: venus|saturn|jupiter|mars|neptune|moon|titan|earth, x, y (about 480),
  R (about 265), rot (turns the planet), aurora (true = glowing polar auroras)}. Optional `planet2` (a small second planet, e.g. Saturn in a
  corner: {preset, x, y, R: 60}), `sun` [x, y, scale] for a glare, `lander` [x, y, scale]. Fits: planets, moons, stars, astronomy.
- `moonsurface`: grey lunar ground under a black starry sky. Options `earth` [x, y, R] (Earth in the sky), `lander` [x, y, scale]
  (gold lander), `prints` (number of footprints). Fits: Moon landings, Moon facts, astronauts.
- `ocean`: underwater light rays, particles, bubbles. `tint` [r,g,b] shifts the water colour. `creature`: `whale` (+ `heart` true for a
  glowing heart; `wx`, `wy`, `ws` position/scale, ws about 0.95) or `plankton` (glowing spiral bloom). Fits: sea animals, ocean, oxygen.
- `storm`: night storm clouds, rain, lightning. `bolts` [[x, y, scale], ...] (start y about 190 so bolts don't touch the brand line).
  Fits: lightning, weather, Earth/atmosphere facts.
- `pulse`: glowing red heart with a neon heartbeat line. Fits: heart, blood, body and health facts.
- `rainhills`: misty green layered hills in heavy rain. Fits: rain, monsoon, mountains, forests, Indian geography.
If no scene fits a fact well, pick a different fact rather than a mismatched picture.
