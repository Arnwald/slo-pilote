"""Interference check of the robot at extreme poses (pairs of parts from different moving groups)."""
import itertools, math, sys
import cadquery as cq
import robot_cad as R

R.build(); R.fixed_parts()
parts = [(n, (s.val() if hasattr(s, "val") else s), g) for n, s, g, c, p in R.PARTS if g not in ("decor", "grille")]

def place(shape, group, x, s, a):
    sh = shape
    if group == "A":
        sh = sh.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -a)
    if group in ("A", "X"):
        sh = sh.translate(cq.Vector(x, 0, 0))
    if group in ("A", "X", "Z"):
        sh = sh.translate(cq.Vector(0, R.TRAVEL_D[0] + s, 0))
    return sh

ok_pairs = {("roue_V_int-", "arc_dente"), ("roue_V_int+", "arc_dente"), ("roue_V_ext", "arc_dente"),
            ("pignon", "arc_dente"), ("manchon_TPU", "collier_micro"), ("micro_SM57", "manchon_TPU")}
bad = []
for (x, s, a) in [(-15, 0, -50), (-15, 0, 50), (135, 150, -50), (135, 150, 50), (60, 75, 0), (-15, 150, 0), (135, 0, 0)]:
    placed = [(n, place(sh, g, x, s, a), g) for n, sh, g in parts]
    for (n1, s1, g1), (n2, s2, g2) in itertools.combinations(placed, 2):
        if g1 == g2:
            continue
        b1, b2 = s1.BoundingBox(), s2.BoundingBox()
        if b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin or b1.zmax < b2.zmin or b2.zmax < b1.zmin:
            continue
        v = s1.intersect(s2).Volume()
        if v > 0.5 and (n1, n2) not in ok_pairs and (n2, n1) not in ok_pairs:
            bad.append(((x, s, a), n1, n2, round(v, 1)))
for b in bad:
    print(b)
print("interferences:", len(bad))
