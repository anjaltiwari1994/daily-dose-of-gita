#!/usr/bin/env python3
"""Animated Gita Reel (1080x1920 mp4, 11 s, with music) from the same design as render_cards.py. No credits.
The video starts with the brand, mood pill, hook and first Sanskrit line ALREADY on screen, over a slowly turning gold mandala and rising
light specks (so frame 0 is never an empty dark screen); the second line, meaning box and meaning words then build in by about 5 s and the
finished layout holds to the end. Schedule with videoCoverMilliseconds 10500 (last frame = cover).
Usage: python3 tools/render_reel.py input.json out.mp4   (input.json = ONE card object, same fields as render_cards.py)"""
import json, sys, os, tempfile, subprocess, html
sys.path.insert(0, os.path.dirname(__file__))
import render_cards as rc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'wow'))
import music

FPS, DUR, OFF = 24, 11.0, 235   # video length 11 s
COVER_FRAMES = 0                # no cover flash; the cover is chosen in Metricool (videoCoverMilliseconds 10500)
def build(p):
    base = rc.page(p)
    base = base.replace('<style>', '<style>body{height:1920px!important}#wrap{position:absolute;left:0;top:%dpx;width:1080px;height:1350px;transform-origin:50%% 45%%}' % OFF, 1)
    base = base.replace('<style>', '<style>#fx{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:0}#wrap{z-index:1}', 1)
    base = base.replace('<body>', '<body><canvas id="fx" width="1080" height="1920"></canvas><div id="wrap">', 1).replace('</body>', '</div></body>')
    return base
PREP = """()=>{(%s)();
const san=document.getElementById('ss');san.innerHTML=san.innerHTML.split('<br>').map(l=>'<div class="ln">'+l+'</div>').join('');
const ms=document.getElementById('ms');ms.innerHTML=ms.textContent.split(' ').map(w=>'<span class="w">'+w+'</span>').join(' ');}""" % rc.FIT[2:] if False else None
PREP = "()=>{(" + rc.FIT + ")();const san=document.getElementById('ss');san.innerHTML=san.innerHTML.split('<br>').map(l=>'<div class=\"ln\">'+l+'</div>').join('');const ms=document.getElementById('ms');ms.innerHTML=ms.textContent.split(' ').map(w=>'<span class=\"w\">'+w+'</span>').join(' ');}"
TICK = """(a)=>{const [t,zt]=a;const e=(a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a))), s=x=>x*x*(3-2*x);
const show=(sel,a,b,dy=26)=>{document.querySelectorAll(sel).forEach((el,i)=>{const k=s(e(a[i]??a[0],b[i]??b[0]));el.style.opacity=k;el.style.transform='translateY('+((1-k)*dy)+'px)';});};
show('#brand',[-1],[-0.5]);show('#pill',[-1],[-0.5]);show('#hook',[-1],[-0.5]);show('#div',[-1],[-0.5]);
show('.ln',[-1,0.3],[-0.5,1.0],24);show('#ref',[1.0],[1.5],14);show('#box',[1.4],[2.0],10);show('#ml',[1.5],[2.0],10);
const ws=[...document.querySelectorAll('.w')];ws.forEach((w,i)=>{const a=1.8+i*(3.4/ws.length);w.style.opacity=s(e(a,a+0.35));});
show('#hd',[2.0],[2.6],10);
const z=1+0.035*Math.min(1,zt/DUR);document.getElementById('wrap').style.transform='scale('+z+')';
// background layer: soft gold glow, slowly turning mandala, rising light specks
const cv=document.getElementById('fx'),x=cv.getContext('2d');x.clearRect(0,0,1080,1920);
const g=x.createRadialGradient(540,835,0,540,835,560);g.addColorStop(0,'rgba(232,177,79,0.20)');g.addColorStop(0.6,'rgba(150,90,120,0.08)');g.addColorStop(1,'rgba(232,177,79,0)');x.fillStyle=g;x.fillRect(0,0,1080,1920);
x.save();x.translate(540,835);
for(let r=0;r<4;r++){const R=190+r*100,n=8+r*4,rot=t*(r%2?-1:1)*(0.10+0.03*r);x.save();x.rotate(rot);x.strokeStyle='rgba(232,177,79,'+(0.30-0.05*r)+')';x.lineWidth=1.8;x.setLineDash(r%2?[4,12]:[20,10]);x.beginPath();x.arc(0,0,R,0,6.283);x.stroke();x.setLineDash([]);
for(let k=0;k<n;k++){x.save();x.rotate(k/n*6.283);x.beginPath();x.ellipse(R,0,17-r*2,5.5,0,0,6.283);x.stroke();x.restore();}x.restore();}
x.restore();
const rd=(i,m,c)=>{const v=Math.sin(i*m)*c;return v-Math.floor(v);};
x.save();x.shadowColor='rgba(255,200,110,0.9)';x.shadowBlur=12;
for(let i=0;i<80;i++){const r1=rd(i,12.9898,43758.5453),r2=rd(i,78.233,12345.6789),r3=rd(i,39.346,9876.54);
const y=(((r2*1920)-t*(28+r3*70))%1920+1920)%1920,px=r1*1080+Math.sin(t*0.8+i)*20,al=(0.25+0.55*Math.abs(Math.sin(t*1.3+i)))*(0.35+0.65*(1-y/1920));
x.fillStyle='rgba(255,215,140,'+al.toFixed(3)+')';x.beginPath();x.arc(px,y,1.5+r3*3.4,0,6.283);x.fill();}
x.restore();}""".replace('DUR', str(DUR))

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
            pg.evaluate(TICK, [i / FPS, i / FPS]); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
        b.close()
    music.make('gita', DUR, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{tmp}/m.wav', '-af', 'aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000', f'{tmp}/m2.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f%04d.jpg', '-i', f'{tmp}/m2.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out)
