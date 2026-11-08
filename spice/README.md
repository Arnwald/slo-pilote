# Simulation SPICE de la tête 100 W pilotable

Prérequis : ngspice (≥ 42), Python 3 avec numpy. Chaque script se lance depuis ce dossier.

## Modèles

- `tubes.lib` : modèles de Koren (12AX7, 12AT7, 12AU7, 6L6GC) en sources comportementales ngspice.
- `slo.py` : générateur de netlist. `netlist("orig")` donne le SLO-100 d'origine, `netlist("mod")` la version
  pilotable. Options principales :
  - réglages : `gain_od`, `gain_n`, `treble`, `bass`, `mid`, `master`, `master_n`, `presence`, `depth` + `depth_net`
    (`orig`, `mod47`, `mod4n7`, `lin100k`, `scaled10`) ;
  - modes : `channel` (`od` / `normal`), `crunch`, `bright_n`, `clipper` (`39k` / `10k` / `4k4`, `clipper_mode`
    `dc` ou `ac`), `bypass` (`full` / `reduced`), `cc_v2a` (`20n` / `2n2`), `push`, `extra` ;
  - alimentation : `psu="ideal"` (509 V derrière 45 Ω) ou `psu="real"` (secondaire 2 × 538 V crête, 40 Ω et
    20 mH par demi-enroulement, deux diodes par branche) ;
  - commutations dynamiques : `sw={"cl2": ("on", 0.3), "mute": ("seq", "off", [(0.295, "on"), (0.5, "off")])}`,
    LDR modélisées par une conductance exponentielle (2,5 ms à l'allumage, 35 ms jusqu'à 100 kΩ à l'extinction),
    relais en 0,3 ms ;
  - charge : `load="r"` (4 Ω) ou `load="spk"` (baffle équivalent, résonance 90 Hz, Q = 4) ;
  - `drive_pi=True` : la source attaque directement l'entrée du déphaseur ;
  - `noise_req=True` : résistances de bruit équivalentes (2,5/gm) dans les grilles, pour les analyses de bruit.
- `sim.py` : lancement de ngspice (transitoire, AC, bruit) et analyse harmonique.
- `ts.py` : Tube Screamer TS808 (9 V) et version pilotable (±15 V, MCP41HV51).

## Campagne de tests

| Script | Contenu | Résultats |
|---|---|---|
| `run.py od`, `clean_test.py`, `pa_test.py`, `loop.py` | première vérification (canal OD, crunch, attaque du déphaseur, stabilité) | `res_od.json`, `res_pa.json` |
| `psu_test.py <cas>` | alimentation réelle : tensions, ondulation par nœud, ronflette au HP, affaissement à pleine puissance | `res_psu_*.json` |
| `modes_test.py <test>` | chaque mode commutable : réponse petit signal au HP, niveau et distorsion à 100 Hz et 1 kHz | `res_modes_*.json` |
| `depth_test.py` | réseaux depth et presence, de l'entrée du déphaseur au HP sur charge de HP | `res_depth.json` |
| `pops_test.py <cas>` | claquements de commutation, LDR et relais dynamiques, séquence de mute | `res_pops_*.json` |
| `noise_test.py` | bruit thermique et de grenaille, contributeurs principaux | `res_noise.json` |
| `ts_test.py` | Tube Screamer : réseau de gain, recalage du tone, grand signal | `res_ts.json` |
| `loop2.py` | gain de boucle de la contre-réaction avec le réseau depth, marges de stabilité | `res_loop2.json` |
| `summarize.py` | synthèse de tous les résultats | `summary.json` |

Limites : pas de bruit en 1/f des lampes, pas de microphonie, pas de couplage par le câblage ni par les filaments,
transfo de sortie idéalisé au-delà de ses fuites et capacités estimées. Les écarts entre l'original et la version
pilotable sont fiables ; les valeurs absolues sont à confirmer au prototype.
