"""Operating point helper: python3 op.py <variant> [key=value ...]"""
import os, re, subprocess, sys, tempfile
import slo
HERE = os.path.dirname(os.path.abspath(__file__))

def op(variant, nodes, **kw):
    an = ".control\nop\nprint " + " ".join(f"v({n})" for n in nodes) + "\n.endc"
    net = slo.netlist(variant, analysis=an, **kw)
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=600)
    os.remove(cir)
    out = {}
    for line in r.stdout.splitlines():
        mm = re.match(r"\s*v\(([^)]+)\)\s*=\s*([-+0-9.eE]+)", line)
        if mm:
            out[mm.group(1)] = float(mm.group(2))
    if not out:
        print(r.stdout[-3000:], r.stderr[-2000:])
    return out

if __name__ == "__main__":
    v = sys.argv[1]
    kw = {}
    for a in sys.argv[2:]:
        k, val = a.split("=")
        try:
            val = eval(val)
        except Exception:
            pass
        kw[k] = val
    nodes = ["b1", "b2", "b3", "b4", "b5", "p1b", "k1b", "p1a", "p2a", "k2a", "p2b", "k2b", "p3b", "k3a", "ts", "p5b", "p5a", "pt"]
    if v == "mod":
        nodes += ["bf", "bw", "bx", "g6a", "k6a", "p6b", "k6b", "pw1", "kw2"]
    res = op(v, nodes, **kw)
    print({k: round(x, 2) for k, x in res.items()})
