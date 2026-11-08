"""Checks the KiCad schematic against itself and against the SPICE model.

python3 check_sch.py <project dir>   (needs kicad-cli on the PATH)

1. Structure: every unit of every multi-unit part placed exactly once, one value per reference,
   labels used only once (likely typos), power rails present.
2. SPICE: every element of spice/slo.py (variant "mod", real supply, individual bias) must find its
   counterpart in the exported netlist: same nets (through NETMAP) and same value, within the
   tolerance of the standard series. Pots, LDRs and relay contacts are matched by function.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spice"))
sys.path.insert(0, HERE)

NETMAP = {
    "0": "GND", "in": "IN_V1",
    "g1b": "V1B_G", "p1b": "V1B_P", "k1b": "V1B_K", "kbx1": "V1B_KX",
    "g6a": "V6A_G", "gbt": "V6A_GB", "k6a": "V6A_K", "c0": "DIV_IN", "odt": "OD_TOP", "odw": "OD_W",
    "cn1": "NRM_MID", "cnt": "NRM_TOP", "cr2": "NRM_CL", "brn": "NRM_BR", "cnw": "NRM_W",
    "p1a": "V1A_P", "k1a": "V1A_K", "c1a": "V1A_OUT", "jx": "CLN_MIX",
    "g2a": "V2A_G", "p2a": "V2A_P", "k2a": "V2A_K", "kbx2": "V2A_KX",
    "n20": "CC20", "n22": "CC2N2", "dsel": "CC_SEL",
    "ex0": "EX_IN", "g6b": "V6B_G", "p6b": "V6B_P", "k6b": "V6B_K", "e1": "EX_OUT",
    "a1": "CLIP_IN", "g2b": "V2B_G", "p2b": "V2B_P", "k2b": "V2B_K", "kc1": "V2B_K10", "kc2": "V2B_K4", "o3": "OD_OUT",
    "jn": "JN", "g3b": "V3B_G", "p3b": "V3B_P", "k3b": "V3B_K", "k3a": "V3A_K",
    "w0": "ATT_IN", "w1": "ATT_OUT", "gw": "WCF_G", "pw1": "WCF_PA", "ts": "WCF_OUT", "gw2": "WCF_GB", "kw2": "WCF_KB",
    "tt": "STK_TT", "ta": "STK_TA", "tb": "STK_TB", "tm": "STK_TM", "tmw": "STK_TMW", "tw": "STK_TW",
    "mw": "MOD_W", "mnw": "MN_W", "piin": "PI_IN",
    "g5b": "PI_GB", "g5a": "PI_GA", "pt": "PI_TAIL", "pk": "PI_K", "p5b": "PI_PB", "p5a": "PI_PA",
    "nfb": "NFB", "pr": "PRES", "nx": "NFB_X", "nd": "DEPTH_X", "sec": "SPK_4R",
    "b1": "B+1", "b2": "B+2", "b3": "B+3", "b4": "B+4", "b5": "B+5", "bf": "B+BUF", "bw": "B+WCF", "bx": "B+EXT",
    "pa": "OT_PA", "pb": "OT_PB", "b2x": "B+2",
}
for side, tubes in (("a", ("V7", "V8")), ("b", ("V9", "V10"))):
    for n, t in enumerate(tubes, start=1):
        NETMAP.update({f"gl{side}{n}": f"{t}_GL", f"g{side}{n}": f"{t}_G1", f"s{side}{n}": f"{t}_G2",
                       f"ks{side}{n}": f"{t}_K", f"bias{side}{n}": f"BIAS_{t}"})

LDRS = {"cr1", "cr2", "br", "ldrx", "dir", "ext", "ldr1", "cl1", "cl2", "ldr2", "push", "ldr3", "ldr4", "mute"}
RELAYS = {"bp1", "bp2", "cc20", "cc22"}
# elements of the model with no part of their own: sources, transformer and choke internals, load
MODEL_ONLY = re.compile(r"^(V|K\d|L[123]$|R[123]w$|Rw\d|Lw\d|Rct$|Cot\d|Rload|Rch$)")
# deliberate differences, each justified (see README)
KNOWN = {
    "Rmdu": "Mid : 10 k log + 3,3 k en parallèle au lieu d'un 2,5 k introuvable en motorisé (≤ 1 dB, mid_test.py)",
    "Rmdd": "idem",
    "Cb1": "2 × 470 µF 350 V en série (235 µF) pour 200 µF simulés",
    "Cb2": "2 × 220 µF 350 V en série (110 µF) pour 100 µF simulés",
    "Rbl": "2 × 220 k en série (équilibrage des condensateurs en série)",
}


# ------------------------------------------------------------------------------------------------
def sexp(s):
    tok = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', s)
    stack, cur = [], []
    for t in tok:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def kicad_netlist(proj):
    out = os.path.join(proj, "slo-pilote.net")
    r = subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out,
                        os.path.join(proj, "slo-pilote.kicad_sch")], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    tree = sexp(open(out).read())
    comps = {}
    for c in find(find(tree, "components")[0], "comp"):
        ref = find(c, "ref")[0][1]
        comps[ref] = {"value": find(c, "value")[0][1], "lib": find(c, "libsource")[0][2][1], "pins": {}}
    nets = {}
    for n in find(find(tree, "nets")[0], "net"):
        name = find(n, "name")[0][1]
        short = name.split("/")[-1] if not name.startswith("unconnected-") else name
        nodes = [(find(nd, "ref")[0][1], find(nd, "pin")[0][1]) for nd in find(n, "node")]
        nets[short] = nets.get(short, []) + nodes
        for ref, pin in nodes:
            if ref in comps:
                comps[ref]["pins"][pin] = short
    os.remove(out)
    return comps, nets


# ------------------------------------------------------------------------------------------------
UNIT = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9}


def val(s):
    """'4.7k 1 W' -> 4700 ; '0.47µ 630 V' -> 4.7e-7 ; '1Meg' -> 1e6 ; '2.2M' -> 2.2e6."""
    s = s.strip().split()[0].replace(",", ".")
    m = re.match(r"^([0-9.]+(?:e[+-]?\d+)?)(Meg|meg|[fpnuµmkKMG])?", s)
    if not m:
        return None
    v = float(m.group(1))
    u = m.group(2)
    if u in ("Meg", "meg"):
        return v * 1e6
    return v * UNIT.get(u, 1.0) if u else v


def spice_elements(net):
    els = []
    for line in net.splitlines():
        if not line or line[0] in "*.+" or line.startswith((".", "*")):
            continue
        p = line.split()
        els.append(p)
    return els


def main(proj):
    import slo
    import slo_sch
    P = slo_sch.P
    report = {"structure": [], "spice_ok": 0, "spice_tol": [], "spice_bad": [], "known": [], "model_only": [],
              "kicad_extra": []}

    # ---- 1. structure ----------------------------------------------------------------------
    placed = {}
    for sh in P.sheets:
        for p in sh.parts:
            placed.setdefault(p.ref, []).append((p.sym, p.unit, p.value, sh.name))
    for ref, lst in sorted(placed.items()):
        sym = P.lib[lst[0][0]]
        if sym.power:
            continue
        units = sorted(u for _, u, _, _ in lst)
        if units != list(range(1, len(sym.units) + 1)):
            report["structure"].append(f"{ref} ({sym.name}) : unités placées {units}, attendu 1..{len(sym.units)}")
        if len({v for _, _, v, _ in lst}) > 1:
            report["structure"].append(f"{ref} : valeurs différentes selon l'unité {sorted({v for _, _, v, _ in lst})}")
    comps, nets = kicad_netlist(proj)
    for n, nodes in sorted(nets.items()):
        if len(nodes) == 1 and not n.startswith("unconnected-"):
            report["structure"].append(f"réseau {n} : une seule broche ({nodes[0][0]}.{nodes[0][1]})")
    for rail in P.POWER:
        if len(nets.get(rail, [])) < 2:
            report["structure"].append(f"rail {rail} absent ou isolé")
    report["n_parts"], report["n_nets"] = len(comps), len(nets)
    report["global_nets"] = sorted(P.global_nets())

    # ---- 2. against the SPICE model --------------------------------------------------------------
    net = slo.netlist("mod", psu="real", bias_offsets={"a1": 0, "a2": 0, "b1": 0, "b2": 0}, depth=0.5, depth_net="lin100k")
    els = spice_elements(net)
    # closed fuses and switches in the HT path are not in the model: merge their nets
    alias = {"HT_RECT": "B+1", "HT_F": "B+1"}
    kn = lambda s: alias.get(NETMAP.get(s, "?" + s), NETMAP.get(s, "?" + s))
    used = set()

    def two_term(ref, a, b):
        c = comps[ref]
        nets_ = set(c["pins"].values())
        return {a, b} == nets_ if a != b else False

    def pair_nets(ref, p1, p2):
        pins = comps[ref]["pins"]
        return {pins.get(p1), pins.get(p2)}

    for p in els:
        name = p[0]
        if MODEL_ONLY.match(name):
            report["model_only"].append(name)
            continue
        if name in KNOWN:
            report["known"].append(f"{name} : {KNOWN[name]}")
            continue
        typ = name[0]
        if typ == "X":
            nodes, model = p[1:-1], p[-1]
            want = [kn(n) for n in nodes]
            if model == "6L6GC":
                keys = ("3", "4", "5", "8")
            else:
                keys = None
            hit = None
            for ref, c in comps.items():
                if c["lib"] != model:
                    continue
                pins = c["pins"]
                tri = [("1", "2", "3"), ("6", "7", "8")] if keys is None else [keys]
                for k in tri:
                    if [pins.get(x) for x in k] == want:
                        hit = f"{ref}({'/'.join(k)})"
            if hit:
                report["spice_ok"] += 1
                used.add(hit)
            else:
                report["spice_bad"].append(f"{name} {model} {want} : lampe introuvable")
            continue
        if typ == "D":
            report["model_only"].append(name + " (redresseur : voir D101-D104)")
            continue
        a, b, v = kn(p[1]), kn(p[2]), p[3]
        base = name[1:]
        if typ == "R" and base in LDRS:
            hit = [r for r, c in comps.items() if c["lib"] == "VTL5C1" and pair_nets(r, "3", "4") == {a, b}]
            (report["spice_bad"].append(f"{name} {a}-{b} : LDR introuvable") if not hit else None)
            report["spice_ok"] += bool(hit)
            continue
        if typ == "R" and base in RELAYS:
            closed = float(v) < 1
            hit = [r for r, c in comps.items() if c["lib"] == "RELAY_2C" and any(
                pair_nets(r, cc, x) == {a, b} for cc, x in ((("1", "2"), ("4", "5")) if closed else (("1", "3"), ("4", "6"))))]
            (report["spice_bad"].append(f"{name} {a}-{b} : contact de relais ({'repos' if closed else 'travail'}) introuvable")
             if not hit else None)
            report["spice_ok"] += bool(hit)
            continue
        if typ == "R" and re.match(r"R(god|gn|tr|mod|mn|md)[ud]$", name):
            # potentiometer half: u = top-wiper (pins 3-2), d = wiper-bottom (2-1)
            half = ("3", "2") if name.endswith("u") else ("2", "1")
            hit = [r for r, c in comps.items() if c["lib"].startswith(("ALPS", "POT")) and pair_nets(r, *half) == {a, b}]
            if hit:
                other = name[:-1] + ("d" if name.endswith("u") else "u")
                vo = next(float(q[3]) for q in els if q[0] == other)
                total = float(v) + vo
                kv = val(comps[hit[0]]["value"])
                if abs(total - kv) / kv > 0.02:
                    report["spice_bad"].append(f"{name} : potentiomètre {hit[0]} {comps[hit[0]]['value']} pour {total:.4g} Ω")
                else:
                    report["spice_ok"] += 1
            else:
                report["spice_bad"].append(f"{name} {a}-{b} : moitié de potentiomètre introuvable")
            continue
        if name in ("Rbs", "Rpres", "Rdep"):
            # rheostats: bass and depth between pin 1 and the wiper (grow clockwise), presence between 3 and wiper
            half = ("3", "2") if name == "Rpres" else ("1", "2")
            hit = [r for r, c in comps.items() if c["lib"].startswith("ALPS") and pair_nets(r, *half) == {a, b}]
            (report["spice_bad"].append(f"{name} {a}-{b} : rhéostat introuvable ou monté à l'envers") if not hit else None)
            report["spice_ok"] += bool(hit)
            continue
        kinds = {"R": ("R",), "C": ("C",), "L": ("L",)}[typ]
        hit = []
        for ref, c in comps.items():
            if re.match(r"^[RCL]\d", ref) and ref[0] in kinds and c["lib"] in ("R", "C", "CP", "L") and two_term(ref, a, b):
                hit.append(ref)
        if not hit:
            report["spice_bad"].append(f"{name} {a}-{b} {v} : aucun composant entre ces nœuds")
            continue
        sv = val(v)
        best = min(hit, key=lambda r: abs(val(comps[r]["value"]) - sv) / sv)
        kv = val(comps[best]["value"])
        used.add(best)
        err = (kv - sv) / sv
        if abs(err) <= 0.01:
            report["spice_ok"] += 1
        elif abs(err) <= (0.25 if typ == "C" and comps[best]["lib"] == "CP" else 0.08):
            report["spice_tol"].append(f"{name} {v} → {best} {comps[best]['value']} ({err * 100:+.0f} %)")
            report["spice_ok"] += 1
        else:
            report["spice_bad"].append(f"{name} {v} → {best} {comps[best]['value']} ({err * 100:+.0f} %)")
    # schematic parts with no counterpart in the model (input box, control, bias, heaters, ...)
    matched_refs = set()
    for r in used:
        matched_refs.add(r.split("(")[0])
    report["kicad_extra_count"] = len([r for r in comps if r not in matched_refs])
    return report


if __name__ == "__main__":
    rep = main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "slo-pilote"))
    print(f"{rep['n_parts']} composants, {rep['n_nets']} réseaux, {len(rep['global_nets'])} étiquettes globales")
    print("Structure :", "aucun problème" if not rep["structure"] else "")
    for s in rep["structure"]:
        print("  -", s)
    print(f"SPICE : {rep['spice_ok']} éléments retrouvés, {len(rep['spice_bad'])} en défaut, "
          f"{len(rep['known'])} écarts voulus, {len(rep['model_only'])} propres au modèle")
    for s in rep["spice_tol"]:
        print("  ~", s)
    for s in rep["known"]:
        print("  =", s)
    for s in rep["spice_bad"]:
        print("  ✗", s)
    json.dump(rep, open(os.path.join(HERE, "check_result.json"), "w"), indent=1, ensure_ascii=False)
