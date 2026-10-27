#!/usr/bin/env python3
"""Gita Reel (1080x1920 mp4, 14 s, music) over a supplied background image (e.g. made in ChatGPT). No credits.
Usage: python3 tools/render_reel_bg.py input.json out.mp4
input.json = {"bg":"path.png","hook":"..","pill":"..","san":"line1\\nline2","ref":"6.25","mean":"2-3 line saar (centred)"}
Brand, pill and hook are on screen from frame 0; Sanskrit lines, ref and meaning build in by ~5 s; bg slowly zooms. Cover = last frame (videoCoverMilliseconds 10500)."""
import json, sys, os, tempfile, subprocess, base64, html
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'wow'))
import render_cards as rc, music
FPS, DUR = 24, 14.0
def page(p):
    b64 = base64.b64encode(open(p['bg'], 'rb').read()).decode()
    san = '</div><div class="ln">'.join(html.escape(l) for l in p['san'].split('\n'))
    words = ''.join(f'<span class="w">{html.escape(w)}</span> ' for w in p['mean'].split())
    return f"""<html><head><style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#080C25}}
#bg{{position:absolute;left:0;top:0;width:1080px;height:1920px;background:url(data:image/png;base64,{b64}) center/cover;transform-origin:50% 55%}}
#top{{position:absolute;left:0;top:0;width:1080px;height:760px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 40%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:1180px;width:1080px;height:740px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.9) 28%,#080C25 55%)}}
#fx{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:330px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}}
#pill{{position:absolute;left:50%;top:385px;transform:translateX(-50%);height:58px;padding:0 34px;border-radius:29px;background:#E8B14F;color:#2A1A05;font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;white-space:nowrap}}
#hook{{top:480px;font:700 60px 'Playfair Display';color:#FFF6E5;white-space:nowrap}}
#ss{{top:1235px;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:74px}}
.ln{{white-space:nowrap}}
#ref{{top:1390px;font:500 22px 'Inter';color:#B2A7CA;letter-spacing:1px}}
#ml{{top:1440px;font:400 33px 'Lora';color:#FFF6E5;line-height:46px;padding:0 80px}}
#hd{{top:1650px;font:500 26px 'Inter';color:#B2A7CA}}
</style></head><body><div id="bg"></div><div id="top"></div><div id="bot"></div><canvas id="fx" width="1080" height="1920"></canvas>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{html.escape(p['pill'])}</div><div class="abs" id="hook">{html.escape(p['hook'])}</div>
<div class="abs" id="ss"><div class="ln">{san}</div></div><div class="abs" id="ref">— Bhagavad Gita {p['ref']} —</div>
<div class="abs" id="ml">{words}</div><div class="abs" id="hd">@daily.doseofgita</div></body></html>"""
FITJS = """()=>{const h=document.getElementById('hook');let s=60;const hw=()=>{const r=document.createRange();r.selectNodeContents(h);return r.getBoundingClientRect().width};while(hw()>980&&s>34){s--;h.style.fontSize=s+'px';}
const ss=document.getElementById('ss');ss.querySelectorAll('.ln').forEach(l=>{});let z=46;const w=()=>{let m=0;ss.querySelectorAll('.ln').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});return m};while(w()>980&&z>30){z--;ss.style.fontSize=z+'px';}const ml=document.getElementById('ml');let f=parseFloat(getComputedStyle(ml).fontSize);const rt=parseFloat(getComputedStyle(ml).lineHeight)/f;while(ml.getBoundingClientRect().height>3*f*rt+2&&f>22){f--;ml.style.fontSize=f+'px';ml.style.lineHeight=(f*rt)+'px';}return s+' '+z+' saar:'+f+' lines:'+Math.round(ml.getBoundingClientRect().height/(f*rt));}"""
TICK = """(t)=>{const e=(a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a))),s=x=>x*x*(3-2*x);
const show=(sel,a,b,dy=24)=>{document.querySelectorAll(sel).forEach((el,i)=>{const k=s(e(a[i]??a[0],b[i]??b[0]));el.style.opacity=k;el.style.transform=(el.id=='pill'?'translateX(-50%) ':'')+'translateY('+((1-k)*dy)+'px)';});};
show('#brand',[-1],[-0.5]);show('#pill',[-1],[-0.5]);show('#hook',[-1],[-0.5]);
show('.ln',[0.2],[0.9]);show('#ref',[1.0],[1.5],12);show('#hd',[2.2],[2.8],10);
const ws=[...document.querySelectorAll('.w')];ws.forEach((w,i)=>{const a=1.5+i*(5.5/ws.length);w.style.opacity=s(e(a,a+0.35));});
document.getElementById('bg').style.transform='scale('+(1+0.09*Math.min(1,t/14))+') translateY('+(-14*Math.min(1,t/14))+'px)';
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
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(page(p)); pg.wait_for_timeout(600); print('fit', pg.evaluate(FITJS))
        for i in range(int(FPS * DUR)):
            pg.evaluate(TICK, i / FPS); pg.screenshot(path=f'{tmp}/f{i:04d}.jpg', type='jpeg', quality=93)
            if i == int(FPS*DUR)-1: pg.screenshot(path=out.replace('.mp4', '_last.png'))
        b.close()
    music.make('gita', DUR, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000',f'{tmp}/m2.wav'],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%04d.jpg','-i',f'{tmp}/m2.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],check=True)
    print('wrote', out)
