#!/usr/bin/env python3
"""Wow reel renderer (no credits). Usage: python3 tools/wow/render.py cfg.json out.mp4
cfg.json: {"engine":"planet"|"ocean", ... engine fields ..., "music":"cosmic|ocean|gita", "events":[[time,freq,amp],...]}
Result: 1080x1920, 13.5 s. The video starts at engine time START (2.3 s), so the headline and planet/scene are
already on screen in the first frame; then the animation plays and the final layout holds. Schedule with
videoCoverMilliseconds 13000 (last frame = cover). Bell event times in cfg are engine times (as in the examples)."""
import json, sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import music, render_cards as rc
FPS, DUR, COVER, START = 30, 13.5, 0, 2.3
if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; here = os.path.dirname(os.path.abspath(__file__))
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.on('pageerror', lambda e: print('PAGEERROR', e))
        pg.goto('file://' + os.path.join(here, cfg['engine'] + '.html'))
        pg.evaluate('(c)=>window.setup(c)', cfg); pg.wait_for_timeout(300)
        ct = pg.evaluate('window.COVER_T')
        for i in range(int(FPS*DUR)):
            if i < COVER: pg.evaluate('window.__zt=0'); t = ct
            else: pg.evaluate(f'window.__zt={i/FPS}'); t = START + i/FPS
            pg.evaluate(f'window.frame({t})'); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=92)
        b.close()
    music.make(cfg.get('music', 'cosmic'), DUR, f'{tmp}/m.wav', [(e[0]-START, e[1], e[2]) for e in cfg.get('events', []) if e[0] >= START])
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.8:120|240|400:0.4|0.3|0.2,lowpass=f=7000',f'{tmp}/m2.wav'], check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%04d.jpg','-i',f'{tmp}/m2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','medium','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out], check=True)
    print('wrote', out)
