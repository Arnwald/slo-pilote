"""Concept renders of the head: front elevation (tubes glowing behind a perforated grille)
and a top-view layout of the chassis."""
import os
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

import geometry as g

PX = 4.0  # pixels per mm for the front render
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

BODY = "#141416"
FASCIA = "#1d1e21"
SHEET = np.array([0.055, 0.055, 0.06])


def _fig(w_mm, h_mm, px=PX, bg="black"):
    fig = plt.figure(figsize=(w_mm * px / 100, h_mm * px / 100), dpi=100, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.axis("off")
    ax.set_facecolor(bg)
    return fig, ax


def _to_array(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return plt.imread(buf)[:, :, :3]


def tube(ax, x, z0, w, h, glow, kind):
    # glow halo
    for r, a in ((w * 1.6, 0.05), (w * 1.1, 0.08), (w * 0.7, 0.12)):
        ax.add_patch(Circle((x, z0 + h * 0.45), r, color="#ff8a1f", alpha=a * glow, lw=0))
    base_h = 18 if kind == "octal" else 6
    ax.add_patch(Rectangle((x - w * 0.42, z0), w * 0.84, base_h, color="#2b1d12", lw=0))
    ax.add_patch(FancyBboxPatch((x - w / 2, z0 + base_h), w, h - base_h,
                                boxstyle=f"round,pad=0,rounding_size={w * 0.45}",
                                fc="#3a3f46", ec="#8b95a1", lw=0.8, alpha=0.55))
    # internal plates
    ax.add_patch(Rectangle((x - w * 0.28, z0 + base_h + h * 0.12), w * 0.56, h * 0.45,
                           color="#202326", lw=0))
    # heater glow
    ax.add_patch(Rectangle((x - w * 0.06, z0 + base_h + h * 0.2), w * 0.12, h * 0.3,
                           color="#ffb347", alpha=0.95 * glow, lw=0))
    ax.add_patch(Circle((x, z0 + base_h + h * 0.33), w * 0.18, color="#ff7a00", alpha=0.35 * glow, lw=0))


def magnet(ax, x0, x1, z0, h, label):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, h, fc="#22252a", ec="#3a3f46", lw=1.2))
    ax.add_patch(Rectangle((x0 + 6, z0 + 6), x1 - x0 - 12, h - 12, fc="#1a1c20", ec="#2c3036", lw=0.8))


def front_scene():
    W, Hh = g.SH_W, g.SH_H
    fig, ax = _fig(W, Hh + 30, bg="#0a0a0b")
    zc = 4.0 + 15.0   # chassis top plate height inside shell (bottom plate stack 4 mm), +15 feet
    feet = 15.0
    top = zc + g.H    # chassis top plate z
    ox = (g.SH_W - g.W) / 2
    # interior background
    ax.add_patch(Rectangle((0, feet), W, Hh, color="#0d0d0f", lw=0))
    # transformers (rear)
    pt, ot, ch = g.PT_BOX, g.OT_BOX, g.CH_BOX
    magnet(ax, ox + pt[0], ox + pt[2], top, 123, "PT")
    magnet(ax, ox + ot[0], ox + ot[2], top, 112, "OT")
    magnet(ax, ox + ch[0], ox + ch[2], top, 85, "CH")
    for _, x in g.POWER:
        tube(ax, ox + x, top, 38, 108, 1.0, "octal")
    for _, x in g.PREAMP:
        tube(ax, ox + x, top, 22, 52, 0.75, "noval")
    img = _to_array(fig)
    return img, feet, top


def grille_mask(shape, feet, top):
    """1 where the perforated sheet has a hole, in the grille area."""
    h, w = shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    xm = xx / PX
    zm = (h - yy) / PX
    pitch, rad = 7.0, 2.5
    row = np.round(zm / (pitch * 0.866))
    xo = xm - (row % 2) * pitch / 2
    cx = np.round(xo / pitch) * pitch
    cz = row * pitch * 0.866
    holes = ((xo - cx) ** 2 + (zm - cz) ** 2) < rad ** 2
    z_lo = top + 3.0
    z_hi = feet + g.SH_H - 6.0
    area = (zm > z_lo) & (zm < z_hi) & (xm > 6) & (xm < g.SH_W - 6)
    return holes & area, area


def front_render(path):
    scene, feet, top = front_scene()
    holes, area = grille_mask(scene.shape, feet, top)
    out = scene.copy()
    sheet = np.broadcast_to(SHEET, out.shape)
    m = area & ~holes
    out[m] = sheet[m]
    # overlay: shell frame, fascia, knobs, labels
    fig, ax = _fig(g.SH_W, g.SH_H + 30, bg="#0a0a0b")
    ax.imshow(out, extent=(0, g.SH_W, 0, g.SH_H + 30), aspect="auto", zorder=0)
    W = g.SH_W
    ax.add_patch(FancyBboxPatch((0, feet), W, g.SH_H, boxstyle="round,pad=0,rounding_size=10",
                                fill=False, ec="#2c2d31", lw=6, zorder=2))
    ax.add_patch(Rectangle((6, top + 3), W - 12, g.SH_H - (top - feet) - 9, fill=False,
                           ec="#26272b", lw=3, zorder=2))
    for fx in (40, W - 40):
        ax.add_patch(FancyBboxPatch((fx - 18, 2), 36, feet - 2, boxstyle="round,pad=0,rounding_size=3",
                                    fc="#0f0f10", ec="#222", lw=1, zorder=2))
    # fascia
    zc = feet + 4.0
    ox = (g.SH_W - g.W) / 2
    ax.add_patch(Rectangle((ox, zc), g.W, g.H, fc=FASCIA, ec="#2e3035", lw=1.5, zorder=3))
    kz = zc + g.FRONT_Z
    for i, lab in enumerate(g.KNOBS):
        x = ox + g.KNOB_X0 + i * g.KNOB_PITCH
        ax.add_patch(Circle((x, kz), 15, fc="#0e0e10", ec="#4a4d55", lw=1.6, zorder=4))
        ax.add_patch(Circle((x, kz), 11.5, fc="#17181b", ec="#2a2c31", lw=0.8, zorder=4))
        ang = np.deg2rad(225 - (i * 37 % 270))
        ax.plot([x + 3 * np.cos(ang), x + 11 * np.cos(ang)], [kz + 3 * np.sin(ang), kz + 11 * np.sin(ang)],
                color="#f2f2f2", lw=1.6, zorder=5, solid_capstyle="round")
        ax.text(x, kz + 23, lab.upper(), color="#c9ccd2", fontsize=4.2, ha="center", zorder=5,
                family="DejaVu Sans")
    # display + encoder + switches + input
    dx = ox + 118
    ax.add_patch(Rectangle((dx - 26, kz - 20), 52, 40, fc="#05070c", ec="#3a3d44", lw=1.2, zorder=4))
    ax.text(dx, kz + 8, "07", color="#ff9a3c", fontsize=11, ha="center", va="center", weight="bold", zorder=5)
    ax.text(dx, kz - 8, "TIGHT · OD+", color="#d9dde3", fontsize=4.5, ha="center", va="center", zorder=5)
    ex = ox + 172
    ax.add_patch(Circle((ex, kz), 9, fc="#0e0e10", ec="#55585f", lw=1.2, zorder=4))
    ax.text(ex, kz + 23, "PRESET", color="#c9ccd2", fontsize=4.2, ha="center", zorder=5)
    for sx, lab in ((ox + 24, "POWER"), (ox + 58, "STANDBY")):
        ax.add_patch(Circle((sx, kz), 6, fc="#2a2c31", ec="#6b6f78", lw=1, zorder=4))
        ax.plot([sx, sx], [kz, kz + 12], color="#d0d3d9", lw=2.4, zorder=5, solid_capstyle="round")
        ax.text(sx, kz - 18, lab, color="#c9ccd2", fontsize=4.2, ha="center", zorder=5)
    jx = ox + g.KNOB_X0 + 8 * g.KNOB_PITCH + 36
    ax.add_patch(Circle((jx, kz), 8, fc="#2a2c31", ec="#a0a4ab", lw=1.2, zorder=4))
    ax.add_patch(Circle((jx, kz), 3.4, fc="#000", zorder=5))
    ax.text(jx, kz + 23, "INPUT", color="#c9ccd2", fontsize=4.2, ha="center", zorder=5)
    # badge
    ax.add_patch(FancyBboxPatch((W / 2 - 46, feet + g.SH_H - 30), 92, 18, boxstyle="round,pad=0,rounding_size=3",
                                fc="#0b0b0c", ec="#5b5e66", lw=1.0, zorder=4))
    ax.text(W / 2, feet + g.SH_H - 21, "DEM · 100", color="#e6e8ec", fontsize=8.5, ha="center",
            va="center", weight="bold", zorder=5)
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


def top_render(path):
    fig = plt.figure(figsize=(12, 5.6), dpi=150, facecolor="white")
    ax = fig.add_axes([0.03, 0.06, 0.94, 0.88])
    ax.set_xlim(-10, g.W + 10)
    ax.set_ylim(-28, g.D + 18)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), g.W, g.D, fc="#f3f4f6", ec="#111", lw=1.2))
    tp = g.top_plate()
    for z in tp.zones:
        if z[4].startswith("Dessous"):
            ax.add_patch(Rectangle((z[0], z[1]), z[2] - z[0], z[3] - z[1], fill=False, ec="#9ca3af",
                                   lw=0.8, ls=(0, (3, 2))))
            ax.text(z[0] + 3, z[1] + 3, z[4].replace("Dessous : ", "dessous : "), fontsize=6, color="#6b7280")
    for box, lab in ((g.PT_BOX, "Transfo d'alimentation\n6,1 kg"), (g.OT_BOX, "Transfo de sortie\n3,7 kg"),
                     (g.CH_BOX, "Self")):
        ax.add_patch(Rectangle((box[0], box[1]), box[2] - box[0], box[3] - box[1], fc="#374151", ec="#111"))
        ax.text((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, lab, color="white", fontsize=7,
                ha="center", va="center")
    for lab, x in g.POWER:
        ax.add_patch(Circle((x, g.POWER_Y), 20, fc="#fde7cf", ec="#c2410c", lw=1.2))
        ax.text(x, g.POWER_Y, lab.replace(" ", "\n"), fontsize=6, ha="center", va="center")
    for lab, x in g.PREAMP:
        ax.add_patch(Circle((x, g.PREAMP_Y), 11.5, fc="#fde7cf", ec="#c2410c", lw=1.2))
        ax.text(x, g.PREAMP_Y + 17, lab, fontsize=6, ha="center")
    for i, lab in enumerate(g.KNOBS):
        x = g.KNOB_X0 + i * g.KNOB_PITCH
        ax.add_patch(Rectangle((x - 12.5, 2), 25, 43, fc="#e5e7eb", ec="#6b7280", lw=0.6))
    ax.text(g.W / 2, -10, "AVANT : façade (pots motorisés, écran, encodeur, entrée)", ha="center", fontsize=8)
    ax.text(g.W / 2, g.D + 8, "ARRIÈRE : secteur, HP, MIDI, USB, pédalier, insert", ha="center", fontsize=8)
    ax.text(-6, g.D / 2, "Puissance / alim", rotation=90, fontsize=7, va="center", ha="right", color="#374151")
    ax.text(g.W + 6, g.D / 2, "Préampli / entrée", rotation=90, fontsize=7, va="center", ha="left", color="#374151")
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    front_render(OUT + "/rendu_facade.png")
    top_render(OUT + "/implantation_dessus.png")
    print("ok")
