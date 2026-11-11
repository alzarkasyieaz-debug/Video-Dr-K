"""Original procedural cinematic score (royalty-free, generated here).
usage: python score.py <duration_s> <mood:serious|inspire|emotional> <seed> <out.wav>
Deterministic for a given seed. Builds slowly; final 20-25% rises, ends on a resolving hit."""
SR = 44100
import sys, wave, numpy as np
from scipy.signal import butter, sosfilt
def lp(x, fc):
    return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)
D, mood, seed, out = float(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4]
rng = np.random.default_rng(seed)
N = int(D * SR) + SR * 3
t = np.arange(N) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
PROGS = {
 "serious":  [(57,[57,60,64]),(53,[53,57,60]),(48,[55,60,64]),(55,[55,59,62])],      # Am F C G
 "inspire":  [(48,[55,60,64]),(55,[55,59,62]),(57,[57,60,64]),(53,[53,57,60])],      # C G Am F
 "emotional":[(50,[57,62,65]),(46,[58,62,65]),(53,[57,60,65]),(48,[55,60,64])],      # Dm Bb F C
}
prog = PROGS[mood]
chord_len = 6.0 if mood != "inspire" else 4.8
L = np.zeros(N); R = np.zeros(N)
def env_seg(n, a, r):
    e = np.ones(n); ai = min(int(a*SR), n); ri = min(int(r*SR), n)
    e[:ai] = np.linspace(0, 1, ai); e[n-ri:] *= np.linspace(1, 0, ri); return e
def strings(f, n, bright):
    x = np.zeros(n); tt = np.arange(n)/SR
    for det in (-0.06, 0.0, 0.07):
        ff = f * 2 ** (det/12)
        vib = 1 + 0.003*np.sin(2*np.pi*5.1*tt + rng.uniform(0, 6))
        for h in range(1, 7):
            x += (bright ** (h-1)) / h * np.sin(2*np.pi*ff*h*np.cumsum(vib)/SR + rng.uniform(0, 6))
    return x / 6
# progress curve: 0..1, intensity rises in last quarter
prog_c = np.clip(t / D, 0, 1)
inten = 0.45 + 0.35*np.clip((prog_c-0.15)/0.6, 0, 1) + 0.35*np.clip((prog_c-0.75)/0.2, 0, 1)
i = 0; start = 0.0
while start < D + 1:
    root, notes = prog[i % len(prog)]
    s = int(start*SR); n = min(int((chord_len+1.5)*SR), N-s)
    if n <= 0: break
    e = env_seg(n, 1.4, 1.6)
    bright = 0.45 + 0.25*min(1, start/D)
    for k, m in enumerate(notes):
        v = strings(hz(m), n, bright) * e * 0.10
        pan = 0.35 + 0.3*k/len(notes)
        L[s:s+n] += v*(1-pan); R[s:s+n] += v*pan
    # sub / cello root
    sub = (np.sin(2*np.pi*hz(root-12)*np.arange(n)/SR) + 0.3*np.sin(2*np.pi*hz(root-12)*2*np.arange(n)/SR)) * e * 0.16
    L[s:s+n] += sub; R[s:s+n] += sub
    # piano-ish arpeggio (emotional/inspire), sparse
    if mood in ("emotional", "inspire"):
        step = chord_len/6
        for j in range(6):
            m = notes[[0,1,2,1,2,0][j]] + 12
            ps = s + int(j*step*SR); pn = min(int(2.5*SR), N-ps)
            if pn <= 0: continue
            pt = np.arange(pn)/SR
            p = sum(np.sin(2*np.pi*hz(m)*h*pt)/(h*h) for h in (1,2,3)) * np.exp(-pt*2.2) * 0.07
            pan = 0.3 + 0.4*(j%3)/2
            L[ps:ps+pn] += p*(1-pan); R[ps:ps+pn] += p*pan
    start += chord_len; i += 1
# percussion: soft pulse from 20%, toms in final 25%
beat = 60/84 if mood != "inspire" else 60/96
def drum(pos, f0, dec, amp, noise=0.0):
    s = int(pos*SR); n = min(int(1.2*SR), N-s)
    if n <= 0: return
    tt = np.arange(n)/SR
    f = f0*(1+1.5*np.exp(-tt*30))
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*dec)
    if noise: x += noise*lp(rng.standard_normal(n), 1800)*np.exp(-tt*dec*3)
    L[s:s+n] += x*amp; R[s:s+n] += x*amp
b = 0.2*D
while b < D - 1.5:
    p = b/D
    if p > 0.2: drum(b, 52, 9, 0.10 + 0.18*max(0, (p-0.2)/0.8))
    if p > 0.72 and int(round(b/beat)) % 4 == 0: drum(b, 80, 6, 0.30, noise=0.15)
    if p > 0.85 and int(round(b/beat)) % 2 == 1: drum(b+beat/2, 140, 14, 0.12, noise=0.3)
    b += beat
# riser into final hit
rs = D - 5.0; ri = int(rs*SR); rn = int(4.6*SR)
if ri > 0:
    tt = np.arange(rn)/SR
    nz = rng.standard_normal(rn)
    parts = [lp(nz, fc) for fc in (400, 900, 2000, 4000)]
    w = np.clip(tt/4.6*3, 0, 3); sweep = np.zeros(rn)
    for k in range(4): sweep += parts[k]*np.clip(1-abs(w-k), 0, 1)
    rise = sweep * (tt/4.6)**2.0 * 0.12
    # rising tone under the noise
    rise += np.sin(2*np.pi*np.cumsum(110*2**(tt/4.6*1.0))/SR) * (tt/4.6)**2 * 0.08
    L[ri:ri+rn] += rise; R[ri:ri+rn] += rise
drum(D-0.4, 45, 2.2, 0.55, noise=0.25)
drum(D-0.4, 90, 4, 0.25)
mix = np.stack([L, R], 1) * np.concatenate([inten, inten]).reshape(2, -1).T[:N]
# simple stereo reverb (feedback comb pair)
for dl, g in ((0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2)):
    d = int(dl*SR); y = mix.copy()
    for _ in range(3):
        y[d:] += g * y[:-d][:, ::-1]
    mix = 0.75*mix + 0.25*y
fade_in = np.minimum(1, t/1.5); tail_end = np.clip((D+2.5 - t)/2.5, 0, 1)
mix *= (fade_in*tail_end)[:, None]
mix = mix[: int((D+0.0)*SR)]
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.4) * 0.85
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", out, D, mood)
