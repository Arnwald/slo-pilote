"""Mid control on a motorised 2-gang pot: 10 k (any taper) with 3.3 k across its ends, against the
2.5 k pot of the scaled tone stack. For each position of the 10 k pot, finds the closest curve of the
2.5 k family (60 Hz - 6 kHz) and prints the worst deviation. Result: <= 1.0 dB with 3.3 k.
"""
import subprocess, numpy as np, os
def run(mid, kind, bass=0.5, treble=0.5, rp=3.3e3):
    L = ["* stack", "V1 src 0 DC 0 AC 1", "Rsrc src ts 150",
         "Ctr ts tt 5.6n", "Rsl ts ta 4.7k", "Cbs ta tb 220n", "Cmd ta tmw 220n",
         f"Rtru tt tw {max(1,(1-treble)*20e3)}", f"Rtrd tw tb {max(1,treble*20e3)}",
         f"Rbs tb tm {max(1, 100e3*(10**(2*bass)-1)/99)}",   # 100k log (approx. 10% at mid)
         "Rload tw 0 50k"]
    if kind == "orig":
        L += [f"Rmu tm tmw {max(1,(1-mid)*2.5e3)}", f"Rmd tmw 0 {max(1,mid*2.5e3)}"]
    else:
        L += [f"Rmu tm tmw {max(1,(1-mid)*10e3)}", f"Rmd tmw 0 {max(1,mid*10e3)}", f"Rp tm 0 {rp}"]
    L += [".control", "set wr_singlescale", "ac dec 30 30 10k", "wrdata out.dat v(tw)", ".endc", ".end"]
    open("s.cir","w").write("\n".join(L))
    subprocess.run(["ngspice","-b","s.cir"],capture_output=True)
    d = np.loadtxt("out.dat"); f = d[:,0]; h = d[:,1]+1j*d[:,2]
    return f, 20*np.log10(np.abs(h))
ms = np.linspace(0,1,41)
O = {m: run(m,"orig")[1] for m in ms}
f = run(0.5,"orig")[0]
sel = (f>=60)&(f<=6000)
for rp in (2.7e3, 3.3e3, 3.9e3):
    worst = 0
    rows = []
    for x in np.linspace(0,1,11):
        h = run(x,"alt",rp=rp)[1]
        errs = {m: np.sqrt(np.mean((h[sel]-O[m][sel])**2)) for m in ms}
        mbest = min(errs, key=errs.get)
        mx = np.max(np.abs(h[sel]-O[mbest][sel]))
        worst = max(worst, mx)
        rows.append((round(x,1), round(mbest,3), round(errs[mbest],2), round(mx,2)))
    print("Rp", rp, "worst max err dB", round(worst,2))
    for r in rows: print("   x=%.1f -> m=%.3f rms %.2f max %.2f" % r)
# range check: mid at 0 and 1 for both
for x in (0,1):
    print("mid", x, "orig@1k %.2f alt@1k %.2f" % (O[x][np.argmin(abs(f-1000))], run(x,"alt")[1][np.argmin(abs(f-1000))]))
