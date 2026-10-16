# Wow reel engines (free, no credits)

Run:  `python3 tools/wow/render.py cfg.json out.mp4`  -> 1080x1920, 20 s, music included.
Frames 0-2 show the finished layout (cover). The animation ends at about 14 s and the last frame holds until 20 s,
so people can read it. Always set `videoCoverMilliseconds: 19500` when scheduling in Metricool.
Fonts (Playfair Display, Inter) are fetched once from github.com/google/fonts via render_cards.ensure_fonts().
Render time is about 2.5 minutes per reel. Open frames with ffmpeg and look at them before scheduling:
`ffmpeg -ss 6 -i out.mp4 -frames:v 1 f.png` (also 12 and 19), then Read the PNGs. Check nothing is cut off.

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
