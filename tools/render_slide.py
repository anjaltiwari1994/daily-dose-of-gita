#!/usr/bin/env python3
"""Second slide for a 2-slide CAROUSEL (1080x1350 PNG), free, no credits. Slide 1 is the normal card
(render_cards.py for Gita, wow/card.py for Wow); this script makes slide 2 in the same colours.
Usage: python3 tools/render_slide.py slides.json outdir
slides.json = list of objects:
  file     output name without .png (convention: <slide-1 file>_s2, e.g. g_6_35_s2 or w_titan_lakes_s2)
  theme    "gita" or "wow"
  pill     small label, ALL CAPS, e.g. 'APPLY IT TODAY' (gita) or 'WHY IT HAPPENS' (wow)
  title    one short line, about 34 chars or fewer (e.g. 'How to calm a restless mind')
  points   2 or 3 short points, each about 70 chars or fewer (plain sentences, no emoji)
  share    one share line naming WHO to send it to, about 60 chars or fewer, e.g.
           'Send this to a friend who overthinks everything' (no emoji: the fonts have none)
  ref      optional small line above the handle, e.g. 'Bhagavad Gita 6.35' or 'Source: NASA'
  handle   '@daily.doseofgita' or '@your.dailydoseofwow'
Text auto-shrinks to fit; still Read every PNG before scheduling."""
import json, sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc

THEMES = {
 'gita': dict(brand='DAILY DOSE OF GITA', bg="radial-gradient(ellipse 560px 460px at 50% 40%,rgba(120,72,82,.40) 0%,rgba(70,44,86,.22) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,#1C1433 0%,#150F2A 55%,#0E0A1C 100%)",
              gold='#E8B14F', text='#FFF6E5', muted='#B2A7CA', title_font="'Playfair Display'", body_font="'Lora'", num_ink='#2A1A05'),
 'wow':  dict(brand='DAILY DOSE OF WOW', bg="radial-gradient(ellipse 700px 520px at 20% 18%,rgba(70,60,190,.30) 0%,rgba(0,0,0,0) 70%),radial-gradient(ellipse 600px 500px at 90% 90%,rgba(40,150,170,.18) 0%,rgba(0,0,0,0) 70%),linear-gradient(180deg,#0b0716 0%,#06040f 60%,#030208 100%)",
              gold='#E8B14F', text='#EDE6F5', muted='#cfc8b8', title_font="'Playfair Display'", body_font="'Inter'", num_ink='#1a1205'),
}

def page(s):
    t = THEMES[s.get('theme', 'gita')]
    pts = ''.join(f'<div class="pt"><div class="n">{i+1}</div><div class="tx">{html.escape(p)}</div></div>' for i, p in enumerate(s['points'][:3]))
    ref = f'<div class="abs" id="ref">{html.escape(s["ref"])}</div>' if s.get('ref') else ''
    return f"""<html><head><style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{t['bg']}}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:70px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:{t['gold']}}}
#pill{{position:absolute;left:340px;top:140px;width:400px;height:58px;border-radius:29px;background:{t['gold']};color:{t['num_ink']};font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;justify-content:center}}
#title{{top:250px;padding:0 80px;font:700 60px {t['title_font']};line-height:74px;color:{t['text']}}}
#pts{{position:absolute;left:90px;width:900px;top:430px;height:560px;display:flex;flex-direction:column;justify-content:center;gap:34px}}
.pt{{display:flex;align-items:flex-start;gap:28px;padding:30px 34px;border-radius:26px;border:1px solid rgba(232,177,79,.28);background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.03))}}
.n{{flex:0 0 58px;height:58px;border-radius:29px;background:{t['gold']};color:{t['num_ink']};font:800 30px 'Inter';display:flex;align-items:center;justify-content:center}}
.tx{{font:400 36px {t['body_font']};line-height:50px;color:{t['text']}}}
#share{{top:1050px;padding:0 90px;font:italic 600 38px 'Playfair Display';line-height:52px;color:{t['gold']}}}
#ref{{top:1205px;font:500 22px 'Inter';letter-spacing:1px;color:{t['muted']}}}
#hd{{top:1250px;font:500 26px 'Inter';color:{t['muted']}}}
</style></head><body>
<div class="abs" id="brand">{t['brand']}</div><div id="pill">{html.escape(s['pill'])}</div>
<div class="abs" id="title">{html.escape(s['title'])}</div>
<div id="pts">{pts}</div>
<div class="abs" id="share">{html.escape(s['share'])}</div>{ref}
<div class="abs" id="hd">{html.escape(s.get('handle',''))}</div></body></html>"""

FIT = """()=>{const shrink=(el,maxH,min,lh)=>{let f=parseFloat(getComputedStyle(el).fontSize);while(el.scrollHeight>maxH&&f>min){f-=2;el.style.fontSize=f+'px';el.style.lineHeight=(f*lh)+'px';}};
shrink(document.getElementById('title'),160,40,1.23);
const box=document.getElementById('pts');let f=36;const txs=[...document.querySelectorAll('.tx')];
while(box.scrollHeight>box.clientHeight+2&&f>26){f-=2;txs.forEach(t=>{t.style.fontSize=f+'px';t.style.lineHeight=(f*1.39)+'px';});}
shrink(document.getElementById('share'),120,28,1.37);
const p=document.getElementById('pill');let pf=22;while(p.scrollWidth>p.clientWidth&&pf>14){pf-=1;p.style.fontSize=pf+'px';}
return {pointsOverflow: box.scrollHeight>box.clientHeight+2};}"""

if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in items:
            pg.set_content(page(s)); pg.wait_for_timeout(500); info = pg.evaluate(FIT); pg.wait_for_timeout(150)
            pg.screenshot(path=f"{out}/{s['file']}.png")
            print('rendered', s['file'], 'WARNING: points still too long, shorten them' if info['pointsOverflow'] else '')
        b.close()
