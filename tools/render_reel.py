#!/usr/bin/env python3
"""Animated Gita Reel (1080x1920 mp4, silent) from the same design as render_cards.py. No credits.
Usage: python3 tools/render_reel.py input.json out.mp4   (input.json = ONE card object, same fields as render_cards.py)"""
import json, sys, os, tempfile, subprocess, html
sys.path.insert(0, os.path.dirname(__file__))
import render_cards as rc

FPS, DUR, OFF = 24, 10.0, 235
def build(p):
    base = rc.page(p)
    base = base.replace('<style>', '<style>body{height:1920px!important}#wrap{position:absolute;left:0;top:%dpx;width:1080px;height:1350px;transform-origin:50%% 45%%}' % OFF, 1)
    base = base.replace('<body>', '<body><div id="wrap">', 1).replace('</body>', '</div></body>')
    return base
PREP = """()=>{(%s)();
const san=document.getElementById('ss');san.innerHTML=san.innerHTML.split('<br>').map(l=>'<div class="ln">'+l+'</div>').join('');
const ms=document.getElementById('ms');ms.innerHTML=ms.textContent.split(' ').map(w=>'<span class="w">'+w+'</span>').join(' ');}""" % rc.FIT[2:] if False else None
PREP = "()=>{(" + rc.FIT + ")();const san=document.getElementById('ss');san.innerHTML=san.innerHTML.split('<br>').map(l=>'<div class=\"ln\">'+l+'</div>').join('');const ms=document.getElementById('ms');ms.innerHTML=ms.textContent.split(' ').map(w=>'<span class=\"w\">'+w+'</span>').join(' ');}"
TICK = """(t)=>{const e=(a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a))), s=x=>x*x*(3-2*x);
const show=(sel,a,b,dy=26)=>{document.querySelectorAll(sel).forEach((el,i)=>{const k=s(e(a[i]??a[0],b[i]??b[0]));el.style.opacity=k;el.style.transform='translateY('+((1-k)*dy)+'px)';});};
show('#brand',[0.1],[0.8]);show('#pill',[0.5],[1.1]);show('#hook',[1.0],[1.9],30);show('#div',[1.9],[2.4]);
show('.ln',[2.5,3.7],[3.6,4.8],24);show('#ref',[4.9],[5.5],14);show('#box',[5.6],[6.2],10);show('#ml',[5.8],[6.3],10);
const ws=[...document.querySelectorAll('.w')];ws.forEach((w,i)=>{const a=6.3+i*(2.6/ws.length);w.style.opacity=s(e(a,a+0.35));});
show('#hd',[6.4],[7.0],10);
const z=1+0.035*e(0,DUR);document.getElementById('wrap').style.transform='scale('+z+')';}""".replace('DUR', str(DUR))

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); p = p[0] if isinstance(p, list) else p; out = sys.argv[2]
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(build(p)); pg.wait_for_timeout(500); pg.evaluate(PREP); pg.wait_for_timeout(200)
        n = int(FPS * DUR)
        for i in range(n):
            pg.evaluate(TICK, i / FPS); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
        b.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f%04d.jpg', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out], check=True)
    print('wrote', out)
