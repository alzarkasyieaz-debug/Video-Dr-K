import numpy as np, wave, sys
sr=48000; dur=float(sys.argv[2]); out=sys.argv[1]
rng=np.random.default_rng(7)
n=int(sr*dur); t=np.arange(n)/sr
def hz(m): return 440*2**((m-69)/12)
# reflective progression (each chord 8s): Dm9, Bbmaj7, Fadd9, C/E -> Am7, Bbmaj7, Gm9, A sus
chords=[[50,57,62,65,69,72],[46,53,58,62,65,69],[41,53,57,60,64,67],[52,55,60,64,67,72],
        [45,52,57,60,64,67],[46,53,58,62,65,69],[43,50,55,58,62,65],[45,52,57,62,64,69]]
L=np.zeros(n); R=np.zeros(n)
cl=8.0
for k in range(int(dur/cl)+1):
    ch=chords[k%len(chords)]; s0=k*cl
    a=int(s0*sr); b=min(n,int((s0+cl+3)*sr))
    if a>=n: break
    tt=t[a:b]-s0
    env=np.clip(tt/2.5,0,1)*np.clip((cl+3-tt)/3.0,0,1)
    env=env**1.5
    for i,m in enumerate(ch):
        f=hz(m); det=1+0.0015*(i-2.5)
        v=(np.sin(2*np.pi*f*det*tt)+0.25*np.sin(2*np.pi*2*f*tt+0.3)+0.08*np.sin(2*np.pi*3*f*tt))
        g=0.05*(1.0 if m<60 else 0.7)
        pan=0.5+0.35*np.sin(i*1.7)
        L[a:b]+=v*env*g*(1-pan); R[a:b]+=v*env*g*pan
    # soft piano-like notes
    for j,(off,m) in enumerate([(0.0,ch[-1]+12),(2.0,ch[-2]+12),(4.0,ch[-3]+12),(6.0,ch[-2]+12)]):
        if rng.random()<0.35: continue
        s=s0+off; a2=int(s*sr); b2=min(n,int((s+5)*sr))
        if a2>=n: continue
        tt=t[a2:b2]-s; f=hz(m)
        e=np.exp(-tt*1.1)*np.clip(tt/0.01,0,1)
        v=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*2)+0.1*np.sin(2*np.pi*3*f*tt)*np.exp(-tt*3))*e*0.06
        p=0.3+0.4*rng.random()
        L[a2:b2]+=v*(1-p); R[a2:b2]+=v*p
# one-pole lowpass for warmth
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/sr); y=np.empty_like(x); z=0.0
    # vectorised via lfilter-free approach: chunked recursion
    from itertools import accumulate
    y=np.frombuffer(np.array(list(accumulate(x*(1-a),lambda p,q:p*a+q)),dtype=float))
    return y
L=lp(L,2600); R=lp(R,2600)
# reverb via FFT convolution with decaying noise IR
ir_len=int(sr*3.2); it=np.arange(ir_len)/sr
irL=rng.standard_normal(ir_len)*np.exp(-it*1.6); irR=rng.standard_normal(ir_len)*np.exp(-it*1.6)
irL/=np.sqrt((irL**2).sum()); irR/=np.sqrt((irR**2).sum())
def conv(x,h):
    N=1<<int(np.ceil(np.log2(len(x)+len(h))))
    return np.fft.irfft(np.fft.rfft(x,N)*np.fft.rfft(h,N),N)[:len(x)]
L2=0.6*L+0.55*conv(L,irL); R2=0.6*R+0.55*conv(R,irR)
fade=np.clip(t/3,0,1)*np.clip((dur-t)/4,0,1)
L2*=fade; R2*=fade
pk=max(abs(L2).max(),abs(R2).max()); L2/=pk/0.5; R2/=pk/0.5
d=(np.stack([L2,R2],1)*32767).astype('<i2')
w=wave.open(out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(d.tobytes()); w.close()
