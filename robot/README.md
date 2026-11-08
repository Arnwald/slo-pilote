# Robot de micro XZθ

Positionneur télécommandé d'un micro devant un HP de 12 pouces, posé sur un pied de micro et piloté par le contrôleur
de la tête : le robot n'a pas de contrôleur à lui, seulement trois servomoteurs pas à pas en boucle fermée sur le bus
CAN de la tête, qui leur fournit aussi le 24 V par le même câble. La régie commande l'ensemble en Ethernet (pas de Wi-Fi).

| Axe | Rôle | Course | Entraînement | Codeur (14 bits) |
|---|---|---|---|---|
| X | position radiale de la capsule (0 = centre du cache) | −15 à +135 mm | rail MGN12H, vis T8 pas 2 mm | 0,12 µm |
| Y | distance capsule – tissu | 10 à 160 mm | rail MGN12H, vis T8 pas 2 mm | 0,12 µm |
| A | angle du micro autour de la capsule | ±50° | arc denté m 1,5 (148 dents) et pignon 14 dents | 0,002° |

L'angle est un goniomètre : le chariot du micro roule sur un arc centré sur la capsule. Tourner le micro ne déplace
donc pas la capsule, et les trois réglages restent indépendants, comme on les décrit au studio
(« bord du cache, 2 cm du tissu, 30° »). Rien ne dépasse devant la capsule : l'arc est à 84 mm derrière elle.

## Deux moteurs au lieu de trois ?

Trois réglages indépendants demandent trois entrées indépendantes. Avec deux moteurs, il faut soit lier deux
réglages (par exemple l'angle à la position radiale, pour viser toujours le cache), ce qui interdit justement la
comparaison la plus courante (dans l'axe ou à 45° au même endroit), soit aiguiller un moteur vers l'un ou l'autre axe
par un embrayage, qui demande lui-même un actionneur et ajoute une cause de panne. Si l'on veut vraiment un moteur
de moins, le plus sensé est de régler l'angle à la main : retirer le pignon et bloquer le chariot de l'arc par une vis.

## Liaison avec la tête

- Câble M12 code A 5 points blindé (câble capteur CANopen), 3 m : 1 blindage, 2 +24 V, 3 0 V, 4 CAN_H, 5 CAN_L.
  Côté tête : HAT CAN du Raspberry Pi (Waveshare RS485 CAN HAT, MCP2515 et SN65HVD230, interface `can0` de Linux),
  fusible réarmable 2,5 A sur le 24 V (feuille Pilotage du schéma).
- Sur le robot, un petit bornier répartit le bus vers les trois servos, en chaîne ; 120 Ω au dernier servo.
- 500 kbit/s ; adresses 1 (X), 2 (Y), 3 (A).

## Pilotage par le logiciel de la tête

Commandes MKS SERVO42D utilisées, d'après la bibliothèque [mksservocan](https://github.com/thespaceegg/mksservocan)
et le manuel CAN V1.0.9 de Makerbase (unités exactes à confirmer au premier essai) :
position absolue `0xFE`, vitesse `0xF6`, activation `0xF3`, réglage et lancement de la prise d'origine `0x90` / `0x91`,
mise à zéro `0x92`, lecture du codeur `0x31`, débit et adresse `0x8A` / `0x8B`.

- Conversions : 16 384 points de codeur par tour ; X et Y 2 mm par tour, soit 8 192 points/mm ;
  A 360 × 14 / 148 = 34,05° par tour, soit 481 points par degré.
- Prise d'origine au démarrage, Y d'abord en s'éloignant du baffle, puis X, puis A ; fins de course sur les entrées des servos.
- Garde au tissu : la face avant du SM57 (rayon 16 mm, 8 mm devant la capsule) est à `D − 8 cos A − 16 |sin A|` du tissu.
  Le logiciel refuse toute cible à moins de 2 mm (paramètres par modèle de micro).
- Déplacement sûr : reculer d'abord (Y), puis tourner et décaler, puis avancer.
- Surveillance : relecture des codeurs après chaque mouvement ; un écart de suivi arrête tout (micro bloqué, obstacle).
- Courant : le module 24 V de la tête fournit 2,5 A pour le robot et le 5 V ; le logiciel déplace le robot après les pots.
- Au repos, servos désactivés 250 ms après chaque mouvement : silence et aucun champ pendant les prises.
  Les vis T8 pas 2 mm sont irréversibles ; l'arc tient par frottement et démultiplication.
- La position du micro peut faire partie d'un preset de la tête, et se commande aussi depuis la régie en Ethernet :
  page web servie par la tête, et OSC (`/micro/position 25 20 30`, `/micro/home`).

## Fichiers

- `robot_cad.py` : modèle paramétrique CadQuery (pièces imprimées, pièces achetées simplifiées, assemblage).
- `out/step/`, `out/stl/` : pièces imprimées ; `out/robot_micro_assemblage.step` : assemblage en position de repos.
- `collide.py` : contrôle d'interférence aux positions extrêmes (aucune collision) ; `masses.py` : masse et centre de masse.
- `build_viewer.py` : maquette 3D interactive (three.js).

## Pièces imprimées (PETG, sauf manchon en TPU 95A)

| Pièce | Qté | Remarque |
|---|---|---|
| arc_dente | 1 | 219 × 110 mm ; imprimer à plat, face dentée en haut ; 4 périmètres, 40 % de remplissage |
| plaque_angle | 1 | porte le servo d'angle (à 30° du micro), deux roues fixes et une roue excentrique |
| collier_micro, manchon_TPU | 1 + 1 | SM57 (Ø 32) ; un manchon par modèle de micro ; le TPU isole aussi le micro électriquement |
| pignon | 1 | m 1,5, 14 dents, alésage 5 mm (ou pignon acier du commerce) |
| plaque_X, plaque_Z | 1 + 1 | se vissent sur les chariots MGN12H |
| bloc_ecrou_X, bloc_ecrou_Z | 1 + 1 | écrou T8 anti-jeu |
| bloc_moteur_X/Z, palier_X/Z | 2 + 2 | bouts de poutre 2020 : servo et roulement 608ZZ |
| adaptateur_pied | 1 | insert laiton 3/8"-16 (ou 5/8"-27), placé au centre de masse |

## Pièces achetées (≈ 215 €, hors pied)

| Pièce | Qté | Prix indicatif |
|---|---|---|
| Profilé 2020, 260 et 250 mm | 2 | 8 € |
| Rail MGN12 250 mm + chariot MGN12H | 2 | 24 € |
| Vis T8 pas 2 mm, 300 mm + écrou POM anti-jeu | 2 | 16 € |
| Accouplement 5 × 8 mm, roulement 608ZZ | 2 + 2 | 6 € |
| Servo pas à pas MKS SERVO42D CAN avec moteur NEMA 17 de 40 mm | 3 | 105 € |
| Roues V mini (POM) avec entretoise excentrique | 3 | 6 € |
| Fins de course | 3 | 3 € |
| Câble M12 code A 5 points blindé, 3 m | 1 | 12 € |
| Bornier de répartition CAN, câbles, visserie, filament | — | 35 € |

Côté tête (dans sa nomenclature) : HAT CAN du Pi, embase M12 et fusible, module secteur 24 V, traversée Ethernet.
Masse : ≈ 2,8 kg avec le SM57, centre de masse au-dessus de l'adaptateur de pied.

## Montage et réglages

1. Assembler les deux modules linéaires (identiques), puis poser la poutre X sur la plaque Z, perpendiculaire.
2. Visser l'arc sur la plaque X ; régler l'excentrique de la roue extérieure jusqu'à supprimer tout jeu sans durcir le roulement.
3. Engrener le pignon : jeu minimal sans point dur sur toute la course.
4. Le pied doit être d'aplomb, l'axe Y perpendiculaire au baffle (équerre posée sur le tissu), l'axe X horizontal.
   La capsule est 17 cm au-dessus de l'adaptateur : il faut un pied court à embase lourde pour les HP du haut d'un 4×12 posé au sol.
5. Après la prise d'origine, définir le zéro acoustique depuis la tête : capsule centrée sur le cache (pointe laser ou gabarit),
   grille du micro au contact d'une cale de 2 mm, puis enregistrer X = 0, D = 10, A = 0.

## Vibrations et son

- Rien devant la capsule ; le corps du robot reste à plus de 70 mm derrière elle sous tous les angles.
- Manchon TPU entre le micro et le collier ; câble micro d'un côté, câble M12 de l'autre.
- À la première mise en service, balayage sinusoïdal 40-400 Hz au niveau de jeu, en écoutant la piste du micro :
  tout bourdonnement se traite par une rondelle feutre ou TPU sous la pièce concernée.

## Points à vérifier sur prototype

- Profil des arêtes en V imprimées contre les roues V mini (impression test d'un segment d'arc).
- Montage du servo d'angle et de sa carte sur la plaque d'angle (hauteur 78 mm, connecteurs côté extérieur).
- Rigidité de l'ensemble au bout de 15 cm de course Y.
- Hauteur minimale du pied choisi pour les HP du haut.
