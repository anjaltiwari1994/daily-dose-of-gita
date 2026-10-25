#!/usr/bin/env python3
"""HINDI version. Add a 'SWIPE ->' hook banner to the bottom of a carousel's FIRST slide (1080x1350 PNG), free, no credits.
It covers the old handle line with a strip in the image's own bottom colour, draws a gold pill
[ SWIPE -> | <hook line> ] and redraws the handle (and an optional small source credit).
Usage: python3 tools/swipe_banner.py items.json outdir
items.json = list of {"src": "cards/g_6_19.png", "file": "g_6_19_hook",
                      "hook": "the 5-minute fix for a restless mind", "handle": "@daily.doseofgita",
                      "source": "" (optional, e.g. "Data: NASA")}
Hook line: short (about 38 chars or fewer), curiosity-driven, tells people what they get by swiping.
Read every output PNG before scheduling."""
import json, sys, os, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc
from PIL import Image

TOP = 1224  # strip starts here (Gita meaning box ends at 1205, Wow detail text ends near 1222)

def page(src_png, it, rgb):
    b64 = base64.b64encode(open(src_png, 'rb').read()).decode()
    r, g, b = rgb
    src = f'<div id="src">{html.escape(it["source"])}</div>' if it.get('source') else ''
    return f"""<html><head><style>*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:url(data:image/png;base64,{b64}) 0 0/1080px 1350px no-repeat}}
#strip{{position:absolute;left:0;top:{TOP-14}px;width:1080px;height:{1350-TOP+14}px;
background:linear-gradient(180deg,rgba({r},{g},{b},0) 0px,rgba({r},{g},{b},1) 14px)}}
#pill{{position:absolute;left:50%;top:{TOP+8}px;transform:translateX(-50%);height:72px;max-width:1000px;display:flex;align-items:center;
border-radius:36px;background:#E8B14F;box-shadow:0 6px 28px rgba(232,177,79,.35);padding:0 30px 0 8px;white-space:nowrap}}
#sw{{height:54px;border-radius:27px;background:#1a1205;color:#E8B14F;font:700 26px 'Noto Sans Devanagari';display:flex;align-items:center;padding:0 20px;margin-right:18px}}
#hk{{font:700 30px 'Noto Sans Devanagari';color:#1a1205}}
#hd{{position:absolute;left:0;width:1080px;top:{TOP+94}px;text-align:center;font:500 21px 'Inter';color:#B2A7CA;letter-spacing:.5px}}
#src{{position:absolute;right:28px;bottom:14px;font:400 15px 'Inter';color:rgba(184,171,208,.55)}}
</style></head><body><div id="strip"></div>
<div id="pill"><div id="sw">स्वाइप &#8594;</div><div id="hk">{html.escape(it['hook'])}</div></div>
<div id="hd">{html.escape(it.get('handle',''))}</div>{src}</body></html>"""

FIT = """()=>{const p=document.getElementById('pill'),h=document.getElementById('hk');let f=30;
while(p.scrollWidth>1000&&f>18){f-=1;h.style.fontSize=f+'px';}return p.scrollWidth>1000;}"""

if __name__ == '__main__':
    items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    import render_reel_hi as rh; rh.ensure_hindi_fonts()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for it in items:
            im = Image.open(it['src']).convert('RGB').resize((1080, 1350))
            px = [im.getpixel((x, 1346)) for x in range(20, 1060, 40)]
            rgb = tuple(sorted(c[i] for c in px)[len(px)//2] for i in range(3))
            tmp = f"/tmp/_sb_{os.getpid()}.png"; im.save(tmp)
            pg.set_content(page(tmp, it, rgb)); pg.wait_for_timeout(300); too_long = pg.evaluate(FIT)
            pg.screenshot(path=f"{out}/{it['file']}.png")
            print('rendered', it['file'], 'WARNING: hook too long, shorten it' if too_long else '')
        b.close()
