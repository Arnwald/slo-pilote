"""Exact parts list from the schematic model (slo_sch.py), grouped by value.

python3 bom_sch.py [out.csv]  -> CSV (one line per value) + category counts used by the costed BOM.
"""
import csv
import re
import sys
from collections import OrderedDict, defaultdict

import slo_sch

P = slo_sch.P
HEAD = {"Alimentation", "Préampli", "Tone stack et déphaseur", "Puissance"}


def category(sym, value, sheet):
    v = value
    if sym == "R":
        w = re.search(r"(\d+(?:,\d+)?) W", v)
        if sheet in HEAD:
            if w and float(w.group(1).replace(",", ".")) >= 1:
                return "Résistance 1 à 3 W"
            return "Résistance couche métal 1/2 W 1 %"
        return "Résistance 1/4 W 1 % (basse tension)"
    if sym == "C":
        if "630 V" in v or "400 V" in v:
            return "Condensateur film HT (400-630 V)"
        if sheet in HEAD and re.match(r"^\d+(\.\d+)?[pn]$", v.split()[0]):
            return "Condensateur mica / céramique HT (500 V)"
        if "63 V" in v:
            return "Condensateur film 63 V"
        return "Condensateur céramique / film basse tension"
    if sym == "CP":
        return "Électrolytique (tête)" if sheet in HEAD else "Électrolytique basse tension"
    if sym in ("ALPS_2G",):
        return "Pot motorisé ALPS RK16812MG"
    if sym == "POT":
        return "Ajustable"
    if sym == "VTL5C1":
        return "LDR VTL5C1"
    if sym == "RELAY_2C":
        return "Relais signal 2RT 5 V"
    if sym in ("D", "LED"):
        return "Diode " + v.split()[0]
    if sym in ("12AX7", "12AU7", "6L6GC"):
        return "Lampe " + sym
    return sym


def collect():
    first = OrderedDict()
    for sh in P.sheets:
        for p in sh.parts:
            if P.lib[p.sym].power:
                continue
            if p.ref not in first:
                first[p.ref] = (p.sym, p.value, sh.name)
    groups = defaultdict(list)
    for ref, (sym, val, sheet) in first.items():
        groups[(category(sym, val, sheet), sym, val, "tête" if sheet in HEAD else sheet)].append(ref)
    return first, groups


def natural(ref):
    m = re.match(r"([A-Z#]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "nomenclature_kicad.csv"
    first, groups = collect()
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Catégorie", "Ensemble", "Symbole", "Valeur", "Quantité", "Repères"])
        for (cat, sym, val, where), refs in sorted(groups.items()):
            w.writerow([cat, where, sym, val, len(refs), " ".join(sorted(refs, key=natural))])
    cats = defaultdict(int)
    for (cat, sym, val, where), refs in groups.items():
        cats[(where, cat)] += len(refs)
    for k in sorted(cats):
        print(f"{k[0]:18s} {k[1]:45s} {cats[k]}")
    print(len(first), "références")
