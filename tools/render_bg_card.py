#!/usr/bin/env python3
"""Verse card on an AI-painted background from bgbank/ (free, no credits).
Usage: python3 tools/render_bg_card.py items.json outdir
items.json = list of {"bg":"bgbank/n04.png","file":"gpt_3_35","ch":"3","v":"35","hook":"Comparing your life to others?",
  "pill":"YOUR OWN PATH","mean":"one short English line (<=50 chars)","san":"line1\nline2",
  "banner":"optional SWIPE hook (<=36 chars) -> also writes <file>_hook.png"}
Text sits on the bottom ~35% and top ~15%, so pick backgrounds whose subject is in the middle. Read every output PNG."""
import json, sys, os, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc
from playwright.sync_api import sync_playwright
def _base(it,scene_b64,dy,pill,hook,mean):
    san=html.escape(it['san']).replace('\n','</span><span class="l">')
    return f"""<html><head><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#080C25}}
#art{{position:absolute;left:0;top:{235+dy}px;width:1080px;height:1064px;background:url(data:image/png;base64,{scene_b64}) center/100% 100%}}
#top{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 38%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:880px;width:1080px;height:470px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.88) 32%,#080C25 62%)}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:62px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}}
#pill{{position:absolute;left:50%;top:122px;transform:translateX(-50%);height:58px;padding:0 34px;border-radius:29px;background:#E8B14F;color:#2A1A05;font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#hook{{top:215px;font:700 60px 'Playfair Display';color:#FFF6E5;white-space:nowrap}}
#san{{top:960px;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:74px}}
#san .l{{display:block;white-space:nowrap}}
#ref{{top:1105px;font:500 22px 'Inter';color:#B2A7CA;letter-spacing:1px}}
#mean{{top:1160px;font:400 33px 'Lora';color:#FFF6E5;line-height:46px;white-space:nowrap}}
#hd{{top:1288px;font:500 26px 'Inter';color:#B2A7CA}}
</style></head><body><div id="art"></div><div id="top"></div><div id="bot"></div>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{html.escape(pill)}</div>
<div class="abs" id="hook">{html.escape(hook)}</div>
<div class="abs" id="san"><span class="l">{san}</span></div>
<div class="abs" id="ref">— Bhagavad Gita {it['ch']}.{it['v']} —</div>
<div class="abs" id="mean">{html.escape(mean)}</div>
<div class="abs" id="hd">@daily.doseofgita</div></body></html>"""
FIT="""()=>{let w=[];for(const [id,f] of [['hook',60],['mean',33]]){const e=document.getElementById(id);let s=f;while(e.scrollWidth>0&&e.getBoundingClientRect().width>0){const r=document.createRange();r.selectNodeContents(e);if(r.getBoundingClientRect().width<=980||s<=24)break;s-=1;e.style.fontSize=s+'px';}w.push(id+':'+s);}
const sn=document.getElementById('san');let s=46;while(s>30){let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});if(m<=980)break;s-=1;sn.style.fontSize=s+'px';}w.push('san:'+s);return w.join(' ');}"""

def page(it,b64):
    h=_base(it,'',0,it['pill'],it['hook'],it['mean'])
    h=h.replace("#art{position:absolute;left:0;top:235px;width:1080px;height:1064px;background:url(data:image/png;base64,) center/100% 100%}",
      f"#art{{position:absolute;left:0;top:0;width:1080px;height:1350px;background:url(data:image/png;base64,{b64}) center/cover}}")
    assert 'cover' in h
    return h
if __name__=='__main__':
    items=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
    rc.ensure_fonts(); ban=[]
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1350})
        for it in items:
            b64=base64.b64encode(open(it['bg'],'rb').read()).decode()
            pg.set_content(page(it,b64)); pg.wait_for_timeout(600); print(it['file'],pg.evaluate(FIT))
            pg.screenshot(path=f"{out}/{it['file']}.png")
            if it.get('banner'): ban.append({'src':f"{out}/{it['file']}.png",'file':it['file']+'_hook','hook':it['banner'],'handle':'@daily.doseofgita'})
        b.close()
    if ban:
        json.dump(ban,open('/tmp/_bg_banners.json','w'))
        os.system(f"python3 {os.path.dirname(os.path.abspath(__file__))}/swipe_banner.py /tmp/_bg_banners.json {out}")
