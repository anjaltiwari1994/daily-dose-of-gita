import numpy as np, wave
SR = 44100

def _save(y, path):
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()

def _bell(t, t0, f, amp, decay=1.6):
    m = t >= t0; tt = np.where(m, t - t0, 0)
    return m * amp * np.exp(-tt / decay) * (np.sin(2*np.pi*f*tt) + .5*np.sin(2*np.pi*f*2.76*tt) + .25*np.sin(2*np.pi*f*5.4*tt))

def _tone(t, f, amp, harm=6, det=0.0):
    return sum(amp/(k**1.4)*np.sin(2*np.pi*f*k*(1+det)*t+k) for k in range(1, harm+1))

def make(style, T, path, events=()):
    """style: cosmic | ocean | gita ; events: list of (time_sec, freq_hz, amp) bell accents"""
    t = np.arange(int(SR*T))/SR; y = np.zeros_like(t); rng = np.random.default_rng(3)
    if style == 'cosmic':
        for f, a in [(55,.5),(110,.45),(164.8,.3),(220,.28),(261.6,.2),(329.6,.18),(392,.12)]:
            lfo = 1+0.25*np.sin(2*np.pi*(0.07+f/4000)*t+f); y += (_tone(t,f,a,5,.0015)+_tone(t,f,a,5,-.0015))*lfo*.5
        sh = sum(np.sin(2*np.pi*f*t)*(0.5+0.5*np.sin(2*np.pi*(5+f/600)*t)) for f in (1318.5,1760,2093,2637))
        y += sh*np.clip((t-3)/8,0,1)**2*np.clip((T-3-t)/1.0,0,1)*0.05
        nl = np.convolve(rng.standard_normal(len(t)), np.ones(200)/200, 'same'); y += nl*np.exp(-((t-1.2)/0.6)**2)*3.0
        y += _bell(t,.35,440,.12)
    elif style == 'ocean':
        for f, a in [(49,.55),(73.4,.4),(98,.35),(146.8,.22),(174.6,.15),(220,.12)]:
            lfo = 1+0.3*np.sin(2*np.pi*(0.05+f/5000)*t+f); y += (_tone(t,f,a,4,.002)+_tone(t,f,a,4,-.002))*lfo*.5
        beat = 60/58.0
        s = 3.0
        while s < T-1:   # soft heartbeat lub-dub from 3s
            y += _bell(t,s,62,.5,.35)+_bell(t,s+.28,55,.35,.3); s += beat*1.0
        for _ in range(26):  # bubbles
            t0 = rng.uniform(1, T-2); f = rng.uniform(700,1800); m = t>=t0; tt=np.where(m,t-t0,0)
            y += m*.05*np.exp(-tt/.08)*np.sin(2*np.pi*(f+900*tt)*tt)
        y += _bell(t,.4,392,.10)
    else:  # gita: tanpura-like drone
        sa = 138.59
        def pluck(f0, start, period, amp):
            o = np.zeros_like(t); s = start
            while s < T:
                m = t >= s; tt = (t-s)[m]; env = np.exp(-tt/2.8)*(1-np.exp(-tt*60))
                o[m] += amp*env*sum((1/k**1.1)*np.sin(2*np.pi*f0*k*tt+.3*k) for k in range(1,9)); s += period
            return o
        y = pluck(sa/2,0,2.6,.5)+pluck(sa*1.5,.9,2.6,.35)+pluck(sa,1.7,2.6,.35)+pluck(sa,2.3,5.2,.2)
        y += .05*(np.sin(2*np.pi*sa*t)+.6*np.sin(2*np.pi*sa*1.5*t)+.4*np.sin(2*np.pi*sa*2*t))*(1+.15*np.sin(2*np.pi*.2*t))
    for te, f, a in events:
        y += _bell(t, te, f, a)
    y *= np.minimum(1, t/1.0)*np.minimum(1, (T-t)/2.5)
    y = y/np.max(np.abs(y))*0.55
    _save(y, path)
