#!/usr/bin/env python3
"""Wow fact CARD renderer (free, no credits). Usage: python3 tools/wow/card.py cards.json outdir
cards.json = list of card objects; each makes outdir/<file>.png at 1080x1350 (Instagram 4:5 feed size).
Fields per card:
  file     output name without .png (e.g. w_titan_lakes)
  scene    space | moonsurface | ocean | storm | pulse | rainhills   (see README_CARDS.md)
  tag      category pill, e.g. SPACE FACT / BODY FACT / ANIMAL FACT / INDIA FACT
  head1    white first headline line, ALL CAPS, <= ~18 chars
  head2    gold second line, <= ~26 chars (may wrap to 2 lines)
  detail   1-2 sentences; wrap ONE key phrase in [[double brackets]] to colour it gold
  handle   @your.dailydoseofwow
  source   optional small credit bottom-right, e.g. 'Data: NASA'
  seed     optional integer, changes the random stars/particles
  plus scene options (planet, planet2, sun, lander, earth, prints, creature, heart, tint, bolts ...)."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import render_cards as rc

if __name__ == '__main__':
    cards = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__)); rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        pg.on('pageerror', lambda e: print('PAGEERROR', e))
        for c in cards:
            pg.goto('file://' + os.path.join(here, 'card.html'))
            info = pg.evaluate('(c)=>setup(c)', c); pg.wait_for_timeout(200)
            pg.screenshot(path=f"{out}/{c['file']}.png")
            print('rendered', c['file'], 'text starts at y=%d' % info['textTop'])
        b.close()
