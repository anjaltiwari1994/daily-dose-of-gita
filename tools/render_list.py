#!/usr/bin/env python3
"""'Save-worthy' LIST carousels (1080x1350 PNGs), free, no credits. English Gita page.
Usage: python3 tools/render_list.py list.json outdir
list.json = list of slide objects, each with "type":
  cover  {file, bg:"bgbank/n13.png", pill:"SAVE THIS", hook:"Work stress? Save these 5 shloks.", sub:"For the next hard Monday", handle}
  verse  {file, pill:"SHLOKA 1 OF 5", title:"Anxious about the result?", san:"line1\\nline2", ref:"Bhagavad Gita 2.47",
          mean:"one short meaning (<=90 chars)", tip:"one concrete action (<=100 chars)", handle}
  recap  {file, pill:"QUICK RECAP", title:"Your 5-line cheat sheet", rows:[["2.47","Do the work, drop the worry"],...], share:"Save this. Send it to ...", handle}
Text auto-shrinks to fit. Always Read every PNG before scheduling."""
import json, sys, os, html, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc

BG = "radial-gradient(ellipse 560px 460px at 50% 40%,rgba(120,72,82,.40) 0%,rgba(70,44,86,.22) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,#1C1433 0%,#150F2A 55%,#0E0A1C 100%)"
GOLD, TEXT, MUTED, INK = '#E8B14F', '#FFF6E5', '#B2A7CA', '#2A1A05'
E = html.escape
BASE = f"""*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{BG}}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:70px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:{GOLD}}}
#pill{{position:absolute;left:50%;top:132px;transform:translateX(-50%);height:58px;padding:0 36px;border-radius:29px;background:{GOLD};color:{INK};font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#hd{{top:1262px;font:500 26px 'Inter';color:{MUTED}}}
.box{{position:absolute;left:90px;width:900px;border-radius:26px;border:1px solid rgba(232,177,79,.28);background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.03))}}
.lab{{font:700 20px 'Inter';letter-spacing:4px;color:{GOLD}}}
"""

def verse(s):
    san = E(s['san']).replace('\n', '</span><span class="l">')
    return f"""<html><head><style>{BASE}
#title{{top:232px;padding:0 70px;font:700 58px 'Playfair Display';line-height:72px;color:{TEXT};height:150px;display:flex;align-items:center;justify-content:center}}
#sanbox{{top:420px;height:250px;display:flex;flex-direction:column;align-items:center;justify-content:center}}
#san{{font:400 44px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:72px;text-align:center}}
#san .l{{display:block;white-space:nowrap}}
#ref{{margin-top:8px;font:500 21px 'Inter';letter-spacing:1px;color:{MUTED}}}
#meanbox{{top:705px;height:215px;padding:30px 40px}}
#mean{{margin-top:12px;font:400 36px 'Lora';line-height:50px;color:{TEXT}}}
#tipbox{{top:950px;height:255px;padding:30px 40px;border-color:rgba(232,177,79,.6);background:linear-gradient(180deg,rgba(232,177,79,.16),rgba(232,177,79,.06))}}
#tip{{margin-top:12px;font:600 36px 'Lora';line-height:50px;color:{TEXT}}}
</style></head><body>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{E(s['pill'])}</div>
<div class="abs" id="title"><span>{E(s['title'])}</span></div>
<div class="box" id="sanbox"><div id="san"><span class="l">{san}</span></div><div id="ref">— {E(s['ref'])} —</div></div>
<div class="box" id="meanbox"><div class="lab">MEANING</div><div id="mean">{E(s['mean'])}</div></div>
<div class="box" id="tipbox"><div class="lab">TRY THIS TODAY</div><div id="tip">{E(s['tip'])}</div></div>
<div class="abs" id="hd">{E(s.get('handle',''))}</div></body></html>"""

VFIT = """()=>{
const fit=(id,maxH,min,lh)=>{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollHeight>maxH&&f>min){f-=2;e.style.fontSize=f+'px';e.style.lineHeight=(f*lh)+'px';}};
const t=document.getElementById('title'),sp=t.querySelector('span');let f=58;while(sp.getBoundingClientRect().height>150&&f>38){f-=2;t.style.fontSize=f+'px';t.style.lineHeight=(f*1.24)+'px';}
const sn=document.getElementById('san');let s=44;while(s>28){let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});if(m<=820)break;s-=1;sn.style.fontSize=s+'px';}
let bad=[];for(const [id,box,min] of [['mean','meanbox',26],['tip','tipbox',26]]){const e=document.getElementById(id),b=document.getElementById(box);let z=parseFloat(getComputedStyle(e).fontSize);while(b.scrollHeight>b.clientHeight+1&&z>min){z-=2;e.style.fontSize=z+'px';e.style.lineHeight=(z*1.39)+'px';}if(b.scrollHeight>b.clientHeight+1)bad.push(id);}
return {overflow:bad,sanSize:s,titleSize:f};}"""

def cover(s, b64):
    return f"""<html><head><style>{BASE}
#art{{position:absolute;left:0;top:0;width:1080px;height:1350px;background:url(data:image/png;base64,{b64}) center/cover}}
#top{{position:absolute;left:0;top:0;width:1080px;height:620px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 40%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:900px;width:1080px;height:450px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.9) 40%,#080C25 70%)}}
#hook{{top:235px;padding:0 70px;font:700 80px 'Playfair Display';line-height:98px;color:{TEXT};height:300px}}
#sub{{top:1040px;padding:0 90px;font:italic 600 44px 'Playfair Display';line-height:60px;color:{GOLD}}}
#sw{{top:1170px;font:700 24px 'Inter';letter-spacing:5px;color:{TEXT}}}
</style></head><body><div id="art"></div><div id="top"></div><div id="bot"></div>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{E(s['pill'])}</div>
<div class="abs" id="hook">{E(s['hook']).replace(chr(10),'<br>')}</div>
<div class="abs" id="sub">{E(s['sub'])}</div><div class="abs" id="sw">SWIPE  &rarr;</div>
<div class="abs" id="hd">{E(s.get('handle',''))}</div></body></html>"""

CFIT = """()=>{const h=document.getElementById('hook');let f=80;while(h.scrollHeight>300&&f>50){f-=2;h.style.fontSize=f+'px';h.style.lineHeight=(f*1.22)+'px';}
const s=document.getElementById('sub');let z=44;while(s.scrollHeight>130&&z>28){z-=2;s.style.fontSize=z+'px';s.style.lineHeight=(z*1.36)+'px';}return {overflow:[]};}"""

def recap(s):
    rows = ''.join(f'<div class="r"><div class="k">{E(a)}</div><div class="t">{E(b)}</div></div>' for a, b in s['rows'])
    return f"""<html><head><style>{BASE}
#title{{top:232px;padding:0 70px;font:700 58px 'Playfair Display';line-height:72px;color:{TEXT}}}
#rows{{position:absolute;left:90px;width:900px;top:400px;height:620px;display:flex;flex-direction:column;justify-content:center;gap:20px}}
.r{{display:flex;align-items:center;gap:26px;padding:22px 30px;border-radius:24px;border:1px solid rgba(232,177,79,.28);background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.03))}}
.k{{flex:0 0 120px;font:700 30px 'Inter';color:{INK};background:{GOLD};border-radius:22px;height:56px;display:flex;align-items:center;justify-content:center}}
.t{{font:400 34px 'Lora';line-height:46px;color:{TEXT}}}
#share{{top:1080px;padding:0 90px;font:italic 600 42px 'Playfair Display';line-height:58px;color:{GOLD}}}
</style></head><body>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{E(s['pill'])}</div>
<div class="abs" id="title">{E(s['title'])}</div><div id="rows">{rows}</div>
<div class="abs" id="share">{E(s['share'])}</div>
<div class="abs" id="hd">{E(s.get('handle',''))}</div></body></html>"""

RFIT = """()=>{const b=document.getElementById('rows');let f=34;const ts=[...document.querySelectorAll('.t')];while(b.scrollHeight>b.clientHeight+2&&f>24){f-=2;ts.forEach(t=>{t.style.fontSize=f+'px';t.style.lineHeight=(f*1.35)+'px'});}
const s=document.getElementById('share');let z=42;while(s.scrollHeight>130&&z>28){z-=2;s.style.fontSize=z+'px';s.style.lineHeight=(z*1.38)+'px';}
return {overflow:b.scrollHeight>b.clientHeight+2?['rows']:[]};}"""

if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in items:
            t = s['type']
            if t == 'cover':
                pg.set_content(cover(s, base64.b64encode(open(s['bg'], 'rb').read()).decode())); fit = CFIT
            elif t == 'verse': pg.set_content(verse(s)); fit = VFIT
            else: pg.set_content(recap(s)); fit = RFIT
            pg.wait_for_timeout(600); info = pg.evaluate(fit); pg.wait_for_timeout(150)
            pg.screenshot(path=f"{out}/{s['file']}.png")
            print('rendered', s['file'], 'WARNING overflow: ' + ','.join(info['overflow']) if info['overflow'] else '', info)
        b.close()
