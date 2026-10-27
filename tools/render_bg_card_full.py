#!/usr/bin/env python3
"""Standalone verse card (1080x1350): hook + Sanskrit + a centred 2-3 line SAAR (essence: what the shloka means and what to take from it).
No section headers. Replaces the old one-line cards. Free, no credits. English and Hindi.
Usage: python3 tools/render_bg_card_full.py items.json outdir
items = [{"lang":"en"|"hi","bg":"bgbank/n04.png","file":"f_3_35","ref":"3.35","hook":"Comparing your life to others?","pill":"YOUR OWN PATH",
          "san":"line1\\nline2","saar":"2-3 centred lines, ~110-170 chars (English) / ~90-130 (Hindi)"}]
Text auto-shrinks to fit; Read every PNG before scheduling."""
import json, sys, os, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc
import render_reel_hi as rh
from playwright.sync_api import sync_playwright
E = html.escape
T = {
 'en': dict(brand='DAILY DOSE OF GITA', handle='@daily.doseofgita',
            ref=lambda r: f'— Bhagavad Gita {r} —',
            css="""#brand{top:58px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}
#pill{height:58px;top:118px;padding:0 34px;border-radius:29px;font:700 22px 'Inter';letter-spacing:3.5px}
#hook{top:208px;font:700 60px 'Playfair Display';color:#FFF6E5;white-space:nowrap}
#ref{font:500 22px 'Inter';letter-spacing:1px}
#saar{font:400 34px 'Lora';line-height:49px}"""),
 'hi': dict(brand='दैनिक गीता सार', handle='@daily.doseofgita.hindi',
            ref=lambda r: f'— श्रीमद्भगवद्गीता {r} —',
            css="""#brand{top:46px;font:400 36px 'Tiro Devanagari Hindi';color:#E8B14F}
#pill{height:60px;top:114px;padding:0 34px;border-radius:30px;font:700 26px 'Noto Sans Devanagari'}
#hook{top:200px;font:700 56px 'Noto Serif Devanagari';color:#FFF6E5;white-space:nowrap;line-height:1.3}
#ref{font:500 24px 'Noto Sans Devanagari'}
#saar{font:400 32px 'Noto Serif Devanagari';line-height:50px}"""),
}
def page(it, b64):
    t = T[it.get('lang', 'en')]
    san = '</div><div class="l">'.join(E(l) for l in it['san'].split('\n'))
    return f"""<html><head><meta charset="utf-8"><style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#080C25}}
#art{{position:absolute;left:0;top:0;width:1080px;height:1350px;background:url(data:image/png;base64,{b64}) center/cover}}
#top{{position:absolute;left:0;top:0;width:1080px;height:520px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 36%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:760px;width:1080px;height:590px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.9) 24%,#080C25 46%)}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#pill{{position:absolute;left:50%;transform:translateX(-50%);background:#E8B14F;color:#2A1A05;display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#san{{top:872px;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:70px}}
#san .l{{white-space:nowrap}}
#ref{{top:1022px;color:#B2A7CA}}
#sbox{{position:absolute;left:80px;width:920px;top:1066px;height:176px;display:flex;align-items:center;justify-content:center}}
#saar{{text-align:center;color:#FFF6E5}}
#hd{{top:1292px;font:500 26px 'Inter';color:#B2A7CA}}
{t['css']}
</style></head><body><div id="art"></div><div id="top"></div><div id="bot"></div>
<div class="abs" id="brand">{E(t['brand'])}</div><div id="pill">{E(it['pill'])}</div>
<div class="abs" id="hook">{E(it['hook'])}</div>
<div class="abs" id="san"><div class="l">{san}</div></div>
<div class="abs" id="ref">{E(t['ref'](it['ref']))}</div>
<div id="sbox"><div id="saar">{E(it['saar'])}</div></div>
<div class="abs" id="hd">{E(t['handle'])}</div></body></html>"""
FIT = """()=>{
const h=document.getElementById('hook');let s=parseFloat(getComputedStyle(h).fontSize);const hw=()=>{const r=document.createRange();r.selectNodeContents(h);return r.getBoundingClientRect().width};while(hw()>980&&s>34){s-=1;h.style.fontSize=s+'px';}
const sn=document.getElementById('san');let z=46;const w=()=>{let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});return m};while(w()>980&&z>28){z-=1;sn.style.fontSize=z+'px';}
const e=document.getElementById('saar');const cs=getComputedStyle(e);let f=parseFloat(cs.fontSize);const ratio=parseFloat(cs.lineHeight)/f;
while(e.getBoundingClientRect().height>3*f*ratio+2&&f>22){f-=1;e.style.fontSize=f+'px';e.style.lineHeight=(f*ratio)+'px';}
const lines=Math.round(e.getBoundingClientRect().height/(f*ratio));
return 'saar:'+f+' lines:'+lines+(lines>3?' OVERFLOW':'')+' san:'+z+' hook:'+s;}"""
if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rc.ensure_fonts(); rh.ensure_hindi_fonts()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for it in items:
            b64 = base64.b64encode(open(it['bg'], 'rb').read()).decode()
            pg.set_content(page(it, b64)); pg.wait_for_timeout(700); print(it['file'], pg.evaluate(FIT))
            pg.screenshot(path=f"{out}/{it['file']}.png")
        b.close()
