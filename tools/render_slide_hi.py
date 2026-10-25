#!/usr/bin/env python3
"""HINDI slide 2 of a carousel (1080x1350) for @daily.doseofgita.hindi. Same input as render_slide.py
(file, title, points[3], share, ref) but Hindi fonts/brand/pill. Usage: python3 tools/render_slide_hi.py slides.json outdir"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_slide as rs, render_cards as rc, render_reel_hi as rh
def page(s):
    h = rs.page(s)
    for a, b in [("font:500 28px 'Playfair Display';letter-spacing:6.2px", "font:400 38px 'Tiro Devanagari Hindi'"),
        ("DAILY DOSE OF GITA", "दैनिक गीता सार"),
        ("font:700 22px 'Inter';letter-spacing:3.5px", "font:700 26px 'Noto Sans Devanagari'"),
        ("font:700 60px 'Playfair Display';line-height:74px", "font:700 56px 'Noto Serif Devanagari';line-height:76px"),
        ("font:400 36px 'Lora';line-height:50px", "font:400 34px 'Noto Serif Devanagari';line-height:54px"),
        ("font:italic 600 38px 'Playfair Display';line-height:52px", "font:600 36px 'Noto Serif Devanagari';line-height:56px"),
        ("font:500 22px 'Inter';letter-spacing:1px", "font:500 24px 'Noto Sans Devanagari'"),
        ("font:500 26px 'Inter'", "font:500 26px 'Inter'")]:
        assert a in h, a
        h = h.replace(a, b)
    return h.replace('<html><head>', '<html><head><meta charset="utf-8">', 1)
if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rc.ensure_fonts(); rh.ensure_hindi_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in items:
            pg.set_content(page(s)); pg.wait_for_timeout(600); info = pg.evaluate(rs.FIT); pg.wait_for_timeout(150)
            pg.screenshot(path=f"{out}/{s['file']}.png")
            print('rendered', s['file'], 'WARNING: too long' if info['pointsOverflow'] else '')
        b.close()
