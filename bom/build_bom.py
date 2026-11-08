"""Detailed, sourced bill of materials (v2) for the pilotable 100 W head + optional cab.

Prices are entered as listed by the supplier (catalogue price, with the VAT rate it includes
and its currency), then brought to a common net-of-VAT EUR basis by formula. The summary sheet
converts to CHF, adds Swiss import VAT and per-supplier shipping/clearance estimates.
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

TT = "Tube-Town (DE)"
TAD = "Tube Amp Doctor (DE)"
THO = "Thomann (DE)"
AUD = "Audiophonics (FR)"
BUE = "Bürklin (DE)"
RS = "RS Components"
ED = "Electric Druid (UK)"
BAN = "Banzai Music (DE)"
THONK = "Thonk (UK)"
PIHUT = "The Pi Hut (UK)"
ROBO = "RobotShop (EU)"
ELEC = "Distributeur électronique (Mouser, Bürklin, Distrelec…)"
SHEET = "Découpe laser en ligne (ex. laserteile4you.de) ou atelier local"
LOCAL = "Achat local / divers"

R, E = "relevé nov. 2026", "estimation"

# (section, ref, designation, mfr_ref, supplier, link, qty, price, vat_incl, cur, basis, remark)
ITEMS = [
    ("Magnétiques", "T1", "Transfo d'alimentation 720 V PC 400 mA, 6,3 V 7,5 A + 3 A", "TT-Slo100 (tt-pwSLO100)", TT,
     "https://www.tubetown.net/ttstore/en/tt-slo100-soldano-style-powertransformer.html", 1, 139.00, 0.19, "EUR", R, ""),
    ("Magnétiques", "T2", "Transfo de sortie 2,2 kΩ PP, 4/8/16 Ω, 100 W", "TT-Slo100 (tt-otSLO100)", TT,
     "https://tubetown.net/ttstore/en/tt-slo100-soldano-slo-100-watt-output-transformer.html", 1, 119.00, 0.19, "EUR", R, ""),
    ("Magnétiques", "L1", "Self 10 H (alimentation des écrans)", "TT-CK10", TT,
     "https://tubetown.net/ttstore/en/tt-ck10-choke-10-h.html", 1, 36.20, 0.19, "EUR", R,
     "Courant nominal à vérifier sur la fiche (≥ 100 mA suffit : écrans + préampli)"),
    ("Magnétiques", "T3", "Transfo torique 2 × 15 V, 10 VA (±15 V du boîtier d'entrée)", "à choisir", ELEC, "", 1, 15.00, 0.19, "EUR", E,
     "Le 5 V et le robot passent par le module 24 V : ce transfo ne fournit plus que l'analogique"),

    ("Lampes et supports", "V1–V3, V5", "12AX7 / ECC83", "JJ ECC83S", TAD,
     "https://www.tubeampdoctor.com/en/jj-ecc83s/12ax7-jj-electronic", 4, 17.80, 0.19, "EUR", R, ""),
    ("Lampes et supports", "V4, V6", "12AU7 / ECC82", "JJ ECC82", TAD, "", 2, 17.80, 0.19, "EUR", E, "Prix supposé égal à l'ECC83S"),
    ("Lampes et supports", "V7–V10", "6L6GC, quartet appairé", "Engl 6L6GC Matched Quartett", THO,
     "https://www.thomann.pt/engl_6l6gc_matched_quartett.htm", 1, 149.00, 0.19, "EUR", R,
     "TVA portugaise affichée ; prix équivalent sur thomann.de à vérifier"),
    ("Lampes et supports", "", "Support noval châssis", "Belton VT9-ST-C", TT,
     "https://tubetown.net/ttstore/en/socket-noval-belton-vt9-st-c-chassis.html", 6, 1.90, 0.19, "EUR", R, ""),
    ("Lampes et supports", "", "Support octal châssis", "Belton VT8", TT,
     "https://tubetown.net/ttstore/en/socket-octal-belton-chassis-vt8.html", 4, 2.35, 0.19, "EUR", R, ""),
    ("Lampes et supports", "", "Maintien de lampe de puissance", "ressort / étrier", TT, "", 4, 2.00, 0.19, "EUR", E, ""),

    ("Alimentation HT", "C101, C102", "Électrolytique 470 µF 350 V (B+1, deux en série)", "F&T 470/350", TT, "", 2, 12.00, 0.19, "EUR", E, ""),
    ("Alimentation HT", "C103, C104", "Électrolytique 220 µF 350 V (B+2, deux en série)", "F&T 220/350 axial", TT,
     "https://www.tubetown.net/ttstore/en/f-t-220-f-350-volt-axial.html", 2, 6.65, 0.19, "EUR", R, ""),
    ("Alimentation HT", "C105–C110", "Électrolytique ≥ 550 V : 3 × 47 µF, 3 × 10 µF (B+3 à B+5, cellules dédiées)", "F&T", TT, "", 6, 6.00,
     0.19, "EUR", E, "Lampes froides, ces nœuds montent vers 535 V : 550 V minimum, ou 2 condensateurs 350 V en série"),
    ("Alimentation HT", "R124, R128, C113, C114", "Surélévation des filaments (+62 V, +99 V) : 2 × 330 k 3 W, 47 µF 100 V et 160 V",
     "", TT, "", 1, 5.00, 0.19, "EUR", E, "Le TT-SLO100 a des enroulements 6,3 V à point milieu : pas de point milieu artificiel"),
    ("Alimentation HT", "D101–D105", "Diodes UF4007 (HT) et 1N4007 (polarisation)", "", TT, "", 5, 0.15, 0.19, "EUR", E, ""),
    ("Alimentation HT", "", "Résistances 1–3 W (équilibrage, cellules de filtrage)", "", TT, "", 12, 0.50, 0.19, "EUR", E, ""),
    ("Alimentation HT", "", "Polarisation : 2 × 100 µF 160 V, 4 ajustables 25 k, 4 × 1 Ω 1 %", "", TT, "", 1, 9.00, 0.19, "EUR", E,
     "Prise 60 V du transfo d'alimentation ; réglage de −43 à −66 V"),

    ("Préampli et déphaseur", "", "Résistances couche métal 1/2 W 1 % (toute la tête)", "", TT, "", 79, 0.12, 0.19, "EUR", E,
     "Liste exacte par valeur : kicad/nomenclature_kicad.csv"),
    ("Préampli et déphaseur", "", "Résistances 1–3 W (cathodes de V3A et V6A, plaque de V6B, White CF, écrans)", "", TT, "", 8, 0.40,
     0.19, "EUR", E, ""),
    ("Préampli et déphaseur", "", "Condensateurs film 400–630 V", "", TT, "", 21, 1.00, 0.19, "EUR", E,
     "Dont les trois condensateurs du tone stack : son entrée est à 233 V continus (sortie de la White CF)"),
    ("Préampli et déphaseur", "", "Condensateurs mica / céramique 500 V", "", TT, "", 7, 0.40, 0.19, "EUR", E, ""),
    ("Préampli et déphaseur", "", "Condensateurs film 63 V (découplages de cathode, contre-réaction)", "", TT, "", 8, 0.50, 0.19, "EUR", E,
     "Film plutôt qu'électrolytique sous 2 V"),
    ("Préampli et déphaseur", "C304", "Électrolytique 220 µF 25 V (White CF)", "", TT, "", 1, 0.50, 0.19, "EUR", E, ""),
    ("Préampli et déphaseur", "K201, K202", "Relais signal 2RT 5 V (découplages de V1B et V2A, liaison 2,2 / 20 nF)", "Omron G6K-2", ELEC, "",
     2, 2.00, 0.19, "EUR", E, "Relais plutôt que LDR sur les découplages : les ~1 kΩ d'une LDR passante coûtaient 1,5 dB vers 300 Hz"),
    ("Préampli et déphaseur", "", "Plaque à turrets 300 × 60, 2 × 30 turrets", "TT EZ-Board tbez-005", TT,
     "https://tubetown.net/ttstore/en/components-10662/parts-for-amps/turrets-eyeletts-boards/tt-ez-boards", 2, 15.00, 0.19, "EUR", R,
     "Préampli et puissance"),
    ("Préampli et déphaseur", "", "Plaque à turrets 140 × 47, 2 × 15 turrets", "TT EZ-Board tbez-032-sw", TT,
     "https://tubetown.net/ttstore/en/components-10662/parts-for-amps/turrets-eyeletts-boards/tt-ez-boards", 1, 7.30, 0.19, "EUR", R,
     "Alimentation"),

    ("Commandes motorisées", "RV201–RV307, RV802", "Pot motorisé ALPS RK16812MG, 2 pistes (100 k log ×3, 100 k lin ×3, 20 k lin ×2, 10 k log ×1, 10 k lin ×1 pour le Blend)",
     "RK16812MG", AUD,
     "https://www.audiophonics.fr/en/potentiometres-potentiometre-alps/alps-rk16812mg-2-way-motorized-potentiometer-d-log-100k-p-5028.html",
     10, 15.90, 0.20, "EUR", R, "12,90 à 15,90 € chez Audiophonics selon valeur et stock ; 27,79 € chez Bürklin. "
     "Mid : 10 k log avec 3,3 k en parallèle (à 1 dB près d'un 2,5 k), la seconde piste sert de capteur"),
    ("Commandes motorisées", "", "Boutons aluminium, axe 6 mm", "", LOCAL, "", 11, 4.00, 0.19, "EUR", E, "10 pots et l'encodeur"),

    ("Commutation (LDR)", "", "Optocoupleur LED/LDR Xvive VTL5C1", "Xvive VTL5C1", ED,
     "https://electricdruid.net/product/xvive-vtl5c1/", 16, 4.95, 0.0, "GBP", R, "14 en service + 2 de réserve ; prix hors TVA ; aussi chez Tube-Town"),
    ("Commutation (LDR)", "U708–U710", "Pilote ULN2803 + résistances", "ULN2803A (DIP-18)", ELEC, "", 3, 1.00, 0.19, "EUR", E, ""),
    ("Commutation (LDR)", "U706, U707", "Extenseur 16 E/S I²C", "MCP23017-E/SP (DIP-28)", ELEC, "", 2, 1.50, 0.19, "EUR", E, ""),

    ("Pilotage", "A601", "Raspberry Pi 4 modèle B, 2 Go (contrôleur unique, Ethernet intégré)", "RPI4-MODBP-2GB", BUE,
     "https://www.buerklin.com/en/p/raspberry-pi/single-board-computer/rpi4-modbp-2gb/64S3341", 1, 58.83, 0.19, "EUR", R,
     "Wi-Fi et Bluetooth désactivés, système en lecture seule, refroidissement passif"),
    ("Pilotage", "", "Carte microSD d'endurance 16 Go", "", LOCAL, "", 1, 15.00, 0.19, "EUR", E, ""),
    ("Pilotage", "A602", "HAT CAN (MCP2515 + SN65HVD230) pour le robot de micro", "Waveshare RS485 CAN HAT", PIHUT,
     "https://thepihut.com/products/rs485-can-hat-for-raspberry-pi", 1, 12.60, 0.20, "GBP", R, "Prix soldé ; partie RS485 inutilisée"),
    ("Pilotage", "U701–U705", "Contrôleur double de moteurs CC, I²C (pots motorisés)", "Pololu Motoron M2T256, picots soudés", ROBO,
     "https://eu.robotshop.com/products/pololu-motoron-m2t256-dual-i2c-motor-controller-header-pins-soldered", 5, 21.68, 0.20, "EUR", R,
     "Prix soldé, 29,90 € au prix normal ; un 6e pour motoriser plus tard le drive et le tone de la TS"),
    ("Pilotage", "U609", "Régulateur abaisseur 5 V 3,2 A (alimentation du Pi)", "Pololu D36V28F5", ROBO, "", 1, 16.00, 0.20, "EUR", E, ""),
    ("Pilotage", "U610, U611", "CAN 8 voies 12 bits SPI (pistes capteur, bias, enveloppe du gate)", "MCP3208-CI/P (DIP-16)", ELEC, "", 2,
     4.50, 0.19, "EUR", E, ""),
    ("Pilotage", "U612, U613", "CNA double 12 bits SPI (VCA, seuil et fondu du gate)", "MCP4822-E/P (DIP-8)", ELEC, "", 2, 3.00, 0.19,
     "EUR", E, ""),
    ("Pilotage", "", "Écran 2,4\" SPI", "TFT ST7789", LOCAL, "", 1, 10.00, 0.19, "EUR", E, ""),
    ("Pilotage", "", "Encodeur rotatif à poussoir", "EC11", ELEC, "", 1, 1.50, 0.19, "EUR", E, ""),
    ("Pilotage", "", "Interface MIDI (6N138 + passifs)", "", ELEC, "", 1, 3.00, 0.19, "EUR", E, ""),
    ("Pilotage", "U601–U603", "LM7815, LM7915, module abaisseur 5 V, redresseur et filtrage", "", ELEC, "", 1, 12.00, 0.19, "EUR", E, ""),
    ("Pilotage", "U604, F601", "Module secteur 24 V 60 W à bornier (robot, moteurs, Pi)", "Mean Well IRM-60-24ST", ELEC, "", 1, 22.00, 0.19,
     "EUR", E, "Fusible T1 A en amont"),
    ("Pilotage", "U606", "Mesure du bias (ampli op quadruple 3,3 V)", "MCP6004-I/P (DIP-14)", ELEC, "", 1, 2.00, 0.19, "EUR", E, ""),
    ("Pilotage", "", "Carte d'interface traversante, connecteurs, nappes, câble de la barrette des moteurs", "", LOCAL, "", 1, 25.00, 0.19,
     "EUR", E, "Plaque à pastilles ou circuit imprimé traversant commandé nu"),
    ("Pilotage", "", "Boîtier de blindage", "", LOCAL, "", 1, 8.00, 0.19, "EUR", E, ""),

    ("Boîtier d'entrée et gate", "U802, U808", "Quadruple VCA (mélange TS / HM-2 ; noise gate)", "Alfa AS2164 (DIP-16)", THONK,
     "https://www.thonk.co.uk/shop/as2164/", 2, 5.75, 0.0, "GBP", R, "Prix hors TVA ; brochage SSM2164 / V2164"),
    ("Boîtier d'entrée et gate", "U503, U505–U507", "Ampli op double 4558 (TS808, clone HM-2)", "NJM4558D", ELEC, "", 4, 0.60, 0.19, "EUR",
     E, ""),
    ("Boîtier d'entrée et gate", "U501, U801, U803, U807", "Ampli op double faible bruit", "OPA2134PA", ELEC, "", 4, 4.00, 0.19, "EUR", E,
     ""),
    ("Boîtier d'entrée et gate", "U804–U806", "Commandes et détection du gate", "2 × TL074CN, LM393N", ELEC, "", 1, 2.00, 0.19, "EUR", E,
     ""),
    ("Boîtier d'entrée et gate", "Q501, Q502, D506, D507", "Transistors et diodes germanium de la HM-2", "BC550C, BC560C, 2 × 1N34A", ELEC,
     "", 1, 2.50, 0.19, "EUR", E, "Remplacent les 2SC2240, 2SA970 et 1S188FM d'origine"),
    ("Boîtier d'entrée et gate", "RV501–RV505, RV801", "Ajustables multitours (drive, tone, dist, Color Mix ×2, release)",
     "Bourns 3296W", ELEC, "", 6, 2.00, 0.19, "EUR", E, ""),
    ("Boîtier d'entrée et gate", "U502, U504, U809", "Régulateurs 78L09 et sonde de température", "2 × 78L09, DS18B20", ELEC, "", 1, 4.00,
     0.19, "EUR", E, ""),
    ("Boîtier d'entrée et gate", "K501–K503", "Relais signal (TS, insert, polarité du chemin B)", "Omron G6K-2", ELEC, "", 3, 2.00, 0.19,
     "EUR", E, ""),
    ("Boîtier d'entrée et gate", "", "Passifs (film, électrolytiques, résistances 1 %) et diodes", "", ELEC, "", 1, 15.00, 0.19, "EUR", E,
     ""),

    ("Connectique et façade", "", "Jack d'entrée", "Neutrik NMJ4HC-S", TT,
     "https://tubetown.net/ttstore/en/components-10662/jacks-plugs/jacks-6-3-mm", 1, 1.65, 0.19, "EUR", R, ""),
    ("Connectique et façade", "", "Jacks HP et insert", "Cliff 1160", TT,
     "https://tubetown.net/ttstore/en/components-10662/jacks-plugs/jacks-6-3-mm", 4, 1.20, 0.19, "EUR", R, ""),
    ("Connectique et façade", "", "Jack pédalier stéréo", "Cliff 1220", TT,
     "https://tubetown.net/ttstore/en/components-10662/jacks-plugs/jacks-6-3-mm", 1, 1.60, 0.19, "EUR", R, ""),
    ("Connectique et façade", "", "Sélecteur d'impédance 3 positions", "", TT, "", 1, 10.00, 0.19, "EUR", E, ""),
    ("Connectique et façade", "", "Embase IEC C14 avec porte-fusible", "Schurter", TT,
     "https://tubetown.net/ttstore/en/tubetown.html?page=21", 1, 4.20, 0.19, "EUR", R, ""),
    ("Connectique et façade", "", "Porte-fusible HT + jeu de fusibles", "", TT, "", 1, 5.00, 0.19, "EUR", E, ""),
    ("Connectique et façade", "", "Interrupteurs Power et Standby 250 V", "", TT, "", 2, 4.00, 0.19, "EUR", E, ""),
    ("Connectique et façade", "", "Embases MIDI DIN 5 format D", "", ELEC, "", 2, 4.00, 0.19, "EUR", E, ""),
    ("Connectique et façade", "", "Traversée RJ45 format D (Ethernet)", "Neutrik NE8FDP", THO, "", 1, 9.00, 0.19, "EUR", E, ""),
    ("Connectique et façade", "J605, F602", "Embase M12 code A 5 points (robot) et fusible réarmable 2,5 A", "", ELEC, "", 1, 12.00, 0.19,
     "EUR", E, "Brochage CANopen : CAN et 24 V sur un seul câble"),
    ("Connectique et façade", "", "Traversée USB format D", "Neutrik NAUSB-W", BUE,
     "https://buerklin.com/en/p/neutrik/adapter-for-d-sub-connectors-usb-connectors-pc-connectors/nausb-w/73F1084", 1, 7.71, 0.19, "EUR", R, ""),

    ("Mécanique", "", "Châssis acier 1,5 mm, découpe + 6 plis", "chassis_developpe.dxf", SHEET, "", 1, 95.00, 0.19, "EUR", E,
     "Faire un devis en ligne avec le DXF"),
    ("Mécanique", "", "Capot alu 2 mm en U + fond", "capot_developpe.dxf, fond.dxf", SHEET, "", 1, 110.00, 0.19, "EUR", E,
     "Variante bois + tolex, comme le Randall Satan : ~50 €"),
    ("Mécanique", "", "Thermolaquage noir (châssis + capot)", "", LOCAL, "", 1, 60.00, 0.081, "CHF", E, "Atelier local"),
    ("Mécanique", "", "Tôle perforée noire, 2 panneaux", "grille_x2.dxf", LOCAL, "", 1, 25.00, 0.19, "EUR", E, ""),
    ("Mécanique", "", "Entretoises, vis, écrous à sertir, rivets", "", TT, "", 1, 20.00, 0.19, "EUR", E, ""),
    ("Mécanique", "", "Poignée + pieds + équerres", "", LOCAL, "", 1, 25.00, 0.19, "EUR", E, ""),

    ("Câblage et consommables", "", "Fil isolé, câble blindé, gaines, soudure", "", TT, "", 1, 35.00, 0.19, "EUR", E, ""),

    ("Baffle 4×12 (hors tête)", "", "HP 12\" Eminence Karnivore, 60 W, 16 Ω (câblage série-parallèle : 16 Ω)", "The Karnivore-16", THO,
     "https://www.thomann.fr/eminence_the_karnivore_16.htm", 4, 198.00, 0.20, "EUR", R,
     "TVA française affichée. Variante mixte : 2 Karnivore + 2 Celestion Vintage 30 à 138 € (thomann.fr)"),
    ("Baffle 4×12 (hors tête)", "", "Multiplis bouleau 18 mm", "", LOCAL, "", 1, 90.00, 0.081, "CHF", E, ""),
    ("Baffle 4×12 (hors tête)", "", "Habillage, tissu, coins, poignées, plaque jack", "", LOCAL, "", 1, 70.00, 0.19, "EUR", E, ""),
]

SHIPPING = [  # supplier, CHF estimate for shipping + Swiss clearance fee
    (TT, 35), (TAD, 20), (THO, 15), (AUD, 20), (ED, 15), (ELEC, 20), (BUE, 15), (THONK, 15), (PIHUT, 15), (ROBO, 20),
]

FONT = "Arial"
BLUE = Font(name=FONT, color="0000FF", size=10)
BLACK = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
HEAD = Font(name=FONT, size=10, bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="1F2937")
SFILL = PatternFill("solid", fgColor="E5E7EB")
YFILL = PatternFill("solid", fgColor="FFFF00")
THIN = Border(bottom=Side(style="thin", color="D1D5DB"))
NUM = '#,##0.00;(#,##0.00);"-"'
NUM0 = '#,##0;(#,##0);"-"'
PCT = '0.0%'
LINK = Font(name=FONT, size=10, color="1D4ED8", underline="single")

wb = Workbook()
sy = wb.active
sy.title = "Synthèse"
ws = wb.create_sheet("Nomenclature")

# ---- assumptions (Synthèse) ----
sy.column_dimensions["A"].width = 44
sy.column_dimensions["B"].width = 16
sy.column_dimensions["C"].width = 70
sy["A1"] = "Tête 100 W pilotable : coût détaillé"
sy["A1"].font = Font(name=FONT, size=14, bold=True)
for c, v in (("A3", "Hypothèses"), ("B3", "Valeur"), ("C3", "Note")):
    sy[c] = v
    sy[c].font, sy[c].fill = HEAD, HFILL
assump = [
    ("Cours CHF pour 1 €", 0.94, "À ajuster au cours du jour"),
    ("Cours € pour 1 £", 1.17, "À ajuster au cours du jour"),
    ("TVA suisse à l'importation", 0.081, "Taux normal 2026"),
    ("Marge pour imprévus", 0.05, "Pièces oubliées, casse"),
]
for i, (a, v, n) in enumerate(assump, start=4):
    sy.cell(row=i, column=1, value=a).font = BLACK
    c = sy.cell(row=i, column=2, value=v)
    c.font, c.fill = BLUE, YFILL
    c.number_format = PCT if v < 0.5 else "0.00"
    sy.cell(row=i, column=3, value=n).font = BLACK
EUR_CHF, GBP_EUR, VAT_CH, CONT = "Synthèse!$B$4", "Synthèse!$B$5", "Synthèse!$B$6", "Synthèse!$B$7"

# ---- nomenclature ----
headers = ["Section", "Repère", "Désignation", "Référence", "Fournisseur", "Lien", "Qté",
           "Prix catalogue", "TVA incluse", "Devise", "PU net (€)", "Total net (€)", "Base", "Remarque"]
widths = [22, 10, 46, 26, 24, 8, 6, 12, 10, 8, 11, 12, 16, 46]
for i, (h, w) in enumerate(zip(headers, widths), start=1):
    c = ws.cell(row=1, column=i, value=h)
    c.font, c.fill = HEAD, HFILL
    c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 30
r = 2
for sec, ref, des, mfr, sup, link, q, p, vat, cur, basis, rem in ITEMS:
    vals = [sec, ref, des, mfr, sup, "lien" if link else "", q, p, vat, cur, None, None, basis, rem]
    for i, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=i, value=v)
        c.font, c.border = BLACK, THIN
        c.alignment = Alignment(vertical="top", wrap_text=i in (3, 4, 5, 14))
    for col in (7, 8, 9):
        ws.cell(row=r, column=col).font = BLUE
    ws.cell(row=r, column=8).number_format = NUM
    ws.cell(row=r, column=9).number_format = '0%'
    # net EUR = price / (1+vat) converted from the row currency
    ws.cell(row=r, column=11, value=(
        f'=H{r}/(1+I{r})*IF(J{r}="GBP",{GBP_EUR},IF(J{r}="CHF",1/{EUR_CHF},1))')).number_format = NUM
    ws.cell(row=r, column=12, value=f"=G{r}*K{r}").number_format = NUM
    if link:
        ws.cell(row=r, column=6).hyperlink = link
        ws.cell(row=r, column=6).font = LINK
    r += 1
last = r - 1
ws.freeze_panes = "D2"
ws.auto_filter.ref = f"A1:N{last}"
ws.cell(row=last + 2, column=1, value="Légende").font = BOLD
ws.cell(row=last + 3, column=1, value="Bleu : quantités, prix et taux à ajuster. PU net = prix catalogue sans la TVA du pays du vendeur, en euros.").font = BLACK
ws.cell(row=last + 4, column=1, value="Base « relevé » : prix lu sur la page du lien en novembre 2026 ; « estimation » : à confirmer.").font = BLACK

# ---- summary ----
sy["A9"], sy["B9"], sy["C9"] = "Section (tête)", "Net (€)", "Part"
for c in ("A9", "B9", "C9"):
    sy[c].font, sy[c].fill = HEAD, HFILL
secs = []
for it in ITEMS:
    if it[0] not in secs and not it[0].startswith("Baffle"):
        secs.append(it[0])
row = 10
for s in secs:
    sy.cell(row=row, column=1, value=s).font = BLACK
    c = sy.cell(row=row, column=2, value=f'=SUMIFS(Nomenclature!$L$2:$L${last},Nomenclature!$A$2:$A${last},A{row})')
    c.number_format, c.font = NUM0, BLACK
    row += 1
s0, s1 = 10, row - 1
for rr in range(s0, s1 + 1):
    c = sy.cell(row=rr, column=3, value=f"=B{rr}/$B${row}")
    c.number_format, c.font = PCT, BLACK
sy.cell(row=row, column=1, value="Tête : composants, net").font = BOLD
c = sy.cell(row=row, column=2, value=f"=SUM(B{s0}:B{s1})")
c.number_format, c.font = NUM0, BOLD
net_row = row
row += 2
lines = [
    ("En CHF", f"=B{net_row}*{EUR_CHF}"),
    ("+ TVA suisse à l'importation", f"=B{row}*{VAT_CH}"),
    ("+ Port et dédouanement (tableau ci-dessous)", None),
    ("+ Imprévus", None),
]
chf_row = row
sy.cell(row=row, column=1, value="Tête : composants, en CHF").font = BLACK
c = sy.cell(row=row, column=2, value=f"=B{net_row}*{EUR_CHF}")
c.number_format, c.font = NUM0, BLACK
row += 1
sy.cell(row=row, column=1, value="+ TVA suisse à l'importation, achats à l'étranger (CHF)").font = BLACK
c = sy.cell(row=row, column=2, value=f'=SUMIFS(Nomenclature!$L$2:$L${last},Nomenclature!$J$2:$J${last},"<>CHF",Nomenclature!$A$2:$A${last},"<>Baffle 4×12 (hors tête)")*{EUR_CHF}*{VAT_CH}')
c.number_format, c.font = NUM0, BLACK
vat_row = row
row += 1
ship_ref_row = row
sy.cell(row=row, column=1, value="+ Port et dédouanement (CHF)").font = BLACK
row += 1
sy.cell(row=row, column=1, value="+ Imprévus (CHF)").font = BLACK
cont_row = row
row += 1
sy.cell(row=row, column=1, value="Tête : total estimé (CHF)").font = BOLD
total_row = row
row += 2
sy.cell(row=row, column=1, value="Baffle 4×12, net (€)").font = BLACK
c = sy.cell(row=row, column=2, value=f'=SUMIFS(Nomenclature!$L$2:$L${last},Nomenclature!$A$2:$A${last},"Baffle 4×12 (hors tête)")')
c.number_format, c.font = NUM0, BLACK
cab_net = row
row += 1
sy.cell(row=row, column=1, value="Baffle 4×12, total estimé (CHF)").font = BOLD
c = sy.cell(row=row, column=2, value=f'=B{cab_net}*{EUR_CHF}+SUMIFS(Nomenclature!$L$2:$L${last},Nomenclature!$J$2:$J${last},"<>CHF",Nomenclature!$A$2:$A${last},"Baffle 4×12 (hors tête)")*{EUR_CHF}*{VAT_CH}')
c.number_format, c.font = NUM0, BOLD
cab_total = row
row += 1
sy.cell(row=row, column=1, value="Tête + baffle (CHF)").font = BOLD
c = sy.cell(row=row, column=2, value=f"=B{total_row}+B{cab_total}")
c.number_format, c.font = NUM0, BOLD
c.fill = SFILL
row += 2
sy.cell(row=row, column=1, value="Port et dédouanement par fournisseur").font = HEAD
sy.cell(row=row, column=1).fill = HFILL
sy.cell(row=row, column=2, value="CHF").font = HEAD
sy.cell(row=row, column=2).fill = HFILL
sy.cell(row=row, column=3, value="Note").font = HEAD
sy.cell(row=row, column=3).fill = HFILL
row += 1
sh0 = row
for sup, chf in SHIPPING:
    sy.cell(row=row, column=1, value=sup).font = BLACK
    c = sy.cell(row=row, column=2, value=chf)
    c.font, c.number_format = BLUE, NUM0
    sy.cell(row=row, column=3, value="estimation : envoi + frais de dédouanement du transporteur").font = BLACK
    row += 1
sh1 = row - 1
c = sy.cell(row=ship_ref_row, column=2, value=f"=SUM(B{sh0}:B{sh1})")
c.number_format, c.font = NUM0, BLACK
c = sy.cell(row=cont_row, column=2, value=f"=(B{chf_row}+B{vat_row})*{CONT}")
c.number_format, c.font = NUM0, BLACK
c = sy.cell(row=total_row, column=2, value=f"=B{chf_row}+B{vat_row}+B{ship_ref_row}+B{cont_row}")
c.number_format, c.font = NUM0, BOLD
c.fill = SFILL
row += 1
sy.cell(row=row, column=1, value="Les vendeurs de l'UE facturent sans leur TVA à l'export ; la TVA suisse (8,1 %) s'applique à l'arrivée.").font = Font(name=FONT, size=9, italic=True)
sy.cell(row=row + 1, column=1, value="Non compris : robot de micro, micro, outillage (variac, lampe série pour la première mise sous tension).").font = Font(name=FONT, size=9, italic=True)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nomenclature_tete_100W.xlsx")
wb.save(out)
print(out, last)
