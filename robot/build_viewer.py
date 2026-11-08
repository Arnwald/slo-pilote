"""Interactive 3D viewer of the microphone robot (three.js), meshes embedded in the page.

python3 build_viewer.py out/meshes.json viewer.html [--local DIR]
"""
import base64
import json
import sys

import numpy as np

src, dst = sys.argv[1], sys.argv[2]
local = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--local" else None
Q = 0.05     # mm per unit of the int16 vertex coordinates

meshes = []
for m in json.load(open(src)):
    v = np.round(np.array(m["v"], dtype=np.float64) / Q).astype(np.int16)
    t = np.array(m["t"], dtype=np.uint32)
    big = int(t.max()) > 65535
    t = t.astype(np.uint32 if big else np.uint16)
    meshes.append({"n": m["name"], "g": m["group"], "c": m["colour"], "big": big,
                   "v": base64.b64encode(v.tobytes()).decode(), "t": base64.b64encode(t.tobytes()).decode()})
data = json.dumps(meshes, separators=(",", ":"))

if local:
    scripts = (f'<script src="{local}/three.min.js"></script>\n'
               f'<script src="{local}/OrbitControls.js"></script>')
else:
    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
               '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>')

html = r"""<title>Robot de micro XZθ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600&display=swap">
<style>
/* Layout: one-screen workshop tool, 3D view on the left, control panel on the right (stacked on phones). */
:root {
  --bg: #e9edf1; --panel: #f7f9fb; --ink: #17202a; --muted: #56616e; --line: #cdd5de;
  --accent: #b45309; --accent-ink: #ffffff; --ok: #15803d; --warn: #b91c1c; --scene: #dfe5ea;
  --display: "Barlow Semi Condensed", "Arial Narrow", sans-serif;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e1318; --panel: #151c23; --ink: #e6ebf0; --muted: #98a4b1; --line: #2a3541;
  --accent: #f59e0b; --accent-ink: #1a1206; --ok: #4ade80; --warn: #f87171; --scene: #121a21; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0e1318; --panel: #151c23; --ink: #e6ebf0; --muted: #98a4b1; --line: #2a3541;
  --accent: #f59e0b; --accent-ink: #1a1206; --ok: #4ade80; --warn: #f87171; --scene: #121a21; color-scheme: dark }
html, body { height: 100%; }
body { background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.45;
  display: flex; flex-direction: column; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 12px; box-sizing: border-box; gap: 12px; }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 16px; }
h1 { font-family: var(--display); font-weight: 600; font-size: 1.6rem; letter-spacing: 0.01em; margin: 0; text-wrap: balance; }
header p { margin: 0; color: var(--muted); max-width: 70ch; }
main { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 330px; gap: 12px; }
#view { position: relative; min-height: 320px; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: var(--scene); }
#c { display: block; width: 100%; height: 100%; touch-action: none; }
.views { position: absolute; left: 10px; bottom: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
.views button, .presets button { font: 500 0.82rem var(--body); color: var(--ink); background: var(--panel);
  border: 1px solid var(--line); border-radius: 4px; padding: 5px 9px; cursor: pointer; }
.views button:hover, .presets button:hover { border-color: var(--accent); }
button:focus-visible, input:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
aside { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 14px; overflow-y: auto;
  display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.axis { display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; align-items: baseline; }
.axis label { font-family: var(--display); font-weight: 600; font-size: 1.02rem; letter-spacing: 0.02em; }
.axis output { font: 500 0.95rem var(--mono); font-variant-numeric: tabular-nums; }
.axis input { grid-column: 1 / -1; width: 100%; accent-color: var(--accent); }
.axis small { grid-column: 1 / -1; color: var(--muted); font-size: 0.82rem; }
h2 { font-family: var(--display); font-weight: 600; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--muted); margin: 0 0 6px; }
.presets { display: flex; flex-wrap: wrap; gap: 6px; }
.state { display: flex; flex-direction: column; gap: 6px; }
.pill { display: inline-flex; align-items: center; gap: 6px; font: 500 0.85rem var(--mono); padding: 3px 8px; border-radius: 999px;
  border: 1px solid currentColor; width: fit-content; }
.pill.ok { color: var(--ok); } .pill.warn { color: var(--warn); }
code { font: 0.86rem var(--mono); background: var(--bg); border: 1px solid var(--line); border-radius: 4px; padding: 4px 6px; display: block; overflow-x: auto; white-space: nowrap; }
dl { display: grid; grid-template-columns: auto 1fr; gap: 3px 10px; margin: 0; font-size: 0.88rem; }
dt { color: var(--muted); } dd { margin: 0; font-family: var(--mono); font-size: 0.82rem; font-variant-numeric: tabular-nums; }
@media (max-width: 760px) {
  body { height: auto; } main { grid-template-columns: minmax(0, 1fr); } #view { height: 62vh; } aside { overflow: visible; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<header>
  <h1>Robot de micro XZθ</h1>
  <p>Positionneur à trois servomoteurs pour un HP de 12 pouces, piloté par la tête : position radiale, distance au tissu et angle autour de la capsule. Faites tourner la vue à la souris ou au doigt.</p>
</header>
<main>
  <div id="view">
    <canvas id="c" aria-label="Vue 3D du robot de micro devant le baffle"></canvas>
    <div class="views">
      <button type="button" id="v-iso">Trois-quarts</button>
      <button type="button" id="v-top">Dessus</button>
      <button type="button" id="v-side">Côté</button>
      <button type="button" id="v-close">Gros plan</button>
    </div>
  </div>
  <aside>
    <div class="axis">
      <label for="ax">Position radiale</label><output id="ox">25 mm</output>
      <input type="range" id="ax" min="-15" max="135" step="1" value="25">
      <small>0 = centre du cache-noyau, 25 = bord du cache, 115 ≈ bord du cône</small>
    </div>
    <div class="axis">
      <label for="ad">Distance capsule – tissu</label><output id="od">20 mm</output>
      <input type="range" id="ad" min="10" max="160" step="1" value="20">
      <small>Capsule du SM57 à 8 mm derrière sa grille</small>
    </div>
    <div class="axis">
      <label for="aa">Angle</label><output id="oa">0°</output>
      <input type="range" id="aa" min="-50" max="50" step="1" value="0">
      <small>Rotation autour de la capsule ; positif = nez vers le centre du HP</small>
    </div>
    <div class="state">
      <span class="pill ok" id="clear">jeu au tissu 12,0 mm</span>
      <code id="gcode" title="Message OSC envoyé à la tête">/micro/position 25.0 20.0 0.0</code>
    </div>
    <div>
      <h2>Positions de départ</h2>
      <div class="presets">
        <button type="button" data-p="0,12,0">Centre du cache</button>
        <button type="button" data-p="25,12,0">Bord du cache</button>
        <button type="button" data-p="25,25,45">Bord du cache, 45°</button>
        <button type="button" data-p="60,33,0">Cône, 2,5 cm</button>
        <button type="button" data-p="40,110,15">Recul, 10 cm</button>
      </div>
    </div>
    <div>
      <h2>Caractéristiques</h2>
      <dl>
        <dt>Courses</dt><dd>150 mm × 150 mm × ±50°</dd>
        <dt>Entraînement</dt><dd>vis T8 pas 2 mm ; arc denté m 1,5</dd>
        <dt>Codeurs</dt><dd>14 bits : 0,12 µm ; 0,002°</dd>
        <dt>Vitesses</dt><dd>10 mm/s ; 60°/s</dd>
        <dt>Moteurs</dt><dd>3 servos pas à pas CAN (MKS SERVO42D)</dd>
        <dt>Commande</dt><dd>contrôleur de la tête, bus CAN ; Ethernet vers la régie</dd>
        <dt>Masse</dt><dd>≈ 2,8 kg avec le SM57</dd>
      </dl>
    </div>
  </aside>
</main>
""" + scripts + r"""
<script>
const MESHES = """ + data + r""";
const Q = """ + str(Q) + r""";
const canvas = document.getElementById("c");
const view = document.getElementById("view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 5, 6000);
camera.up.set(0, 0, 1);
const controls = new THREE.OrbitControls(camera, canvas);
controls.enableDamping = false;
scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.75));
const key = new THREE.DirectionalLight(0xffffff, 0.75); key.position.set(-400, 600, 900); scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.35); fill.position.set(700, -200, 300); scene.add(fill);

const zg = new THREE.Group(), xg = new THREE.Group(), ag = new THREE.Group();
scene.add(zg); zg.add(xg); xg.add(ag);
const parent = { A: ag, X: xg, Z: zg };
function b64(s, T) { const bin = atob(s); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new T(u.buffer); }
for (const m of MESHES) {
  const vi = b64(m.v, Int16Array), pos = new Float32Array(vi.length);
  for (let i = 0; i < vi.length; i++) pos[i] = vi[i] * Q;
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(b64(m.t, m.big ? Uint32Array : Uint16Array), 1));
  const glass = m.g === "grille";
  const mat = new THREE.MeshStandardMaterial({ color: m.c, roughness: 0.62, metalness: 0.08, flatShading: true,
    transparent: glass, opacity: glass ? 0.16 : 1, depthWrite: !glass, side: glass ? THREE.DoubleSide : THREE.FrontSide });
  const mesh = new THREE.Mesh(g, mat); mesh.name = m.n;
  (parent[m.g] || scene).add(mesh);
}
// capsule marker (the rotation centre) and its line of sight to the grille
const dot = new THREE.Mesh(new THREE.SphereGeometry(3, 20, 14), new THREE.MeshBasicMaterial({ color: 0xf59e0b }));
ag.add(dot);
const sight = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -1, 0)]),
  new THREE.LineDashedMaterial({ color: 0xf59e0b, dashSize: 4, gapSize: 3 }));
scene.add(sight);

const VIEWS = {
  iso: [[-500, 780, 380], [80, 150, -80]],
  top: [[70, 330, 1000], [70, 150, -60]],
  side: [[980, 190, 40], [60, 170, -70]],
  close: [[-270, 340, 180], [20, 70, -30]],
};
function setView(k) { const [p, t] = VIEWS[k]; camera.position.set(...p); controls.target.set(...t); controls.update(); render(); }

const ax = document.getElementById("ax"), ad = document.getElementById("ad"), aa = document.getElementById("aa");
const fr = (v, d = 1) => v.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });
function apply() {
  const X = +ax.value, D = +ad.value, A = +aa.value, r = A * Math.PI / 180;
  zg.position.y = D; xg.position.x = X; ag.rotation.z = -r;
  document.getElementById("ox").textContent = X + " mm";
  document.getElementById("od").textContent = D + " mm";
  document.getElementById("oa").textContent = (A > 0 ? "+" : "") + A + "°";
  // closest point of the SM57 front face (radius 16 mm, 8 mm ahead of the capsule) to the grille cloth
  const gap = D - (8 * Math.cos(r) + 16 * Math.abs(Math.sin(r)));
  const pill = document.getElementById("clear");
  pill.className = "pill " + (gap >= 2 ? "ok" : "warn");
  pill.textContent = gap >= 2 ? "jeu au tissu " + fr(gap) + " mm" : "touche le tissu : reculer de " + fr(2 - gap) + " mm";
  document.getElementById("gcode").textContent = "/micro/position " + X.toFixed(1) + " " + D.toFixed(1) + " " + A.toFixed(1);
  const c = new THREE.Vector3(X, D, 0);
  sight.geometry.setFromPoints([c, new THREE.Vector3(X - D * Math.tan(r), 0, 0)]);
  sight.computeLineDistances();
  render();
}
for (const el of [ax, ad, aa]) el.addEventListener("input", apply);
for (const b of document.querySelectorAll(".presets button")) b.addEventListener("click", () => {
  const [x, d, a] = b.dataset.p.split(",").map(Number); ax.value = x; ad.value = d; aa.value = a; apply(); });
for (const k of Object.keys(VIEWS)) document.getElementById("v-" + k).addEventListener("click", () => setView(k));

function sceneColour() { return getComputedStyle(document.documentElement).getPropertyValue("--scene").trim() || "#dfe5ea"; }
function render() { renderer.setClearColor(sceneColour()); renderer.render(scene, camera); }
function resize() {
  const w = view.clientWidth, h = view.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / Math.max(h, 1); camera.updateProjectionMatrix(); render();
}
new ResizeObserver(resize).observe(view);
controls.addEventListener("change", render);
try { matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render); } catch (e) {}
new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
setView("iso"); apply(); resize();
</script>
"""
open(dst, "w").write(html)
print(dst, round(len(html) / 1e6, 2), "MB")
