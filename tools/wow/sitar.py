"""Tanpura drone + sitar phrases (raag Yaman feel) whose accents land on given scene-change times. Free, synthesized.
make(T, cuts, path): T = length in s, cuts = scene-change times in s (a swarmandal sweep + a new sitar phrase starts on each)."""
import numpy as np, wave
from scipy.signal import lfilter
SR = 44100
SA = 138.59  # C#3
# Yaman: S R G M# P D N (just-ish ratios)
R = {'S': 1, 'R': 9/8, 'G': 5/4, 'M': 45/32, 'P': 3/2, 'D': 5/3, 'N': 15/8}

def note(sym):
    oct = 1
    while sym.endswith("'"): oct *= 2; sym = sym[:-1]
    while sym.startswith('.'): oct /= 2; sym = sym[1:]
    return SA * 2 * R[sym] * oct  # sitar plays one octave above the drone Sa

def ks(f, dur, amp, rng, bright=0.996):
    """Karplus-Strong pluck with a little jawari buzz."""
    n = int(SR * dur); N = max(2, int(SR / f))
    x = np.zeros(n); x[:N] = rng.uniform(-1, 1, N)
    b = [1.0]; a = np.zeros(N + 2); a[0] = 1; a[N] = -bright / 2; a[N + 1] = -bright / 2
    y = lfilter(b, a, x)
    y = np.tanh(2.2 * y) / np.tanh(2.2)  # buzz
    y += 0.25 * np.diff(np.concatenate([[0], y]))  # brighter attack
    return amp * y * np.exp(-np.arange(n) / SR / (dur / 2.2))

def add(buf, t0, sig):
    i = int(t0 * SR)
    if i >= len(buf): return
    m = min(len(sig), len(buf) - i); buf[i:i + m] += sig[:m]

def tanpura(T):
    t = np.arange(int(SR * T)) / SR; y = np.zeros_like(t)
    def pl(f0, start, period, amp):
        o = np.zeros_like(t); s = start
        while s < T:
            m = t >= s; tt = (t - s)[m]; env = np.exp(-tt / 3.2) * (1 - np.exp(-tt * 40))
            # jawari: rich harmonics with slow shimmer
            o[m] += amp * env * sum((1 / k ** 0.9) * np.sin(2 * np.pi * f0 * k * tt + .3 * k) * (1 + .3 * np.sin(2 * np.pi * (0.7 + k * .13) * tt)) for k in range(1, 13))
            s += period
        return o
    per = 3.2
    y = pl(SA * 1.5 / 2, 0, per, .38) + pl(SA, .8, per, .32) + pl(SA, 1.6, per, .32) + pl(SA / 2, 2.4, per, .45)
    return y

def sweep(buf, t0, rng, up=True):
    notes = ['S', 'R', 'G', 'M', 'P', 'D', 'N', "S'", "R'", "G'"]
    if not up: notes = notes[::-1]
    for i, s in enumerate(notes):
        add(buf, t0 + i * 0.035, ks(note(s) * 2, 1.6, .16, rng, 0.998))

def make(T, cuts, path):
    rng = np.random.default_rng(7)
    y = tanpura(T) * 0.30
    s = np.zeros_like(y)
    # phrases: list of (offset, swar, length)
    P1 = [(0.0, "S'", 1.6), (0.5, 'N', .9), (0.9, 'D', 1.4)]
    P2 = [(0.0, '.N', .7), (0.35, 'R', .7), (0.7, 'G', 1.4), (2.4, 'M', .8), (2.8, 'G', .8), (3.2, 'R', 1.2), (4.6, 'S', 2.2),
          (7.0, 'G', .8), (7.4, 'M', .8), (7.8, 'P', 1.6), (9.4, 'M', .8), (9.8, 'G', 2.0)]
    P3 = [(0.0, 'P', .7), (0.35, 'D', .7), (0.7, 'N', .7), (1.05, "S'", 2.4), (3.6, 'N', .8), (4.0, 'D', .8), (4.4, 'P', 1.6),
          (6.4, 'M', .8), (6.8, 'G', .8), (7.2, 'R', 1.2), (8.6, 'G', .7), (9.0, 'R', .7), (9.4, 'S', 3.0)]
    phrases = [P1, P2, P3, P3]
    starts = [0.25] + list(cuts)
    for k, t0 in enumerate(starts):
        if k > 0: sweep(s, t0 - 0.15, rng)
        for off, sw, ln in phrases[min(k, len(phrases) - 1)]:
            if t0 + off < T - 1.5:
                add(s, t0 + off + (k > 0) * 0.2, ks(note(sw), ln + 0.8, .85 if off == 0 else .62, rng))
    y = y + s
    t = np.arange(len(y)) / SR
    y *= np.minimum(1, t / 0.4) * np.minimum(1, (T - t) / 2.0)
    y = y / np.max(np.abs(y)) * 0.6
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
