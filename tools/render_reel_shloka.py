"""Shloka-first Reel (1080x1920 mp4, ~13.6 s, free). Format chosen by the owner on 22 Nov 2026: a universal FEELING hook -> the verse -> one-line lesson.
Scene 1 hook (3.0 s): no branding on screen; line 1 from frame 0, line 2 slams in at 0.6 s with a dhol hit; fast push-in on the background.
Scene 2 verse (6.5 s): Sanskrit lines appear one by one, then the meaning. Scene 3 (5.5 s): the lesson, the share line, then the brand.
Music: tools/wow/sitar.py (tanpura + sitar, phrase on each scene change) + dhol hits at 0 s and on line 2.
Usage: python3 tools/render_reel_shloka.py input.json out.mp4
input.json = {"bg":"bgbank/n22.png","big":"Feeling alone\\neven in a full room?","san":"line1\\nline2","ref":"6.30",
 "mean":"faithful English meaning (~150 chars)","tip":"one-line lesson (~60 chars)","share":"Send this to ..."}"""
import json, sys, os, tempfile, subprocess, html, base64, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wow'))
import render_cards as rc, sitar, numpy as np
from render_reel_story_v2 import JS, hit
E = html.escape; FPS = 24; DURS = [3.0, 6.5, 5.5]; XF = 0.7; L2 = 0.6

CSS = """*{box-sizing:border-box;margin:0;padding:0}body{width:1080px;height:1920px;position:relative;overflow:hidden;background:#0B0B22}
.abs{position:absolute;left:0;width:1080px;text-align:center}#hd{top:1720px;font:500 28px 'Inter';color:#B2A7CA}"""
def page(inner, css, bg, dim):
    b64 = base64.b64encode(open(bg, 'rb').read()).decode()
    return (f"<html><head><style>{CSS}{css}</style></head><body><div style='position:absolute;inset:0;transform-origin:50% 40%;"
            f"background:url(data:image/png;base64,{b64}) center/cover'></div><div style='position:absolute;inset:0;background:rgba(8,10,34,{dim})'></div>"
            f"{inner}</body>{JS}</html>")

def s1(p):
    l1, l2 = p['big'].split('\n')
    return page(f"<div id='big' data-shake='{L2}'><div>{E(l1)}</div><div class='l2' data-in='{L2}' data-k='slam' data-d='0.14'>{E(l2)}</div></div>",
                "#big{position:absolute;left:0;width:1080px;top:640px;text-align:center;font:700 92px 'Playfair Display';line-height:112px;color:#FFF6E5;padding:0 50px;text-shadow:0 6px 30px rgba(0,0,0,.85)}"
                "#big .l2{color:#FFD27A}", p['bg'], .38)
def s2(p):
    lines = p['san'].split('\n'); t = [0.15 + 0.45 * i for i in range(len(lines))]
    san = ''.join(f"<div data-in='{t[i]:.2f}' data-k='up' data-d='0.45'>{E(l)}</div>" for i, l in enumerate(lines))
    fs = 50 if len(lines) <= 2 else 44
    return page(f"<div class='abs' id='lb' data-in='0' data-k='fade'>BHAGAVAD GITA {E(p['ref'])}</div><div class='abs' id='san' style='font-size:{fs}px'>{san}</div>"
                f"<div class='abs' id='mn' data-in='{t[-1]+0.9:.2f}' data-k='up' data-d='0.5'>{E(p['mean'])}</div>",
                "#lb{top:470px;font:700 26px 'Inter';letter-spacing:6px;color:#E8B14F}"
                "#san{top:560px;font-family:'Tiro Devanagari Hindi';line-height:1.6;color:#F2C25A;padding:0 60px;text-shadow:0 3px 16px rgba(0,0,0,.8)}"
                "#mn{top:1010px;font:400 44px 'Lora';line-height:64px;color:#FFF6E5;padding:0 90px;text-shadow:0 3px 16px rgba(0,0,0,.8)}", p['bg'], .78)
def s3(p):
    return page(f"<div class='abs' id='tp' data-in='0.15' data-k='up' data-d='0.5'>{E(p['tip'])}</div>"
                f"<div class='abs' id='sh' data-in='1.9' data-k='up' data-d='0.5'>{E(p['share'])} 🙏</div>"
                f"<div class='abs' id='br' data-in='3.0' data-k='fade' data-d='0.5'><div class='b1'>DAILY DOSE OF GITA</div><div class='b2'>Follow for one verse a day</div></div>"
                f"<div class='abs' id='hd' data-in='3.0' data-k='fade'>@daily.doseofgita</div>",
                "#tp{top:640px;font:700 70px 'Playfair Display';line-height:88px;color:#FFF6E5;padding:0 80px;text-shadow:0 4px 24px rgba(0,0,0,.8)}"
                "#sh{top:1080px;font:italic 500 46px 'Playfair Display';line-height:60px;color:#E8B14F;padding:0 90px}"
                "#br{top:1420px}.b1{font:500 32px 'Playfair Display';letter-spacing:7px;color:#E8B14F}.b2{margin-top:14px;font:500 30px 'Inter';color:#B2A7CA}", p['bg'], .8)

CHECK = """()=>{const bad=[];document.querySelectorAll('body *').forEach(el=>{const r=el.getBoundingClientRect();if(r.height>0&&r.height<1900&&(r.right>1081||r.left<-1||r.bottom>1780))bad.push((el.id||el.className||el.tagName)+':'+Math.round(r.bottom));});
 const a=document.querySelector('#san'),b=document.querySelector('#mn');if(a&&b&&a.getBoundingClientRect().bottom>b.getBoundingClientRect().top-20)bad.push('san/mn overlap');
 const c=document.querySelector('#tp'),d=document.querySelector('#sh');if(c&&d&&c.getBoundingClientRect().bottom>d.getBoundingClientRect().top-20)bad.push('tip/share overlap');return bad.slice(0,6);}"""

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]; rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for i, fn in enumerate([s1, s2, s3]):
            pg.set_content(fn(p)); pg.evaluate('window.ZOOM=%s' % ('true' if i == 0 else 'false')); pg.wait_for_timeout(800)
            pg.evaluate('setT(99)'); bad = pg.evaluate(CHECK); print('scene', i + 1, 'OVERFLOW ' + str(bad) if bad else 'ok')
            os.makedirs(f'{tmp}/s{i}')
            for n in range(int(DURS[i] * FPS)):
                pg.evaluate(f'setT({n / FPS})'); pg.screenshot(path=f'{tmp}/s{i}/{n:04d}.png')
        b.close()
    T = sum(DURS) - XF * (len(DURS) - 1); cuts, c = [], 0.0
    for d in DURS[:-1]: c += d - XF; cuts.append(c)
    sitar.make(T, cuts, f'{tmp}/m.wav')
    w = wave.open(f'{tmp}/m.wav'); ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(float).reshape(-1, ch) / 32768; w.close()
    def put(t0, sig):
        i = int(t0 * sr); m = min(len(sig), len(a) - i); a[i:i + m] += sig[:m, None]
    put(0.0, hit()); put(L2, hit(f0=80, amp=1.0))
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
