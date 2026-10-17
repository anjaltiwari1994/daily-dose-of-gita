"""Shared drawing + encoding helpers for History Shorts (1080x1920, 30 fps, free).

A Short is a small Python file (see examples/moksha_patam.py) that defines scene functions and calls run().
Look: dark parchment/ink background, gold accents, floating gold dust, word-highlight captions,
thin gold progress bar on top. Fonts are in tools/history/fonts (SIL OFL).
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
W, H, FPS = 1080, 1920, 30
GOLD = (232, 190, 110); GOLD2 = (255, 214, 140); CREAM = (245, 230, 200)
RED = (214, 72, 52); GREEN = (120, 190, 120); BLUE = (120, 180, 230)

_FONTS = {"cinzel": "cinzel-latin-700-normal.woff", "cinzel8": "cinzel-latin-800-normal.woff",
          "inter": "inter-latin-800-normal.woff", "inter7": "inter-latin-700-normal.woff",
          "inter4": "inter-latin-400-normal.woff", "play": "playfair-display-latin-400-italic.woff",
          "deva": "tiro-devanagari-sanskrit-devanagari-400-normal.woff", "poppins": "poppins-latin-700-normal.woff"}
_cache = {}
def F(name, size):
    k = (name, size)
    if k not in _cache: _cache[k] = ImageFont.truetype(os.path.join(FD, _FONTS[name]), size)
    return _cache[k]

def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def out_cubic(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def fade(t, t0, t1, fin=0.35, fout=0.3):
    if t < t0 or t > t1: return 0.0
    return min(ease((t - t0) / fin), ease((t1 - t) / fout))

rng = np.random.default_rng(3)
def make_bg(tint=(1.0, 1.0, 1.0)):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.42) / H * 1.15) ** 2)
    v = np.clip(1.0 - r * 1.55, 0, 1)
    base = np.stack([(30 + 46 * v) * tint[0], (16 + 26 * v) * tint[1], (10 + 14 * v) * tint[2]], -1)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n * 30) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255 - 0.5
    base = base * (1 + n[..., None] * 0.35 + rng.normal(0, 1, (H, W, 1)).astype(np.float32) * 0.025)
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (mx, my, R) in [(W / 2, -40, 520), (W / 2, H + 60, 560)]:
        for k in range(6):
            rr = R - k * 70; d.ellipse([mx - rr, my - rr, mx + rr, my + rr], outline=GOLD + (18,), width=2)
        for a in range(0, 360, 10):
            t = math.radians(a)
            d.line([mx + math.cos(t) * 120, my + math.sin(t) * 120, mx + math.cos(t) * R, my + math.sin(t) * R], fill=GOLD + (10,), width=2)
    img.alpha_composite(ov)
    return img.convert("RGB")

def text_layer(txt, font, fill, alpha=1.0, glow=None, stroke=0, stroke_fill=(0, 0, 0)):
    bb = font.getbbox(txt, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 60
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.text((30 - bb[0], 30 - bb[1]), txt, font=font, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    if glow:
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text((30 - bb[0], 30 - bb[1]), txt, font=font, fill=glow + (255,))
        g = g.filter(ImageFilter.GaussianBlur(14)); g.alpha_composite(L); L = g
    if alpha < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    return L

def put(canvas, layer, cx, cy, scale=1.0):
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.LANCZOS)
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))

def with_alpha(layer, al):
    if al < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * al)))
    return layer

def wrap(txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        tst = (cur + " " + w).strip()
        if font.getlength(tst) <= maxw: cur = tst
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def bezier(p0, p3, c1, c2, n=120):
    return [((1-t)**3*p0[0] + 3*(1-t)**2*t*c1[0] + 3*(1-t)*t**2*c2[0] + t**3*p3[0],
             (1-t)**3*p0[1] + 3*(1-t)**2*t*c1[1] + 3*(1-t)*t**2*c2[1] + t**3*p3[1]) for t in (k / n for k in range(n + 1))]

# -------- runtime --------
class Short:
    """Loads WORKDIR/timeline.json; scenes are (name, t0, t1, fn(canvas, t)) tuples."""
    def __init__(self, workdir, tint=(1, 1, 1)):
        self.wd = workdir
        tl = json.load(open(os.path.join(workdir, "timeline.json")))
        self.SEG, self.TOTAL = tl["segments"], tl["total"]
        self.BG = make_bg(tint); self.scenes = []
        n = 70; self.px = rng.uniform(0, W, n); self.py = rng.uniform(0, H, n)
        self.ps = rng.uniform(1.5, 4.5, n); self.pv = rng.uniform(8, 30, n); self.ph = rng.uniform(0, 6.28, n)
        self.capf = F("inter", 62); self.hide_captions = []
    def s(self, i): return self.SEG[i]["start"]
    def e(self, i): return self.SEG[i]["end"]
    def span(self, a, b, pre=0.15, post=0.2): return (self.s(a) - pre, self.e(b) + post)
    def add(self, name, t0, t1, fn): self.scenes.append((name, t0, t1, fn))

    def captions(self, c, t):
        cur = None
        for s in self.SEG:
            if s["start"] - 0.05 <= t <= s["end"] + 0.15: cur = s
        if not cur or cur["i"] in self.hide_captions: return
        words = cur["text"].split(); dur = max(0.2, cur["end"] - cur["start"])
        lens = np.array([len(w) + 2 for w in words], float); cum = np.cumsum(lens) / lens.sum()
        prog = (t - cur["start"]) / dur
        lines = wrap(cur["text"], self.capf, 900)
        L = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(L); yy, wi = 20, 0
        for ln in lines:
            x = W / 2 - self.capf.getlength(ln) / 2
            for w in ln.split():
                spoken = prog >= (cum[wi - 1] if wi > 0 else 0)
                col = (255, 214, 120) if spoken and prog < cum[wi] + 0.02 else (255, 255, 255)
                a = 255 if spoken else 110
                d.text((x, yy), w, font=self.capf, fill=col + (a,), stroke_width=7, stroke_fill=(10, 5, 2, a))
                x += self.capf.getlength(w + " "); wi += 1
            yy += 80
        c.alpha_composite(L, (0, int(1490 - (len(lines) - 1) * 40 - 40)))

    def frame(self, t):
        c = self.BG.copy().convert("RGBA")
        P = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
        for q in range(len(self.px)):
            yy = (self.py[q] - self.pv[q] * t) % H; xx = self.px[q] + 12 * math.sin(t * 0.6 + self.ph[q])
            a = int(110 * (0.5 + 0.5 * math.sin(t * 1.3 + self.ph[q])))
            d.ellipse([xx - self.ps[q], yy - self.ps[q], xx + self.ps[q], yy + self.ps[q]], fill=GOLD2 + (a,))
        c.alpha_composite(P)
        for _, t0, t1, fn in self.scenes:
            if t0 <= t <= t1: fn(c, t)
        self.captions(c, t)
        ImageDraw.Draw(c).rectangle([0, 0, int(W * t / self.TOTAL), 8], fill=GOLD + (200,))
        return c.convert("RGB")

    def run(self, argv):
        """argv: OUT.mp4 [--audio voice|mix_yt] [--preview t1,t2,...]"""
        out = argv[0]
        if "--preview" in argv:
            ts = [float(x) for x in argv[argv.index("--preview") + 1].split(",")]
            th = [self.frame(t).resize((270, 480)) for t in ts]
            sheet = Image.new("RGB", (270 * len(th), 480))
            for k, im in enumerate(th): sheet.paste(im, (270 * k, 0))
            sheet.save(out, quality=85); print("preview saved", out); return
        audio = argv[argv.index("--audio") + 1] if "--audio" in argv else "mix_yt"
        tmp = out + ".tmp.mp4"; n = int(self.TOTAL * FPS)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-i", os.path.join(self.wd, audio + ".wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", tmp], stdin=subprocess.PIPE)
        for k in range(n):
            p.stdin.write(self.frame(k / FPS).tobytes())
            if k % 300 == 0: print(k, "/", n, flush=True)
        p.stdin.close(); p.wait()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=7",
                        "-ar", "44100", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
        os.remove(tmp); print("done", out)
