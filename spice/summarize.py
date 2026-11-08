"""Collect the campaign results (res_*.json) into compact tables (stdout) and summary.json."""
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda p: json.load(open(os.path.join(HERE, p)))
S = {}


def at(d, f):
    return float(np.interp(np.log(f), np.log(d["f"]), d["db"]))


def psu():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, "res_psu_*.json"))):
        r = json.load(open(p))
        out[r["case"]] = {k: v for k, v in r.items() if k not in ("params",)}
    S["psu"] = out
    print("== PSU")
    for c, r in out.items():
        if "dc" in r:
            print(f"{c:16s} B+1..5 {[r['dc'][n] for n in ('b1', 'b2', 'b3', 'b4', 'b5')]} ripple100(mV) "
                  f"{ {k: v for k, v in r['ripple_100Hz_mVpk'].items()} } hum {r['hum_total_dB_re_100W']} dB")
        else:
            print(f"{c:16s} idle B+1 {r['idle']['b1']} loaded {r['loaded']['b1']} (min {r['b1_min']}) "
                  f"B+2 {r['idle']['b2']}->{r['loaded']['b2']} P_fund {r.get('p_fund_W')} W THD {r.get('thd_out')} fund {r['fund_Vpk']} V")


def modes():
    out = {}
    base = None
    if os.path.exists(os.path.join(HERE, "res_modes_od_base.json")):
        base = J("res_modes_od_base.json")
    print("== MODES")
    for p in sorted(glob.glob(os.path.join(HERE, "res_modes_*.json"))):
        r = json.load(open(p))
        name = r["test"]
        row = {}
        ac = r["ac"]
        if "orig" in ac and "mod" in ac:
            f = np.array(ac["orig"]["f"])
            d = np.array(ac["mod"]["db"]) - np.array(ac["orig"]["db"])
            band = (f >= 40) & (f <= 8000)
            row["mod_minus_orig_dB"] = {str(x): round(float(np.interp(np.log(x), np.log(f), d)), 2) for x in (100, 1000, 5000)}
            row["max_abs_dB_40_8k"] = round(float(np.max(np.abs(d[band]))), 2)
        if base is not None and name != "od_base":
            bm = base["ac"]["mod"]
            f = np.array(bm["f"])
            d = np.array(ac["mod"]["db"]) - np.array(bm["db"])
            row["vs_base_dB"] = {str(x): round(float(np.interp(np.log(x), np.log(f), d)), 2) for x in (60, 100, 300, 1000, 3000, 6000)}
        row["large"] = r["large"]
        out[name] = row
        print(name, json.dumps({k: v for k, v in row.items() if k != "large"}))
        for v, L in r["large"].items():
            print("   ", v, {k: (x["v1"], x["thd"]) for k, x in L.items()})
    S["modes"] = out


def depth():
    if not os.path.exists(os.path.join(HERE, "res_depth.json")):
        return
    r = J("res_depth.json")
    out = {}
    print("== DEPTH (gain dB from PI input to speaker)")
    ref = r["orig_none"]
    for k, d in r.items():
        if k == "sweep100Hz":
            continue
        out[k] = {str(x): round(at(d, x) - at(ref, x), 2) for x in (50, 100, 200, 500, 1000, 3000, 6000)}
        print(f"{k:12s}", out[k])
    out["sweep100Hz"] = {k: [round(x - v[0], 2) for x in v] for k, v in r["sweep100Hz"].items()}
    for k, v in out["sweep100Hz"].items():
        print("sweep", k, v)
    S["depth"] = out


def pops():
    out = {}
    print("== POPS")
    for p in sorted(glob.glob(os.path.join(HERE, "res_pops_*.json"))):
        r = json.load(open(p))
        out[r["case"]] = {k: v for k, v in r.items() if not k.startswith("trace")}
        print(f"{r['case']:18s} peak {r['peak_V']:8.4f} V {r['peak_dB_re_100W']:6.1f} dB  settle {r['settle_10mV_s']} s  jn {r['jn_peak_V']} piin {r['piin_peak_V']}")
    S["pops"] = out


def noise():
    if os.path.exists(os.path.join(HERE, "res_noise.json")):
        S["noise"] = J("res_noise.json")
        print("== NOISE")
        for k, v in S["noise"].items():
            print(k, v)


def tsbox():
    if os.path.exists(os.path.join(HERE, "res_ts.json")):
        S["ts"] = J("res_ts.json")
        print("== TS")
        r = S["ts"]
        for d in r["clip_ac"]["ts808"]:
            a, b = r["clip_ac"]["ts808"][d], r["clip_ac"]["pilot"][d]
            print("clip drive", d, "ts808", a, "delta", [round(y - x, 2) for x, y in zip(a, b)])
        for t in r["tone"]:
            print("tone", t)
        for k, v in r["large"].items():
            print(k, v)


if __name__ == "__main__":
    for fn in (psu, modes, depth, pops, noise, tsbox):
        fn()
    json.dump(S, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
