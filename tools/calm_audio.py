#!/usr/bin/env python3
"""Soothing Gita soundscape (free, numpy only): flowing river water + soft droplets, tanpura drone,
slow bansuri-like flute phrase, temple bell at the start and a soft bell when the 'apply it' part begins.
Usage: python3 tools/calm_audio.py out.wav [seconds] [bell2_time]   (stereo 44.1 kHz WAV)"""
import sys, wave
import numpy as np
SR = 44100

def _bandnoise(n, lo, hi, rng):
    """white noise band-passed in the frequency domain (smooth edges)"""
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    g = np.clip((f - lo * .7) / (lo * .3), 0, 1) * np.clip((hi * 1.3 - f) / (hi * .3), 0, 1) / np.sqrt(np.maximum(f, 20))
    y = np.fft.irfft(X * g, n); return y / (np.max(np.abs(y)) + 1e-9)

def _bell(t, t0, f, amp, decay=2.2):
    m = t >= t0; tt = np.where(m, t - t0, 0)
    return m * amp * np.exp(-tt / decay) * (1 - np.exp(-tt * 400)) * (np.sin(2*np.pi*f*tt) + .45*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt) + .2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-2*tt))

def _flute(t, notes, amp):
    """notes: list of (start, dur, freq). sine + soft 2nd/3rd harmonic, vibrato, breath noise, slow attack."""
    rng = np.random.default_rng(11); breath = _bandnoise(len(t), 1500, 5000, rng)
    y = np.zeros_like(t)
    for s, d, f in notes:
        m = (t >= s) & (t < s + d + 1.2); tt = t[m] - s
        env = np.clip(tt / .35, 0, 1) * np.clip((d + 1.2 - tt) / 1.2, 0, 1)
        vib = 1 + .006 * np.sin(2*np.pi*5.2*tt) * np.clip((tt - .4) / .6, 0, 1)
        ph = 2*np.pi*np.cumsum(f * vib) / SR
        y[m] += amp * env * (np.sin(ph) + .18*np.sin(2*ph) + .06*np.sin(3*ph) + .05*breath[m])
    return y

def make(T, path, bell2=8.6):
    n = int(SR * T); t = np.arange(n) / SR; rng = np.random.default_rng(7)
    # river: two bands of noise with slow, independent swells (left/right differ slightly)
    def river(seed):
        r = np.random.default_rng(seed)
        low = _bandnoise(n, 120, 700, r) * (0.75 + .25*np.sin(2*np.pi*.11*t + seed))
        mid = _bandnoise(n, 700, 3200, r) * (0.55 + .45*np.abs(np.sin(2*np.pi*.37*t + seed)) ** 2)
        return .55*low + .32*mid
    wl, wr = river(1), river(2)
    # droplets / small splashes: short rising sine chirps
    drops = np.zeros(n)
    for _ in range(int(T * 2.2)):
        t0 = rng.uniform(.3, T - .5); f0 = rng.uniform(900, 2200); m = (t >= t0) & (t < t0 + .12); tt = t[m] - t0
        drops[m] += rng.uniform(.08, .2) * np.exp(-tt / .025) * np.sin(2*np.pi*(f0*tt + 5000*tt*tt))
    # tanpura drone (Sa = C#3), soft plucks
    sa = 138.59; drone = np.zeros(n)
    for f0, st, per, a in [(sa/2, 0, 2.8, .45), (sa*1.5, .9, 2.8, .3), (sa, 1.7, 2.8, .3), (sa, 2.3, 5.6, .18)]:
        s = st
        while s < T:
            m = t >= s; tt = t[m] - s; env = np.exp(-tt / 3.0) * (1 - np.exp(-tt * 40))
            drone[m] += a * env * sum((1 / k**1.2) * np.sin(2*np.pi*f0*k*tt + .3*k) for k in range(1, 7)); s += per
    # flute: slow pentatonic phrase (Sa Re Ga Pa Dha) starting after the hook
    S = sa * 2
    scale = {'S': S, 'R': S*9/8, 'G': S*5/4, 'P': S*3/2, 'D': S*5/3, "S'": S*2}
    phrase = [(3.2, 1.6, 'G'), (4.9, 1.0, 'P'), (6.0, 2.2, 'D'), (9.4, 1.4, 'P'), (10.9, 1.0, 'G'), (12.0, 2.4, 'R'),
              (15.0, 1.2, 'G'), (16.3, 1.0, 'R'), (17.4, 2.2, 'S')]
    flute = _flute(t, [(s, d, scale[k]) for s, d, k in phrase if s < T - 1.5], .22)
    bells = _bell(t, .05, 523.25, .5, 2.6) + _bell(t, bell2, 659.25, .28, 2.4)
    mono = .55*drone + flute + bells + drops
    L = mono + .5*wl; R = mono + .5*wr
    fade = np.minimum(1, t / .25) * np.minimum(1, (T - t) / 2.0)
    st = np.stack([L * fade, R * fade], 1); st = st / np.max(np.abs(st)) * .6
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()

if __name__ == '__main__':
    make(float(sys.argv[2]) if len(sys.argv) > 2 else 20.0, sys.argv[1], float(sys.argv[3]) if len(sys.argv) > 3 else 8.6)
