"""Export DXF flat patterns and A3 PDF drawings for the pilotable SLO head."""
import math
import os

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

import geometry as g

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT + "/dxf", exist_ok=True)

INK = "#1b1b1b"
CUTC = "#1b1b1b"
VERC = "#c2410c"
BENDC = "#2563eb"
ZONEC = "#9ca3af"

# ------------------------------------------------------------------------------------
# Flat patterns
# ------------------------------------------------------------------------------------

def chassis_flat():
    """Return (outline polygon, holes [(x,y,Hole)], bend lines) of the one-piece chassis tray."""
    o = g.H - g.BD
    s = g.RET - g.BD
    W, D, c = g.W, g.D, g.T_CH + 0.5
    poly = [(o, 0), (o + W, 0), (o + W, o + c), (2 * o + W + s, o + c), (2 * o + W + s, o + D - c),
            (o + W, o + D - c), (o + W, 2 * o + D), (o, 2 * o + D), (o, o + D - c), (-s, o + D - c),
            (-s, o + c), (o, o + c)]
    holes = []
    for h in g.top_plate().holes:
        holes.append((o + h.x, o + h.y, h))
    for h in g.front_wall().holes:
        holes.append((o + h.x, h.y, h))
    ytot = 2 * o + D
    for h in g.rear_wall().holes:
        holes.append((o + h.x, ytot - h.y, h))
    xr = 2 * o + W
    for h in g.side_wall(True).holes:   # h.x = along wall from front, h.y = height z
        holes.append((h.y, o + h.x, g.Hole(0, 0, w=h.h, h=h.w, label=h.label)))
    # chassis fixing holes in the side returns (r = RET/2 from the outer face)
    r = g.RET / 2
    for u in (50.0, g.D - 50.0):
        holes.append((g.BD - r, o + u, g.Hole(0, 0, d=4.5, label="Fixation M4 (retour)")))
        holes.append((xr + (r - g.BD), o + u, g.Hole(0, 0, d=4.5, label="Fixation M4 (retour)")))
    bends = [((o, o + c), (o, o + D - c)), ((o + W, o + c), (o + W, o + D - c)),
             ((o, o), (o + W, o)), ((o, o + D), (o + W, o + D)),
             ((0, o + c), (0, o + D - c)), ((xr, o + c), (xr, o + D - c))]
    reliefs = [(o, o), (o + W, o), (o, o + D), (o + W, o + D)]
    return poly, holes, bends, reliefs


T_SH, R_SH = g.T_SH, 2.0
BD_SH = 2 * (R_SH + T_SH) - math.pi / 2 * (R_SH + g.K * T_SH)
RET_SH = 25.0


def shell_flat():
    """U cover: left return, left side, top, right side, right return (unfolded across x)."""
    o = g.SH_H - BD_SH
    s = RET_SH - BD_SH
    Wt = 2 * o + g.SH_W
    poly = [(-s, 0), (Wt + s, 0), (Wt + s, g.SH_D), (-s, g.SH_D)]
    top, _ = g.shell_parts()
    holes = [(o + h.x, h.y, h) for h in top.holes]
    # bottom-plate screws through the returns, at r = RET_SH/2
    r = RET_SH / 2
    for y in (30.0, g.SH_D / 2, g.SH_D - 30.0):
        holes.append((BD_SH - r, y, g.Hole(0, 0, d=4.5, label="Vis M4 fond")))
        holes.append((Wt + (r - BD_SH), y, g.Hole(0, 0, d=4.5, label="Vis M4 fond")))
    # chassis fixing screws also pass through the returns
    ox = (g.SH_W - g.W) / 2
    rc = ox + g.RET / 2
    for u in (50.0, g.D - 50.0):
        y = g.CH_SETBACK + u
        holes.append((BD_SH - rc, y, g.Hole(0, 0, d=4.5, label="Fixation châssis M4")))
        holes.append((Wt + (rc - BD_SH), y, g.Hole(0, 0, d=4.5, label="Fixation châssis M4")))
    # grille brackets: 2 rivet holes per bracket on each side wall, front and rear
    for depth in (10.0, g.SH_D - 10.0):
        for z in (130.0, 235.0):
            holes.append((z, depth, g.Hole(0, 0, d=4.1, label="Rivet équerre grille")))
            holes.append((Wt - z, depth, g.Hole(0, 0, d=4.1, label="Rivet équerre grille")))
    bends = [((0, 0), (0, g.SH_D)), ((o, 0), (o, g.SH_D)), ((o + g.SH_W, 0), (o + g.SH_W, g.SH_D)),
             ((Wt, 0), (Wt, g.SH_D))]
    return poly, holes, bends


def bottom_plate():
    w = g.SH_W - 2 * T_SH - 1.0
    d = g.SH_D
    x0 = T_SH + 0.5
    _, bot = g.shell_parts()
    holes = [(h.x - x0, h.y, h) for h in bot.holes if "Fixation" not in h.label]
    # bottom-plate rivnuts (M4) above the shell returns
    r = RET_SH / 2
    for y in (30.0, g.SH_D / 2, g.SH_D - 30.0):
        holes.append((r - x0, y, g.Hole(0, 0, d=6.0, label="Écrou à sertir M4")))
        holes.append((w - (r - x0), y, g.Hole(0, 0, d=6.0, label="Écrou à sertir M4")))
    ox = (g.SH_W - g.W) / 2
    for h in bot.holes:
        if "Fixation" in h.label:
            holes.append((h.x - x0, h.y, g.Hole(0, 0, d=4.5, label="Fixation châssis M4")))
    poly = [(0, 0), (w, 0), (w, d), (0, d)]
    return poly, holes, w, d


def grille():
    w = g.SH_W - 2 * T_SH - 1.0
    z0 = 4.0 + g.H + 3.0              # just above the chassis top plate
    hgt = g.SH_H - T_SH - 1.0 - z0
    holes = [(x, y, g.Hole(0, 0, d=4.5, label="Vis M4 équerre"))
             for x in (10.0, w - 10.0) for y in (hgt * 0.2, hgt * 0.85)]
    poly = [(0, 0), (w, 0), (w, hgt), (0, hgt)]
    return poly, holes, w, hgt


# ------------------------------------------------------------------------------------
# DXF
# ------------------------------------------------------------------------------------

def write_dxf(path, poly, holes, bends=(), reliefs=(), title=""):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for name, col, lt in (("DECOUPE", 7, "CONTINUOUS"), ("PLIAGE", 5, "DASHED"),
                          ("A_VERIFIER", 30, "CONTINUOUS"), ("TEXTE", 8, "CONTINUOUS")):
        doc.layers.add(name, color=col, linetype=lt)
    msp = doc.modelspace()
    msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "DECOUPE"})
    for x, y, h in holes:
        layer = "A_VERIFIER" if h.verify else "DECOUPE"
        if h.d:
            msp.add_circle((x, y), h.d / 2, dxfattribs={"layer": layer})
        else:
            msp.add_lwpolyline([(x - h.w / 2, y - h.h / 2), (x + h.w / 2, y - h.h / 2),
                                (x + h.w / 2, y + h.h / 2), (x - h.w / 2, y + h.h / 2)],
                               close=True, dxfattribs={"layer": layer})
    for (a, b) in bends:
        msp.add_line(a, b, dxfattribs={"layer": "PLIAGE"})
    for (x, y) in reliefs:
        msp.add_circle((x, y), 1.5, dxfattribs={"layer": "DECOUPE"})
    if title:
        minx = min(p[0] for p in poly)
        miny = min(p[1] for p in poly)
        msp.add_text(title, height=6, dxfattribs={"layer": "TEXTE"}).set_placement((minx, miny - 15))
    doc.saveas(path)


# ------------------------------------------------------------------------------------
# PDF drawings (A3 landscape, true scale given per view)
# ------------------------------------------------------------------------------------
A3 = (16.54, 11.69)


def frame(fig, title, sheet, scale_note=""):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.8, ec=INK))
    ax.add_patch(Rectangle((250, 10), 160, 22, fill=False, lw=0.6, ec=INK))
    ax.text(254, 25, title, fontsize=10, weight="bold", color=INK, va="center")
    ax.text(254, 16, f"Tête 100 W pilotable · {scale_note} · cotes en mm", fontsize=6.5, color=INK)
    ax.text(404, 16, f"F{sheet}", fontsize=8, ha="right", color=INK)
    return ax


def view_axes(fig, x0, y0, w, h, xlim, ylim):
    """Axes placed in mm on the A3 sheet with an equal data scale."""
    ax = fig.add_axes([x0 / 420, y0 / 297, w / 420, h / 297])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


def draw_part(ax, poly, holes, bends=(), label_ids=True, start=1, hole_fs=4.2):
    if poly:
        ax.add_patch(Polygon(poly, closed=True, fill=False, lw=0.9, ec=CUTC))
    for (a, b) in bends:
        ax.plot([a[0], b[0]], [a[1], b[1]], ls=(0, (6, 3)), lw=0.6, color=BENDC)
    rows = []
    n = start
    for x, y, h in holes:
        col = VERC if h.verify else CUTC
        if h.d:
            ax.add_patch(Circle((x, y), h.d / 2, fill=False, lw=0.6, ec=col))
            size = f"Ø{h.d:g}"
        else:
            ax.add_patch(Rectangle((x - h.w / 2, y - h.h / 2), h.w, h.h, fill=False, lw=0.6, ec=col))
            size = f"{h.w:g}×{h.h:g}"
        if label_ids and (h.label or h.d >= 9 or h.w):
            ax.text(x, y + max(h.d, h.h) / 2 + 2.5, str(n), fontsize=hole_fs, ha="center", color=col)
            rows.append((n, x, y, size, h.label, h.verify))
            n += 1
    return rows


def hole_table(ax, rows, x, y, title, max_rows=34, fs=5.2, origin=""):
    ax.text(x, y, title, fontsize=7, weight="bold", color=INK)
    ax.text(x, y - 4, origin, fontsize=5.2, color="#4b5563")
    yy = y - 9
    ax.text(x, yy, "N°", fontsize=fs, weight="bold")
    ax.text(x + 8, yy, "X", fontsize=fs, weight="bold")
    ax.text(x + 22, yy, "Y", fontsize=fs, weight="bold")
    ax.text(x + 36, yy, "Taille", fontsize=fs, weight="bold")
    ax.text(x + 52, yy, "Désignation", fontsize=fs, weight="bold")
    for n, hx, hy, size, lab, ver in rows[:max_rows]:
        yy -= 4.6
        col = VERC if ver else INK
        ax.text(x, yy, str(n), fontsize=fs, color=col)
        ax.text(x + 8, yy, f"{hx:.1f}", fontsize=fs, color=col)
        ax.text(x + 22, yy, f"{hy:.1f}", fontsize=fs, color=col)
        ax.text(x + 36, yy, size, fontsize=fs, color=col)
        ax.text(x + 52, yy, (lab or "") + (" — à vérifier" if ver else ""), fontsize=fs, color=col)
    return yy


def outer_dims(ax, w, h, off=8, fs=6):
    ax.annotate("", xy=(0, -off), xytext=(w, -off), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(w / 2, -off - 5, f"{w:g}", ha="center", fontsize=fs)
    ax.annotate("", xy=(-off, 0), xytext=(-off, h), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(-off - 3, h / 2, f"{h:g}", ha="right", va="center", fontsize=fs, rotation=90)


def sheet_overview(pdf, render_png):
    fig = plt.figure(figsize=A3)
    ax = frame(fig, "Vue d'ensemble", 1, "rendu indicatif")
    img = plt.imread(render_png)
    axi = fig.add_axes([18 / 420, 60 / 297, 384 / 420, 220 / 297])
    axi.imshow(img)
    axi.axis("off")
    notes = [
        "Châssis : acier DC01 1,5 mm, plateau à 4 parois d'une pièce, rayon intérieur 1,5 mm, K = 0,42 (à recaler sur l'outillage du plieur).",
        "Capot : aluminium 5754 2 mm, en U avec retours, fond rapporté ; thermolaquage noir mat texturé. Grilles avant et arrière : tôle perforée achetée, noire.",
        f"Encombrement : {g.SH_W:g} × {g.SH_H:g} × {g.SH_D:g} mm (l × h × p) hors poignée et boutons ; masse estimée ~20 kg.",
        "Trous en orange : dépendent d'une pièce à recevoir (transfos, embase IEC, écran). Commander ces pièces et relever leurs cotes avant la découpe.",
    ]
    for i, t in enumerate(notes):
        ax.text(18, 50 - i * 6, "• " + t, fontsize=6.6, color=INK)
    pdf.savefig(fig)
    plt.close(fig)


def sheet_top(pdf):
    fig = plt.figure(figsize=A3)
    ax = frame(fig, "Châssis : dessus, perçages", 2, "vue de dessus, éch. 1:2,5")
    s = 1 / 2.5
    vx = view_axes(fig, 25, 135, g.W * s + 10, g.D * s + 20, (-15, g.W + 10), (-25, g.D + 25))
    tp = g.top_plate()
    vx.add_patch(Rectangle((0, 0), g.W, g.D, fill=False, lw=0.9, ec=CUTC))
    for z in tp.zones:
        vx.add_patch(Rectangle((z[0], z[1]), z[2] - z[0], z[3] - z[1], fill=False, lw=0.4,
                               ec=ZONEC, ls=(0, (2, 2))))
        vx.text((z[0] + z[2]) / 2, z[3] - 4, z[4], fontsize=3.6, ha="center", color="#6b7280")
    rows = draw_part(vx, [], [(h.x, h.y, h) for h in tp.holes], label_ids=True, hole_fs=5)
    outer_dims(vx, g.W, g.D)
    vx.text(g.W / 2, g.D + 12, "ARRIÈRE", ha="center", fontsize=6)
    vx.text(g.W / 2, -20, "AVANT (façade)", ha="center", fontsize=6)
    hole_table(ax, rows, 30, 125, "Tableau des perçages : dessus",
               origin="Origine : coin avant gauche, vue de dessus ; X vers la droite, Y vers l'arrière.")
    pdf.savefig(fig)
    plt.close(fig)


def sheet_walls(pdf):
    fig = plt.figure(figsize=A3)
    ax = frame(fig, "Châssis : façade et panneau arrière", 3, "vues extérieures, éch. 1:2,5")
    s = 1 / 2.5
    fw = g.front_wall()
    v1 = view_axes(fig, 25, 220, g.W * s + 10, g.H * s + 20, (-15, g.W + 10), (-25, g.H + 15))
    v1.add_patch(Rectangle((0, 0), g.W, g.H, fill=False, lw=0.9, ec=CUTC))
    r1 = draw_part(v1, [], [(h.x, h.y, h) for h in fw.holes], hole_fs=5)
    outer_dims(v1, g.W, g.H)
    v1.text(0, g.H + 5, "Façade, vue de face (bas = bord libre, haut = pli avec le dessus)", fontsize=5.5)
    rw = g.rear_wall()
    v2 = view_axes(fig, 25, 160, g.W * s + 10, g.H * s + 20, (-15, g.W + 10), (-25, g.H + 15))
    v2.add_patch(Rectangle((0, 0), g.W, g.H, fill=False, lw=0.9, ec=CUTC))
    r2 = draw_part(v2, [], [(g.W - h.x, h.y, h) for h in rw.holes], start=len(r1) + 1, hole_fs=5)
    outer_dims(v2, g.W, g.H)
    v2.text(0, g.H + 5, "Panneau arrière, vue de l'arrière (cotes X depuis le bord gauche vu de l'arrière)", fontsize=5.5)
    hole_table(ax, r1, 30, 150, "Façade", origin="Origine : coin inférieur gauche, vue de face.")
    hole_table(ax, r2, 225, 150, "Panneau arrière", origin="Origine : coin inférieur gauche, vue de l'arrière.")
    pdf.savefig(fig)
    plt.close(fig)


def sheet_flat(pdf, flat):
    poly, holes, bends, reliefs = flat
    fig = plt.figure(figsize=A3)
    ax = frame(fig, "Châssis : développé (découpe laser)", 4, "éch. 1:3")
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    s = 1 / 3
    v = view_axes(fig, 20, 40, (max(xs) - min(xs)) * s + 20, (max(ys) - min(ys)) * s + 20,
                  (min(xs) - 25, max(xs) + 25), (min(ys) - 25, max(ys) + 25))
    draw_part(v, poly, holes, bends, label_ids=False)
    for x, y in reliefs:
        v.add_patch(Circle((x, y), 1.5, fill=False, lw=0.5, ec=CUTC))
    v.text(min(xs), max(ys) + 8, f"Développé : {max(xs) - min(xs):.1f} × {max(ys) - min(ys):.1f} mm, "
           f"déduction de pli {g.BD:.2f} mm par pli (acier 1,5 mm, Ri 1,5, K 0,42)", fontsize=6)
    ax.text(300, 120, "Plis (bleu tireté) :", fontsize=6.5, weight="bold")
    for i, t in enumerate(["4 plis à 90° vers le bas : façade, arrière, joues",
                           "2 plis à 90° vers l'intérieur : retours bas des joues (15 mm)",
                           "Ordre conseillé : retours, joues, puis façade et arrière",
                           "Fichier : chassis_developpe.dxf (calques DECOUPE, PLIAGE, A_VERIFIER)",
                           "Le calque A_VERIFIER n'est pas à découper avant validation"]):
        ax.text(300, 113 - i * 6, "• " + t, fontsize=6)
    pdf.savefig(fig)
    plt.close(fig)


def sheet_shell(pdf, sflat, bplate, gr):
    fig = plt.figure(figsize=A3)
    ax = frame(fig, "Capot, fond et grilles", 5, "éch. 1:4")
    s = 1 / 4
    poly, holes, bends = sflat
    xs = [p[0] for p in poly]
    v = view_axes(fig, 20, 150, (max(xs) - min(xs)) * s + 15, g.SH_D * s + 20,
                  (min(xs) - 20, max(xs) + 20), (-25, g.SH_D + 25))
    draw_part(v, poly, holes, bends, label_ids=False)
    v.text(min(xs), g.SH_D + 8, f"Capot en U, développé {max(xs) - min(xs):.1f} × {g.SH_D:g} mm "
           f"(alu 5754 2 mm, Ri 2, déduction {BD_SH:.2f} mm) : retour · joue · dessus · joue · retour", fontsize=5.5)
    p2, h2, w2, d2 = bplate
    v2 = view_axes(fig, 20, 40, w2 * s + 15, d2 * s + 15, (-20, w2 + 20), (-20, d2 + 20))
    draw_part(v2, p2, h2, label_ids=False)
    v2.text(0, d2 + 6, f"Fond {w2:g} × {d2:g} mm (alu 2 mm)", fontsize=5.5)
    p3, h3, w3, d3 = gr
    v3 = view_axes(fig, 200, 50, w3 * s + 15, d3 * s + 15, (-20, w3 + 20), (-20, d3 + 20))
    draw_part(v3, p3, h3, label_ids=False)
    v3.text(0, d3 + 6, f"Grilles avant et arrière (×2) : {w3:g} × {d3:.0f} mm, tôle perforée noire", fontsize=5.5)
    pdf.savefig(fig)
    plt.close(fig)


def main(render_png):
    flat = g_flat = chassis_flat()
    poly, holes, bends, reliefs = flat
    write_dxf(OUT + "/dxf/chassis_developpe.dxf", poly, holes, bends, reliefs,
              "Chassis acier DC01 1,5 mm - developpe")
    sp = shell_flat()
    write_dxf(OUT + "/dxf/capot_developpe.dxf", sp[0], sp[1], sp[2], (), "Capot alu 5754 2 mm - developpe")
    bp = bottom_plate()
    write_dxf(OUT + "/dxf/fond.dxf", bp[0], bp[1], (), (), "Fond alu 2 mm")
    gr = grille()
    write_dxf(OUT + "/dxf/grille_x2.dxf", gr[0], gr[1], (), (), "Grille perforee (x2)")
    with PdfPages(OUT + "/plans_chassis.pdf") as pdf:
        sheet_overview(pdf, render_png)
        sheet_top(pdf)
        sheet_walls(pdf)
        sheet_flat(pdf, g_flat)
        sheet_shell(pdf, sp, bp, gr)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return dict(chassis_flat=(round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)),
                shell_flat=(round(max(p[0] for p in sp[0]) - min(p[0] for p in sp[0]), 1), g.SH_D))


if __name__ == "__main__":
    import sys
    print(main(sys.argv[1]))
