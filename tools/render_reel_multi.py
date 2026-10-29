#!/usr/bin/env python3
"""Multi-scene Gita Reel (1080x1920, 15 s, music): several bgbank backgrounds crossfade with a slow zoom, text builds on top.
Usage: python3 tools/render_reel_multi.py input.json out.mp4
input.json = {"lang":"en"|"hi","bgs":["bgbank/k05.png",..(2-4)],"hook":"..","pill":"..","san":"l1\\nl2","ref":"9.26","mean":"2-3 line saar"}
Scene i starts at i*DUR*0.25 (crossfade 0.9 s). Cover: videoCoverMilliseconds 14000."""
import json, sys, os, tempfile, subprocess, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_reel_bg as rb, render_reel_bg_hi as rbh, render_reel_hi as rh
from playwright.sync_api import sync_playwright
DUR = 15.0
def page(p):
    hi = p.get('lang') == 'hi'
    q = dict(p); q['bg'] = p['bgs'][0]
    h = (rbh.page if hi else rb.page)(q)
    layers = ''.join(f'<div class="bgl" style="background-image:url(data:image/png;base64,{base64.b64encode(open(b,"rb").read()).decode()})"></div>' for b in p['bgs'])
    assert '<div id="bg"></div>' in h
    h = h.replace('<div id="bg"></div>', layers)
    old = "top:1180px;width:1080px;height:740px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.9) 28%,#080C25 55%)"
    assert old in h
    h = h.replace(old, "top:1050px;width:1080px;height:870px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.88) 22%,#080C25 40%)")
    h = h.replace('</style>', '.bgl{position:absolute;left:0;top:0;width:1080px;height:1920px;background-size:cover;background-position:center;transform-origin:50% 55%;opacity:0}</style>', 1)
    return h
TICK = """(t)=>{const e=(a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a))),s=x=>x*x*(3-2*x);
const show=(sel,a,b,dy=24)=>{document.querySelectorAll(sel).forEach((el,i)=>{const k=s(e(a[i]??a[0],b[i]??b[0]));el.style.opacity=k;el.style.transform=(el.id=='pill'?'translateX(-50%) ':'')+'translateY('+((1-k)*dy)+'px)';});};
show('#brand',[-1],[-0.5]);show('#pill',[-1],[-0.5]);show('#hook',[-1],[-0.5]);
show('.ln',[3.0],[3.8]);show('#ref',[4.0],[4.5],12);show('#hd',[2.2],[2.8],10);
const ws=[...document.querySelectorAll('.w')];ws.forEach((w,i)=>{const a=7.0+i*(4.0/ws.length);w.style.opacity=s(e(a,a+0.35));});
const L=[...document.querySelectorAll('.bgl')],n=L.length,step=DUR_/n;
L.forEach((el,i)=>{const st=i*step;el.style.opacity=i==0?1:s(e(st-0.9,st));const z=Math.min(1,Math.max(0,(t-st+0.9)/(step+0.9)));el.style.transform='scale('+(1.0+0.07*z)+') translateY('+(-12*z)+'px)';el.style.zIndex=i;});
const cv=document.getElementById('fx'),x=cv.getContext('2d');x.clearRect(0,0,1080,1920);
const rd=(i,m,c)=>{const v=Math.sin(i*m)*c;return v-Math.floor(v);};
x.save();x.shadowColor='rgba(255,200,110,0.9)';x.shadowBlur=12;
for(let i=0;i<70;i++){const r1=rd(i,12.9898,43758.5453),r2=rd(i,78.233,12345.6789),r3=rd(i,39.346,9876.54);
const y=(((r2*1920)-t*(28+r3*70))%1920+1920)%1920,px=r1*1080+Math.sin(t*0.8+i)*20,al=(0.2+0.5*Math.abs(Math.sin(t*1.3+i)))*(0.3+0.7*(1-y/1920));
x.fillStyle='rgba(255,215,140,'+al.toFixed(3)+')';x.beginPath();x.arc(px,y,1.3+r3*3,0,6.283);x.fill();}
x.restore();}""".replace('DUR_', str(DUR))
if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]
    rh.ensure_hindi_fonts()
    tmp = tempfile.mkdtemp(); FPS = 24
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(page(p)); pg.wait_for_timeout(900); print('fit', pg.evaluate(rb.FITJS))
        dbg = {int(x * FPS) for x in (2, 5, 9, 12)}
        for i in range(int(FPS * DUR)):
            pg.evaluate(TICK, i / FPS); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
            if i in dbg: pg.screenshot(path=out.replace('.mp4', f'_t{i}.png'))
            if i == int(FPS * DUR) - 1: pg.screenshot(path=out.replace('.mp4', '_last.png'))
        b.close()
    rb.music.make('gita', DUR, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000',f'{tmp}/m2.wav'],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%04d.jpg','-i',f'{tmp}/m2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],check=True)
    print('wrote', out)
