#!/usr/bin/env python3
"""HINDI Gita Reel for @daily.doseofgita.hindi (1080x1920 mp4, 11 s, music). Same design and timing as render_reel.py
(frame 0 already shows brand, mood pill, hook and the first Sanskrit line over a turning gold mandala and rising light specks;
second line 0.3-1.0 s, meaning box 1.4-2.0 s, meaning words 1.8-5.2 s, layout holds to 11 s), but with Hindi text and Devanagari fonts.
Schedule with videoCoverMilliseconds 10500.
Usage: python3 tools/render_reel_hi.py input.json out.mp4
input.json = ONE object: {"mood": "संतोष", "hook": "<Hindi hook>", "sanskrit": "<line 1>\\n<line 2>", "ref": "4.22",
                          "meaning": "<Hindi meaning>", "handle": "@daily.doseofgita.hindi"}"""
import json, sys, os, glob, shutil, subprocess, tempfile, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc, render_reel as rr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wow'))
import music

def ensure_hindi_fonts():
    rc.ensure_fonts()
    fd = os.path.expanduser('~/.fonts'); have = subprocess.run(['fc-list'], capture_output=True, text=True).stdout
    need = {'Noto Serif Devanagari': 'notoserifdevanagari', 'Noto Sans Devanagari': 'notosansdevanagari'}
    missing = [d for n, d in need.items() if n not in have]
    if not missing: return
    tmp = tempfile.mkdtemp()
    subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--sparse', 'https://github.com/google/fonts.git', tmp + '/gf'], check=True)
    subprocess.run(['git', '-C', tmp + '/gf', 'sparse-checkout', 'set'] + ['ofl/' + d for d in missing], check=True)
    for d in missing:
        for f in glob.glob(f'{tmp}/gf/ofl/{d}/*.ttf'): shutil.copy(f, fd)
    subprocess.run(['fc-cache', '-f'], capture_output=True)

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;position:relative;overflow:hidden;
background:radial-gradient(ellipse 520px 420px at 50% 44%,rgba(120,72,82,.42) 0%,rgba(70,44,86,.25) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,#1C1433 0%,#150F2A 55%,#0E0A1C 100%)}
.abs{position:absolute;left:0;width:1080px;text-align:center}
#brand{top:62px;font:400 36px 'Tiro Devanagari Hindi';color:#E8B14F}
#pill{left:0;right:0;margin:0 auto;width:max-content;top:138px;min-width:220px;padding:0 34px;height:60px;border-radius:30px;background:#E8B14F;color:#2A1A05;font:700 26px 'Noto Sans Devanagari';display:flex;align-items:center;justify-content:center;position:absolute;white-space:nowrap}
#hook{top:262px;height:96px;display:flex;align-items:center;justify-content:center;font:700 60px 'Noto Serif Devanagari';color:#FFF6E5;white-space:nowrap;line-height:1.3}
#div{top:392px;font:400 32px 'DejaVu Sans';color:#E8B14F;word-spacing:4px}
#san{top:490px;height:220px;display:flex;align-items:center;justify-content:center;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:76px}
#ref{top:768px;font:500 24px 'Noto Sans Devanagari';color:#B2A7CA}
#box{left:70px;top:835px;width:940px;height:370px;border-radius:28px;border:1px solid rgba(232,177,79,.28);background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.03));position:absolute}
#ml{top:862px;font:700 26px 'Noto Sans Devanagari';color:#E8B14F}
#mt{left:110px;width:860px;top:915px;height:262px;display:flex;align-items:center;justify-content:center;text-align:center;font:400 38px 'Noto Serif Devanagari';line-height:60px;color:#FFF6E5;position:absolute}
#hd{top:1250px;font:500 26px 'Inter';color:#B2A7CA}"""
FIT = """()=>{const fit=(id,sid,maxw,maxh,min,lh)=>{const c=document.getElementById(id),s=document.getElementById(sid);let f=parseFloat(getComputedStyle(c).fontSize);
while((s.scrollWidth>maxw||s.offsetHeight>maxh)&&f>min){f-=2;c.style.fontSize=f+'px';if(lh)c.style.lineHeight=(f*lh)+'px';}};
fit('hook','hs',940,96,36,0);fit('san','ss',960,220,28,1.62);fit('mt','ms',860,258,26,1.55);}"""

def page(p):
    san = html.escape(p['sanskrit']).replace('\n', '<br>')
    return f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="abs" id="brand">दैनिक गीता सार</div><div id="pill">{html.escape(p['mood'])}</div>
<div class="abs" id="hook"><span id="hs">{html.escape(p['hook'])}</span></div><div class="abs" id="div">✦ ❁ ✦</div>
<div class="abs" id="san"><div id="ss">{san}</div></div><div class="abs" id="ref">— श्रीमद्भगवद्गीता {html.escape(p['ref'])} —</div>
<div id="box"></div><div class="abs" id="ml">अर्थ</div><div id="mt"><div id="ms">{html.escape(p['meaning'])}</div></div>
<div class="abs" id="hd">{html.escape(p.get('handle', '@daily.doseofgita.hindi'))}</div></body></html>"""

def build(p):
    base = page(p); OFF = rr.OFF
    base = base.replace('<style>', '<style>body{height:1920px!important}#wrap{position:absolute;left:0;top:%dpx;width:1080px;height:1350px;transform-origin:50%% 45%%}' % OFF, 1)
    base = base.replace('<style>', '<style>#fx{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:0}#wrap{z-index:1}', 1)
    return base.replace('<body>', '<body><canvas id="fx" width="1080" height="1920"></canvas><div id="wrap">', 1).replace('</body>', '</div></body>')

PREP = "()=>{(" + FIT + ")();const san=document.getElementById('ss');san.innerHTML=san.innerHTML.split('<br>').map(l=>'<div class=\"ln\">'+l+'</div>').join('');const ms=document.getElementById('ms');ms.innerHTML=ms.textContent.split(' ').map(w=>'<span class=\"w\">'+w+'</span>').join(' ');}"

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); p = p[0] if isinstance(p, list) else p; out = sys.argv[2]
    ensure_hindi_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(); FPS, DUR = rr.FPS, rr.DUR
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(build(p)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(700); pg.evaluate(PREP); pg.wait_for_timeout(200)
        for i in range(int(FPS * DUR)):
            pg.evaluate(rr.TICK, [i / FPS, i / FPS]); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
        b.close()
    music.make('gita', DUR, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{tmp}/m.wav', '-af', 'aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000', f'{tmp}/m2.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f%04d.jpg', '-i', f'{tmp}/m2.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out)
