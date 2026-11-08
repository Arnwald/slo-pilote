"""Remote microphone positioner for a guitar cab: radial position, distance, angle (3 closed-loop CAN steppers).

The angle axis is a goniometer: a toothed arc centred on the capsule, so turning the microphone
leaves the capsule where it is. Radial and distance axes are two identical linear modules
(2020 beam, MGN12H rail, T8x2 lead screw, NEMA 17 + MKS SERVO42D on the CAN bus of the head).

python3 robot_cad.py <outdir>   -> STEP + STL of the printed parts, assembly STEP, meshes for the viewer.
World frame: grille plane y = 0 (cab at y < 0), target speaker centre at x = z = 0,
x = radial direction, y = away from the cab, z up. Robot frame: origin on the capsule at home.
"""
import json
import math
import os
import sys

import cadquery as cq

# ---------------------------------------------------------------- parameters (mm, degrees)
R_IN, R_OUT = 84.0, 112.0           # wheel tracks (V ridges) of the arc
SPAN_V = 72.0                       # half span of the guiding zone
CH = 2.5                            # 45 deg chamfers forming the ridges
MOD = 1.5                           # rack module
RP = 111.0                          # rack pitch radius: 148 teeth on a full circle
N_FULL = int(round(2 * RP / MOD))
R_RACK_IN = 86.0
RACK_SPAN = (-28.0, 88.0)          # the pinion sweeps A + 30 deg for A in [-50, +50]
Z_V = (-68.0, -58.0)
Z_RACK = (-58.0, -50.0)
Z_PLATE = (-48.0, -42.0)
WHEEL_OD, WHEEL_W, WHEEL_OFF = 15.2, 8.8, 6.5    # mini V wheel; centre 6.5 mm off the ridge
INNER_ANG = 14.0                    # the two fixed wheels on the inner ridge
PIN_ANG = 30.0                      # pinion / servo position on the carriage (clear of the mic and its clamp)
PIN_Z = 14
R_PIN = RP + PIN_Z * MOD / 2        # 121.5
MIC_D, MIC_L, CAPSULE = 32.0, 157.0, 8.0          # Shure SM57; capsule 8 mm behind the grille
CLAMP = (66.0, 86.0)                # clamp ring, distance behind the capsule
LINER = 2.0                         # TPU liner
RING_T = 4.0
TRAVEL_X = (-15.0, 135.0)           # capsule radial position (0 = dust cap centre)
TRAVEL_D = (10.0, 160.0)            # capsule-to-grille distance
TRAVEL_A = (-50.0, 50.0)
Y_XC = 98.0                         # X carriage centre, behind the capsule
Y_XS = 128.0                        # X lead screw axis
Z_XBEAM = (-107.0, -87.0)
Z_XS = -97.0
X_ZC = 60.0                         # Z module axis (x)
X_ZS = 90.0                         # Z lead screw axis (x)
Z_ZBEAM = (-148.0, -128.0)
Z_ZS = -138.0
NEMA = 42.3

PARTS = []      # (name, shape, group, colour, printed)


def add(name, shape, group, colour, printed=False):
    PARTS.append((name, shape, group, colour, printed))
    return shape


def polar(r, phi):
    """phi measured from +y towards +x (0 = straight behind the capsule)."""
    a = math.radians(phi)
    return (r * math.sin(a), r * math.cos(a))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def cyl(d, h, base, axis="Z"):
    v = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}[axis]
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(d / 2, h, cq.Vector(*base), cq.Vector(*v)))


def revolve_sector(profile, half_span):
    """Revolve an (r, z) profile about the z axis over +-half_span around phi = 0."""
    w = cq.Workplane("XZ").polyline(profile).close().revolve(2 * half_span, (0, 0, 0), (0, 1, 0))
    return w.rotate((0, 0, 0), (0, 0, 1), 90 - half_span)


# ---------------------------------------------------------------- arc (sector) with its rack
def make_sector():
    zb, zt = Z_V
    prof = [(R_IN + CH, zb), (R_OUT - CH, zb), (R_OUT, zb + CH), (R_OUT, zt - CH), (R_OUT - CH, zt),
            (R_IN + CH, zt), (R_IN, zt - CH), (R_IN, zb + CH)]
    guide = revolve_sector(prof, SPAN_V)
    # rack zone: trapezoidal teeth (20 deg); with 148 teeth the involute is almost straight
    pitch = 360.0 / N_FULL
    r_root, r_tip = RP - 1.25 * MOD, RP + MOD
    s_p = math.pi * MOD / 2
    tan20 = math.tan(math.radians(20))
    hw = lambda r: (s_p - 2 * (r - RP) * tan20) / (2 * r)          # half angular width (rad)
    a0, a1 = RACK_SPAN
    pts = [polar(R_RACK_IN, a0 + i * (a1 - a0) / 80) for i in range(81)]
    pts.append(polar(r_root, a1))
    kmax, kmin = int((a1 - pitch) / pitch), -int((-a0 - pitch) / pitch)
    for k in range(kmax, kmin - 1, -1):
        c = math.radians(k * pitch)
        for r, s in ((r_root, +1), (r_tip, +1), (r_tip, -1), (r_root, -1)):
            a = c + s * hw(r)
            pts.append((r * math.sin(a), r * math.cos(a)))
    pts.append(polar(r_root, a0))
    rack = cq.Workplane("XY").polyline(pts).close().extrude(Z_RACK[1] - Z_RACK[0]).translate((0, 0, Z_RACK[0]))
    sector = guide.union(rack)
    # 4 x M3 to the X adapter plate, counterbored from the top of the rack zone
    for x, y in ((-20, 94), (20, 94), (-20, 102), (20, 102)):
        sector = sector.cut(cyl(3.4, 40, (x, y, Z_V[0] - 5))).cut(cyl(6.2, 4.0, (x, y, Z_RACK[1] - 4.0)))
    return sector


# ---------------------------------------------------------------- angle carriage
def make_arc_plate():
    zb, zt = Z_PLATE
    a0, a1 = -22.0, 46.0
    pts = [polar(60.0, a0 + i * (a1 - a0) / 28) for i in range(29)] + [polar(134.0, a1 - i * (a1 - a0) / 28) for i in range(29)]
    plate = cq.Workplane("XY").polyline(pts).close().extrude(zt - zb).translate((0, 0, zb))
    # motor: centre bore and 4 x M3 on a 31 mm square, square aligned with the radius
    mx, my = polar(R_PIN, PIN_ANG)
    plate = plate.cut(cyl(22.5, 20, (mx, my, zb - 5)))
    for dx, dy in ((15.5, 15.5), (-15.5, 15.5), (15.5, -15.5), (-15.5, -15.5)):
        a = math.radians(-PIN_ANG)
        rx, ry = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
        plate = plate.cut(cyl(3.4, 20, (mx + rx, my + ry, zb - 5)))
    # wheels: two fixed on the inner ridge, one eccentric on the outer ridge
    for s in (-1, 1):
        x, y = polar(R_IN - WHEEL_OFF, s * INNER_ANG)
        plate = plate.cut(cyl(5.2, 20, (x, y, zb - 5)))
    x, y = polar(R_OUT + WHEEL_OFF, 0.0)
    plate = plate.cut(cyl(7.2, 20, (x, y, zb - 5)))
    # clamp foot: 2 x M4
    for r in (70.0, 82.0):
        x, y = polar(r, 0.0)
        plate = plate.cut(cyl(4.3, 20, (x, y, zb - 5)))
    return plate


def make_clamp():
    """Ring around the mic body (TPU liner inside), on a foot screwed to the carriage plate."""
    r_o = MIC_D / 2 + LINER + RING_T
    length = CLAMP[1] - CLAMP[0]
    ring = cyl(2 * r_o, length, (0, CLAMP[0], 0), "Y")
    foot = box(-10, 10, CLAMP[0], CLAMP[1], Z_PLATE[1], -r_o + 4)
    ears = box(-9, 9, CLAMP[0] + 3, CLAMP[1] - 3, r_o - 4, r_o + 6)
    part = ring.union(foot).union(ears)
    part = part.cut(cyl(MIC_D + 2 * LINER, length + 2, (0, CLAMP[0] - 1, 0), "Y"))
    part = part.cut(box(-1.5, 1.5, CLAMP[0] - 1, CLAMP[1] + 1, 0, r_o + 8))            # split
    part = part.cut(cyl(4.3, 30, (-15, (CLAMP[0] + CLAMP[1]) / 2, r_o + 1), "X"))       # pinch screw
    for r in (70.0, 82.0):
        part = part.cut(cyl(4.3, 30, (0, r, Z_PLATE[1] - 1)))
        part = part.cut(cyl(8.0, 30, (0, r, Z_PLATE[1] + 6)))                           # screw access
    return part


def make_liner():
    return cyl(MIC_D + 2 * LINER, CLAMP[1] - CLAMP[0] - 2, (0, CLAMP[0] + 1, 0), "Y").cut(
        cyl(MIC_D, CLAMP[1] - CLAMP[0], (0, CLAMP[0], 0), "Y"))


def make_pinion():
    """14-tooth pinion, module 1.5, 8 mm wide, bore 5 mm with a flat (printed or bought)."""
    r_root, r_tip = PIN_Z * MOD / 2 - 1.25 * MOD, PIN_Z * MOD / 2 + MOD
    rp = PIN_Z * MOD / 2
    tan20 = math.tan(math.radians(20))
    s_p = math.pi * MOD / 2
    pts = []
    for k in range(PIN_Z):
        c = 2 * math.pi * k / PIN_Z
        for r, s in ((r_root, -1), (r_tip, -1), (r_tip, 1), (r_root, 1)):
            hw = (s_p - 2 * (r - rp) * tan20) / (2 * r)
            a = c + s * hw
            pts.append((r * math.cos(a), r * math.sin(a)))
    g = cq.Workplane("XY").polyline(pts).close().extrude(8.0)
    g = g.cut(cyl(5.1, 10, (0, 0, -1)))
    hub = cyl(12, 6, (0, 0, 8)).cut(cyl(5.1, 8, (0, 0, 7)))
    return g.union(hub)


# ---------------------------------------------------------------- linear modules (X shown; Z is the same)
def beam_2020(length, axis):
    s = cq.Workplane("XY").rect(20, 20).extrude(length)
    for dx, dy in ((10, 0), (-10, 0), (0, 10), (0, -10)):
        s = s.cut(cq.Workplane("XY").center(dx, dy).rect(6.2 if dx == 0 else 6.0, 6.0 if dx == 0 else 6.2).extrude(length))
    s = s.cut(cq.Workplane("XY").circle(2.1).extrude(length))
    if axis == "X":
        s = s.rotate((0, 0, 0), (0, 1, 0), 90)
    else:
        s = s.rotate((0, 0, 0), (1, 0, 0), -90)
    return s


def motor_block(axis_len_dir):
    """Printed end block: clamps the 2020 end, holds a NEMA 17 face and houses the coupler.
    Built along +x with the screw axis at (y = 30, z = 0) relative to the beam axis."""
    b = box(0, 26, -14, 52, -21, 23)
    b = b.cut(box(-1, 6, -10.2, 10.2, -10.2, 10.2))                     # beam end pocket
    b = b.cut(cyl(5.2, 30, (-1, 0, 0), "X"))                            # M5 into the beam end tap
    b = b.cut(cyl(9.5, 6, (6, 0, 0), "X"))                              # screw head
    b = b.cut(cyl(24, 30, (-1, 30, 0), "X"))                            # coupler cavity
    for dy, dz in ((15.5, 15.5), (-15.5, 15.5), (15.5, -15.5), (-15.5, -15.5)):
        b = b.cut(cyl(3.4, 40, (-5, 30 + dy, dz), "X"))
    return b


def bearing_block():
    b = box(-26, 0, -14, 52, -21, 23)
    b = b.cut(box(-6, 1, -10.2, 10.2, -10.2, 10.2))
    b = b.cut(cyl(5.2, 30, (-27, 0, 0), "X"))
    b = b.cut(cyl(9.5, 6, (-12, 0, 0), "X"))
    b = b.cut(cyl(22.1, 7.2, (-7.2, 30, 0), "X"))                       # 608ZZ seat
    b = b.cut(cyl(12, 40, (-30, 30, 0), "X"))
    return b


def nut_block():
    """Hangs under the carriage plate; holds the T8 anti-backlash nut flange (4 x M3 on 16 mm)."""
    b = box(-6, 6, -12, 12, -35, 0)
    b = b.cut(cyl(11, 20, (-10, 0, -23), "X"))
    for a in (45, 135, 225, 315):
        b = b.cut(cyl(3.4, 20, (-10, 8 * math.cos(math.radians(a)), -23 + 8 * math.sin(math.radians(a))), "X"))
    for dy in (-7, 7):
        b = b.cut(cyl(3.4, 12, (0, dy, -11)))
    return b


def adapter_x():
    p = box(-26, 26, 84, 142, -74, -68)
    for x, y in ((-10, 88), (10, 88), (-10, 108), (10, 108)):          # MGN12H, counterbored from the top
        p = p.cut(cyl(3.4, 10, (x, y, -75))).cut(cyl(6.2, 3.6, (x, y, -71.6)))
    for x, y in ((-20, 94), (20, 94), (-20, 102), (20, 102)):          # heat-set inserts for the arc
        p = p.cut(cyl(4.2, 5.0, (x, y, -73)))
    for dy in (-7, 7):                                                   # nut block
        p = p.cut(cyl(3.4, 10, (0, Y_XS + dy, -75))).cut(cyl(6.2, 3.6, (0, Y_XS + dy, -71.6)))
    return p


def cross_plate_z():
    """Sits on the Z carriage and carries the X beam (2 x M5 into T-nuts) and the Z nut block."""
    p = box(X_ZC - 30, X_ZS + 14, Y_XC - 18, Y_XC + 16, -115, -107)      # stays clear of the X nut block (y >= 116)
    for x, y in ((X_ZC - 10, Y_XC - 10), (X_ZC + 10, Y_XC - 10), (X_ZC - 10, Y_XC + 10), (X_ZC + 10, Y_XC + 10)):
        p = p.cut(cyl(3.4, 12, (x, y, -116))).cut(cyl(6.2, 3.6, (x, y, -110.6)))
    for x in (X_ZC - 22, X_ZC + 22):
        p = p.cut(cyl(5.3, 12, (x, Y_XC, -116)))
    for dx in (-7, 7):
        p = p.cut(cyl(3.4, 12, (X_ZS + dx, Y_XC, -116)))
    return p


def stand_adapter(y0):
    """Under the Z beam: 2 x M5 into T-nuts, brass insert 3/8"-16 (or 5/8"-27) from below,
    plus a split collar for the stand tube (anti-rotation)."""
    b = box(X_ZC - 22, X_ZC + 14, y0 - 30, y0 + 30, -173, -148)          # stays clear of the Z nut block (x >= 78)
    for dy in (-18, 18):
        b = b.cut(cyl(5.3, 30, (X_ZC, y0 + dy, -175))).cut(cyl(9.5, 18, (X_ZC, y0 + dy, -175)))
    b = b.cut(cyl(12.2, 16, (X_ZC, y0, -175)))
    return b


# ---------------------------------------------------------------- purchased parts (simplified)
def nema(length, base, axis_dir):
    """NEMA 17 body with its shaft; face at base, body extending along axis_dir (+x, -x, +y, -y, -z...)."""
    body = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, 0, length).edges("|Z").chamfer(4)
    shaft = cyl(5, 24, (0, 0, -24))
    boss = cyl(22, 2, (0, 0, -2))
    m = body.union(shaft).union(boss)
    rot = {"+z": None, "-z": ((1, 0, 0), 180), "+x": ((0, 1, 0), 90), "-x": ((0, 1, 0), -90),
           "+y": ((1, 0, 0), -90), "-y": ((1, 0, 0), 90)}[axis_dir]
    if rot:
        m = m.rotate((0, 0, 0), rot[0], rot[1])
    return m.translate(base)


def servo(base, axis_dir):
    """Closed-loop CAN stepper: NEMA 17 40 mm with an MKS SERVO42D board on its back (14 mm, connectors on one side)."""
    body = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, 0, 40).edges("|Z").chamfer(4)
    board = box(-NEMA / 2, NEMA / 2, -NEMA / 2, NEMA / 2, 40, 54)
    plugs = box(NEMA / 2, NEMA / 2 + 6, -12, 12, 44, 52)
    m = body.union(board).union(plugs).union(cyl(5, 24, (0, 0, -24))).union(cyl(22, 2, (0, 0, -2)))
    rot = {"+z": None, "+x": ((0, 1, 0), 90), "+y": ((1, 0, 0), -90)}[axis_dir]
    if rot:
        m = m.rotate((0, 0, 0), rot[0], rot[1])
    return m.translate(base)


def mgn12_rail(length, axis):
    r = box(0, length, -6, 6, 0, 8)
    return r if axis == "X" else r.rotate((0, 0, 0), (0, 0, 1), 90)


def mgn12h(axis):
    c = box(-22.7, 22.7, -13.5, 13.5, 3, 13).cut(box(-30, 30, -6.5, 6.5, 2, 8.2))
    return c if axis == "X" else c.rotate((0, 0, 0), (0, 0, 1), 90)


def v_wheel(base):
    w = cyl(WHEEL_OD, WHEEL_W, (0, 0, -WHEEL_W / 2))
    groove = cq.Workplane("XZ").polyline([(WHEEL_OD / 2 + 1, -3), (WHEEL_OD / 2 - 2.2, 0), (WHEEL_OD / 2 + 1, 3)]).close().revolve(
        360, (0, 0, 0), (0, 1, 0))
    return w.cut(groove).cut(cyl(5, 20, (0, 0, -10))).translate(base)


def sm57():
    tip = -CAPSULE
    head = cyl(MIC_D, 33, (0, tip, 0), "Y")
    neck = cyl(MIC_D - 4, 6, (0, tip + 33, 0), "Y")
    body = cyl(MIC_D - 2, MIC_L - 39, (0, tip + 39, 0), "Y")
    return head.union(neck).union(body)


# ---------------------------------------------------------------- assembly
def build():
    sector = add("arc_dente", make_sector(), "X", "#d97706", True)
    add("plaque_X", adapter_x(), "X", "#64748b", True)
    add("bloc_ecrou_X", nut_block().rotate((0, 0, 0), (0, 0, 1), 0).translate((0, Y_XS, -74)), "X", "#64748b", True)
    add("chariot_MGN12H_X", mgn12h("X").translate((0, Y_XC, Z_XBEAM[1])), "X", "#9ca3af")
    # angle carriage, built at angle 0
    add("plaque_angle", make_arc_plate(), "A", "#334155", True)
    add("collier_micro", make_clamp(), "A", "#334155", True)
    add("manchon_TPU", make_liner(), "A", "#111827", True)
    mx, my = polar(R_PIN, PIN_ANG)
    add("servo_angle", servo((mx, my, Z_PLATE[1]), "+z").rotate((mx, my, 0), (mx, my, 1), -PIN_ANG), "A", "#1f2937")
    add("pignon", make_pinion().rotate((0, 0, 0), (1, 0, 0), 180).translate((mx, my, Z_RACK[1])), "A", "#f59e0b", True)
    for s in (-1, 1):
        x, y = polar(R_IN - WHEEL_OFF, s * INNER_ANG)
        add(f"roue_V_int{'+' if s > 0 else '-'}", v_wheel((x, y, (Z_V[0] + Z_V[1]) / 2)), "A", "#e5e7eb")
    x, y = polar(R_OUT + WHEEL_OFF, 0.0)
    add("roue_V_ext", v_wheel((x, y, (Z_V[0] + Z_V[1]) / 2)), "A", "#e5e7eb")
    add("micro_SM57", sm57(), "A", "#374151")
    # X linear module (moves with Z)
    add("poutre_X", beam_2020(260, "X").translate((-70, Y_XC, (Z_XBEAM[0] + Z_XBEAM[1]) / 2)), "Z", "#cbd5e1")
    add("rail_X", mgn12_rail(250, "X").translate((-65, Y_XC, Z_XBEAM[1])), "Z", "#94a3b8")
    add("bloc_moteur_X", motor_block("X").translate((190, Y_XC, Z_XS + 0)).translate((0, 0, -0)), "Z", "#475569", True)
    add("palier_X", bearing_block().translate((-70, Y_XC, Z_XS)), "Z", "#475569", True)
    add("servo_X", servo((216, Y_XS, Z_XS), "+x"), "Z", "#1f2937")
    add("vis_X", cyl(8, 290, (-90, Y_XS, Z_XS), "X"), "Z", "#a8a29e")
    add("plaque_Z", cross_plate_z(), "Z", "#64748b", True)
    add("bloc_ecrou_Z", nut_block().rotate((0, 0, 0), (0, 0, 1), 90).translate((X_ZS, Y_XC, -115)), "Z", "#64748b", True)
    add("chariot_MGN12H_Z", mgn12h("Y").translate((X_ZC, Y_XC, Z_ZBEAM[1])), "Z", "#9ca3af")
    return sector


def fixed_parts():
    """Fixed parts in world coordinates (the robot frame origin sits at y = TRAVEL_D[0] when s = 0)."""
    y_home = TRAVEL_D[0]
    y_c0 = y_home + Y_XC                       # Z carriage centre at s = 0
    y_front = y_c0 - 22.7 - 10 - 15
    length = 250.0
    add("poutre_Z", beam_2020(length, "Y").translate((X_ZC, y_front, (Z_ZBEAM[0] + Z_ZBEAM[1]) / 2)), "fixe", "#cbd5e1")
    add("rail_Z", mgn12_rail(240, "Y").translate((X_ZC, y_front + 5, Z_ZBEAM[1])), "fixe", "#94a3b8")
    blk = motor_block("X").rotate((0, 0, 0), (0, 0, 1), 90)
    blk = blk.mirror("YZ")                      # screw on +x side of the beam
    add("bloc_moteur_Z", blk.translate((X_ZC, y_front + length, Z_ZS)), "fixe", "#475569", True)
    pal = bearing_block().rotate((0, 0, 0), (0, 0, 1), 90).mirror("YZ")
    add("palier_Z", pal.translate((X_ZC, y_front, Z_ZS)), "fixe", "#475569", True)
    add("servo_Z", servo((X_ZS, y_front + length + 26, Z_ZS), "+y"), "fixe", "#1f2937")
    add("vis_Z", cyl(8, length + 40, (X_ZS, y_front - 20, Z_ZS), "Y"), "fixe", "#a8a29e")
    ys = y_front + length * 0.62
    add("adaptateur_pied", stand_adapter(ys), "fixe", "#475569", True)
    return ys


def stand_and_cab(ys, z_floor=-560.0):
    add("pied_tube", cyl(25, -173 - z_floor - 60, (X_ZC, ys, z_floor + 60)), "decor", "#3f3f46")
    for k in range(3):
        a = math.radians(90 + 120 * k)
        leg = cyl(16, 330, (0, 0, 0), "X").rotate((0, 0, 0), (0, 1, 0), 12).rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        add(f"pied_jambe{k}", leg.translate((X_ZC, ys, z_floor + 60)), "decor", "#3f3f46")
    # 4x12 cab: target = top-left speaker at (0, 0); the cab centre is at (+180, -180)
    add("baffle", box(-200, 560, -360, -18, z_floor, 200), "decor", "#1c1917")
    add("grille", box(-185, 545, -3, 0, z_floor + 15, 185), "grille", "#57534e")
    for cx, cz in ((0, 0), (360, 0), (0, -360), (360, -360)):
        add(f"hp_{cx}_{cz}", cyl(280, 3, (cx, -18, cz), "Y"), "decor", "#44403c")
        add(f"cache_{cx}_{cz}", cyl(50, 4, (cx, -15, cz), "Y"), "decor", "#a8a29e")


def tess(shape, tol=0.25):
    verts, tris = shape.val().tessellate(tol, 0.3) if hasattr(shape, "val") else shape.tessellate(tol, 0.3)
    return [round(c, 2) for v in verts for c in (v.x, v.y, v.z)], [i for t in tris for i in t]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(os.path.join(out, "stl"), exist_ok=True)
    os.makedirs(os.path.join(out, "step"), exist_ok=True)
    build()
    ys = fixed_parts()
    stand_and_cab(ys)
    meshes, report = [], []
    for name, shp, group, colour, printed in PARTS:
        solid = shp.val() if hasattr(shp, "val") else shp
        vol = solid.Volume()
        bb = solid.BoundingBox()
        report.append({"name": name, "group": group, "printed": printed, "volume_cm3": round(vol / 1000, 2),
                       "bbox": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]})
        if printed:
            cq.exporters.export(shp, os.path.join(out, "stl", name + ".stl"), tolerance=0.05, angularTolerance=0.1)
            cq.exporters.export(shp, os.path.join(out, "step", name + ".step"))
        v, t = tess(shp, 0.4 if group in ("decor", "grille") else 0.15)
        meshes.append({"name": name, "group": group, "colour": colour, "v": v, "t": t})
    json.dump(meshes, open(os.path.join(out, "meshes.json"), "w"), separators=(",", ":"))
    json.dump({"parts": report, "params": {"R_IN": R_IN, "R_OUT": R_OUT, "RP": RP, "teeth": N_FULL, "pinion": PIN_Z,
                                           "module": MOD, "R_PIN": R_PIN, "travel_x": TRAVEL_X, "travel_d": TRAVEL_D,
                                           "travel_a": TRAVEL_A, "y_home": TRAVEL_D[0], "stand_y": ys}},
              open(os.path.join(out, "report.json"), "w"), indent=1, ensure_ascii=False)
    asm = cq.Assembly()
    for name, shp, group, colour, printed in PARTS:
        if group in ("decor", "grille"):
            continue
        loc = cq.Location(cq.Vector(0, TRAVEL_D[0], 0)) if group != "fixe" else cq.Location()
        asm.add(shp, name=name, loc=loc, color=cq.Color(colour))
    asm.save(os.path.join(out, "robot_micro_assemblage.step"))
    for r in report:
        print(f"{r['name']:22s} {r['group']:6s} {'imp' if r['printed'] else '   '} {r['volume_cm3']:8.2f} cm3  {r['bbox']}")
