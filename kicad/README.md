# Schéma KiCad de la tête 100 W pilotable

Le dossier `slo-pilote/` s'ouvre avec KiCad 7 ou plus récent (KiCad 8 et 9 convertissent le format à l'ouverture).
Les symboles du projet sont dans `slo-pilote/slo.kicad_sym`, déclarée dans la table de bibliothèques du projet.

## Feuilles

| Feuille | Contenu | Repères |
|---|---|---|
| Alimentation | secteur, transfo TT-SLO100, redressement, B+1 à B+5 et cellules dédiées, polarisation individuelle, surélévation des filaments, terre | 1xx |
| Préampli | V1B, buffer V6A, diviseurs OD et Normal, V1A, V2A, liaison commutable, étage supplémentaire V6B, cold clipper V2B, V3B, V3A | 2xx |
| Tone stack et déphaseur | atténuateur de poussée, White CF (V4), tone stack ÷10, masters, mute, déphaseur V5, presence et depth | 3xx |
| Puissance | 4 × 6L6GC, mesure du courant, transfo de sortie, sélecteur d'impédance | 4xx |
| Boîtier d'entrée | buffer, Tube Screamer à potentiomètres numériques, insert HM-2, noise gate à VCA THAT 2181 | 5xx |
| Pilotage | alimentations ±15 V et 24 V, NUCLEO-G474RE, Ethernet (W5500), bus CAN vers le robot, écran, encodeur, pédalier, MIDI, mesure du bias | 6xx |
| Commandes | moteurs et pistes capteur des 9 pots ALPS, PCA9685 et DRV8833, LED des LDR et bobines des relais | 7xx |

Chaque broche porte le nom de son nœud (étiquette locale, globale entre feuilles, ou symbole d'alimentation) ; les broches
alignées d'un même nœud sont reliées par un fil. On peut donc déplacer les composants dans KiCad sans rien débrancher,
puis redessiner les liaisons à la main au fil de l'implantation. Les noms de nœuds sont ceux de la simulation SPICE.

## Génération et vérification

```
python3 slo_sch.py slo-pilote     # écrit le projet (kgen.py : écriture des fichiers KiCad)
python3 check_sch.py slo-pilote   # contrôle de structure + comparaison au modèle SPICE (kicad-cli requis)
python3 bom_sch.py                # nomenclature exacte par valeur -> nomenclature_kicad.csv
```

Résultat du contrôle (`check_result.json`) : 410 composants, 411 nœuds, aucune broche isolée, toutes les unités placées ;
les 168 éléments du modèle SPICE (`spice/slo.py`, variante `mod`, alimentation réelle, polarisation individuelle) sont
retrouvés avec les mêmes nœuds et la même valeur à la série normalisée près (8 écarts de 3 à 18 %, listés). Écarts voulus :

- B+1 = 2 × 470 µF en série (235 µF, 200 µF simulés), B+2 = 2 × 220 µF en série (110 µF, 100 µF simulés), avec leurs
  résistances d'équilibrage ;
- Mid : un ALPS 10 k log à deux pistes avec 3,3 k en parallèle remplace le 2,5 k (aucun pot motorisé de cette valeur) ;
  chaque position reste à 1 dB d'une courbe du 2,5 k (`spice/mid_test.py`), et les extrémités sont identiques.

Éléments propres au modèle, sans composant : sources, résistances et inductances internes des transfos et de la self, charge.

## Points à vérifier au montage

- Brochage du VTL5C1 (cellule 3-4, LED 1-2 dans ce schéma) et numérotation des connecteurs des modules DRV8833, W5500 et CAN.
- Embase robot M12 code A 5 points, brochage CANopen : 1 blindage, 2 +24 V, 3 0 V, 4 CAN_H, 5 CAN_L.
- Prise de polarisation du TT-SLO100 : 60 V sur l'enroulement HT ; le réseau donne −43 à −66 V.
- Potentiomètres ALPS : broche 1 = extrémité anti-horaire, la résistance 1-curseur croît dans le sens horaire.
  Bass et depth sont montés entre 1 et le curseur, presence entre 3 et le curseur (le presence augmente en tournant).
- KiCad 7 ne fait pas l'ERC en ligne de commande : lancer l'ERC dans l'éditeur (drapeaux d'alimentation déjà posés).
