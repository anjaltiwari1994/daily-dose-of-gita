#!/usr/bin/env python3
"""HINDI Gita Reel (1080x1920, 11 s, music) on a bgbank/ background, for @daily.doseofgita.hindi.
Usage: python3 tools/render_reel_bg_hi.py input.json out.mp4
input.json = {"bg":"bgbank/n09.png","hook":"<Hindi>","pill":"<Hindi mood>","san":"line1\\nline2","ref":"15.15","mean":"<short Hindi line>"}
Schedule with videoCoverMilliseconds 10500."""
import json, sys, os, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_reel_bg as rb, render_reel_hi as rh
from playwright.sync_api import sync_playwright
def page(p):
    h = rb.page(p)
    for a, b in [("DAILY DOSE OF GITA", "दैनिक गीता सार"), ("font:500 28px 'Playfair Display';letter-spacing:6.2px", "font:400 38px 'Tiro Devanagari Hindi'"),
        ("font:700 22px 'Inter';letter-spacing:3.5px", "font:700 26px 'Noto Sans Devanagari'"), ("font:700 60px 'Playfair Display'", "font:700 56px 'Noto Serif Devanagari'"),
        ("— Bhagavad Gita ", "— श्रीमद्भगवद्गीता "), ("font:500 22px 'Inter'", "font:500 24px 'Noto Sans Devanagari'"),
        ("font:400 33px 'Lora';line-height:46px", "font:400 32px 'Noto Serif Devanagari';line-height:52px"), ("@daily.doseofgita<", "@daily.doseofgita.hindi<"), ("top:1565px", "top:1605px")]:
        assert a in h, a
        h = h.replace(a, b)
    return h.replace('<html><head>', '<html><head><meta charset="utf-8">', 1)
if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]
    rh.ensure_hindi_fonts()
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(page(p)); pg.wait_for_timeout(800); print('fit', pg.evaluate(rb.FITJS))
        for i in range(int(rb.FPS * rb.DUR)):
            pg.evaluate(rb.TICK, i / rb.FPS); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
            if i == int(rb.FPS * rb.DUR) - 1: pg.screenshot(path=out.replace('.mp4', '_last.png'))
        b.close()
    rb.music.make('gita', rb.DUR, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000',f'{tmp}/m2.wav'],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(rb.FPS),'-i',f'{tmp}/f%04d.jpg','-i',f'{tmp}/m2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],check=True)
    print('wrote', out)
