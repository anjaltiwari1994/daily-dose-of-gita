"""Story Reel v2 (SAMPLE): same 3 scenes/timings as render_reel_story.py, but with motion in the first seconds.
Scene 1: line 1 on screen from frame 0, chat-style bubbles pop in (0.2-0.7 s), line 2 slams in at 0.9 s with a shake,
fast push-in on the background, tease fades in at 2.2 s. Scene 2: paragraphs appear one by one. Scene 3: boxes stagger in.
Audio: same tanpura/sitar + a dhol-style hit at 0 s and on line 2, soft pops on bubbles.
input.json = same as render_reel_story.py plus optional "bubbles":[{"from":"Bua","text":"Beta, shaadi kab?"},..],"more":"+11 more"
Usage: python3 tools/render_reel_story_v2.py input.json out.mp4"""
import json, sys, os, tempfile, subprocess, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wow'))
import render_reel_story as R, render_cards as rc, sitar, numpy as np, wave
E = html.escape; FPS = 24; DURS = R.DURS; XF = R.XF
L2 = 0.9  # line-2 slam time

JS = """<script>
function eo(x){x=Math.min(Math.max(x,0),1);return 1-Math.pow(1-x,3)}
function back(x){x=Math.min(Math.max(x,0),1);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}
window.setT=function(t){
 const bg=document.body.firstElementChild; if(bg&&bg.id!='brand'&&window.ZOOM){bg.style.transform='scale('+(1+0.10*eo(t/1.6)+0.03*Math.min(t/5.5,1))+')'}
 document.querySelectorAll('[data-in]').forEach(el=>{const t0=+el.dataset.in,k=el.dataset.k||'up',d=+(el.dataset.d||0.4),x=(t-t0)/d;
  if(k=='up'){el.style.opacity=eo(x);el.style.transform='translateY('+(30*(1-eo(x)))+'px)'}
  else if(k=='pop'){el.style.opacity=Math.min(Math.max(x*3,0),1);el.style.transform='scale('+(x<=0?0.6:0.6+0.4*back(x))+')'}
  else if(k=='slam'){const s=x<=0?0:(x>=1?1:x);el.style.opacity=s;let sh=0;if(t>t0&&t<t0+0.35){sh=Math.sin((t-t0)*90)*14*(1-(t-t0)/0.35)}
   el.style.transform='translateX('+sh+'px) scale('+(1.5-0.5*eo(x))+')'}
  else if(k=='fade'){el.style.opacity=eo(x)}});
 document.querySelectorAll('[data-shake]').forEach(el=>{const t0=+el.dataset.shake;let sh=0;if(t>t0&&t<t0+0.35){sh=Math.sin((t-t0)*90)*10*(1-(t-t0)/0.35)};el.style.transform='translateX('+sh+'px)'});
}</script>"""

def s1(p):
    l1, l2 = p['big'].split('\n')
    bub = ''
    for i, b in enumerate(p.get('bubbles', [])):
        bub += (f"<div class='bb' data-in='{0.2+0.25*i:.2f}' data-k='pop' data-d='0.3'><div class='nm'>{E(b['from'])}</div>"
                f"<div class='mg'>{E(b['text'])}</div></div>")
    if p.get('more'): bub += f"<div class='more' data-in='0.95' data-k='pop' data-d='0.3'>{E(p['more'])}</div>"
    inner = (f"<div class='pill'>A STORY + A SHLOKA</div><div class='abs' id='big' data-shake='{L2}'><div>{E(l1)}</div>"
             f"<div class='l2' data-in='{L2}' data-k='slam' data-d='0.14'>{E(l2)}</div></div>"
             f"<div id='bubs'>{bub}</div><div class='abs' id='tease' data-in='2.2' data-k='up' data-d='0.5'>{E(p['tease'])}</div>")
    css = ("#big{top:430px;font:700 84px 'Playfair Display';line-height:100px;color:#FFF6E5;padding:0 50px;text-shadow:0 4px 24px rgba(0,0,0,.7)}"
           "#big .l2{color:#FFD27A;display:block}"
           "#bubs{position:absolute;left:110px;width:860px;top:720px;display:flex;flex-direction:column;gap:22px;align-items:flex-start}"
           ".bb{background:#FFFFFF;border-radius:8px 28px 28px 28px;padding:18px 30px 20px;box-shadow:0 10px 40px rgba(0,0,0,.55);transform-origin:left center;max-width:760px}"
           ".bb:nth-child(2){margin-left:60px}.bb:nth-child(3){margin-left:120px}"
           ".nm{font:700 24px 'Inter';color:#C2185B;margin-bottom:4px}.mg{font:500 40px 'Inter';color:#1A1A1A}"
           ".more{margin-left:180px;background:#E8B14F;color:#2A1A05;font:700 30px 'Inter';padding:12px 28px;border-radius:30px;box-shadow:0 10px 30px rgba(0,0,0,.5)}"
           "#tease{top:1480px;font:italic 500 46px 'Playfair Display';color:#E8B14F;padding:0 70px;line-height:60px;text-shadow:0 2px 12px rgba(0,0,0,.8)}")
    h = R.wrap(inner, css, p['bg'])
    return h.replace('<div style="position:absolute;inset:0;', '<div style="position:absolute;inset:0;transform-origin:50% 40%;', 1).replace('</body>', JS + '</body>')

def s2(p):
    ts = [0.35, 3.4, 6.6]
    paras = ''.join(f"<p data-in='{ts[i]}' data-k='up' data-d='0.5'>{E(x)}</p>" for i, x in enumerate(p['story']))
    h = R.wrap(f"<div class='pill'>THE STORY</div><div id='st'>{paras}<p class='q' data-in='9.0' data-k='up' data-d='0.5'>{E(p['quote'])}</p></div>",
               "#st{position:absolute;left:90px;width:900px;top:480px;font:400 46px 'Lora';line-height:66px;color:#FFF6E5}"
               "#st p{margin-bottom:38px}#st .q{font:italic 500 50px 'Playfair Display';line-height:68px;color:#E8B14F}")
    return h.replace('</body>', JS + '</body>')

def s3(p):
    h = R.s3(p)
    for sel, t in (("id='b1'", 0.2), ("id='b2'", 1.6), ("id='b3'", 3.4), ("id='sh3'", 5.0)):
        h = h.replace(sel, f"{sel} data-in='{t}' data-k='up' data-d='0.5'", 1)
    return h.replace('</body>', JS + '</body>')

def hit(dur=0.6, f0=95, amp=0.9):
    t = np.arange(int(sitar.SR * dur)) / sitar.SR
    f = f0 * (1 + 1.2 * np.exp(-t * 30)); ph = 2 * np.pi * np.cumsum(f) / sitar.SR
    body = np.sin(ph) * np.exp(-t * 7)
    click = np.random.default_rng(3).uniform(-1, 1, len(t)) * np.exp(-t * 120) * 0.5
    return amp * (body + click)

def pop(amp=0.25):
    t = np.arange(int(sitar.SR * 0.08)) / sitar.SR
    return amp * np.sin(2 * np.pi * (900 + 1500 * t / 0.08) * t) * np.exp(-t * 50)

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for i, fn in enumerate([s1, s2, s3]):
            pg.set_content(fn(p)); pg.evaluate('window.ZOOM=%s' % ('true' if i == 0 else 'false')); pg.wait_for_timeout(800)
            pg.evaluate('setT(99)'); bad = pg.evaluate(R.CHECK); print('scene', i + 1, 'OVERFLOW ' + str(bad) if bad else 'ok')
            os.makedirs(f'{tmp}/s{i}')
            for n in range(int(DURS[i] * FPS)):
                pg.evaluate(f'setT({n / FPS})'); pg.screenshot(path=f'{tmp}/s{i}/{n:04d}.png')
        b.close()
    T = sum(DURS) - XF * (len(DURS) - 1); cuts, c = [], 0.0
    for d in DURS[:-1]: c += d - XF; cuts.append(c)
    sitar.make(T, cuts, f'{tmp}/m.wav')
    w = wave.open(f'{tmp}/m.wav'); ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(float).reshape(-1, ch) / 32768; w.close()
    def put(t0, sig):
        i = int(t0 * sr); m = min(len(sig), len(a) - i); a[i:i + m] += sig[:m, None]
    put(0.0, hit()); put(L2, hit(f0=80, amp=1.0))
    for k in range(len(p.get('bubbles', []))): put(0.2 + 0.25 * k, pop())
    a = a / max(1.0, np.abs(a).max() / 0.95)
    w = wave.open(f'{tmp}/m1.wav', 'wb'); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m1.wav','-af','aecho=0.8:0.6:70|140:0.25|0.12,lowpass=f=7000,loudnorm=I=-16:TP=-1.5:LRA=11',f'{tmp}/m2.wav'],check=True)
    args = ['ffmpeg','-y','-loglevel','error']
    for i in range(3): args += ['-framerate', str(FPS), '-i', f'{tmp}/s{i}/%04d.png']
    args += ['-i', f'{tmp}/m2.wav']; fl = [f'[{i}:v]format=yuv420p,setsar=1[v{i}]' for i in range(3)]
    prev, off = 'v0', 0.0
    for i in range(1, 3):
        off += DURS[i - 1] - XF; fl.append(f'[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]'); prev = f'x{i}'
    args += ['-filter_complex', ';'.join(fl), '-map', f'[{prev}]', '-map', '3:a', '-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart', out]
    subprocess.run(args, check=True); print('wrote', out, 'duration', T)
