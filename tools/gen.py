import json,base64,html,sys
from scenes import SCENES
from playwright.sync_api import sync_playwright
M=json.load(open('manifest.json'))
# idx: (scene, dy, pill, hook override or None, short meaning, banner or None)
A={
0:('hill',-190,'SELF-MASTERY',None,'Master your mind and it becomes your best friend.','3 ways to befriend your mind'),
1:('lotus',-110,'CONTENTMENT',None,'Be content, disciplined and steady in resolve.',None),
2:('peak',-130,'FOCUS','Too many goals, zero progress?','A focused mind has one aim. Others scatter.','3 ways to focus today'),
3:('ghat',-190,'CHANGE',None,'The soul moves through ages. Change is natural.',None),
4:('forest',-190,'CALM','Does criticism ruin your day?','Praise and blame feel the same to the steady mind.',None),
5:('diya',-110,'RESTLESS MIND',None,'Arjuna: the mind is restless and hard to hold.',None),
6:('chariot',0,'ENDURANCE',None,'Pleasure and pain come and go. Endure them.',None),
7:('peepal',-190,'EQUANIMITY','Want to stay calm with everyone?','Be the same in honour and dishonour.',None),
8:('hill',-190,'LETTING GO',None,'Let go of results and you find lasting peace.',None),
9:('forest',-190,'THE REAL ENEMY',None,'Desire and anger are the real enemy within.',None),
10:('lotus',-110,'FAITH','Want real knowledge? Start here.','Faith, devotion and control lead to knowledge.',None),
11:('peepal',-190,'YOUR OWN PATH',None,"Your own path, imperfect, beats another's.",None),
12:('ghat',-190,'ACTION',None,'Action is better than inaction. Do your work.',None),
13:('diya',-110,'SELFLESS WORK',"Want work that doesn't drain you?",'Work done as an offering sets you free.','Turn work into freedom'),
14:('chariot',0,'COURAGE',None,"Don't give in to weakness. Rise, Arjuna.",None),
15:('peak',-130,'DOUBT',None,'Doubt destroys. Faith brings peace.',None),
16:('hill',-190,'KNOWLEDGE','The purest thing you can chase','Nothing purifies like knowledge.',None),
17:('forest',-190,'OBSTACLES',None,'Fix your mind on Me and cross every obstacle.',None),
18:('lotus',-110,'PEACE',None,'Without a steady mind there is no peace.','How to find calm in 3 steps'),
19:('peepal',-190,'YOUR CRAFT','Want to master your craft?','Devotion to your own work leads to perfection.','3 steps to master your craft'),
20:('peak',-130,'SELF-CONTROL',None,'Know the Self, steady the mind, conquer desire.','3 ways to build self-control'),
21:('ghat',-190,'EFFORT',None,'No effort is ever lost, here or beyond.',None),
22:('diya',-110,'MINDFULNESS','Mind wandering again?','When the mind wanders, gently bring it back.',None),
23:('lotus',-110,'INNER PEACE',None,'Self-control brings lasting peace.',None),
24:('chariot',0,'DISCIPLINE','Hard now, sweet later?','Bitter at first, nectar in the end.','How to make discipline easier'),
25:('diya',-110,'SACRED WORK',None,'Offer everything you do, and it becomes sacred.','Turn any task into something sacred'),
}
def page(it,scene_b64,dy,pill,hook,mean):
    san=html.escape(it['san']).replace('\n','</span><span class="l">')
    return f"""<html><head><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#080C25}}
#art{{position:absolute;left:0;top:{235+dy}px;width:1080px;height:1064px;background:url(data:image/png;base64,{scene_b64}) center/100% 100%}}
#top{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(180deg,#0E1030 0%,#0E1030 38%,rgba(14,16,48,0) 100%)}}
#bot{{position:absolute;left:0;top:880px;width:1080px;height:470px;background:linear-gradient(180deg,rgba(8,12,37,0) 0%,rgba(8,12,37,.88) 32%,#080C25 62%)}}
.abs{{position:absolute;left:0;width:1080px;text-align:center}}
#brand{{top:62px;font:500 28px 'Playfair Display';letter-spacing:6.2px;color:#E8B14F}}
#pill{{position:absolute;left:50%;top:122px;transform:translateX(-50%);height:58px;padding:0 34px;border-radius:29px;background:#E8B14F;color:#2A1A05;font:700 22px 'Inter';letter-spacing:3.5px;display:flex;align-items:center;justify-content:center;white-space:nowrap}}
#hook{{top:215px;font:700 60px 'Playfair Display';color:#FFF6E5;white-space:nowrap}}
#san{{top:960px;font:400 46px 'Tiro Devanagari Hindi';color:#E8B84A;line-height:74px}}
#san .l{{display:block;white-space:nowrap}}
#ref{{top:1105px;font:500 22px 'Inter';color:#B2A7CA;letter-spacing:1px}}
#mean{{top:1160px;font:400 33px 'Lora';color:#FFF6E5;line-height:46px;white-space:nowrap}}
#hd{{top:1288px;font:500 26px 'Inter';color:#B2A7CA}}
</style></head><body><div id="art"></div><div id="top"></div><div id="bot"></div>
<div class="abs" id="brand">DAILY DOSE OF GITA</div><div id="pill">{html.escape(pill)}</div>
<div class="abs" id="hook">{html.escape(hook)}</div>
<div class="abs" id="san"><span class="l">{san}</span></div>
<div class="abs" id="ref">— Bhagavad Gita {it['ch']}.{it['v']} —</div>
<div class="abs" id="mean">{html.escape(mean)}</div>
<div class="abs" id="hd">@daily.doseofgita</div></body></html>"""
FIT="""()=>{let w=[];for(const [id,f] of [['hook',60],['mean',33]]){const e=document.getElementById(id);let s=f;while(e.scrollWidth>0&&e.getBoundingClientRect().width>0){const r=document.createRange();r.selectNodeContents(e);if(r.getBoundingClientRect().width<=980||s<=24)break;s-=1;e.style.fontSize=s+'px';}w.push(id+':'+s);}
const sn=document.getElementById('san');let s=46;while(s>30){let m=0;sn.querySelectorAll('.l').forEach(l=>{const r=document.createRange();r.selectNodeContents(l);m=Math.max(m,r.getBoundingClientRect().width)});if(m<=980)break;s-=1;sn.style.fontSize=s+'px';}w.push('san:'+s);return w.join(' ');}"""
if __name__=='__main__':
    import os
    out='/home/claude/daily-dose-of-gita/cards'
    sel=[int(a) for a in sys.argv[1:]] or list(A)
    b64={}
    with sync_playwright() as p:
        br=p.chromium.launch(); pg=br.new_page(viewport={'width':1080,'height':1350})
        ban=[]
        for i in sel:
            it=M[i]; sc,dy,pill,hook,mean,banner=A[i]
            if sc not in b64:
                pg.set_viewport_size({'width':1080,'height':1064}); pg.set_content(f'<body style="margin:0">{SCENES[sc]()}</body>'); pg.screenshot(path=f'scene_{sc}.png'); b64[sc]=base64.b64encode(open(f'scene_{sc}.png','rb').read()).decode(); pg.set_viewport_size({'width':1080,'height':1350})
            h=hook or it['hook']
            pg.set_content(page(it,b64[sc],dy,pill,h,mean)); pg.wait_for_timeout(500)
            info=pg.evaluate(FIT)
            fn=f"ill_{it['ch']}_{it['v']}"
            pg.screenshot(path=f'{out}/{fn}.png'); print(i,fn,info)
            if banner: ban.append({'src':f'cards/{fn}.png','file':fn+'_hook','hook':banner,'handle':'@daily.doseofgita'})
        br.close()
    json.dump(ban,open('banners.json','w'),indent=1)
