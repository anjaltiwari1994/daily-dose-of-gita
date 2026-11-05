#!/usr/bin/env python3
"""Gita 'verse + apply it' Reel (1080x1920 mp4, 20 s, music, free). Same content as a carousel (slide 1 verse + slide 2 steps).
Usage: python3 tools/render_reel_apply.py input.json out.mp4
input.json = {
 "bg":"bgbank/n07.png",
 "big":"[Overthinking] is\\nstealing your sleep?",   1-3 lines, ~22 chars/line, [word] = gold highlight. FIRST-SECOND HOOK:
                                                      make the problem feel big, or the fix feel easy/fast.
 "sub":"Krishna's 3-step fix",                         gold line under the big hook (~28 chars), promise of the payoff
 "hook":"Can't switch off your mind?",                 small hook kept at the top after 2.6 s (~40 chars)
 "pill":"OVERTHINKING", "san":"line1\\nline2", "ref":"6.35", "mean":"short English line (~90 chars)",
 "title":"How to calm a racing mind", "points":["..","..",".."], "share":"Send this to a friend who overthinks"}
Timeline: 0-2.6 s big hook on screen from frame 0 | 2.6-8.6 s verse + meaning | 8.6-20 s APPLY IT TODAY: title, 3 steps one by one, share line.
Cover: videoCoverMilliseconds 19500 (everything visible). Debug PNGs (0 s, 6 s, 13 s, last frame) are written to the temp dir, never into reels/; paths are printed."""
import json, sys, os, re, tempfile, subprocess, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wow'))
import render_reel_bg as rb, render_cards as rc, music
FPS, DUR = 24, 20.0

def big_html(t):
    out = []
    for line in t.split('\n'):
        e = html.escape(line)
        e = re.sub(r'\[(.+?)\]', r'<span class="hl">\1</span>', e)
        out.append(f'<div class="bl">{e}</div>')
    return ''.join(out)

def page(p):
    h = rb.page(p)
    pts = ''.join(f'<div class="pt"><div class="n">{i+1}</div><div class="tx">{html.escape(x)}</div></div>' for i, x in enumerate(p['points'][:3]))
    extra_css = """#dim{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#080C25;opacity:.6}
#big{position:absolute;left:60px;width:960px;top:640px;text-align:center;font:800 92px 'Playfair Display';line-height:108px;color:#FFF6E5;text-shadow:0 4px 30px rgba(0,0,0,.85)}
.bl{white-space:nowrap}.hl{color:#F2C35E}
#sub{position:absolute;left:0;width:1080px;text-align:center;top:1080px;font:700 44px 'Inter';color:#F2C35E;letter-spacing:1px;text-shadow:0 3px 20px rgba(0,0,0,.9)}
#arrow{position:absolute;left:0;width:1080px;text-align:center;top:1160px;font:700 54px 'Inter';color:#F2C35E}
#ap{position:absolute;left:0;width:1080px;top:700px;display:flex;justify-content:center}
#ap span{height:56px;padding:0 34px;border-radius:28px;background:#E8B14F;color:#2A1A05;font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center}
#tt{position:absolute;left:70px;width:940px;top:790px;text-align:center;font:700 58px 'Playfair Display';line-height:70px;color:#FFF6E5}
#pts{position:absolute;left:80px;width:920px;top:960px;height:640px;display:flex;flex-direction:column;justify-content:center;gap:30px}
.pt{display:flex;align-items:flex-start;gap:26px;padding:28px 32px;border-radius:26px;border:1px solid rgba(232,177,79,.35);background:rgba(20,18,50,.72)}
.n{flex:0 0 60px;height:60px;border-radius:30px;background:#E8B14F;color:#2A1A05;font:800 30px 'Inter';display:flex;align-items:center;justify-content:center}
.tx{font:400 38px 'Lora';line-height:52px;color:#FFF6E5}
#sh{position:absolute;left:80px;width:920px;top:1640px;text-align:center;font:italic 600 40px 'Playfair Display';line-height:54px;color:#E8B14F}
#hd{z-index:20;top:1810px !important}"""
    h = h.replace('</style>', extra_css + '</style>', 1)
    h = h.replace('<canvas id="fx"', '<div id="dim"></div><canvas id="fx"', 1)
    h = h.replace('</body>', f"""<div id="big">{big_html(p['big'])}</div><div id="sub">{html.escape(p.get('sub',''))}</div><div id="arrow">&#8595;</div>
<div id="ap"><span>APPLY IT TODAY</span></div><div id="tt">{html.escape(p['title'])}</div><div id="pts">{pts}</div><div id="sh">{html.escape(p['share'])}</div></body>""", 1)
    return h

FIT2 = """()=>{const big=document.getElementById('big');let f=92;const W=()=>Math.max(...[...big.querySelectorAll('.bl')].map(l=>{const r=document.createRange();r.selectNodeContents(l);return r.getBoundingClientRect().width}));
while(W()>960&&f>56){f-=2;big.style.fontSize=f+'px';big.style.lineHeight=(f*1.17)+'px';}
const bh=big.getBoundingClientRect().height;big.style.top=(880-bh/2)+'px';
document.getElementById('sub').style.top=(880+bh/2+40)+'px';document.getElementById('arrow').style.top=(880+bh/2+115)+'px';
const tt=document.getElementById('tt');let g=58;while(tt.scrollHeight>150&&g>40){g-=2;tt.style.fontSize=g+'px';tt.style.lineHeight=(g*1.2)+'px';}
const box=document.getElementById('pts');let k=38;const txs=[...document.querySelectorAll('.tx')];
while(box.scrollHeight>box.clientHeight+2&&k>26){k-=2;txs.forEach(t=>{t.style.fontSize=k+'px';t.style.lineHeight=(k*1.37)+'px';});}
const sh=document.getElementById('sh');let m=40;while(sh.scrollHeight>120&&m>28){m-=2;sh.style.fontSize=m+'px';sh.style.lineHeight=(m*1.35)+'px';}
return {big:f,title:g,steps:k,share:m,overflow:box.scrollHeight>box.clientHeight+2};}"""

TICK = """(t)=>{const e=(a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a))),s=x=>x*x*(3-2*x);
const op=(id,v,dy=0,base='')=>{const el=document.getElementById(id);el.style.opacity=v;el.style.transform=base+'translateY('+dy+'px)';};
// phase A: big hook visible from frame 0, out 2.3-2.8
const A=1-s(e(2.3,2.8));op('big',A,-(1-A)*30);op('sub',A);op('arrow',A,Math.sin(t*6)*8);
// brand, pill and small hook: hidden during big hook, in 2.6-3.1, stay to the end
const H=s(e(2.6,3.1));op('brand',H);op('pill',H,(1-H)*20,'translateX(-50%) ');op('hook',H,(1-H)*20);
// phase B: verse 3.0-8.6
const B=s(e(3.0,3.6))*(1-s(e(8.4,8.9)));
document.querySelectorAll('.ln').forEach(l=>{l.style.opacity=B;});op('ss',1);op('ref',s(e(3.6,4.1))*(1-s(e(8.4,8.9))));
const ws=[...document.querySelectorAll('.w')];ws.forEach((w,i)=>{const a=3.8+i*(3.4/ws.length);w.style.opacity=s(e(a,a+0.3))*(1-s(e(8.4,8.9)));});
op('ml',1);op('hd',1);
// dim layer: strong behind big hook, light during verse, strong for steps
const d=0.62-0.5*s(e(2.4,3.0))+0.3*s(e(8.5,9.2));document.getElementById('dim').style.opacity=d;
// phase C: apply it today
op('ap',s(e(8.8,9.3)),(1-s(e(8.8,9.3)))*20);op('tt',s(e(9.0,9.6)),(1-s(e(9.0,9.6)))*20);
[...document.querySelectorAll('.pt')].forEach((el,i)=>{const a=9.9+i*2.0,k=s(e(a,a+0.5));el.style.opacity=k;el.style.transform='translateX('+((1-k)*60)+'px)';});
op('sh',s(e(16.2,16.8)),(1-s(e(16.2,16.8)))*16);
document.getElementById('bg').style.transform='scale('+(1+0.1*Math.min(1,t/20))+') translateY('+(-16*Math.min(1,t/20))+'px)';
const cv=document.getElementById('fx'),x=cv.getContext('2d');x.clearRect(0,0,1080,1920);
const rd=(i,m,c)=>{const v=Math.sin(i*m)*c;return v-Math.floor(v);};
x.save();x.shadowColor='rgba(255,200,110,0.9)';x.shadowBlur=12;
for(let i=0;i<70;i++){const r1=rd(i,12.9898,43758.5453),r2=rd(i,78.233,12345.6789),r3=rd(i,39.346,9876.54);
const y=(((r2*1920)-t*(28+r3*70))%1920+1920)%1920,px=r1*1080+Math.sin(t*0.8+i)*20,al=(0.2+0.5*Math.abs(Math.sin(t*1.3+i)))*(0.3+0.7*(1-y/1920));
x.fillStyle='rgba(255,215,140,'+al.toFixed(3)+')';x.beginPath();x.arc(px,y,1.3+r3*3,0,6.283);x.fill();}
x.restore();}"""

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(); N = int(FPS * DUR)
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(page(p)); pg.wait_for_timeout(700)
        print('fit', pg.evaluate(rb.FITJS), pg.evaluate(FIT2))
        dbg = {0: '_t0', int(6 * FPS): '_t6', int(13 * FPS): '_t13', N - 1: '_last'}
        for i in range(N):
            pg.evaluate(TICK, i / FPS); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
            if i in dbg:
                dp = os.path.join(tempfile.gettempdir(), os.path.basename(out).replace('.mp4', dbg[i] + '.png'))
                pg.screenshot(path=dp); print('debug frame', dp)
        b.close()
    import calm_audio  # river water + droplets + tanpura + soft flute + temple bells
    calm_audio.make(DUR, f'{tmp}/m.wav', bell2=8.6)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.6:120:0.25,lowpass=f=7000,loudnorm=I=-17:TP=-1.5:LRA=11','-ar','44100',f'{tmp}/m2.wav'],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%04d.jpg','-i',f'{tmp}/m2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],check=True)
    print('wrote', out)
