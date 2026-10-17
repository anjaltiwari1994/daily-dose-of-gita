"""History Shorts audio prep (free, no credits).

Usage:
  python3 tools/history/audio.py vo.mp3 captions.json WORKDIR

captions.json = list of caption chunks in speaking order. Split the script at every
sentence end and every comma, exactly as it is spoken (the narrator pauses there).

Writes to WORKDIR:
  voice.wav      narration only, long pauses tightened (use for the Instagram version;
                 Instagram library music is added by Metricool at low volume)
  mix_yt.wav     narration + very soft self-made drone (~10% under the voice, louder in gaps)
                 for YouTube, where library music cannot be added by API
  timeline.json  {total, segments:[{i,start,end,text}]} timed to voice.wav
"""
import json, os, subprocess, sys
import numpy as np

SR = 44100

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

def save(path, x):
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", path],
                   input=x.tobytes(), check=True)

def silences(path, noise="-35dB", d=0.25):
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    out, s = [], None
    for ln in err.splitlines():
        if "silence_start:" in ln: s = float(ln.split("silence_start:")[1].split()[0])
        if "silence_end:" in ln and s is not None:
            out.append((s, float(ln.split("silence_end:")[1].split("|")[0]))); s = None
    return out

def drone(n, cycle=2.6):
    """Soft tanpura-like drone (Karplus-Strong plucks Pa Sa Sa Sa in D) + low pad. Self-made, copyright free."""
    rng = np.random.default_rng(7)
    def pluck(freq, length, decay):
        m = int(SR * length); p = int(SR / freq)
        buf = rng.uniform(-1, 1, p); out = np.zeros(m, np.float32)
        for k in range(m):
            v = buf[k % p]; out[k] = v; buf[k % p] = decay * 0.5 * (v + buf[(k + 1) % p])
        return out
    notes = [110.0, 146.83, 146.83, 73.42]
    cache = {f: pluck(f, 4.0, 0.9993 if f < 100 else 0.9990) for f in set(notes)}
    bed = np.zeros(n + SR * 5, np.float32); t, k = 0.0, 0
    while int(t * SR) < n:
        f = notes[k % 4]; a = int(t * SR); s = cache[f]
        bed[a:a + len(s)] += s * (0.55 if f < 100 else 0.42); t += cycle / 4; k += 1
    bed = bed[:n]; tv = np.arange(n) / SR
    pad = (0.12 * np.sin(2 * np.pi * 73.42 * tv) + 0.07 * np.sin(2 * np.pi * 110 * tv)) * (0.6 + 0.4 * np.sin(2 * np.pi * tv / 9))
    m = np.convolve(bed + pad, np.ones(9) / 9, mode="same"); m /= (np.abs(m).max() + 1e-9)
    fi, fo = int(1.2 * SR), int(1.8 * SR); m[:fi] *= np.linspace(0, 1, fi); m[-fo:] *= np.linspace(1, 0, fo)
    return m

def main():
    vo_path, cap_path, wd = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(wd, exist_ok=True)
    caps = json.load(open(cap_path))
    vo = load(vo_path); dur = len(vo) / SR
    segs, prev = [], 0.0
    for s, e in silences(vo_path):
        if s - prev > 0.05: segs.append((prev, s))
        prev = e
    if dur - prev > 0.05: segs.append((prev, dur))
    PAD, GAP, LEAD, TAIL = 0.04, 0.22, 0.35, 1.6
    pieces, spans, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
    for i, (s, e) in enumerate(segs):
        if i: pieces.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
        a, b = max(0, int((s - PAD) * SR)), min(len(vo), int((e + PAD) * SR))
        ch = vo[a:b].copy(); f = int(0.012 * SR); r = np.linspace(0, 1, f); ch[:f] *= r; ch[-f:] *= r[::-1]
        pieces.append(ch); spans.append((t, t + len(ch) / SR)); t += len(ch) / SR
    pieces.append(np.zeros(int(TAIL * SR), np.float32))
    voice = np.concatenate(pieces); total = len(voice) / SR
    # map captions to speech spans
    if len(spans) == len(caps):
        timeline = [{"i": i, "start": round(a, 3), "end": round(b, 3), "text": c} for i, ((a, b), c) in enumerate(zip(spans, caps))]
        mode = "exact"
    else:  # proportional by characters over the spoken time
        speech = [(a, b) for a, b in spans]; tot_sp = sum(b - a for a, b in speech)
        lens = np.array([len(c) for c in caps], float); bounds = np.concatenate([[0], np.cumsum(lens) / lens.sum()]) * tot_sp
        def at(x):
            acc = 0.0
            for a, b in speech:
                if acc + (b - a) >= x: return a + (x - acc)
                acc += b - a
            return speech[-1][1]
        timeline = [{"i": i, "start": round(at(bounds[i]), 3), "end": round(at(bounds[i + 1]), 3), "text": c} for i, c in enumerate(caps)]
        mode = f"proportional (speech parts {len(spans)} != captions {len(caps)})"
    peak = np.abs(voice).max() + 1e-9; voice = voice / peak * 0.89
    music = drone(len(voice))
    win = int(0.25 * SR); env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
    duck = np.convolve(np.where(env > 0.01, 0.10, 0.18), np.ones(win) / win, mode="same")
    save(os.path.join(wd, "voice.wav"), voice)
    save(os.path.join(wd, "mix_yt.wav"), voice + music * duck)
    json.dump({"total": round(total, 3), "segments": timeline}, open(os.path.join(wd, "timeline.json"), "w"), indent=1)
    print("caption timing:", mode); print("total seconds:", round(total, 2))
    for x in timeline: print(x["start"], x["end"], x["text"])

if __name__ == "__main__":
    main()
