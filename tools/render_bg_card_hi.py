#!/usr/bin/env python3
"""HINDI verse card (1080x1350) on an AI-painted background from bgbank/ (free). For @daily.doseofgita.hindi.
Usage: python3 tools/render_bg_card_hi.py items.json outdir
items = [{"bg":"bgbank/n04.png","file":"gh_4_11","ref":"4.11","hook":"<Hindi hook>","pill":"<Hindi mood word>",
 "mean":"<ONE short Hindi line, ~45 chars or fewer>","san":"line1\\nline2","banner":"<Hindi swipe hook, ~34 chars or fewer, optional>"}]
With banner it also writes <file>_hook.png (slide 1 of the carousel). Read every output PNG."""
import json, sys, os, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_reel_hi as rh
from playwright.sync_api import sync_playwright
def page(it, b64):
    san = '</div><div class="l">'.join(html.escape(l) for l in it['san'].split('\n'))
    return f"""<html><head><meta charset="utf-8"><style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#080C25}}
#art{{position:absolute;left:0;top:0;width:1080px;height:1350px;background:url(data:image/png;base64,{b64}) center/cover}}
#top{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 38%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:860px;width:1080px;height:490px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.88) 32%,#080C25 62%)}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:52px;font:400 36px 'Tiro Devanagari Hindi';color:#E8B14F}}
#pill{{position:absolute;left:50%;top:122px;transform:translateX(-50%);height:60px;padding:0 34px;border-radius:30px;background:#E8B14F;color:#2A1A05;font:700 26px 'Noto Sans Devanagari';display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#hook{{top:210px;font:700 56px 'Noto Serif Devanagari';color:#FFF6E5;white-space:nowrap;line-height:1.3}}
#san{{top:928px;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:74px}}
#san .l{{white-space:nowrap}}
#ref{{top:1086px;font:500 24px 'Noto Sans Devanagari';color:#B2A7CA}}
#mean{{position:absolute;left:80px;width:920px;top:1128px;height:84px;display:flex;align-items:center;justify-content:center;font:400 33px 'Noto Serif Devanagari';color:#FFF6E5;line-height:44px}}
#hd{{top:1290px;font:500 26px 'Inter';color:#B2A7CA}}
</style></head><body><div id="art"></div><div id="top"></div><div id="bot"></div>
<div class="abs" id="brand">दैनिक गीता सार</div><div id="pill">{html.escape(it['pill'])}</div>
<div class="abs" id="hook">{html.escape(it['hook'])}</div>
<div class="abs" id="san"><div class="l">{san}</div></div>
<div class="abs" id="ref">— श्रीमद्भगवद्गीता {html.escape(it['ref'])} —</div>
<div id="mean"><span id="ms">{html.escape(it['mean'])}</span></div>
<div class="abs" id="hd">@daily.doseofgita.hindi</div></body></html>"""
FIT = """()=>{const h=document.getElementById('hook');let s=56;const hw=()=>{const r=document.createRange();r.selectNodeContents(h);return r.getBoundingClientRect().width};while(hw()>980&&s>34){s-=1;h.style.fontSize=s+'px';}
const sn=document.getElementById('san');let z=46;const w=()=>{let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});return m};while(w()>980&&z>28){z-=1;sn.style.fontSize=z+'px';}
const m=document.getElementById('mean'),ms=document.getElementById('ms');let f=33;while(ms.getBoundingClientRect().height>84&&f>22){f-=1;m.style.fontSize=f+'px';m.style.lineHeight=(f*1.4)+'px';}
return s+' '+z+' '+f;}"""
if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rh.ensure_hindi_fonts(); ban = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for it in items:
            b64 = base64.b64encode(open(it['bg'], 'rb').read()).decode()
            pg.set_content(page(it, b64)); pg.wait_for_timeout(700); print(it['file'], pg.evaluate(FIT))
            pg.screenshot(path=f"{out}/{it['file']}.png")
            if it.get('banner'): ban.append({'src': f"{out}/{it['file']}.png", 'file': it['file'] + '_hook', 'hook': it['banner'], 'handle': '@daily.doseofgita.hindi'})
        b.close()
    if ban:
        json.dump(ban, open('/tmp/_bgh_banners.json', 'w'))
        os.system(f"python3 {os.path.dirname(os.path.abspath(__file__))}/swipe_banner_hi.py /tmp/_bgh_banners.json {out}")
