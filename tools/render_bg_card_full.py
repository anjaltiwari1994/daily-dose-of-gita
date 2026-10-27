#!/usr/bin/env python3
"""DETAILED single-image verse card (1080x1350): hook + Sanskrit + FULL meaning + LEARNING + WAY FORWARD, all on the image.
For standalone (non-carousel) posts, so the image alone teaches something and says what to do. Free, no credits. English and Hindi.
Usage: python3 tools/render_bg_card_full.py items.json outdir
items = [{"lang":"en"|"hi","bg":"bgbank/n04.png","file":"f_3_35","ref":"3.35","hook":"Comparing your life to others?","pill":"YOUR OWN PATH",
          "san":"line1\\nline2","mean":"full meaning, ~100-170 chars",
          "learn":"the lesson in one clear sentence, ~70-110 chars","way":"one concrete thing to do today, ~70-110 chars"}]
Text auto-shrinks to fit; Read every PNG before scheduling."""
import json, sys, os, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc
import render_reel_hi as rh
from playwright.sync_api import sync_playwright
E = html.escape
T = {
 'en': dict(brand='DAILY DOSE OF GITA', handle='@daily.doseofgita', lm='MEANING', ll='WHAT IT TEACHES', lw='WHAT TO DO TODAY',
            ref=lambda r: f'— Bhagavad Gita {r} —',
            css="""#brand{top:58px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}
#pill{height:58px;top:118px;padding:0 34px;border-radius:29px;font:700 22px 'Inter';letter-spacing:3.5px}
#hook{top:208px;font:700 60px 'Playfair Display';color:#FFF6E5;white-space:nowrap}
#san{font-family:'Tiro Devanagari Hindi'}
#ref{font:500 22px 'Inter';letter-spacing:1px}
.lab{font:700 19px 'Inter';letter-spacing:4px}
#mean{font:400 30px 'Lora';line-height:42px}
#learn{font:600 30px 'Lora';line-height:41px}
#way{font:600 30px 'Lora';line-height:41px}"""),
 'hi': dict(brand='दैनिक गीता सार', handle='@daily.doseofgita.hindi', lm='अर्थ', ll='सीख', lw='आज क्या करें',
            ref=lambda r: f'— श्रीमद्भगवद्गीता {r} —',
            css="""#brand{top:46px;font:400 36px 'Tiro Devanagari Hindi';color:#E8B14F}
#pill{height:60px;top:114px;padding:0 34px;border-radius:30px;font:700 26px 'Noto Sans Devanagari'}
#hook{top:200px;font:700 56px 'Noto Serif Devanagari';color:#FFF6E5;white-space:nowrap;line-height:1.3}
#san{font-family:'Tiro Devanagari Hindi'}
#ref{font:500 24px 'Noto Sans Devanagari'}
.lab{font:700 22px 'Noto Sans Devanagari';letter-spacing:1px}
#mean{font:400 28px 'Noto Serif Devanagari';line-height:42px}
#learn{font:600 28px 'Noto Serif Devanagari';line-height:42px}
#way{font:600 28px 'Noto Serif Devanagari';line-height:42px}"""),
}
def page(it, b64):
    t = T[it.get('lang', 'en')]
    san = '</div><div class="l">'.join(E(l) for l in it['san'].split('\n'))
    return f"""<html><head><meta charset="utf-8"><style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#080C25}}
#art{{position:absolute;left:0;top:0;width:1080px;height:720px;background:url(data:image/png;base64,{b64}) 50% 18%/cover}}
#top{{position:absolute;left:0;top:0;width:1080px;height:480px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 36%,rgba(14,16,48,0) 100%)}}
#fade{{position:absolute;left:0;top:440px;width:1080px;height:300px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.85) 55%,#080C25 100%)}}
#solid{{position:absolute;left:0;top:740px;width:1080px;height:610px;background:#080C25}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#pill{{position:absolute;left:50%;transform:translateX(-50%);background:#E8B14F;color:#2A1A05;display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#san{{top:640px;font-size:44px;color:#E8B84A;line-height:66px}}
#san .l{{white-space:nowrap}}
#ref{{top:776px;color:#B2A7CA}}
.lab{{color:#E8B14F;margin-bottom:6px}}
.blk{{position:absolute;left:80px;width:920px}}
#mbox{{top:822px;height:168px}}
#lbox{{top:1004px;height:112px;padding-left:22px;border-left:4px solid #E8B14F}}
#wbox{{top:1124px;height:142px;padding:14px 24px;border-radius:20px;background:linear-gradient(180deg,rgba(232,177,79,.20),rgba(232,177,79,.08));border:1px solid rgba(232,177,79,.55)}}
#mean{{color:#E8DFF5}}
#learn{{color:#FFF6E5}}
#way{{color:#FFF6E5}}
#hd{{top:1303px;font:500 26px 'Inter';color:#B2A7CA}}
{t['css']}
</style></head><body><div id="art"></div><div id="top"></div><div id="fade"></div><div id="solid"></div>
<div class="abs" id="brand">{E(t['brand'])}</div><div id="pill">{E(it['pill'])}</div>
<div class="abs" id="hook">{E(it['hook'])}</div>
<div class="abs" id="san"><div class="l">{san}</div></div>
<div class="abs" id="ref">{E(t['ref'](it['ref']))}</div>
<div class="blk" id="mbox"><div class="lab">{E(t['lm'])}</div><div id="mean">{E(it['mean'])}</div></div>
<div class="blk" id="lbox"><div class="lab">{E(t['ll'])}</div><div id="learn">{E(it['learn'])}</div></div>
<div class="blk" id="wbox"><div class="lab">{E(t['lw'])}</div><div id="way">{E(it['way'])}</div></div>
<div class="abs" id="hd">{E(t['handle'])}</div></body></html>"""
FIT = """()=>{const out=[];
const h=document.getElementById('hook');let s=parseFloat(getComputedStyle(h).fontSize);const hw=()=>{const r=document.createRange();r.selectNodeContents(h);return r.getBoundingClientRect().width};while(hw()>980&&s>34){s-=1;h.style.fontSize=s+'px';}
const sn=document.getElementById('san');let z=44;const w=()=>{let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});return m};while(w()>980&&z>28){z-=1;sn.style.fontSize=z+'px';}
const fit=(id,maxLines,min)=>{const e=document.getElementById(id);const cs=getComputedStyle(e);let f=parseFloat(cs.fontSize);const ratio=parseFloat(cs.lineHeight)/f;while(e.getBoundingClientRect().height>maxLines*f*ratio+2&&f>min){f-=1;e.style.fontSize=f+'px';e.style.lineHeight=(f*ratio)+'px';}return (e.getBoundingClientRect().height>maxLines*f*ratio+3?id+' OVERFLOW':id+':'+f);};
out.push(fit('mean',3,22));out.push(fit('learn',2,22));out.push(fit('way',2,22));
return out.join(' ')+' san:'+z+' hook:'+s;}"""
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
