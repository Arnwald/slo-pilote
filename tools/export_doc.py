"""Turns the Markdown export of the working design doc (Claude Docs) into docs/conception.md.

python3 tools/export_doc.py <export.json> <date text>
The export's figures (interactive widgets) and pictures become links to the repository's scripts, data
and renders; private links are replaced; the byline becomes a dated note.
"""
import base64
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMB = [
    "> Figure : réponses du tone stack d'origine et remis à l'échelle — script [`sim/tonestack.py`](../sim/tonestack.py), données [`sim/curves.json`](../sim/curves.json).",
    "> Figure : distorsion de la cathode follower simple et de la White cathode follower sur le tone stack ÷10 — script [`sim/cf_drive.py`](../sim/cf_drive.py), données [`sim/cf_drive.json`](../sim/cf_drive.json).",
    "> Figure : gain et distorsion de V1B chargée par les diviseurs ÷5, avec et sans buffer — script [`sim/v1b_buffer.py`](../sim/v1b_buffer.py), données [`sim/v1b_buffer.json`](../sim/v1b_buffer.json).",
    "> Figure : réseaux presence et depth, de l'entrée du déphaseur au HP — script [`spice/depth_test.py`](../spice/depth_test.py), données [`spice/res_depth.json`](../spice/res_depth.json).",
    "> Nomenclature détaillée et sourcée : [`bom/nomenclature_tete_100W.xlsx`](../bom/nomenclature_tete_100W.xlsx) (générée par [`bom/build_bom.py`](../bom/build_bom.py)) ; prix relevés en novembre 2026 quand une source est citée, estimations sinon.",
]
IMG = [
    "![Rendu de face : grille perforée, lampes allumées, façade à boutons motorisés](../mech/out/rendu_facade.png)",
    "![Implantation vue de dessus du châssis](../mech/out/implantation_dessus.png)",
    "![Robot de micro devant le HP du haut à gauche : modules linéaires, arc denté centré sur la capsule, servo d'angle derrière le micro, SM57 au bord du cache à 45°](../robot/web/rendu_robot_micro.jpg)",
]


def main(src, date_text):
    d = json.load(open(src))
    text = d[1]["text"]
    j = json.loads(text[text.index("{"):])
    md = base64.b64decode(j["data"]["bytes_b64"]).decode("utf-8")
    lines = md.split("\n")
    assert re.match(r"^\w+ \d+, 20\d\d · @", lines[2]), lines[2]
    lines[2] = (f"*Export du dossier de conception de travail, état du {date_text}. Les figures interactives du document "
                "d'origine sont remplacées par des liens vers les scripts et les données qui les produisent.*")
    md = "\n".join(lines)
    pe = re.compile(r"^&#91;embedded content: .*\\\]$", re.M)
    pi = re.compile(r"^&#91;image: .*\\\]$", re.M)
    assert len(pe.findall(md)) == len(EMB) and len(pi.findall(md)) == len(IMG), (len(pe.findall(md)), len(pi.findall(md)))
    it = iter(EMB)
    md = pe.sub(lambda m: next(it), md)
    it = iter(IMG)
    md = pi.sub(lambda m: next(it), md)
    md = re.sub(r"La \[maquette 3D\]\(https://claude\.ai/artifact/[^)]+\) se manipule",
                "La maquette 3D ([`robot/web/robot_micro.html`](../robot/web/robot_micro.html), à ouvrir dans un navigateur) se manipule", md)
    md = md.replace("sont dans robot\\_micro\\_cad.zip.", "sont dans le dossier [`robot/`](../robot/).")
    md = md.replace("How_the_Saldano_SLO-100_Works", "How_the_Soldano_SLO-100_Works")
    md = re.sub(r"\| (chassis|capot)\\_developpe\.dxf \|", lambda m: f"| [`{m.group(1)}_developpe.dxf`](../mech/out/dxf/{m.group(1)}_developpe.dxf) |", md)
    md = md.replace("| fond.dxf |", "| [`fond.dxf`](../mech/out/dxf/fond.dxf) |")
    md = md.replace("| grille\\_x2.dxf |", "| [`grille_x2.dxf`](../mech/out/dxf/grille_x2.dxf) |")
    assert "claude.ai" not in md and "@Arnaud" not in md
    open(os.path.join(ROOT, "docs", "conception.md"), "w").write(md)
    print("docs/conception.md", len(md), "caractères")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
