#!/usr/bin/env python3
"""Render Daily Dose of Gita post cards (1080x1350 PNG), no Orshot needed.
Usage: python3 tools/render_cards.py input.json outdir
input.json = list of {"file":"g_6_5","mood":"SELF-DOUBT","hook":"...","sanskrit":"line1\\nline2",
                      "ref":"6.5","meaning":"...","handle":"@daily.doseofgita"}
Fonts (Playfair Display, Inter, Lora, Tiro Devanagari Hindi) are fetched once from github.com/google/fonts."""
import json, sys, os, html, subprocess, glob, shutil, tempfile

def ensure_fonts():
    fd = os.path.expanduser('~/.fonts'); os.makedirs(fd, exist_ok=True)
    have = subprocess.run(['fc-list'], capture_output=True, text=True).stdout
    need = {'Playfair Display': 'playfairdisplay', 'Inter': 'inter', 'Lora': 'lora', 'Tiro Devanagari Hindi': 'tirodevanagarihindi'}
    missing = [d for n, d in need.items() if n not in have]
    if not missing: return
    tmp = tempfile.mkdtemp()
    subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--sparse', 'https://github.com/google/fonts.git', tmp + '/gf'], check=True)
    subprocess.run(['git', '-C', tmp + '/gf', 'sparse-checkout', 'set'] + ['ofl/' + d for d in missing], check=True)
    for d in missing:
        for f in glob.glob(f'{tmp}/gf/ofl/{d}/*.ttf'):
            shutil.copy(f, fd)
    subprocess.run(['fc-cache', '-f'], capture_output=True)

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;position:relative;overflow:hidden;
background:radial-gradient(ellipse 520px 420px at 50% 44%,rgba(120,72,82,.42) 0%,rgba(70,44,86,.25) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,#1C1433 0%,#150F2A 55%,#0E0A1C 100%)}
.abs{position:absolute;left:0;width:1080px;text-align:center}
#brand{top:70px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}
#pill{left:390px;top:140px;width:300px;height:58px;border-radius:29px;background:#E8B14F;color:#2A1A05;font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;justify-content:center;position:absolute}
#hook{top:268px;height:80px;display:flex;align-items:center;justify-content:center;font:700 62px 'Playfair Display';color:#FFF6E5;white-space:nowrap}
#div{top:392px;font:400 32px 'DejaVu Sans';color:#E8B14F;word-spacing:4px}
#san{top:500px;height:200px;display:flex;align-items:center;justify-content:center;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:74px}
#ref{top:768px;font:500 22px 'Inter';color:#B2A7CA;letter-spacing:1px}
#box{left:70px;top:835px;width:940px;height:370px;border-radius:28px;border:1px solid rgba(232,177,79,.28);background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.03));position:absolute}
#ml{top:868px;font:700 20px 'Inter';letter-spacing:4.5px;color:#E8B14F}
#mt{left:120px;width:840px;top:920px;height:250px;display:flex;align-items:center;justify-content:center;text-align:center;font:400 38px 'Lora';line-height:52px;color:#FFF6E5;position:absolute}
#hd{top:1250px;font:500 26px 'Inter';color:#B2A7CA}"""
FIT = """()=>{const fit=(id,sid,maxw,maxh,min)=>{const c=document.getElementById(id),s=document.getElementById(sid);let f=parseFloat(getComputedStyle(c).fontSize);
while((s.scrollWidth>maxw||s.offsetHeight>maxh)&&f>min){f-=2;c.style.fontSize=f+'px';if(id=='san')c.style.lineHeight=(f*1.54)+'px';if(id=='mt')c.style.lineHeight=(f*1.37)+'px';}};
fit('hook','hs',900,90,40);fit('san','ss',960,210,30);fit('mt','ms',840,240,28);}"""

def page(p):
    san = html.escape(p['sanskrit']).replace('\n', '<br>')
    return f"""<html><head><style>{CSS}</style></head><body>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{html.escape(p['mood'])}</div>
<div class="abs" id="hook"><span id="hs">{html.escape(p['hook'])}</span></div><div class="abs" id="div">✦ ❁ ✦</div>
<div class="abs" id="san"><div id="ss">{san}</div></div><div class="abs" id="ref">— Bhagavad Gita {html.escape(p['ref'])} —</div>
<div id="box"></div><div class="abs" id="ml">MEANING</div><div id="mt"><div id="ms">{html.escape(p['meaning'])}</div></div>
<div class="abs" id="hd">{html.escape(p.get('handle','@daily.doseofgita'))}</div></body></html>"""

if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    ensure_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for p in items:
            pg.set_content(page(p)); pg.wait_for_timeout(500); pg.evaluate(FIT); pg.wait_for_timeout(200)
            pg.screenshot(path=f"{out}/{p['file']}.png"); print('rendered', p['file'])
        b.close()
