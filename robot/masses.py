"""Mass budget and centre of mass of the robot (mid travel), printed parts at 50 % effective density."""
import json, math
import cadquery as cq
import robot_cad as R

R.build(); ys = R.fixed_parts()
FIXED = {"chariot_MGN12H_X": 54, "chariot_MGN12H_Z": 54, "servo_angle": 310, "servo_X": 310, "servo_Z": 310,
         "micro_SM57": 284, "roue_V_int-": 10, "roue_V_int+": 10, "roue_V_ext": 10}
PER_M = {"poutre_X": 500, "poutre_Z": 500, "rail_X": 650, "rail_Z": 650, "vis_X": 390, "vis_Z": 390}
x, s, a = 60.0, 75.0, 0.0
tot, mom, rows = 0.0, cq.Vector(0, 0, 0), []
for n, shp, g, c, printed in R.PARTS:
    if g in ("decor", "grille"):
        continue
    sol = shp.val() if hasattr(shp, "val") else shp
    if g == "A":
        sol = sol.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -a)
    if g in ("A", "X"):
        sol = sol.translate(cq.Vector(x, 0, 0))
    if g in ("A", "X", "Z"):
        sol = sol.translate(cq.Vector(0, R.TRAVEL_D[0] + s, 0))
    if n in FIXED:
        m = FIXED[n]
    elif n in PER_M:
        bb = sol.BoundingBox()
        m = PER_M[n] * max(bb.xlen, bb.ylen, bb.zlen) / 1000
    elif printed:
        m = sol.Volume() / 1000 * (1.2 if n == "manchon_TPU" else 1.27) * 0.5
    else:
        m = sol.Volume() / 1000 * 7.85
    com = cq.Shape.centerOfMass(sol)
    tot += m
    mom += com * m
    rows.append((n, round(m)))
extra = 60 + 2 * 20 + 2 * 12 + 2 * 20 + 50 + 60     # nuts, couplers, 608ZZ, endstops, screws, CAN wiring
tot += extra
com = mom / (tot - extra)
print(sorted(rows, key=lambda r: -r[1]))
print(f"masse totale ~ {tot/1000:.2f} kg (dont visserie {extra} g) ; centre de masse y = {com.y:.0f} mm, x = {com.x:.0f} mm ; adaptateur de pied y = {ys:.0f}")
