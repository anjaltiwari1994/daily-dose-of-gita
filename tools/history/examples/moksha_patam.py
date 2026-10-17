"""EXAMPLE History Short: Snakes and Ladders / Moksha Patam (published 17 Oct 2026).
Copy this file for a new Short and rewrite the scenes. Run:
  python3 tools/history/examples/moksha_patam.py WORKDIR OUT.mp4 --audio mix_yt     (YouTube version)
  python3 tools/history/examples/moksha_patam.py WORKDIR OUT.mp4 --audio voice      (Instagram version)
  python3 tools/history/examples/moksha_patam.py WORKDIR preview.jpg --preview 1.5,8,15,25,40
WORKDIR must contain timeline.json, voice.wav and mix_yt.wav from tools/history/audio.py.
Segment indices below refer to the caption chunks in captions.json (0-based).
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *

sh = Short(sys.argv[1])
SEG, TOTAL = sh.SEG, sh.TOTAL

def draw_snake(d, pts, width, col, head=True, frac=1.0):
    m = max(2, int(len(pts)*frac))
    p = pts[:m]
    for k in range(len(p)-1):
        w = width*(0.35+0.65*min(1, (k+8)/len(pts)*1.6)) if False else width*(0.45+0.55*(1-k/len(pts)))
        d.line([p[k], p[k+1]], fill=col, width=int(w))
        if k % 6 == 0:
            d.ellipse([p[k][0]-w*0.18, p[k][1]-w*0.18, p[k][0]+w*0.18, p[k][1]+w*0.18], fill=(250, 220, 120))
    if head and frac > 0.02:
        hx, hy = pts[0]; r = width*0.75
        d.ellipse([hx-r, hy-r*0.8, hx+r, hy+r*0.8], fill=col)
        d.ellipse([hx-r*0.45, hy-r*0.35, hx-r*0.15, hy-r*0.05], fill=(255, 240, 200))
        d.ellipse([hx+r*0.15, hy-r*0.35, hx+r*0.45, hy-r*0.05], fill=(255, 240, 200))

def draw_ladder(d, x0, y0, x1, y1, w, col, rungs=7, frac=1.0):
    dx, dy = x1-x0, y1-y0; L = math.hypot(dx, dy); nx, ny = -dy/L*w/2, dx/L*w/2
    fx, fy = x0+dx*frac, y0+dy*frac
    d.line([x0+nx, y0+ny, fx+nx, fy+ny], fill=col, width=9)
    d.line([x0-nx, y0-ny, fx-nx, fy-ny], fill=col, width=9)
    for k in range(1, rungs+1):
        t = k/(rungs+1)
        if t > frac: break
        cx, cy = x0+dx*t, y0+dy*t
        d.line([cx+nx, cy+ny, cx-nx, cy-ny], fill=col, width=7)

def make_board(size=900):
    img = Image.new("RGBA", (size, size), (0,0,0,0)); d = ImageDraw.Draw(img)
    c = size/10; fnt = F("inter7", 22)
    tones = [(222, 196, 150), (196, 160, 110)]
    for r in range(10):
        for q in range(10):
            x0, y0 = q*c, r*c
            d.rectangle([x0, y0, x0+c, y0+c], fill=tones[(r+q) % 2]+(255,), outline=(120, 80, 40, 255), width=2)
            row = 9-r; num = row*10 + (q+1 if row % 2 == 0 else 10-q)
            d.text((x0+8, y0+5), str(num), font=fnt, fill=(90, 55, 25, 255))
    # top-left square 100 = moksha
    d.rectangle([0, 0, c, c], fill=(250, 210, 120, 255), outline=(150, 90, 30, 255), width=4)
    d.text((c/2, c/2+8), "मोक्ष", font=F("deva", 34), fill=(120, 40, 20, 255), anchor="mm")
    for (a, b) in [((1.5, 9.5), (2.5, 6.5)), ((6.5, 8.5), (7.5, 4.5)), ((3.5, 4.5), (4.5, 1.5)), ((8.5, 3.5), (8.5, 0.5))]:
        draw_ladder(d, a[0]*c, a[1]*c, b[0]*c, b[1]*c, 46, (110, 70, 30, 255), rungs=5)
    for (h, t, c1, c2, col) in [((5.5, 1.5), (3.5, 6.5), (7.5, 3), (2, 4.5), (60, 140, 70, 255)),
                                ((2.5, 2.5), (1.5, 5.5), (0.5, 3.5), (3.5, 4.5), (170, 50, 40, 255)),
                                ((8.5, 6.5), (6.5, 9.5), (9.8, 8), (5.5, 8), (190, 120, 30, 255))]:
        pts = bezier((h[0]*c, h[1]*c), (t[0]*c, t[1]*c), (c1[0]*c, c1[1]*c), (c2[0]*c, c2[1]*c))
        draw_snake(d, pts, 30, col)
    frame = Image.new("RGBA", (size+40, size+40), (70, 40, 20, 255))
    ImageDraw.Draw(frame).rectangle([6, 6, size+33, size+33], outline=GOLD+(255,), width=4)
    frame.alpha_composite(img, (20, 20))
    return frame
BOARD = make_board()


# scene windows: name -> (first caption index, last caption index)
S = {k: (SEG[a]["start"]-0.15, SEG[b]["end"]+0.2) for k, (a, b) in
     {"hook": (0, 1), "title": (2, 4), "karma": (5, 5), "ladder": (6, 8), "snake": (9, 10),
      "moksha": (11, 13), "travel": (14, 17), "bite": (18, 20), "cta": (21, 21)}.items()}
S["hook"] = (0, S["hook"][1]); S["cta"] = (S["cta"][0], TOTAL)

def scene_hook(c, t):
    a0, a1 = S["hook"]; k = (t-a0)/(a1-a0)
    al = fade(t, a0, a1, 0.25, 0.3)
    sc = 0.95 + 0.12*k
    b = BOARD.copy()
    if al < 1: b.putalpha(b.getchannel("A").point(lambda v: int(v*al)))
    b = b.rotate(-4+6*k, resample=Image.BICUBIC, expand=True)
    put(c, b, W/2, 930, sc*0.82)
    put(c, text_layer("YOU'VE PLAYED THIS", F("cinzel8", 64), CREAM, al, glow=(0,0,0)), W/2, 250)
    put(c, text_layer("GAME 100 TIMES", F("cinzel8", 92), GOLD2, al, glow=(120, 60, 0)), W/2, 345)

def scene_title(c, t):
    a0, a1 = S["title"]; al = fade(t, a0, a1)
    b = BOARD.copy().resize((520, 520), Image.LANCZOS)
    b.putalpha(b.getchannel("A").point(lambda v: int(v*0.35*al)))
    put(c, b, W/2, 820, 1.0 + 0.08*(t-a0)/(a1-a0))
    s2 = SEG[3]["start"]; s3 = SEG[4]["start"]
    put(c, text_layer("SNAKES & LADDERS", F("cinzel8", 74), CREAM, al, glow=(0,0,0)), W/2, 330)
    a2 = al*out_cubic((t-s2)/0.4)
    put(c, text_layer("was born in", F("play", 58), GOLD, a2), W/2, 440)
    put(c, text_layer("INDIA", F("cinzel8", 120), GOLD2, a2, glow=(140, 60, 0)), W/2, 560, 0.9+0.1*out_cubic((t-s2)/0.5))
    a3 = al*out_cubic((t-s3)/0.4)
    put(c, text_layer("मोक्ष पटम", F("deva", 150), GOLD2, a3, glow=(160, 70, 0)), W/2, 1000 - 30*out_cubic((t-s3)/0.6))
    put(c, text_layer("MOKSHA PATAM", F("cinzel", 58), CREAM, a3), W/2, 1130)

def scene_karma(c, t):
    a0, a1 = S["karma"]; al = fade(t, a0, a1, 0.25, 0.25); k = (t-a0)/(a1-a0)
    put(c, text_layer("A GAME TO TEACH", F("cinzel", 60), CREAM, al), W/2, 520)
    put(c, text_layer("कर्म", F("deva", 260), GOLD2, al, glow=(170, 80, 0)), W/2, 800, 0.9+0.15*out_cubic(k*1.5))
    put(c, text_layer("KARMA", F("cinzel8", 96), GOLD, al), W/2, 1020)

def scene_ladder(c, t):
    a0, a1 = S["ladder"]; al = fade(t, a0, a1)
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    grow = out_cubic((t-a0)/1.6)
    draw_ladder(d, W/2, 1240, W/2, 330, 170, GOLD+(255,), rungs=8, frac=grow)
    if al < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v*al)))
    g = L.filter(ImageFilter.GaussianBlur(10)); c.alpha_composite(g); c.alpha_composite(L)
    put(c, text_layer("LADDER = VIRTUE", F("cinzel8", 70), GREEN, al*out_cubic((t-SEG[7]["start"])/0.4), glow=(0, 40, 0)), W/2, 210)
    s9 = SEG[8]["start"]
    for j, (wd, yy) in enumerate([("Generosity", 1010), ("Humility", 760)]):
        ta = s9 + j*0.9
        a = al*out_cubic((t-ta)/0.4)
        put(c, text_layer(wd, F("play", 66), CREAM, a, glow=(0,0,0)), W/2 + (260 if j % 2 == 0 else -260), yy - 40*out_cubic((t-ta)/0.5))
    a = al*out_cubic((t-(s9+2.6))/0.4)
    put(c, text_layer("↑", F("inter", 120), GOLD2, a), W/2, 420 - 60*out_cubic((t-(s9+2.6))/0.8))

SNAKE = bezier((W/2+40, 360), (W/2-60, 1230), (W/2+430, 640), (W/2-470, 930), 160)
def scene_snake(c, t):
    a0, a1 = S["snake"]; al = fade(t, a0, a1)
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    draw_snake(d, SNAKE, 74, (175, 45, 35, 255), frac=out_cubic((t-a0)/1.4))
    if al < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v*al)))
    c.alpha_composite(L)
    put(c, text_layer("SNAKE = VICE", F("cinzel8", 74), RED, al, glow=(40, 0, 0)), W/2, 210)
    s11 = SEG[10]["start"]
    for j, (wd, x, y) in enumerate([("Anger", W/2-250, 620), ("Greed", W/2+250, 930)]):
        ta = s11 + j*0.7; a = al*out_cubic((t-ta)/0.35)
        put(c, text_layer(wd, F("play", 72), CREAM, a, glow=(0,0,0)), x, y)
    a = al*out_cubic((t-(s11+1.6))/0.4)
    put(c, text_layer("↓", F("inter", 120), RED, a), W/2, 1180 + 60*out_cubic((t-(s11+1.6))/0.8))

def scene_moksha(c, t):
    a0, a1 = S["moksha"]; al = fade(t, a0, a1)
    put(c, text_layer("THE FINAL SQUARE", F("cinzel", 62), CREAM, al), W/2, 300)
    s13 = SEG[12]["start"]; k = out_cubic((t-s13+0.6)/0.8)
    sq = 300 + 60*math.sin(t*2)*0.1
    G = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(G)
    r = 210
    d.rounded_rectangle([W/2-r, 760-r, W/2+r, 760+r], radius=28, fill=(250, 205, 110, int(255*al)), outline=(255, 240, 190, int(255*al)), width=8)
    glow = G.filter(ImageFilter.GaussianBlur(40 + 20*k)); c.alpha_composite(glow); c.alpha_composite(G)
    put(c, text_layer("100", F("cinzel8", 70), (120, 40, 20), al), W/2, 620)
    put(c, text_layer("मोक्ष", F("deva", 170), (110, 30, 15), al*k), W/2, 790, 0.85+0.15*k)
    s14 = SEG[13]["start"]; a = al*out_cubic((t-s14)/0.4)
    put(c, text_layer("MOKSHA", F("cinzel8", 100), GOLD2, al*k, glow=(150, 60, 0)), W/2, 1080)
    put(c, text_layer("freedom from rebirth", F("play", 60), CREAM, a), W/2, 1180)

def scene_travel(c, t):
    a0, a1 = S["travel"]; al = fade(t, a0, a1)
    put(c, text_layer("BRITISH RULE", F("cinzel8", 78), CREAM, al, glow=(0,0,0)), W/2, 280)
    # route: India (bottom right) -> England (top left)
    p0, p1 = (W*0.70, 1080), (W*0.30, 560)
    s16 = SEG[15]["start"]; k = out_cubic((t-s16)/1.3)
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    pts = [(p0[0]+(p1[0]-p0[0])*u + math.sin(u*math.pi)*-160, p0[1]+(p1[1]-p0[1])*u) for u in np.linspace(0, k, 60)]
    for q in range(0, len(pts)-1, 2): d.line([pts[q], pts[q+1]], fill=GOLD+(int(255*al),), width=8)
    for (p, lab) in [(p0, "INDIA"), (p1, "ENGLAND")]:
        if lab == "ENGLAND" and k < 0.98: continue
        d.ellipse([p[0]-18, p[1]-18, p[0]+18, p[1]+18], fill=GOLD2+(int(255*al),))
    c.alpha_composite(L)
    put(c, text_layer("INDIA", F("cinzel8", 64), GOLD2, al), p0[0], p0[1]+70)
    put(c, text_layer("ENGLAND", F("cinzel8", 64), GOLD2, al*out_cubic((t-s16-1.2)/0.4)), p1[0], p1[1]-70)
    s17 = SEG[16]["start"]; s18 = SEG[17]["start"]
    a = al*out_cubic((t-s17)/0.4)
    put(c, text_layer("the lessons faded...", F("play", 62), (200, 180, 150), a*(1-0.6*out_cubic((t-s18)/0.6))), W/2, 1300)
    a = al*out_cubic((t-s18)/0.4)
    put(c, text_layer("...the fun stayed", F("cinzel8", 64), GOLD2, a, glow=(120, 50, 0)), W/2, 1400)

def scene_bite(c, t):
    a0, a1 = S["bite"]; al = fade(t, a0, a1, 0.2, 0.25)
    s20 = SEG[19]["start"]; s21 = SEG[20]["start"]
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    pts = bezier((W/2, 470), (W/2-40, 960), (W/2+360, 600), (W/2-360, 820), 140)
    draw_snake(d, pts, 64, (175, 45, 35, 255), frac=out_cubic((t-a0)/1.2))
    if al < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v*al)))
    shake = 10*math.sin(t*60)*max(0, 1-(t-s21)/0.4) if t > s21 else 0
    c.alpha_composite(L, (int(shake), 0))
    put(c, text_layer("next time a snake bites you...", F("play", 58), CREAM, al), W/2, 300)
    a = al*out_cubic((t-s20)/0.3)
    put(c, text_layer("maybe it's", F("cinzel", 66), CREAM, a), W/2, 1090)
    a = al*out_cubic((t-s21)/0.25)
    put(c, text_layer("KARMA", F("cinzel8", 170), GOLD2, a, glow=(190, 70, 0)), W/2 + shake, 1240, 1.25-0.25*out_cubic((t-s21)/0.35))

def scene_cta(c, t):
    a0, a1 = S["cta"]; al = fade(t, a0, a1+1, 0.35, 0.3)
    put(c, text_layer("FORGOTTEN STORIES", F("cinzel8", 72), GOLD2, al, glow=(120, 50, 0)), W/2, 620)
    put(c, text_layer("FROM INDIA", F("cinzel8", 72), GOLD2, al, glow=(120, 50, 0)), W/2, 710)
    a = al*out_cubic((t-a0-0.4)/0.4)
    put(c, text_layer("Follow for more", F("play", 64), CREAM, a), W/2, 850)
    a = al*out_cubic((t-a0-1.0)/0.4)
    put(c, text_layer("DAILY DOSE OF WOW", F("inter", 52), (255, 255, 255), a, glow=(0,0,0)), W/2, 1000)


for name, fn in [("hook", scene_hook), ("title", scene_title), ("karma", scene_karma), ("ladder", scene_ladder),
                 ("snake", scene_snake), ("moksha", scene_moksha), ("travel", scene_travel), ("bite", scene_bite), ("cta", scene_cta)]:
    a0, a1 = S[name]; sh.add(name, a0, a1 + (1 if name == "cta" else 0), fn)
sh.run(sys.argv[2:])
