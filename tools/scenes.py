import math,random
W,H=1080,1064
INK='#07091C'
def stars(n,ymax,seed=3,col='#FFE9B8'):
    r=random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(0,ymax)}" r="{r.choice([1,1.5,2,2.5])}" fill="{col}" opacity="{r.uniform(.35,.95):.2f}"/>' for _ in range(n))
def bokeh(n,seed,cols,ymin=0,ymax=H,rmin=6,rmax=40):
    r=random.Random(seed);s=''
    for _ in range(n):
        s+=f'<circle cx="{r.randint(0,W)}" cy="{r.randint(ymin,ymax)}" r="{r.randint(rmin,rmax)}" fill="{r.choice(cols)}" opacity="{r.uniform(.08,.3):.2f}"/>'
    return s
def rays(cx,cy,n=36,op=.3,col='#FFE29A',w=2.2):
    s=''
    for i in range(n):
        a=i*360/n
        s+=f'<polygon points="{cx},{cy} {cx+1500*math.cos(math.radians(a-w))},{cy+1500*math.sin(math.radians(a-w))} {cx+1500*math.cos(math.radians(a+w))},{cy+1500*math.sin(math.radians(a+w))}" fill="{col}" opacity="{op}"/>'
    return s
def grad(i,stops,x2=0,y2=1):
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">'+''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o,c in stops)+'</linearGradient>'
def rad(i,c,a0=1):
    return f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{a0}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
def mount(pts,fill): return f'<path d="M'+' L'.join(f'{x},{y}' for x,y in pts)+f' L{W},{H} L0,{H}Z" fill="{fill}"/>'
def wrap(defs,body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>{body}</svg>'
def wheel(x,y,r):
    s=f'<g transform="translate({x},{y})" fill="none" stroke="{INK}" stroke-width="7"><circle r="{r}" stroke-width="11"/><circle r="{r*0.18}" fill="{INK}"/>'
    for k in range(12):
        a=math.radians(k*30); s+=f'<line x1="0" y1="0" x2="{r*math.cos(a)}" y2="{r*math.sin(a)}"/>'
    return s+'</g>'
def person(x,y,s=1,col=INK):
    return f'<g transform="translate({x},{y}) scale({s})" fill="{col}"><ellipse cx="0" cy="-92" rx="15" ry="18"/><path d="M-17,-72 L17,-72 L26,0 L-26,0Z"/></g>'

def sunrise_chariot():
    d=grad('sky',[(0,'#0E1030'),(.35,'#3A1B5C'),(.6,'#B8436A'),(.8,'#F08A3C'),(1,'#FFC857')])+rad('sun','#FFF6D6')+rad('glow','#FFD36B',.9)+grad('m1',[(0,'#6B2E63'),(1,'#C2506B')])+grad('m2',[(0,'#3B1D55'),(1,'#7A2F5E')])+grad('m3',[(0,'#1B1240'),(1,'#2A1650')])
    cx,cy=540,560
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'+stars(70,330)+rays(cx,cy,36,.28)
    b+=f'<circle cx="{cx}" cy="{cy}" r="360" fill="url(#glow)" opacity=".7"/><circle cx="{cx}" cy="{cy}" r="150" fill="url(#sun)"/><circle cx="{cx}" cy="{cy}" r="205" fill="none" stroke="#FFE29A" stroke-opacity=".55" stroke-width="2"/>'
    b+=mount([(0,640),(120,560),(230,620),(360,520),(470,610),(600,540),(720,620),(860,520),(980,600),(1080,560)],'url(#m1)')
    b+=mount([(0,720),(90,660),(200,710),(330,640),(450,720),(580,660),(700,730),(840,650),(960,720),(1080,680)],'url(#m2)')
    b+=f'<path d="M0,800 C200,760 360,800 540,790 C720,780 880,760 1080,800 L1080,{H} L0,{H}Z" fill="url(#m3)"/>'
    b+=f'<g transform="translate(-135,-30) translate(540,0) scale(1.15) translate(-540,0) translate(0,-185)">{wheel(690,858,64)}<path d="M600,800 L800,800 L790,840 L612,840Z" fill="{INK}"/><path d="M610,800 L610,748 L800,748 L800,800" fill="none" stroke="{INK}" stroke-width="7"/><ellipse cx="672" cy="690" rx="15" ry="18" fill="{INK}"/><path d="M655,708 L690,708 L698,800 L650,800Z" fill="{INK}"/><path d="M690,722 L640,780" stroke="{INK}" stroke-width="7"/><ellipse cx="748" cy="700" rx="15" ry="18" fill="{INK}"/><path d="M733,718 L766,718 L772,800 L728,800Z" fill="{INK}"/><path d="M788,670 C830,720 830,780 788,830" fill="none" stroke="{INK}" stroke-width="5"/><line x1="788" y1="670" x2="788" y2="830" stroke="{INK}" stroke-width="2"/><line x1="800" y1="748" x2="800" y2="640" stroke="{INK}" stroke-width="5"/><path d="M800,640 L860,660 L800,682Z" fill="{INK}"/></g>'
    b+=f'<path d="M0,910 C240,880 420,920 620,900 C820,880 940,900 1080,890 L1080,{H} L0,{H}Z" fill="#0A0A24"/>'
    return wrap(d,b)

def lotus_moon():
    d=grad('sky',[(0,'#071B2E'),(.5,'#12405A'),(.8,'#2B6A7A'),(1,'#7FB9A8')])+rad('moon','#F4FBFF')+rad('mg','#BFE9F2',.8)+grad('wat',[(0,'#0F3A4E'),(1,'#06141F')])+grad('pet',[(0,'#FFD7E8'),(1,'#F26FA3')])+grad('pet2',[(0,'#FFC2DA'),(1,'#D9487F')])
    cx,cy=540,330
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'+stars(90,420,5,'#E6F7FF')
    b+=f'<circle cx="{cx}" cy="{cy}" r="330" fill="url(#mg)" opacity=".55"/><circle cx="{cx}" cy="{cy}" r="150" fill="url(#moon)"/><circle cx="{cx}" cy="{cy}" r="200" fill="none" stroke="#CFEFF7" stroke-opacity=".4" stroke-width="2"/>'
    b+=mount([(0,560),(150,520),(300,560),(460,500),(620,550),(800,505),(960,545),(1080,520)],'#0C2C40')
    b+=f'<rect y="600" width="{W}" height="{H-600}" fill="url(#wat)"/>'
    # moon reflection
    b+=f'<ellipse cx="{cx}" cy="700" rx="130" ry="26" fill="#CFEFF7" opacity=".35"/><ellipse cx="{cx}" cy="760" rx="90" ry="14" fill="#CFEFF7" opacity=".25"/>'
    for y,rx in [(640,300),(700,380),(770,470),(850,520),(930,540)]:
        b+=f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{rx*.12}" fill="none" stroke="#9FD8E6" stroke-opacity=".25" stroke-width="2"/>'
    # pads
    for x,y,r in [(180,760,90),(900,790,110),(330,900,120),(780,930,130),(90,950,80)]:
        b+=f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*.22}" fill="#0B4A44"/><ellipse cx="{x}" cy="{y-3}" rx="{r*.9}" ry="{r*.17}" fill="#13665B"/>'
    # lotus
    fx,fy=540,800
    b+=f'<ellipse cx="{fx}" cy="{fy+30}" rx="170" ry="34" fill="#0B4A44"/>'
    def petal(a,l,w,fill):
        return f'<g transform="translate({fx},{fy}) rotate({a})"><path d="M0,0 C{-w},{-l*.35} {-w*.8},{-l*.85} 0,{-l} C{w*.8},{-l*.85} {w},{-l*.35} 0,0Z" fill="url(#{fill})" stroke="#FFF0F6" stroke-opacity=".35" stroke-width="2"/></g>'
    for a in (-78,78): b+=petal(a,150,48,'pet2')
    for a in (-52,52): b+=petal(a,200,56,'pet2')
    for a in (-26,26): b+=petal(a,240,58,'pet')
    b+=petal(0,270,60,'pet')
    b+=f'<circle cx="{fx}" cy="{fy-40}" r="26" fill="#FFD36B" opacity=".5"/>'
    b+=bokeh(14,9,['#BFE9F2','#FFD7E8'],300,900,5,22)
    b+=f'<rect y="1000" width="{W}" height="64" fill="#04101A" opacity=".8"/>'
    return wrap(d,b)

def diya():
    d=grad('bg',[(0,'#1A0A14'),(.55,'#3B1410'),(1,'#7A2A10')])+rad('fl','#FFD27A')+rad('fg','#FF9A2E',.8)+grad('cup',[(0,'#E8A23A'),(1,'#8A4A12')])+rad('fl2','#FFF4D0')
    cx=540
    b=f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'+bokeh(40,4,['#FFB347','#FFD27A','#FF7A3A'],0,900,8,46)
    b+=f'<circle cx="{cx}" cy="560" r="520" fill="url(#fg)" opacity=".55"/>'+rays(cx,560,24,.07,'#FFD27A',3)
    # flame
    b+=f'<path d="M{cx},330 C{cx+70},430 {cx+90},520 {cx},600 C{cx-90},520 {cx-70},430 {cx},330Z" fill="url(#fl)"/>'
    b+=f'<path d="M{cx},430 C{cx+36},490 {cx+42},545 {cx},590 C{cx-42},545 {cx-36},490 {cx},430Z" fill="url(#fl2)"/>'
    b+=f'<path d="M{cx-4},595 L{cx+4},595 L{cx+3},625 L{cx-3},625Z" fill="#2A1008"/>'
    # diya body
    b+=f'<path d="M{cx-250},640 C{cx-220},760 {cx-110},810 {cx},810 C{cx+110},810 {cx+220},760 {cx+250},640 C{cx+150},690 {cx-150},690 {cx-250},640Z" fill="url(#cup)"/>'
    b+=f'<ellipse cx="{cx}" cy="640" rx="250" ry="42" fill="#FFB94D"/><ellipse cx="{cx}" cy="642" rx="212" ry="30" fill="#6A2E0C"/>'
    b+=f'<path d="M{cx-250},640 C{cx-320},620 {cx-340},590 {cx-330},570 C{cx-310},600 {cx-280},612 {cx-240},620Z" fill="#E8A23A"/>'
    # patterns
    for i in range(7):
        x=cx-150+i*50
        b+=f'<circle cx="{x}" cy="735" r="9" fill="#FFD27A" opacity=".85"/>'
    b+=f'<ellipse cx="{cx}" cy="835" rx="260" ry="30" fill="#000" opacity=".35"/>'
    # small diyas
    for x,y,s in [(130,870,.45),(950,880,.5),(300,950,.35),(780,960,.38)]:
        b+=f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-170 C30,-120 36,-80 0,-50 C-36,-80 -30,-120 0,-170Z" fill="url(#fl)"/><path d="M-250,0 C-220,120 -110,170 0,170 C110,170 220,120 250,0 C150,50 -150,50 -250,0Z" fill="url(#cup)"/><ellipse cx="0" cy="0" rx="250" ry="40" fill="#FFB94D"/></g>'
        b+=f'<circle cx="{x}" cy="{y-70*s*2}" r="{120*s}" fill="url(#fg)" opacity=".5"/>'
    return wrap(d,b)

def lone_hill():
    d=grad('sky',[(0,'#04061A'),(.5,'#161A4A'),(.85,'#3C2A7A'),(1,'#7A4A9A')])+rad('gal','#C9B8FF',.6)+rad('mn','#FFF6E0')+grad('h1',[(0,'#1B1F55'),(1,'#0E1038')])+grad('h2',[(0,'#0B0D2E'),(1,'#05061A')])
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    b+=f'<g transform="rotate(-28 540 300)"><ellipse cx="540" cy="300" rx="760" ry="120" fill="url(#gal)" opacity=".55"/><ellipse cx="540" cy="300" rx="520" ry="60" fill="url(#gal)" opacity=".5"/></g>'
    b+=stars(220,640,11,'#F4EFFF')
    b+=f'<circle cx="830" cy="230" r="70" fill="url(#mn)"/><circle cx="830" cy="230" r="150" fill="url(#mn)" opacity=".18"/>'
    b+=mount([(0,640),(140,600),(300,650),(470,590),(640,650),(820,600),(1000,650),(1080,630)],'#241E66')
    b+=f'<path d="M0,760 C180,700 360,690 540,720 C760,760 900,720 1080,700 L1080,{H} L0,{H}Z" fill="url(#h1)"/>'
    b+=f'<path d="M0,860 C260,800 420,790 560,780 C700,775 760,830 1080,850 L1080,{H} L0,{H}Z" fill="url(#h2)"/>'
    b+=person(600,790,1.55,'#03040F')
    b+=f'<circle cx="600" cy="640" r="60" fill="#FFD36B" opacity=".07"/>'
    b+=f'<path d="M0,960 C300,930 600,980 1080,940 L1080,{H} L0,{H}Z" fill="#03040F"/>'
    return wrap(d,b)

def ghat():
    d=grad('sky',[(0,'#2B1250'),(.4,'#B8426B'),(.7,'#FF9B4A'),(1,'#FFD58A')])+rad('sun','#FFF6D6')+rad('gl','#FFC468',.9)+grad('rv',[(0,'#FFB46A'),(.5,'#B4507A'),(1,'#35194F')])
    cx,cy=380,520
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'+stars(40,200)+rays(cx,cy,30,.2,'#FFE29A',2.4)
    b+=f'<circle cx="{cx}" cy="{cy}" r="320" fill="url(#gl)" opacity=".7"/><circle cx="{cx}" cy="{cy}" r="120" fill="url(#sun)"/>'
    b+=mount([(0,600),(200,570),(420,600),(700,560),(1080,590)],'#7A2F63')
    # temple on right
    t=f'<g fill="#1A0E33"><rect x="760" y="520" width="240" height="190"/><path d="M780,520 C790,430 850,380 880,300 C910,380 970,430 980,520Z"/><rect x="872" y="250" width="16" height="60"/><path d="M880,236 L900,252 L880,256Z"/><path d="M740,520 L1020,520 L1000,545 L760,545Z"/><circle cx="880" cy="600" r="26" fill="#FFB46A" opacity=".5"/></g>'
    b+=t
    b+=f'<rect y="700" width="{W}" height="{H-700}" fill="url(#rv)"/>'
    for i in range(9):
        y=720+i*34; w=60+i*80
        b+=f'<ellipse cx="{cx}" cy="{y}" rx="{w}" ry="5" fill="#FFE2A0" opacity="{.5-i*.04:.2f}"/>'
    # steps
    for i in range(6):
        y=690+i*14
        b+=f'<rect x="{680-i*30}" y="{y}" width="{400+i*30}" height="16" fill="#1A0E33" opacity="{.95-i*.05:.2f}"/>'
    # boat with person
    b+=f'<g transform="translate(300,770)"><path d="M-110,0 L110,0 L80,26 L-80,26Z" fill="#0F0824"/><path d="M-110,0 C-60,-28 60,-28 110,0" fill="#0F0824"/>{person(10,0,.55,"#0F0824")}<line x1="-70" y1="-6" x2="110" y2="-80" stroke="#0F0824" stroke-width="4"/></g>'
    b+=f'<path d="M0,980 C300,960 700,1000 1080,970 L1080,{H} L0,{H}Z" fill="#12091F"/>'
    b+=bokeh(8,2,['#FFD27A'],740,960,4,12)
    return wrap(d,b)

def peepal():
    d=grad('sky',[(0,'#16294A'),(.45,'#6A6BA0'),(.75,'#F3A56A'),(1,'#FFD98A')])+rad('sun','#FFF6D6')+rad('gl','#FFD36B',.8)+grad('fd',[(0,'#6B7A2E'),(1,'#1E2A14')])
    cx,cy=330,560
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'+stars(40,220,8)+rays(cx,cy,28,.16,'#FFF0B8',2.6)
    b+=f'<circle cx="{cx}" cy="{cy}" r="300" fill="url(#gl)" opacity=".8"/><circle cx="{cx}" cy="{cy}" r="110" fill="url(#sun)"/>'
    b+=mount([(0,650),(180,610),(380,650),(620,600),(860,640),(1080,610)],'#8A6A8E')
    b+=f'<path d="M0,700 C250,670 500,720 800,690 C950,675 1030,690 1080,690 L1080,{H} L0,{H}Z" fill="url(#fd)"/>'
    # tree
    t='#10130A'
    b+=f'<g fill="{t}"><path d="M690,900 C700,800 690,720 676,640 C640,600 600,560 560,540 L580,520 C620,540 660,570 690,600 C700,520 690,460 660,420 L684,410 C714,450 726,520 722,596 C760,560 800,520 850,500 L860,522 C820,545 780,580 744,640 C740,720 746,810 770,900Z"/>'
    for (x,y,r) in [(540,470,110),(640,380,130),(760,360,120),(870,430,120),(930,520,90),(480,560,80),(700,470,130),(820,500,110)]:
        b+=f'<circle cx="{x}" cy="{y}" r="{r}"/>'
    b+='</g>'
    # light leaves hearts
    b+=bokeh(18,12,['#FFD36B'],330,640,4,10)
    b+=person(330,860,.9,'#0A0C05')
    b+=f'<path d="M0,930 C300,900 700,950 1080,915 L1080,{H} L0,{H}Z" fill="#0B0F07"/>'
    return wrap(d,b)

def peak():
    d=grad('sky',[(0,'#0B1E4A'),(.5,'#2C5C9A'),(.85,'#9CC6E8'),(1,'#F6E6C8')])+rad('sun','#FFFFFF')+rad('gl','#FFE9A8',.8)+grad('p1',[(0,'#FFFFFF'),(.25,'#C9D8EE'),(1,'#3C5486')])+grad('p2',[(0,'#5A74A8'),(1,'#1B2A55')])+grad('p3',[(0,'#22335F'),(1,'#0B1332')])
    cx,cy=540,380
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'+stars(60,300,2,'#FFFFFF')
    b+=f'<circle cx="{cx}" cy="{cy}" r="380" fill="url(#gl)" opacity=".6"/>'
    for r,o in [(240,.5),(180,.35),(300,.25)]:
        b+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FFE9A8" stroke-opacity="{o}" stroke-width="2"/>'
    b+=f'<circle cx="{cx}" cy="{cy}" r="120" fill="url(#sun)"/>'
    for k in range(16):
        a=math.radians(k*22.5); b+=f'<line x1="{cx+260*math.cos(a)}" y1="{cy+260*math.sin(a)}" x2="{cx+300*math.cos(a)}" y2="{cy+300*math.sin(a)}" stroke="#FFE9A8" stroke-opacity=".5" stroke-width="3"/>'
    b+=mount([(0,720),(150,620),(260,690),(420,560),(540,650),(700,540),(860,660),(980,600),(1080,680)],'#7C93C2')
    b+=mount([(0,780),(200,700),(330,760),(540,520),(760,770),(900,700),(1080,790)],'url(#p1)')
    b+=f'<path d="M540,520 L470,640 L510,625 L540,680 L575,625 L610,650Z" fill="#FFFFFF" opacity=".5"/>'
    b+=mount([(0,860),(240,800),(460,860),(700,790),(900,850),(1080,810)],'url(#p2)')
    b+=f'<path d="M0,930 C300,880 700,940 1080,890 L1080,{H} L0,{H}Z" fill="url(#p3)"/>'
    b+=person(540,520,.42,'#0B1332')
    b+=f'<path d="M0,0" />'
    return wrap(d,b)

def forest():
    d=grad('sky',[(0,'#04170F'),(.5,'#0F3B2A'),(1,'#2F7A4A')])+rad('gl','#E8FFC8',.7)
    cx=620
    b=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    b+=f'<circle cx="{cx}" cy="260" r="420" fill="url(#gl)" opacity=".5"/>'
    # beams
    for i,x in enumerate([400,520,640,760,880]):
        b+=f'<polygon points="{x},0 {x+60},0 {x-200+i*30},{H-100} {x-330+i*30},{H-100}" fill="#E8FFC8" opacity="{.10 if i%2 else .16}"/>'
    # far trees
    r=random.Random(5)
    for layer,(col,ys,hs,n) in enumerate([('#0F3B2A',640,420,16),('#0A2A1E',700,520,12),('#04130D',800,640,9)]):
        for i in range(n):
            x=r.randint(-40,W+40); h=hs*r.uniform(.7,1.1); w=r.randint(18,34)+layer*10
            b+=f'<g fill="{col}"><rect x="{x-w/2}" y="{ys-h}" width="{w}" height="{h+400}"/><ellipse cx="{x}" cy="{ys-h}" rx="{w*3.2}" ry="{w*2.2}"/></g>'
    # path
    b+=f'<path d="M420,{H} C480,880 520,800 560,720 L600,720 C620,820 700,900 860,{H}Z" fill="#C5E39A" opacity=".35"/>'
    b+=person(590,830,.8,'#020B07')
    b+=bokeh(30,6,['#E8FFC8','#BDF08A'],100,900,3,10)
    b+=f'<path d="M0,960 C300,930 700,985 1080,945 L1080,{H} L0,{H}Z" fill="#020B07"/>'
    return wrap(d,b)

SCENES={'chariot':sunrise_chariot,'lotus':lotus_moon,'diya':diya,'hill':lone_hill,'ghat':ghat,'peepal':peepal,'peak':peak,'forest':forest}
if __name__=='__main__':
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':W,'height':H})
        for k,f in SCENES.items():
            pg.set_content(f'<body style="margin:0">{f()}</body>'); pg.screenshot(path=f'scene_{k}.png')
        b.close()
    from PIL import Image
    ims=[Image.open(f'scene_{k}.png').resize((405,399)) for k in SCENES]
    sh=Image.new('RGB',(405*4,399*2))
    for i,im in enumerate(ims): sh.paste(im,((i%4)*405,(i//4)*399))
    sh.save('sheet.png')
