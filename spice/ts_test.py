"""Tube Screamer: TS808 vs pilotable version (drive network, tone remap, large signal)."""
import json
import os

import numpy as np

import ts

HERE = os.path.dirname(os.path.abspath(__file__))
res = {}

# 1. clipping stage, small signal, versus drive (same pot fraction)
FPTS = (100, 300, 720, 1000, 3000, 6000, 10000)
res["clip_ac"] = {}
for v in ("ts808", "pilot"):
    res["clip_ac"][v] = {}
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        f, H = ts.ac("o1", version=v, drive=d, stage="clip")
        db = 20 * np.log10(np.abs(H))
        res["clip_ac"][v][str(d)] = [round(float(np.interp(x, f, db)), 2) for x in FPTS]
        print("clip", v, d, res["clip_ac"][v][str(d)], flush=True)

# 2. tone stage: 20k original vs 10k digital pot, best code for each original position
def tone_curve(version, x=None, code=None):
    f, H = ts.ac("o2", version=version, stage="tone", tone=x if x is not None else 0.5, tone_code=code)
    return f, 20 * np.log10(np.abs(H))

f, _ = tone_curve("ts808", 0.5)
band = (f >= 100) & (f <= 8000)
codes = list(range(0, 256, 5)) + [255]
lib = {c: tone_curve("pilot", code=c)[1] for c in codes}
res["tone"] = []
for x in np.linspace(0, 1, 11):
    ref = tone_curve("ts808", float(x))[1]
    same = tone_curve("pilot", code=int(round(255 * x)))[1]
    err_same = float(np.max(np.abs(same - ref)[band]))
    best = min(codes, key=lambda c: float(np.sqrt(np.mean((lib[c] - ref)[band] ** 2))))
    err_best = float(np.max(np.abs(lib[best] - ref)[band]))
    res["tone"].append(dict(x=round(float(x), 2), ref_db_100_1k_5k=[round(float(np.interp(q, f, ref)), 2) for q in (100, 1000, 5000)],
                            max_err_same_fraction_db=round(err_same, 2), best_code=best, max_err_best_db=round(err_best, 2)))
    print("tone", res["tone"][-1], flush=True)

# 3. large signal, full pedal at tight-boost settings and at mid drive
res["large"] = {}
for v in ("ts808", "pilot"):
    for d in (0.0, 0.5):
        for fr in (100.0, 1000.0):
            for a in (0.1, 0.5):
                t, y = ts.tran(fr, a, "out", cycles=20, version=v, drive=d, tone=0.5, level=1.0)
                T = 8 / fr
                tu = np.linspace(t[-1] - T, t[-1], 4096, endpoint=False)
                yu = np.interp(tu, t, y)
                yu -= yu.mean()
                sp = np.abs(np.fft.rfft(yu)) * 2 / len(yu)
                h = [float(sp[8 * k]) for k in range(1, 8)]
                key = f"{v}_d{d}_{fr:.0f}Hz_{a}V"
                res["large"][key] = dict(v1=round(h[0], 3), thd=round(float(np.sqrt(np.sum(np.square(h[1:]))) / h[0]), 3),
                                         h2=round(h[1] / h[0], 3), h3=round(h[2] / h[0], 3), vpk=round(float(np.abs(yu).max()), 3))
                print(key, res["large"][key], flush=True)
json.dump(res, open(os.path.join(HERE, "res_ts.json"), "w"), indent=1)
