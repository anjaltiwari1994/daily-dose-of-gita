# Wow reel engines (free, no credits)

Run:  `python3 tools/wow/render.py cfg.json out.mp4`  -> 1080x1920, 13.5 s, music included.
The video starts 2.3 s into the animation, so the headline and the planet/scene are ON SCREEN IN THE FIRST FRAME
(the hook must land in the first second; most viewers swipe within 3 s). The final takeaway lines appear at about
9-11 s and hold to the end. Always set `videoCoverMilliseconds: 13000` when scheduling in Metricool.
Because the headline is the hook, write head1/head2 as a curiosity line, not a label (e.g. 'Saturn would FLOAT' / 'in a giant bathtub.').
Fonts (Playfair Display, Inter) are fetched once from github.com/google/fonts via render_cards.ensure_fonts().
Render time is about 1.5 minutes per reel. Open frames with ffmpeg and look at them before scheduling:
`ffmpeg -ss 6 -i out.mp4 -frames:v 1 f.png` (also 0, 10 and 13), then Read the PNGs. Check nothing is cut off.

## Engine "planet" (space facts that compare two numbers)
Fits facts such as: two numbers shown in two counting dials next to a spinning planet.
Examples: examples/venus.json (243 vs 225 days), saturn.json, jupiter.json, mars.json.
Fields: kicker, head1, head2 (headline, keep head1 <= ~20 chars, head2 <= ~26 chars; use h2size to shrink),
planet {preset: venus|saturn|jupiter|mars|neptune|moon, spinTurns, cy},
dials [two items: label, value (number the dial counts up to), scale (optional: ring full at this number),
decimals, unit (short, e.g. 'KM HIGH'), sub (short), colA, colB, endNote],
tag (short word between the dials), final1, final2 (two takeaway lines, <= ~55 chars each), handle, source,
music ("cosmic"), events [[seconds, hz, volume]] bell accents (use 8.5 and 11.0 as in the examples).
One dial only is allowed (dials with one item are centered).

## Engine "ocean" (small-count facts in a deep-sea scene)
Fits facts of the form "X has N of something" (N from 1 to 24), shown as N glowing hearts / orbs / eyes
that appear one by one while a big counter counts up. Examples: octopus.json (3 hearts), boxjelly.json (24 eyes).
Fields: count (1-24), shape (heart|orb|eye), bigLabel (plural noun in CAPS, e.g. HEARTS),
orbRGB / glowRGB ([r,g,b]) to colour the glow, head1, head2, final1, final2, handle, source (may be ""), music ("ocean").

## Choosing facts
Facts must be clearly true (verify with a web search and quote the source in `source` when a recognised
body like NASA/ESA publishes the number). Never repeat a fact already published or scheduled.
