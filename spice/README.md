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
- `ts.py` : Tube Screamer TS808 d'origine (9 V), retenu pour l'entrée, et l'ancienne version à potentiomètres numériques
  (±15 V, MCP41HV51), abandonnée.
- `hm2.py` : Boss HM-2 (MIJ) avec les valeurs du schéma Boss : préampli à transistors, Dist, écrêtage asymétrique,
  zone morte germanium, Color Mix à gyrateurs (84 Hz, 0,95 et 1,26 kHz : +20 à +22 dB à fond), sortie. Positions des
  potentiomètres en fraction de course, loi linéaire.
- `steps.py` : réglages pilotés de la TS et de la HM-2 et fermeture du gate. Chaque potentiomètre devient une échelle de
  résistances lue par un multiplexeur ADG406 (16 positions) ou ADG408 (8) ; les prises sont placées pour des paliers réguliers
  en dB, arrondies en E96 et resimulées avec 50 Ω de multiplexeur dans le curseur (`hm2.py` et `ts.py` ont les options
  `ron`, `r8`, `rgyr`, `kb`, `r49`, `rpots`, `rdrv`). Résultat dans `steps_result.txt`, prises dans `steps.json` (lu par le
  schéma).
- `preset_levels.py` : niveaux de la TS et de la HM-2 aux réglages du preset Line 6 de référence (TS Gain 0,10, Tone 0,90,
  Level 0,90 ; HM-2 Drive 0,55, Color Mix à fond, Level 0,60 ; chemin B à −30 dB), et rapport HM-2 / TS à l'entrée de
  l'ampli selon la note et l'attaque. Point de départ obtenu : VCA A à −4 dB, VCA B à −46 dB.
- `slo.py`, option `gate_buf=True` : la VCA du noise gate entre la sélection des masters (`piin`) et le condensateur de
  liaison du déphaseur, prise comme un tampon idéal de gain 1 (nœud `pidr`).

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
