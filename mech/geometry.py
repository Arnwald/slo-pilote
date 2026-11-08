"""Parametric geometry of the pilotable SLO head: chassis tray, walls, shell and grilles.

Units: mm. Chassis frame: x from left to right (seen from the front), y from front to rear
(on the top plate), z from the bottom edge of a wall upward (on the walls).
Every hole carries a `verify` flag when its geometry depends on a part not yet in hand.
"""
from dataclasses import dataclass, field

# --- sheet metal -------------------------------------------------------------------
T_CH = 1.5      # chassis: DC01 steel, 1.5 mm
R_IN = 1.5      # inner bend radius
K = 0.42        # K-factor (to be matched to the bender's tooling)
BD = 2 * (R_IN + T_CH) - 3.141592653589793 / 2 * (R_IN + K * T_CH)  # bend deduction

# --- chassis outer dimensions ---------------------------------------------------------
W, D, H = 600.0, 250.0, 90.0     # top plate W x D, wall height H
RET = 15.0                       # inward return flange at the bottom of the side walls

# --- shell (aluminium 5754, 2 mm, powder coated) ----------------------------------------
T_SH = 2.0
SH_W, SH_H, SH_D = 612.0, 262.0, 282.0   # outer
CH_SETBACK = 12.0                         # chassis front wall behind the shell front edge


@dataclass
class Hole:
    x: float
    y: float
    d: float = 0.0            # round hole diameter
    w: float = 0.0            # rectangle width (if d == 0)
    h: float = 0.0            # rectangle height
    label: str = ""
    verify: bool = False


@dataclass
class Part:
    name: str
    holes: list = field(default_factory=list)
    zones: list = field(default_factory=list)   # (x0, y0, x1, y1, label) not cut, layout only

    def round(self, x, y, d, label="", verify=False):
        self.holes.append(Hole(x, y, d=d, label=label, verify=verify))

    def rect(self, x, y, w, h, label="", verify=False):
        self.holes.append(Hole(x, y, w=w, h=h, label=label, verify=verify))


# ---------------------------------------------------------------------------------------
# Tube sockets (Belton chassis mount): noval 18.5 mm, screws 28 mm c-c; octal 31 mm, 40 mm c-c
NOVAL_D, NOVAL_CC = 18.5, 28.0
OCTAL_D, OCTAL_CC = 30.5, 40.0
SCREW_D = 3.5

PREAMP_Y = 70.0
PREAMP = [  # (label, x) right to left from the input
    ("V1 12AX7", 550.0), ("V6 12AT7", 495.0), ("V2 12AX7", 440.0),
    ("V3 12AX7", 385.0), ("V4 12AU7", 330.0), ("V5 12AX7", 275.0),
]
POWER_Y = 112.0
POWER = [("V7 6L6GC", 48.0), ("V8 6L6GC", 108.0), ("V9 6L6GC", 168.0), ("V10 6L6GC", 228.0)]

# magnetics footprints (x0, y0, x1, y1) and assumed mounting patterns (to verify on the parts)
PT_BOX = (15.0, 145.0, 140.0, 248.0)     # Tube-Town TT-Slo100 PT, 125 x 103
PT_HOLES = (75.0, 80.0)                  # datasheet D/E, axis assignment assumed
OT_BOX = (250.0, 160.0, 350.0, 242.0)    # Tube-Town TT-Slo100 OT, 100 x 82
OT_HOLES = (70.0, 68.0)
CH_BOX = (160.0, 172.0, 230.0, 242.0)    # choke placeholder (part not chosen)


def top_plate():
    p = Part("Dessus du châssis")
    for lab, x in PREAMP:
        p.round(x, PREAMP_Y, NOVAL_D, lab)
        p.round(x - NOVAL_CC / 2, PREAMP_Y, SCREW_D)
        p.round(x + NOVAL_CC / 2, PREAMP_Y, SCREW_D)
    for lab, x in POWER:
        p.round(x, POWER_Y, OCTAL_D, lab)
        p.round(x - OCTAL_CC / 2, POWER_Y, SCREW_D)
        p.round(x + OCTAL_CC / 2, POWER_Y, SCREW_D)
    for box, holes, lab, pass_d in ((PT_BOX, PT_HOLES, "Transfo d'alimentation", 25.0),
                                    (OT_BOX, OT_HOLES, "Transfo de sortie", 22.0)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        p.round(cx, cy, pass_d, lab + " : passage fils (passe-fil)")
        hx, hy = holes
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.round(cx + sx * hx / 2, cy + sy * hy / 2, 5.5, verify=True)
        p.zones.append((*box, lab))
    cx, cy = (CH_BOX[0] + CH_BOX[2]) / 2, (CH_BOX[1] + CH_BOX[3]) / 2
    p.round(cx, cy, 16.0, "Self : passage fils")
    p.zones.append((*CH_BOX, "Self (perçages selon la pièce)"))
    # under-chassis layout zones (not cut): boards fixed on standoffs drilled at assembly
    p.zones += [
        (20.0, 0.0, 590.0, 52.0, "Dessous : pots motorisés, écran, encodeur"),
        (300.0, 92.0, 585.0, 150.0, "Dessous : carte préampli (turrets)"),
        (380.0, 160.0, 585.0, 242.0, "Dessous : pilotage + boîtier d'entrée (blindés)"),
        (20.0, 60.0, 250.0, 98.0, "Dessous : carte alim + puissance"),
    ]
    return p


FRONT_Z = 48.0
KNOBS = ["Depth", "Presence", "Master OD", "Master Normal", "Treble", "Mid", "Bass",
         "Gain OD", "Gain Normal"]
KNOB_X0, KNOB_PITCH = 212.0, 42.0


def front_wall():
    p = Part("Façade (paroi avant)")
    p.round(24.0, FRONT_Z, 12.2, "Power (interrupteur M12)")
    p.round(58.0, FRONT_Z, 12.2, "Standby (interrupteur M12)")
    p.rect(118.0, FRONT_Z, 52.0, 40.0, "Fenêtre écran 2,4\"", verify=True)
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.round(118.0 + sx * 30.0, FRONT_Z + sz * 23.0, 3.2, verify=True)
    p.round(172.0, FRONT_Z, 7.2, "Encodeur presets (M7)")
    for i, lab in enumerate(KNOBS):
        p.round(KNOB_X0 + i * KNOB_PITCH, FRONT_Z, 9.5, lab + " (ALPS RK168, M9)")
    p.round(KNOB_X0 + 8 * KNOB_PITCH + 36.0, FRONT_Z, 9.5, "Entrée guitare (jack 6,35)")
    return p


def rear_wall():
    """Positions in chassis x (seen from the front); mirrored when drawn from behind."""
    p = Part("Panneau arrière (paroi arrière, vue de l'arrière)")
    # IEC inlet with fuse drawer near the PT
    p.rect(45.0, 45.0, 28.0, 20.0, "Embase IEC + fusible secteur", verify=True)
    p.round(45.0 - 20.0, 45.0, 3.2, verify=True)
    p.round(45.0 + 20.0, 45.0, 3.2, verify=True)
    p.round(100.0, 45.0, 12.5, "Fusible HT (porte-fusible M12)")
    p.round(250.0, 45.0, 9.5, "HP 1")
    p.round(282.0, 45.0, 9.5, "HP 2")
    p.round(318.0, 45.0, 9.5, "Sélecteur 4 / 8 / 16 Ω")
    for x, lab in ((380.0, "MIDI IN"), (420.0, "MIDI THRU")):
        p.round(x, 45.0, 24.0, lab + " (embase D Neutrik)")
        p.round(x - 9.5, 45.0 + 12.0, 3.2)
        p.round(x + 9.5, 45.0 - 12.0, 3.2)
    p.round(460.0, 45.0, 24.0, "USB (Neutrik NAUSB-W, format D)")
    p.round(460.0 - 9.5, 45.0 + 12.0, 3.2)
    p.round(460.0 + 9.5, 45.0 - 12.0, 3.2)
    p.round(500.0, 45.0, 9.5, "Pédalier (jack TRS)")
    p.round(535.0, 45.0, 9.5, "Insert send (HM-2)")
    p.round(568.0, 45.0, 9.5, "Insert return (HM-2)")
    return p


def side_wall(left=True):
    p = Part("Joue " + ("gauche" if left else "droite"))
    # ventilation slots on the left cheek (power side), none on the right (preamp side)
    if left:
        for i in range(6):
            p.rect(40.0 + i * 34.0, 55.0, 6.0, 40.0, "fente" if i == 0 else "")
    return p


def shell_parts():
    top = Part("Capot : dessus")
    # vent slots above the power tubes, in shell-top coordinates (x from left, y from front)
    ox = (SH_W - W) / 2
    oy = CH_SETBACK
    for _, x in POWER:
        for k in range(-1, 2):
            top.rect(ox + x + k * 14.0, oy + POWER_Y, 6.0, 70.0)
    top.round(SH_W / 2 - 130.0, 185.0, 8.5, "Poignée (M8)")
    top.round(SH_W / 2 + 130.0, 185.0, 8.5, "Poignée (M8)")
    bottom = Part("Capot : fond")
    for fx in (40.0, SH_W - 40.0):
        for fy in (35.0, SH_D - 35.0):
            bottom.round(fx, fy, 6.5, "Pied (M6)")
    # chassis fixing through the side-wall return flanges
    for x in (ox + RET / 2, ox + W - RET / 2):
        for y in (oy + 50.0, oy + D - 50.0):
            bottom.round(x, y, 4.5, "Fixation châssis (M4)")
    # vent slots under the power board zone
    for i in range(8):
        bottom.rect(ox + 40.0 + i * 25.0, oy + 80.0, 6.0, 50.0)
    return top, bottom


def clearance_checks():
    """Return a list of human-readable problems (empty = ok)."""
    issues = []
    tp = top_plate()
    circles = [(h.x, h.y, h.d / 2) for h in tp.holes if h.d]
    for i, (x1, y1, r1) in enumerate(circles):
        for x2, y2, r2 in circles[i + 1:]:
            gap = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 - r1 - r2
            if gap < 2.5:
                issues.append(f"trous trop proches ({x1:.0f},{y1:.0f}) / ({x2:.0f},{y2:.0f}) : {gap:.1f} mm")
    for x, y, r in circles:
        if x - r < 8 or x + r > W - 8 or y - r < 8 or y + r > D - 4:
            issues.append(f"trou trop près du bord ({x:.0f},{y:.0f})")
    # tube envelopes vs magnetics (6L6GC ~ 40 mm, noval ~ 22 mm)
    env = [(x, POWER_Y, 20.5) for _, x in POWER] + [(x, PREAMP_Y, 11.5) for _, x in PREAMP]
    for bx in (PT_BOX, OT_BOX, CH_BOX):
        for x, y, r in env:
            dx = max(bx[0] - x, 0, x - bx[2])
            dy = max(bx[1] - y, 0, y - bx[3])
            if (dx * dx + dy * dy) ** 0.5 < r + 5:
                issues.append(f"lampe ({x:.0f},{y:.0f}) trop près d'un transfo {bx}")
    for (x1, y1, r1) in env:
        for (x2, y2, r2) in env:
            if (x1, y1) < (x2, y2):
                if ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 < r1 + r2 + 8:
                    issues.append(f"lampes trop serrées ({x1:.0f},{y1:.0f}) / ({x2:.0f},{y2:.0f})")
    # front: knob 30 mm, pot body 25 mm
    fw = front_wall()
    xs = sorted(h.x for h in fw.holes if h.d >= 9)
    for a, b in zip(xs, xs[1:]):
        if b - a < 30:
            issues.append(f"façade : éléments à {b - a:.0f} mm ({a:.0f}/{b:.0f})")
    # interior height: tallest part (PT 123 mm) under the shell top
    inner_h = SH_H - 2 * T_SH - H - 6.0   # 6 mm feet clearance inside? chassis sits on bottom
    if inner_h - 123.0 < 25.0:
        issues.append(f"dégagement au-dessus du transfo d'alim : {inner_h - 123:.0f} mm")
    return issues


if __name__ == "__main__":
    print("BD =", round(BD, 3))
    for i in clearance_checks():
        print(" -", i)
    print("checks done")
