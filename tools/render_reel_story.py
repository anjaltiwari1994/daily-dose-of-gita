"""Story-style Gita Reel (1080x1920 mp4, ~24.5 s, music, free). Same 4-part flow as the story carousels (gs_*):
hook over a bgbank image -> the story -> what Krishna said (verse + meaning + one-line lesson) -> your turn (question, 3 steps, share line).
Usage: python3 tools/render_reel_story.py input.json out.mp4
input.json = {"bg":"bgbank/n07.png","big":"One quick scroll.\\nTwo hours gone.","tease":"Krishna's tortoise has the fix.",
 "story":["para 1","para 2","para 3"],"quote":"gold italic line","vtitle":"Pull your senses in, like a tortoise.",
 "san":"line1\\nline2","ref":"2.58","mean":"English meaning","tip":"one-line lesson",
 "q":"What steals your focus most?","steps":["..","..",".."],"share":"Send this to ..."}
Scene 1 (hook) is on screen from frame 0. Cover: videoCoverMilliseconds 1000 (the 'your turn' scene)."""
import json, sys, os, tempfile, subprocess, base64, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wow'))
import render_cards as rc, music

DURS = [3.5, 12.0, 12.0, 10.0]; XF = 0.7
E = html.escape
BASE = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;position:relative;overflow:hidden;background:radial-gradient(ellipse at 50% 30%,#2B1E4A 0%,#15122F 55%,#0B0B22 100%)}
.abs{position:absolute;left:0;width:1080px;text-align:center}
#brand{top:250px;font:500 30px 'Playfair Display';letter-spacing:7px;color:#E8B14F}
.pill{position:absolute;left:50%;top:310px;transform:translateX(-50%);height:60px;padding:0 36px;border-radius:30px;background:#E8B14F;color:#2A1A05;font:700 23px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;white-space:nowrap}
#hd{top:1690px;font:500 28px 'Inter';color:#B2A7CA}
"""
def wrap(inner, extra_css='', bg=None):
    bgdiv = ''
    if bg:
        b64 = base64.b64encode(open(bg, 'rb').read()).decode()
        bgdiv = (f'<div style="position:absolute;inset:0;background:url(data:image/png;base64,{b64}) center/cover"></div>'
                 '<div style="position:absolute;left:0;top:0;width:1080px;height:900px;background:linear-gradient(180deg,#0E1030 0%,rgba(14,16,48,.85) 45%,rgba(14,16,48,0) 100%)"></div>'
                 '<div style="position:absolute;left:0;top:1150px;width:1080px;height:770px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.85) 35%,#080C25 70%)"></div>')
    return f"<html><head><style>{BASE}{extra_css}</style></head><body>{bgdiv}<div class='abs' id='brand'>DAILY DOSE OF GITA</div>{inner}<div class='abs' id='hd'>@daily.doseofgita</div></body></html>"

def s1(p):
    big = '<br>'.join(E(l) for l in p['big'].split('\n'))
    return wrap(f"<div class='pill'>A STORY + A SHLOKA</div><div class='abs' id='big'>{big}</div><div class='abs' id='tease'>{E(p['tease'])}</div>",
                "#big{top:430px;font:700 84px 'Playfair Display';line-height:100px;color:#FFF6E5;padding:0 60px;text-shadow:0 4px 24px rgba(0,0,0,.6)}"
                "#tease{top:1480px;font:italic 500 46px 'Playfair Display';color:#E8B14F;padding:0 70px;line-height:60px}", p['bg'])
def s2(p):
    paras = ''.join(f'<p>{E(x)}</p>' for x in p['story'])
    return wrap(f"<div class='pill'>THE STORY</div><div id='st'>{paras}<p class='q'>{E(p['quote'])}</p></div>",
                "#st{position:absolute;left:90px;width:900px;top:480px;font:400 46px 'Lora';line-height:66px;color:#FFF6E5}"
                "#st p{margin-bottom:38px}#st .q{font:italic 500 50px 'Playfair Display';line-height:68px;color:#E8B14F}")
def s3(p):
    san = '<br>'.join(E(l) for l in p['san'].split('\n'))
    return wrap(f"<div class='pill'>WHAT KRISHNA SAID</div><div class='abs' id='vt'>{E(p['vtitle'])}</div>"
                f"<div id='col'><div class='box' id='b1'><div id='san'>{san}</div><div class='rf'>— Bhagavad Gita {E(p['ref'])} —</div></div>"
                f"<div class='box' id='b2'><div class='lb'>MEANING</div><div class='tx'>{E(p['mean'])}</div></div>"
                f"<div class='box gold' id='b3'><div class='lb' style='color:#E8B14F'>TRY THIS TODAY</div><div class='tx b'>{E(p['tip'])}</div></div></div>",
                "#vt{top:430px;font:700 58px 'Playfair Display';line-height:72px;color:#FFF6E5;padding:0 80px}"
                "#col{position:absolute;left:70px;width:940px;top:640px;display:flex;flex-direction:column;gap:30px}.box{border:2px solid rgba(232,177,79,.22);border-radius:22px;background:rgba(255,255,255,.04);padding:30px 36px}"
                ".gold{background:rgba(232,177,79,.10);border-color:rgba(232,177,79,.45)}"
                "#b1{text-align:center}#san{font:400 40px 'Tiro Devanagari Hindi';line-height:64px;color:#E8B84A}"
                ".rf{margin-top:10px;font:500 22px 'Inter';color:#B2A7CA}"
                ".lb{font:700 22px 'Inter';letter-spacing:3px;color:#B2A7CA;margin-bottom:10px}.tx{font:400 36px 'Lora';line-height:50px;color:#FFF6E5}.tx.b{font-weight:600}")
def s4(p):
    steps = ''.join(f"<div class='st'><span class='n'>{i+1}</span><span class='t'>{E(x)}</span></div>" for i, x in enumerate(p['steps']))
    return wrap(f"<div class='pill'>YOUR TURN</div><div class='abs' id='q'>{E(p['q'])}</div><div id='steps'>{steps}</div><div class='abs' id='sh'>{E(p['share'])}</div>",
                "#q{top:430px;font:700 62px 'Playfair Display';line-height:76px;color:#FFF6E5;padding:0 80px}"
                "#steps{position:absolute;left:70px;width:940px;top:680px;display:flex;flex-direction:column;gap:26px}"
                ".st{display:flex;gap:26px;align-items:flex-start;border:2px solid rgba(232,177,79,.22);border-radius:22px;background:rgba(255,255,255,.04);padding:30px 34px}"
                ".n{flex:0 0 54px;height:54px;border-radius:27px;background:#E8B14F;color:#2A1A05;font:700 28px 'Inter';display:flex;align-items:center;justify-content:center}"
                ".t{font:400 38px 'Lora';line-height:52px;color:#FFF6E5}"
                "#sh{top:1480px;font:italic 500 44px 'Playfair Display';line-height:60px;color:#E8B14F;padding:0 80px}")

CHECK = """()=>{const bad=[];document.querySelectorAll('body *').forEach(el=>{const r=el.getBoundingClientRect();if(r.height>0&&r.height<1900&&(r.right>1081||r.left<-1||r.bottom>1660&&el.id!='hd'&&!el.closest('#hd')))bad.push((el.id||el.className||el.tagName)+':'+Math.round(r.bottom));});return bad.slice(0,6);}"""

if __name__ == '__main__':
    p = json.load(open(sys.argv[1])); out = sys.argv[2]
    rc.ensure_fonts()
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(); imgs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for i, fn in enumerate([s1, s2, s3, s4]):
            pg.set_content(fn(p)); pg.wait_for_timeout(700)
            bad = pg.evaluate(CHECK); print('scene', i + 1, 'OVERFLOW ' + str(bad) if bad else 'ok')
            f = f'{tmp}/s{i}.png'; pg.screenshot(path=f); imgs.append(f)
        b.close()
    T = sum(DURS) - XF * (len(DURS) - 1)
    music.make('gita', T, f'{tmp}/m.wav')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{tmp}/m.wav','-af','aecho=0.8:0.7:90|180:0.35|0.2,lowpass=f=5000',f'{tmp}/m2.wav'],check=True)
    args = ['ffmpeg','-y','-loglevel','error']
    for f, d in zip(imgs, DURS): args += ['-loop','1','-t',str(d),'-framerate','24','-i',f]
    args += ['-i', f'{tmp}/m2.wav']
    fl = []
    for i, d in enumerate(DURS):
        n = int(d * 24)
        z = "zoompan=z='1+0.06*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=24" % n if i == 0 else 'fps=24'
        fl.append(f'[{i}:v]scale=1080:1920,{z},format=yuv420p,setsar=1[v{i}]')
    prev, off = 'v0', 0.0
    for i in range(1, len(DURS)):
        off += DURS[i - 1] - XF
        fl.append(f'[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]'); prev = f'x{i}'
    args += ['-filter_complex', ';'.join(fl), '-map', f'[{prev}]', '-map', f'{len(DURS)}:a',
             '-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart', out]
    subprocess.run(args, check=True)
    print('wrote', out, 'duration', T)
