# Schéma KiCad de la tête 100 W pilotable

Le dossier `slo-pilote/` s'ouvre avec KiCad 7 ou plus récent (KiCad 8 et 9 convertissent le format à l'ouverture).
Les symboles du projet sont dans `slo-pilote/slo.kicad_sym`, déclarée dans la table de bibliothèques du projet.

## Feuilles

| Feuille | Contenu | Repères |
|---|---|---|
| Alimentation | secteur, transfo TT-SLO100, redressement, B+1 à B+5 et cellules dédiées, polarisation individuelle, surélévation des filaments, terre | 1xx |
| Préampli | V1B, buffer V6A, diviseurs OD et Normal, V1A, V2A, liaison commutable, étage supplémentaire V6B, cold clipper V2B, V3B, V3A | 2xx |
| Tone stack et déphaseur | atténuateur de poussée, White CF (V4), tone stack ÷10, masters, mute, déphaseur V5 (attaqué par la VCA du gate), presence et depth | 3xx |
| Puissance | 4 × 6L6GC, mesure du courant, transfo de sortie, sélecteur d'impédance | 4xx |
| Boîtier d'entrée | buffer, Tube Screamer TS808 d'origine en 9 V, clone HM-2 (schéma Boss MIJ) en 9 V, insert, relais de chemin et de polarité | 5xx |
| Pilotage | alimentations ±15 V et 24 V, Raspberry Pi 4 B avec HAT CAN, carte d'interface (2 × MCP3208, 2 × MCP4822, 1-Wire, 3 × 74HC595 et nappe vers l'entrée), écran, encodeur, pédalier, MIDI, mesure du bias | 6xx |
| Commandes | 5 Motoron M2T256 pour les 10 pots ALPS (9 de l'ampli et le Blend), pistes capteur, LED des LDR et bobines des relais | 7xx |
| VCA et noise gate | mélange TS / HM-2 par deux VCA AS2164, tensions de commande, détection du gate sur la guitare, VCA du gate entre masters et déphaseur | 8xx |
| Commandes de l'entrée | drive et tone de la TS, dist et Color Mix de la HM-2, fermeture du gate : échelles de résistances 1 % lues par 5 ADG406 et un ADG408 | 9xx |

Chaque broche porte le nom de son nœud (étiquette locale, globale entre feuilles, ou symbole d'alimentation) ; les broches
alignées d'un même nœud sont reliées par un fil. On peut donc déplacer les composants dans KiCad sans rien débrancher,
puis redessiner les liaisons à la main au fil de l'implantation. Les noms de nœuds sont ceux de la simulation SPICE.

## Génération et vérification

```
python3 slo_sch.py slo-pilote     # écrit le projet (kgen.py : écriture des fichiers KiCad)
python3 check_sch.py slo-pilote   # contrôle de structure + comparaison au modèle SPICE (kicad-cli requis)
python3 bom_sch.py                # nomenclature exacte par valeur -> nomenclature_kicad.csv
```

Résultat du contrôle (`check_result.json`, `check_result.txt`) : 666 composants, 574 nœuds, aucune broche isolée, toutes les unités placées ;
les 168 éléments du modèle SPICE (`spice/slo.py`, variante `mod`, alimentation réelle, polarisation individuelle) sont
retrouvés avec les mêmes nœuds et la même valeur à la série normalisée près (8 écarts de 3 à 18 %, listés). Le modèle est appelé avec
`gate_buf=True` : la VCA du gate y est un tampon idéal de gain 1 entre `PI_IN` et `PI_DRV`. Écarts voulus :

- B+1 = 2 × 470 µF en série (235 µF, 200 µF simulés), B+2 = 2 × 220 µF en série (110 µF, 100 µF simulés), avec leurs
  résistances d'équilibrage ;
- Mid : un ALPS 10 k log à deux pistes avec 3,3 k en parallèle remplace le 2,5 k (aucun pot motorisé de cette valeur) ;
  chaque position reste à 1 dB d'une courbe du 2,5 k (`spice/mid_test.py`), et les extrémités sont identiques.

Éléments propres au modèle, sans composant : sources, tampon du gate, résistances et inductances internes des transfos et de la self,
charge. Le boîtier d'entrée n'entre pas dans cette comparaison : la TS et la HM-2 ont leurs propres modèles (`spice/ts.py`,
`spice/hm2.py`, valeurs du schéma Boss).

## Points à vérifier au montage

- Brochage du VTL5C1 (cellule 3-4, LED 1-2 dans ce schéma), des Motoron M2T256 et du HAT CAN (numérotation générique dans
  les symboles), de l'AS2164 (celui du SSM2164), des ADG406 et ADG408 (ceux des DG406 et DG408), du 78L09 (TO-92 : 1 sortie, 2 masse, 3 entrée) et des BC550C / BC560C (C-B-E).
- Raspberry Pi : SPI0 pour le HAT CAN (CE0, interruption GPIO25) et l'écran (CE1) ; SPI1 pour les MCP3208 (CE0, CE1) et les
  MCP4822 (CE2, puis GPIO27 en sélection logicielle), plus les 74HC595 de l'entrée (verrou sur GPIO14) ; I²C pour les Motoron (adresses 16 à 20) et les MCP23017 (0x20, 0x21) ;
  UART5 (GPIO12/13) pour le MIDI ; 1-Wire sur GPIO4 ; encodeur sur GPIO5, 6 et 26 ; pédalier sur GPIO22 et 23.
- Embase robot M12 code A 5 points, brochage CANopen : 1 blindage, 2 +24 V, 3 0 V, 4 CAN_H, 5 CAN_L.
- Prise de polarisation du TT-SLO100 : 60 V sur l'enroulement HT ; le réseau donne −43 à −66 V.
- Potentiomètres ALPS : broche 1 = extrémité anti-horaire, la résistance 1-curseur croît dans le sens horaire.
  Bass et depth sont montés entre 1 et le curseur, presence entre 3 et le curseur (le presence augmente en tournant).
- KiCad 7 ne fait pas l'ERC en ligne de commande : lancer l'ERC dans l'éditeur (drapeaux d'alimentation déjà posés).
