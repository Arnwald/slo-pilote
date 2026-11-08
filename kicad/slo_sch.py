"""Schematic of the pilotable SLO-family head, generated for KiCad 7+.

python3 slo_sch.py <outdir>
Net names follow the SPICE model (spice/slo.py, variant "mod") through NETMAP in check_sch.py.
"""
import sys

import kgen
from kgen import Part, Project, Sheet, ic_symbol, opamp_units, Sym, Unit, Pin, rect, poly, text

P = Project("slo-pilote", "Tête 100 W pilotable, famille SLO-100", rev="0.1", date="2026-11-07",
            company="Projet open source (CERN-OHL-S)",
            comments=["Schéma de référence : SLO-100 annoté par Rob Robinette (v1.6f), redessiné et modifié",
                      "Haute tension mortelle : voir la procédure de mise en route du dossier",
                      "Simulation : spice/slo.py (variante mod) ; vérification : check_sch.py",
                      ""])
for k, v in kgen.build_library().items():
    P.symbol(v)
for n, down in P.POWER.items():
    P.symbol(kgen.power_symbol(n, down))

# ---- integrated circuits and modules ------------------------------------------------------------
P.symbol(ic_symbol("MCP41HV51", "U",
                   [(1, "VL", "power_in"), (2, "SCK", "input"), (3, "CS", "input"), (4, "SDI", "input"),
                    (5, "SDO", "output"), (6, "WLAT", "input"), (7, "SHDN", "input")],
                   [(14, "V+", "power_in"), (13, "P0A"), (12, "P0W"), (11, "P0B"), (10, "V-", "power_in"),
                    (9, "NC"), (8, "DGND", "power_in")], 17.78, "Potentiometre numerique 256 pas, 36 V, TSSOP-14"))
P.symbol(ic_symbol("THAT2181", "U", [(1, "IN", "input"), (2, "EC+", "input"), (3, "EC-", "input"), (4, "SYM", "input")],
                   [(7, "V+", "power_in"), (8, "OUT", "output"), (6, "GND", "power_in"), (5, "V-", "power_in")], 12.7,
                   "VCA Blackmer, SO-8 ou SIP-8 (meme brochage)"))
P.symbol(ic_symbol("MCP4822", "U", [(1, "VDD", "power_in"), (2, "CS", "input"), (3, "SCK", "input"), (4, "SDI", "input")],
                   [(8, "VOUTA", "output"), (6, "VOUTB", "output"), (5, "LDAC", "input"), (7, "VSS", "power_in")], 12.7,
                   "CNA double 12 bits SPI"))
P.symbol(ic_symbol("PCA9685", "U",
                   [(28, "VDD", "power_in"), (26, "SCL", "input"), (27, "SDA", "bidirectional"), (23, "OE", "input"),
                    (25, "EXTCLK", "input"), (1, "A0", "input"), (2, "A1", "input"), (3, "A2", "input"), (4, "A3", "input"),
                    (5, "A4", "input"), (24, "A5", "input"), (14, "VSS", "power_in")],
                   [(6, "LED0", "output"), (7, "LED1", "output"), (8, "LED2", "output"), (9, "LED3", "output"),
                    (10, "LED4", "output"), (11, "LED5", "output"), (12, "LED6", "output"), (13, "LED7", "output"),
                    (15, "LED8", "output"), (16, "LED9", "output"), (17, "LED10", "output"), (18, "LED11", "output"),
                    (19, "LED12", "output"), (20, "LED13", "output"), (21, "LED14", "output"), (22, "LED15", "output")],
                   20.32, "PWM 16 voies I2C, TSSOP-28"))
P.symbol(ic_symbol("MCP23017", "U",
                   [(9, "VDD", "power_in"), (12, "SCL", "input"), (13, "SDA", "bidirectional"), (15, "A0", "input"),
                    (16, "A1", "input"), (17, "A2", "input"), (18, "RESET", "input"), (20, "INTA", "output"),
                    (19, "INTB", "output"), (11, "NC"), (14, "NC"), (10, "VSS", "power_in")],
                   [(21, "GPA0"), (22, "GPA1"), (23, "GPA2"), (24, "GPA3"), (25, "GPA4"), (26, "GPA5"), (27, "GPA6"),
                    (28, "GPA7"), (1, "GPB0"), (2, "GPB1"), (3, "GPB2"), (4, "GPB3"), (5, "GPB4"), (6, "GPB5"),
                    (7, "GPB6"), (8, "GPB7")], 20.32, "Extenseur 16 E/S I2C, SOIC-28"))
P.symbol(ic_symbol("ULN2803A", "U", [(i, f"I{i}", "input") for i in range(1, 9)] + [(9, "GND", "power_in")],
                   [(19 - i, f"O{i}", "open_collector") for i in range(1, 9)] + [(10, "COM", "passive")], 15.24,
                   "8 Darlington, diodes de roue libre vers COM"))
P.symbol(ic_symbol("DRV8833_MOD", "U",
                   [(1, "VM", "power_in"), (2, "GND", "power_in"), (3, "AIN1", "input"), (4, "AIN2", "input"),
                    (5, "BIN1", "input"), (6, "BIN2", "input"), (7, "nSLEEP", "input"), (8, "nFAULT", "open_collector")],
                   [(9, "AOUT1", "output"), (10, "AOUT2", "output"), (11, "BOUT1", "output"), (12, "BOUT2", "output")],
                   17.78, "Module double pont en H DRV8833 ; numerotation du connecteur a adapter au module"))
P.symbol(ic_symbol("6N138", "U", [(2, "A"), (3, "K"), (1, "NC"), (4, "NC")],
                   [(8, "VCC", "power_in"), (7, "VB"), (6, "VO", "open_collector"), (5, "GND", "power_in")], 12.7,
                   "Optocoupleur MIDI"))
P.symbol(ic_symbol("78XX", "U", [(1, "IN", "power_in")], [(3, "OUT", "power_out"), (2, "GND", "power_in")], 10.16, "Regulateur positif"))
P.symbol(ic_symbol("79XX", "U", [(2, "IN", "power_in")], [(3, "OUT", "power_out"), (1, "GND", "power_in")], 10.16, "Regulateur negatif"))
P.symbol(ic_symbol("BUCK_MOD", "U", [(1, "IN+", "power_in"), (2, "IN-", "power_in")],
                   [(3, "OUT+", "power_out"), (4, "OUT-", "power_in")], 12.7, "Module abaisseur LM2596, reglé a 5,0 V"))
P.symbol(ic_symbol("SMPS_MOD", "PS", [("L", "AC/L", "power_in"), ("N", "AC/N", "power_in")],
                   [("V+", "+V", "power_out"), ("V-", "-V", "power_in")], 15.24,
                   "Module secteur encapsule 24 V 60 W a bornier (type Mean Well IRM-60-24ST)"))
P.symbol(ic_symbol("W5500_MOD", "U", [(1, "3V3", "power_in"), (2, "GND", "power_in"), (3, "RSTn", "input"), (4, "INTn", "output")],
                   [(5, "SCLK", "input"), (6, "MOSI", "input"), (7, "MISO", "output"), (8, "SCSn", "input")], 15.24,
                   "Module Ethernet W5500 (pile TCP/IP cablee, SPI) avec RJ45 et transformateurs ; brochage du module a verifier"))
P.symbol(ic_symbol("CAN_MOD", "U", [(1, "3V3", "power_in"), (2, "GND", "power_in"), (3, "CTX", "input"), (4, "CRX", "output")],
                   [(5, "CANH", "bidirectional"), (6, "CANL", "bidirectional")], 15.24,
                   "Module emetteur-recepteur CAN 3,3 V (SN65HVD230), terminaison 120 ohms sur le module"))
P.symbol(ic_symbol("M12_5", "J", [(1, "SH"), (2, "V+"), (3, "V-"), (4, "CAN_H"), (5, "CAN_L")], [], 10.16,
                   "Embase M12 code A 5 points, brochage CANopen (CiA 303-1)"))
NUC_L = ["E5V", "3V3", "GND", "SCL", "SDA", "SCK", "MOSI", "MISO", "CS_DRIVE", "CS_TONE", "CS_LEVEL", "CS_DAC",
         "CS_TFT", "TFT_DC", "TFT_RST", "MIDI_RX", "MIDI_TX", "ENC_A", "ENC_B", "ENC_SW", "FS1", "FS2",
         "MOT_EN", "MOT_FAULT", "PCA_OE", "ETH_SCK", "ETH_MOSI", "ETH_MISO", "ETH_CS", "ETH_INT", "ETH_RST",
         "CAN_TX", "CAN_RX"]
NUC_R = [f"SENSE{i}" for i in range(1, 10)] + [f"BIAS{i}" for i in range(1, 5)] + ["ENV"]
P.symbol(ic_symbol("NUCLEO_G474RE", "A",
                   [(n, n, "power_in" if n in ("E5V", "GND") else ("power_out" if n == "3V3" else "bidirectional")) for n in NUC_L],
                   [(n, n, "input") for n in NUC_R], 25.4,
                   "Carte NUCLEO-G474RE ; broches nommees par fonction, affectation aux ports dans STM32CubeMX"))
P.symbol(ic_symbol("TFT_ST7789", "J", [(1, "GND"), (2, "VCC"), (3, "SCL"), (4, "SDA"), (5, "RES"), (6, "DC"), (7, "CS"), (8, "BLK")],
                   [], 12.7, "Ecran SPI 2,4 pouces 240 x 320"))
P.symbol(ic_symbol("EC11", "SW", [("A", "A"), ("C", "C"), ("B", "B")], [("S1", "S1"), ("S2", "S2")], 10.16,
                   "Encodeur rotatif a poussoir"))
P.symbol(Sym("OPA2134", "U", opamp_units((3, 2, 1), (5, 6, 7)), pin_names_hidden=False, ref_at=(1.27, 6.35), val_at=(1.27, -6.35),
             desc="Double ampli op JFET faible bruit"))
P.symbol(Sym("MCP6002", "U", opamp_units((3, 2, 1), (5, 6, 7)), pin_names_hidden=False, ref_at=(1.27, 6.35), val_at=(1.27, -6.35),
             desc="Double ampli op rail-a-rail 3,3 V"))
q4 = opamp_units((3, 2, 1), (5, 6, 7), (4, 11))
q4c = opamp_units((10, 9, 8), (12, 13, 14), (4, 11))
P.symbol(Sym("MCP6004", "U", [q4[0], q4[1], q4c[0], q4c[1], q4[2]], pin_names_hidden=False, ref_at=(1.27, 6.35),
             val_at=(1.27, -6.35), desc="Quadruple ampli op rail-a-rail 3,3 V"))


def two(sh, ref, sym, val, x, y, n1, n2, rot=0, **fields):
    return sh.add(Part(ref, sym, val, (x, y), rotation=rot, nets={1: n1, 2: n2}, fields=fields))


def ldr(sh, ref, x, y, a, b):
    return sh.add(Part(ref, "VTL5C1", "VTL5C1", (x, y), unit=1, nets={3: a, 4: b}))


def tube(sh, ref, typ, unit, x, y, p, g, k):
    pins = {1: (1, 2, 3), 2: (6, 7, 8)}[unit]
    return sh.add(Part(ref, typ, {"12AX7": "ECC83", "12AU7": "ECC82"}[typ], (x, y), unit=unit,
                       nets={pins[0]: p, pins[1]: g, pins[2]: k}))


def heater(sh, ref, typ, x, y, a, b):
    if typ == "6L6GC":
        return sh.add(Part(ref, typ, typ, (x, y), unit=2, nets={2: a, 7: b}))
    return sh.add(Part(ref, typ, {"12AX7": "ECC83", "12AU7": "ECC82"}[typ], (x, y), unit=3, nets={4: a, 5: a, 9: b}))


# grid helper: column/row cells inside a block
def cell(x0, y0, c, r, w=22.86, h=27.94):
    return x0 + c * w, y0 + r * h


# =================================================================================================
# 1. Alimentation
# =================================================================================================
S1 = P.sheet(Sheet("Alimentation", "alimentation.kicad_sch", "A2", "Alimentation HT, polarisation, filaments"))
S1.frame(10, 10, 140, 120, "Secteur et transformateur")
S1.add(Part("J101", "IEC", "IEC C14 + fusible", (25, 50), nets={"L": "MAINS_L", "N": "MAINS_N", "PE": "PE"}))
two(S1, "F101", "FUSE", "T3,15 A", 50, 47.46, "MAINS_L", "MAINS_LF")
S1.add(Part("SW101", "SW_DPST", "Power", (70, 47.46), unit=1, nets={1: "MAINS_LF", 2: "L_SW"}))
S1.add(Part("SW101", "SW_DPST", "Power", (70, 62.7), unit=2, nets={3: "MAINS_N", 4: "N_SW"}))
S1.add(Part("T101", "PT_SLO", "TT-SLO100", (110, 65), nets={1: "N_SW", 2: "L_SW", 3: "HT_A", 4: "GND", 5: "HT_B",
                                                            6: "BIAS_AC", 7: "HEAT_A1", 8: "HEAT_REF_A", 9: "HEAT_A2",
                                                            10: "HEAT_B1", 11: "HEAT_REF_B", 12: "HEAT_B2"}))
two(S1, "E101", "BOLT", "Terre secteur", 25, 90, "PE", "CHASSIS")
two(S1, "E102", "BOLT", "Point de masse unique", 45, 90, "GND", "CHASSIS")
S1.note("PE : vis dédiée, rondelle éventail et contre-écrou. La masse du montage rejoint le châssis en un seul point (E102).", 14, 112, 1.5)

S1.frame(150, 10, 420, 120, "Redressement et filtrage HT")
x0, y0 = 160, 30
two(S1, "D101", "D", "UF4007", x0 + 5, y0 + 5, "HT_A", "HT_AM")
two(S1, "D102", "D", "UF4007", x0 + 20, y0 + 5, "HT_AM", "HT_RECT")
two(S1, "D103", "D", "UF4007", x0 + 5, y0 + 20, "HT_B", "HT_BM")
two(S1, "D104", "D", "UF4007", x0 + 20, y0 + 20, "HT_BM", "HT_RECT")
two(S1, "F102", "FUSE", "T1 A", x0 + 40, y0 + 5, "HT_RECT", "HT_F")
S1.add(Part("SW102", "SW_SPST", "Standby", (x0 + 60, y0 + 5), nets={1: "HT_F", 2: "B+1"}))
row = [("C101", "CP", "470µ 350 V", "B+1", "CB1_MID"), ("C102", "CP", "470µ 350 V", "CB1_MID", "GND"),
       ("R101", "R", "220k 1 W", "B+1", "CB1_MID"), ("R102", "R", "220k 1 W", "CB1_MID", "GND")]
for i, (r, s_, v, a, b) in enumerate(row):
    two(S1, r, s_, v, x0 + 80 + (i % 2) * 22.86, y0 + 5 + (i // 2) * 27.94, a, b)
S1.add(Part("L101", "L", "10 H (TT-CK10)", (x0 + 140, y0 + 15), rotation=90, nets={1: "B+1", 2: "B+2"}))
row = [("C103", "CP", "220µ 350 V", "B+2", "CB2_MID"), ("C104", "CP", "220µ 350 V", "CB2_MID", "GND"),
       ("R103", "R", "220k 1 W", "B+2", "CB2_MID"), ("R104", "R", "220k 1 W", "CB2_MID", "GND")]
for i, (r, s_, v, a, b) in enumerate(row):
    two(S1, r, s_, v, x0 + 165 + (i % 2) * 22.86, y0 + 5 + (i // 2) * 27.94, a, b)
S1.note("B+1 : 2 × 470 µF 350 V en série (235 µF) ; B+2 : 2 × 220 µF 350 V en série.", x0, y0 + 75, 1.5)

S1.frame(10, 130, 420, 230, "Chaîne de filtrage et cellules dédiées (condensateurs ≥ 550 V : à vide les nœuds montent vers 535 V)")
cells = [("R105", "13k 3 W", "B+2", "B+3", "C105", "47µ 550 V"), ("R106", "15k 1 W", "B+3", "B+4", "C106", "10µ 550 V"),
         ("R107", "15k 1 W", "B+3", "B+5", "C107", "10µ 550 V"), ("R108", "22k 1 W", "B+2", "B+BUF", "C108", "47µ 550 V"),
         ("R109", "10k 2 W", "B+2", "B+WCF", "C109", "47µ 550 V"), ("R110", "68k 1 W", "B+2", "B+EXT", "C110", "10µ 550 V")]
for i, (r, rv, a, b, c, cv) in enumerate(cells):
    x = 30 + i * 62
    S1.add(Part(r, "R", rv, (x, 175), rotation=90, nets={1: a, 2: b}))
    two(S1, c, "CP", cv, x + 22, 195, b, "GND")
S1.note("Tensions au repos (simulation) : B+1 501, B+2 499, B+3 386, B+4 368, B+5 360, B+BUF 404, B+WCF 416, B+EXT 358 V",
        20, 222, 1.6)

S1.frame(10, 240, 200, 400, "Polarisation individuelle (prise 60 V ; réglage de −43 à −66 V)")
two(S1, "D105", "D", "1N4007", 30, 262, "BIAS_RAW", "BIAS_AC")
two(S1, "C111", "CP", "100µ 160 V", 50, 275, "GND", "BIAS_RAW")
S1.add(Part("R111", "R", "2.2k", (70, 262), rotation=90, nets={1: "BIAS_RAW", 2: "BIAS_RAIL"}))
two(S1, "C112", "CP", "100µ 160 V", 90, 275, "GND", "BIAS_RAIL")
for i, t in enumerate(("V7", "V8", "V9", "V10")):
    x = 30 + i * 42
    bt, bb, out = f"BIAS_TOP_{t}", f"BIAS_BOT_{t}", f"BIAS_{t}"
    two(S1, f"R{112 + i * 3}", "R", "10k", x, 305, "BIAS_RAIL", bt)
    S1.add(Part(f"RV{101 + i}", "POT", "25k trim", (x, 330), nets={3: bt, 2: out, 1: bb}))
    two(S1, f"R{113 + i * 3}", "R", "47k", x, 355, bb, "GND")
    two(S1, f"R{114 + i * 3}", "R", "1M", x + 18, 330, out, bt)
S1.note("La résistance de 1 M ramène la grille au plus négatif si le curseur perd le contact.", 15, 392, 1.5)

S1.frame(210, 240, 420, 400, "Filaments surélevés")
two(S1, "R124", "R", "330k 3 W", 230, 270, "B+2", "HEAT_REF_A")
two(S1, "R125", "R", "47k", 230, 300, "HEAT_REF_A", "GND")
two(S1, "C113", "CP", "47µ 100 V", 250, 300, "HEAT_REF_A", "GND")
two(S1, "R128", "R", "330k 3 W", 320, 270, "B+2", "HEAT_REF_B")
two(S1, "R129", "R", "82k", 320, 300, "HEAT_REF_B", "GND")
two(S1, "C114", "CP", "47µ 160 V", 340, 300, "HEAT_REF_B", "GND")
S1.note("HEAT_A (6,3 V 7,5 A) : V1, V2, V3, V5 et les 6L6GC, à +62 V.  HEAT_B (6,3 V 3 A) : V4 et V6, à +99 V.", 215, 345, 1.5)
S1.note("Points milieux des enroulements 6,3 V (TT-SLO100) reliés aux références ; paires torsadées.", 215, 352, 1.5)

# =================================================================================================
# 2. Préampli
# =================================================================================================
S2 = P.sheet(Sheet("Préampli", "preampli.kicad_sch", "A1", "Préampli : V1, V6, V2, V3"))
X, Y = 15, 15
S2.frame(X, Y, X + 190, Y + 120, "V1B — premier étage, buffer V6A et diviseurs ÷5")
two(S2, "R201", "R", "1M", X + 12, Y + 45, "IN_V1", "GND")
S2.add(Part("R202", "R", "68k", (X + 30, Y + 38), rotation=90, nets={1: "IN_V1", 2: "V1B_G"}))
tube(S2, "V1", "12AX7", 2, X + 55, Y + 40, "V1B_P", "V1B_G", "V1B_K")
two(S2, "R203", "R", "220k", X + 55, Y + 18, "B+5", "V1B_P")
two(S2, "R204", "R", "1.8k", X + 45, Y + 70, "V1B_K", "GND")
two(S2, "C201", "C", "0.47µ 63 V", X + 60, Y + 70, "V1B_K", "GND")
two(S2, "C202", "C", "0.47µ 63 V", X + 75, Y + 70, "V1B_K", "V1B_KX")
two(S2, "R205", "R", "1M", X + 75, Y + 95, "V1B_KX", "GND")
S2.add(Part("K201", "RELAY_2C", "G6K-2 5 V", (X + 95, Y + 95), unit=1, nets={1: "V1B_KX", 2: "GND", 3: None}))
S2.add(Part("C203", "C", "47n 630 V", (X + 100, Y + 30), rotation=90, nets={1: "V1B_P", 2: "V6A_G"}))
tube(S2, "V6", "12AU7", 1, X + 130, Y + 40, "B+BUF", "V6A_G", "V6A_K")
two(S2, "R206", "R", "1.2M", X + 115, Y + 62, "B+BUF", "V6A_GB")
two(S2, "R207", "R", "1M", X + 115, Y + 88, "V6A_GB", "GND")
two(S2, "C204", "C", "0.47µ 400 V", X + 102, Y + 75, "V6A_GB", "GND")
S2.add(Part("R208", "R", "1M", (X + 118, Y + 50), rotation=90, nets={1: "V6A_GB", 2: "V6A_G"}))
two(S2, "R209", "R", "47k 2 W", X + 130, Y + 70, "V6A_K", "GND")
S2.add(Part("C205", "C", "0.1µ 630 V", (X + 160, Y + 55), rotation=90, nets={1: "V6A_K", 2: "DIV_IN"}))
S2.note("Relais K201 au repos : découplage complet (1 µF) ; activé : 0,47 µF.", X + 5, Y + 113, 1.4)

X, Y = 215, 15
S2.frame(X, Y, X + 230, Y + 120, "Diviseurs de gain OD et Normal (crunch / clean / bright par LDR)")
two(S2, "R210", "R", "91k", X + 15, Y + 30, "DIV_IN", "OD_TOP")
two(S2, "C206", "C", "10n", X + 32, Y + 30, "DIV_IN", "OD_TOP")
S2.add(Part("RV201", "ALPS_2G", "100k lin (OD Gain)", (X + 25, Y + 62), unit=1, nets={3: "OD_TOP", 2: "OD_W", 1: "GND"}))
two(S2, "C207", "C", "4.7n", X + 50, Y + 62, "OD_TOP", "OD_W")
two(S2, "R211", "R", "91k", X + 85, Y + 30, "DIV_IN", "NRM_MID")
ldr(S2, "LDR201", X + 100, Y + 30, "DIV_IN", "NRM_MID")
two(S2, "R212", "R", "91k", X + 120, Y + 30, "NRM_MID", "NRM_TOP")
two(S2, "C208", "C", "2.2n", X + 140, Y + 30, "NRM_MID", "NRM_BR")
ldr(S2, "LDR203", X + 160, Y + 30, "NRM_BR", "NRM_TOP")
two(S2, "R213", "R", "7.5k", X + 120, Y + 65, "NRM_TOP", "NRM_CL")
ldr(S2, "LDR202", X + 120, Y + 92, "NRM_CL", "GND")
S2.add(Part("RV202", "ALPS_2G", "100k lin (Normal Gain)", (X + 150, Y + 72), unit=1, nets={3: "NRM_TOP", 2: "NRM_W", 1: "GND"}))
S2.note("LDR201 passante = crunch ; LDR202 passante = clean (÷25) ; LDR203 passante = bright.", X + 5, Y + 113, 1.4)

X, Y = 450, 15
S2.frame(X, Y, X + 125, Y + 120, "V1A — canal clair")
tube(S2, "V1", "12AX7", 1, X + 40, Y + 45, "V1A_P", "NRM_W", "V1A_K")
two(S2, "R214", "R", "100k", X + 40, Y + 22, "B+5", "V1A_P")
two(S2, "R215", "R", "2.2k", X + 40, Y + 75, "V1A_K", "GND")
S2.add(Part("C209", "C", "20n 630 V", (X + 70, Y + 32), rotation=90, nets={1: "V1A_P", 2: "V1A_OUT"}))
two(S2, "R216", "R", "2.2M", X + 90, Y + 50, "V1A_OUT", "CLN_MIX")
two(S2, "C210", "C", "120p", X + 105, Y + 50, "V1A_OUT", "CLN_MIX")
ldr(S2, "LDR204", X + 95, Y + 85, "CLN_MIX", "JN")
S2.note("LDR204 coupe le canal clair quand l'étage supplémentaire est en service.", X + 5, Y + 113, 1.4)

X, Y = 15, 145
S2.frame(X, Y, X + 300, Y + 130, "V2A — OD Preamp 2, liaison commutable et étage supplémentaire V6B")
S2.add(Part("R217", "R", "470k", (X + 20, Y + 40), rotation=90, nets={1: "OD_W", 2: "V2A_G"}))
tube(S2, "V2", "12AX7", 1, X + 45, Y + 42, "V2A_P", "V2A_G", "V2A_K")
two(S2, "R218", "R", "100k", X + 45, Y + 20, "B+4", "V2A_P")
two(S2, "R219", "R", "1.8k", X + 35, Y + 72, "V2A_K", "GND")
two(S2, "C211", "C", "0.47µ 63 V", X + 50, Y + 72, "V2A_K", "GND")
two(S2, "C212", "C", "0.47µ 63 V", X + 65, Y + 72, "V2A_K", "V2A_KX")
two(S2, "R220", "R", "1M", X + 65, Y + 97, "V2A_KX", "GND")
S2.add(Part("K201", "RELAY_2C", "G6K-2 5 V", (X + 85, Y + 97), unit=2, nets={4: "V2A_KX", 5: "GND", 6: None}))
two(S2, "C213", "C", "20n 630 V", X + 100, Y + 30, "V2A_P", "CC20")
two(S2, "R221", "R", "4.7M", X + 100, Y + 55, "CC20", "GND")
two(S2, "C214", "C", "2.2n 630 V", X + 118, Y + 30, "V2A_P", "CC2N2")
two(S2, "R222", "R", "4.7M", X + 118, Y + 55, "CC2N2", "GND")
S2.add(Part("K202", "RELAY_2C", "G6K-2 5 V", (X + 140, Y + 80), unit=1, nets={1: "CC_SEL", 2: "CC20", 3: "CC2N2"}))
S2.add(Part("K202", "RELAY_2C", "G6K-2 5 V", (X + 140, Y + 110), unit=2, nets={4: None, 5: None, 6: None}))
ldr(S2, "LDR205", X + 165, Y + 80, "CC_SEL", "CLIP_IN")
two(S2, "C215", "C", "1n 630 V", X + 185, Y + 30, "V2A_P", "EX_IN")
two(S2, "R223", "R", "1M", X + 185, Y + 55, "EX_IN", "V6B_G")
two(S2, "R224", "R", "330k", X + 200, Y + 80, "V6B_G", "GND")
tube(S2, "V6", "12AU7", 2, X + 230, Y + 50, "V6B_P", "V6B_G", "V6B_K")
two(S2, "R225", "R", "100k 1 W", X + 230, Y + 25, "B+EXT", "V6B_P")
two(S2, "R226", "R", "3.3k", X + 222, Y + 85, "V6B_K", "GND")
two(S2, "C216", "C", "0.68µ 63 V", X + 238, Y + 85, "V6B_K", "GND")
two(S2, "C217", "C", "20n 630 V", X + 260, Y + 30, "V6B_P", "EX_OUT")
two(S2, "R227", "R", "4.7M", X + 260, Y + 60, "EX_OUT", "GND")
ldr(S2, "LDR206", X + 280, Y + 60, "EX_OUT", "CLIP_IN")
S2.note("K202 au repos : 20 nF ; activé : 2,2 nF. Les 4,7 M gardent chargé le condensateur non sélectionné.", X + 5, Y + 123, 1.4)

X, Y = 325, 145
S2.frame(X, Y, X + 250, Y + 130, "V2B — cold clipper (39 k / ~10 k / ~4,4 k)")
S2.add(Part("R228", "R", "470k", (X + 20, Y + 40), rotation=90, nets={1: "CLIP_IN", 2: "V2B_G"}))
two(S2, "R229", "R", "1M", X + 30, Y + 70, "V2B_G", "GND")
ldr(S2, "LDR207", X + 45, Y + 70, "V2B_G", "GND")
tube(S2, "V2", "12AX7", 2, X + 75, Y + 40, "V2B_P", "V2B_G", "V2B_K")
two(S2, "R231", "R", "100k", X + 70, Y + 15, "B+4", "V2B_P")
two(S2, "C218", "C", "1n", X + 85, Y + 15, "B+4", "V2B_P")
two(S2, "R230", "R", "39k", X + 65, Y + 72, "V2B_K", "GND")
two(S2, "R232", "R", "12k", X + 85, Y + 72, "V2B_K", "V2B_K10")
ldr(S2, "LDR208", X + 85, Y + 100, "V2B_K10", "GND")
two(S2, "R233", "R", "3.9k", X + 105, Y + 72, "V2B_K", "V2B_K4")
ldr(S2, "LDR209", X + 105, Y + 100, "V2B_K4", "GND")
S2.add(Part("C219", "C", "20n 630 V", (X + 130, Y + 30), rotation=90, nets={1: "V2B_P", 2: "OD_OUT"}))
two(S2, "R234", "R", "2.2M", X + 150, Y + 55, "OD_OUT", "GND")
ldr(S2, "LDR210", X + 170, Y + 55, "OD_OUT", "JN")
S2.note("Changer LDR208 / LDR209 déplace la polarisation : toujours sous mute (50 ms avant, 300 ms après).", X + 5, Y + 123, 1.4)

X, Y = 15, 285
S2.frame(X, Y, X + 230, Y + 120, "V3B — OD4, étage principal de distorsion ; V3A — cathode follower")
two(S2, "R235", "R", "330k", X + 20, Y + 55, "JN", "GND")
S2.add(Part("R236", "R", "220k", (X + 38, Y + 40), rotation=90, nets={1: "JN", 2: "V3B_G"}))
tube(S2, "V3", "12AX7", 2, X + 65, Y + 42, "V3B_P", "V3B_G", "V3B_K")
two(S2, "R237", "R", "220k", X + 65, Y + 18, "B+3", "V3B_P")
two(S2, "R238", "R", "1.8k", X + 58, Y + 72, "V3B_K", "GND")
two(S2, "C220", "C", "1µ 63 V", X + 73, Y + 72, "V3B_K", "GND")
tube(S2, "V3", "12AX7", 1, X + 130, Y + 42, "B+3", "V3B_P", "V3A_K")
two(S2, "R239", "R", "100k 1 W", X + 130, Y + 72, "V3A_K", "GND")
S2.note("V3A attaque l'atténuateur de la White CF (feuille Tone stack et déphaseur).", X + 5, Y + 113, 1.4)

X, Y = 255, 285
S2.frame(X, Y, X + 160, Y + 120, "Chauffage du préampli")
heater(S2, "V1", "12AX7", X + 30, Y + 40, "HEAT_A1", "HEAT_A2")
heater(S2, "V2", "12AX7", X + 80, Y + 40, "HEAT_A1", "HEAT_A2")
heater(S2, "V3", "12AX7", X + 130, Y + 40, "HEAT_A1", "HEAT_A2")
heater(S2, "V6", "12AU7", X + 30, Y + 85, "HEAT_B1", "HEAT_B2")
S2.note("ECC83/ECC82 en 6,3 V : broches 4 et 5 reliées, 9 à l'autre fil.", X + 5, Y + 113, 1.4)

# =================================================================================================
# 3. Tone stack, masters, déphaseur, contre-réaction
# =================================================================================================
S3 = P.sheet(Sheet("Tone stack et déphaseur", "tone_pi.kicad_sch", "A1", "Atténuateur, White CF, tone stack, masters, déphaseur"))
X, Y = 15, 15
S3.frame(X, Y, X + 250, Y + 130, "Atténuateur de poussée et White cathode follower (V4)")
S3.add(Part("C301", "C", "0.1µ 630 V", (X + 20, Y + 40), rotation=90, nets={1: "V3A_K", 2: "ATT_IN"}))
two(S3, "R301", "R", "220k", X + 35, Y + 70, "ATT_IN", "GND")
S3.add(Part("R302", "R", "300k", (X + 60, Y + 40), rotation=90, nets={1: "ATT_IN", 2: "ATT_OUT"}))
ldr(S3, "LDR301", X + 60, Y + 70, "ATT_IN", "ATT_OUT")
S3.add(Part("C302", "C", "0.1µ 630 V", (X + 90, Y + 40), rotation=90, nets={1: "ATT_OUT", 2: "WCF_G"}))
two(S3, "R303", "R", "820k", X + 110, Y + 25, "B+WCF", "WCF_G")
two(S3, "R304", "R", "1M", X + 110, Y + 70, "WCF_G", "GND")
tube(S3, "V4", "12AU7", 1, X + 150, Y + 45, "WCF_PA", "WCF_G", "WCF_OUT")
two(S3, "R305", "R", "3.3k 1 W", X + 150, Y + 20, "B+WCF", "WCF_PA")
S3.add(Part("C303", "C", "0.47µ 630 V", (X + 185, Y + 30), rotation=90, nets={1: "WCF_PA", 2: "WCF_GB"}))
two(S3, "R306", "R", "1M", X + 200, Y + 60, "WCF_GB", "GND")
tube(S3, "V4", "12AU7", 2, X + 225, Y + 75, "WCF_OUT", "WCF_GB", "WCF_KB")
two(S3, "R307", "R", "1k", X + 218, Y + 105, "WCF_KB", "GND")
two(S3, "C304", "CP", "220µ 25 V", X + 236, Y + 105, "WCF_KB", "GND")
S3.note("LDR301 passante = poussée. Ses deux bornes sont à 0 V continu (entre C301 et C302).", X + 5, Y + 123, 1.4)

X, Y = 275, 15
S3.frame(X, Y, X + 300, Y + 130, "Tone stack ÷10 et masters (pots ALPS motorisés)")
S3.add(Part("C305", "C", "5.6n 630 V", (X + 25, Y + 30), rotation=90, nets={1: "WCF_OUT", 2: "STK_TT"}))
S3.add(Part("R308", "R", "4.7k", (X + 25, Y + 60), rotation=90, nets={1: "WCF_OUT", 2: "STK_TA"}))
S3.add(Part("RV301", "ALPS_2G", "20k lin (Treble)", (X + 60, Y + 45), unit=1, nets={3: "STK_TT", 2: "STK_TW", 1: "STK_TB"}))
two(S3, "C306", "C", "220n 630 V", X + 45, Y + 80, "STK_TA", "STK_TB")
two(S3, "C307", "C", "220n 630 V", X + 85, Y + 80, "STK_TA", "STK_TMW")
S3.add(Part("RV302", "ALPS_2G", "100k log (Bass)", (X + 60, Y + 105), unit=1, nets={1: "STK_TB", 2: "STK_TM", 3: "STK_TM"}))
S3.add(Part("RV303", "ALPS_2G", "10k log (Mid)", (X + 120, Y + 100), unit=1, nets={3: "STK_TM", 2: "STK_TMW", 1: "GND"}))
two(S3, "R317", "R", "3.3k", X + 150, Y + 100, "STK_TM", "GND")
S3.add(Part("RV304", "ALPS_2G", "100k log (Master OD)", (X + 210, Y + 45), unit=1, nets={3: "STK_TW", 2: "MOD_W", 1: "GND"}))
S3.add(Part("RV305", "ALPS_2G", "100k log (Master Normal)", (X + 255, Y + 45), unit=1, nets={3: "STK_TW", 2: "MN_W", 1: "GND"}))
ldr(S3, "LDR302", X + 225, Y + 85, "MOD_W", "PI_IN")
ldr(S3, "LDR303", X + 270, Y + 85, "MN_W", "PI_IN")
S3.note("Mid : 10 k log et 3,3 k en parallèle (2,5 k aux extrémités) ; à ±1 dB de la famille de courbes d'un 2,5 k.", X + 5, Y + 123, 1.4)

X, Y = 15, 155
S3.frame(X, Y, X + 300, Y + 140, "Déphaseur (V5), mute et contre-réaction (presence, depth)")
ldr(S3, "LDR304", X + 15, Y + 70, "PI_IN", "GND")
S3.add(Part("C308", "C", "20n 630 V", (X + 35, Y + 45), rotation=90, nets={1: "PI_IN", 2: "PI_GB"}))
two(S3, "R309", "R", "1M", X + 55, Y + 80, "PI_GB", "PI_TAIL")
tube(S3, "V5", "12AX7", 2, X + 80, Y + 45, "PI_PB", "PI_GB", "PI_K")
tube(S3, "V5", "12AX7", 1, X + 140, Y + 45, "PI_PA", "PI_GA", "PI_K")
two(S3, "R310", "R", "1M", X + 120, Y + 80, "PI_GA", "PI_TAIL")
two(S3, "R313", "R", "82k", X + 80, Y + 20, "B+3", "PI_PB")
two(S3, "R314", "R", "100k", X + 140, Y + 20, "B+3", "PI_PA")
S3.add(Part("C309", "C", "47p", (X + 110, Y + 18), rotation=90, nets={1: "PI_PB", 2: "PI_PA"}))
two(S3, "R311", "R", "470", X + 100, Y + 85, "PI_K", "PI_TAIL")
two(S3, "R312", "R", "10k", X + 100, Y + 112, "PI_TAIL", "NFB")
two(S3, "C310", "C", "0.1µ 630 V", X + 160, Y + 85, "PI_GA", "NFB")
two(S3, "R315", "R", "4.7k", X + 180, Y + 112, "NFB", "GND")
two(S3, "C311", "C", "0.12µ 63 V", X + 200, Y + 85, "NFB", "PRES")
S3.add(Part("RV306", "ALPS_2G", "20k lin (Presence)", (X + 200, Y + 115), unit=1, nets={3: "PRES", 2: "GND", 1: "GND"}))
S3.add(Part("R316", "R", "39k", (X + 235, Y + 45), rotation=90, nets={1: "NFB_X", 2: "NFB"}))
S3.add(Part("C312", "C", "0.1µ 63 V", (X + 265, Y + 45), rotation=90, nets={1: "DEPTH_X", 2: "NFB_X"}))
S3.add(Part("RV307", "ALPS_2G", "100k lin (Depth)", (X + 255, Y + 90), unit=1, nets={1: "SPK_4R", 2: "DEPTH_X", 3: "DEPTH_X"}))
two(S3, "C313", "C", "4.7n", X + 280, Y + 90, "DEPTH_X", "SPK_4R")
S3.note("PI_PB attaque V7 et V8, PI_PA attaque V9 et V10 (feuille Puissance). Contre-réaction prise sur la prise 4 Ω.", X + 5, Y + 133, 1.4)

X, Y = 325, 155
S3.frame(X, Y, X + 120, Y + 80, "Chauffage")
heater(S3, "V4", "12AU7", X + 30, Y + 40, "HEAT_B1", "HEAT_B2")
heater(S3, "V5", "12AX7", X + 80, Y + 40, "HEAT_A1", "HEAT_A2")

# =================================================================================================
# 4. Étage de puissance et sortie
# =================================================================================================
S4 = P.sheet(Sheet("Puissance", "puissance.kicad_sch", "A2", "Étage de puissance 4 × 6L6GC et sortie"))
S4.frame(10, 10, 400, 175, "4 × 6L6GC, polarisation individuelle, mesure du courant par 1 Ω")
for i, (t, drv, plate) in enumerate((("V7", "PI_PB", "OT_PA"), ("V8", "PI_PB", "OT_PA"),
                                     ("V9", "PI_PA", "OT_PB"), ("V10", "PI_PA", "OT_PB"))):
    x = 30 + i * 95
    n = 401 + i * 10
    S4.add(Part(f"C{n}", "C", "22n 630 V", (x, 40), rotation=90, nets={1: drv, 2: f"{t}_GL"}))
    two(S4, f"R{n}", "R", "470k", x + 12, 70, f"{t}_GL", f"BIAS_{t}")
    S4.add(Part(f"R{n + 1}", "R", "2.2k", (x + 25, 52), rotation=90, nets={1: f"{t}_GL", 2: f"{t}_G1"}))
    S4.add(Part(t, "6L6GC", "6L6GC", (x + 50, 55), unit=1, nets={3: plate, 4: f"{t}_G2", 5: f"{t}_G1", 8: f"{t}_K"}))
    two(S4, f"R{n + 2}", "R", "470 1 W", x + 70, 35, "B+2", f"{t}_G2")
    two(S4, f"R{n + 3}", "R", "1 1 % 0,5 W", x + 50, 90, f"{t}_K", "GND")
    S4.add(Part(t, "6L6GC", "6L6GC", (x + 40, 130), unit=2, nets={2: "HEAT_A1", 7: "HEAT_A2"}))
S4.note("Courant de repos : 38 mA par lampe, soit 38 mV sur la résistance de 1 Ω (mesure Vx_K vers le pilotage).", 15, 168, 1.5)

S4.frame(10, 185, 400, 290, "Transfo de sortie, sélecteur d'impédance et sorties HP")
S4.add(Part("T401", "OT_SLO", "TT-SLO100", (80, 235), nets={1: "OT_PA", 2: "B+1", 3: "OT_PB", 4: "GND", 5: "SPK_4R",
                                                          6: "SPK_8R", 7: "SPK_16R"}))
S4.add(Part("SW401", "SW_1P3T", "Impédance", (160, 235), nets={"C": "SPK_OUT", 1: "SPK_16R", 2: "SPK_8R", 3: "SPK_4R"}))
S4.add(Part("J401", "JACK_TS", "HP 1", (220, 230), nets={"T": "SPK_OUT", "S": "GND"}))
S4.add(Part("J402", "JACK_TS", "HP 2", (220, 255), nets={"T": "SPK_OUT", "S": "GND"}))
S4.note("Le point milieu du primaire reçoit B+1 ; la contre-réaction part de la prise 4 Ω (SPK_4R) quel que soit le sélecteur.",
        15, 282, 1.5)

# =================================================================================================
# 5. Boîtier d'entrée
# =================================================================================================
S5 = P.sheet(Sheet("Boîtier d'entrée", "boitier_entree.kicad_sch", "A1", "Buffer, Tube Screamer pilotable, insert, noise gate"))
X, Y = 15, 15
S5.frame(X, Y, X + 150, Y + 110, "Entrée et buffer")
S5.add(Part("J501", "JACK_TSN", "Entrée guitare", (X + 15, Y + 40), nets={"T": "GTR_IN", "S": "GND", "TN": "GND"}))
S5.add(Part("R501", "R", "1k", (X + 45, Y + 38), rotation=90, nets={1: "GTR_IN", 2: "BUF_IN"}))
two(S5, "C501", "C", "100p", X + 60, Y + 65, "BUF_IN", "GND")
two(S5, "R502", "R", "1M", X + 72, Y + 65, "BUF_IN", "GND")
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 105, Y + 40), unit=1, nets={3: "BUF_IN", 2: "BUF_OUT", 1: "BUF_OUT"}))
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 125, Y + 85), unit=3, nets={8: "+15V", 4: "-15V"}))

X, Y = 175, 15
S5.frame(X, Y, X + 300, Y + 110, "Tube Screamer : étage d'écrêtage (drive numérique 100 k)")
S5.add(Part("C502", "C", "1µ film", (X + 15, Y + 35), rotation=90, nets={1: "BUF_OUT", 2: "TS_X1"}))
two(S5, "R503", "R", "10k", X + 30, Y + 65, "TS_X1", "GND")
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 60, Y + 37), unit=2, nets={5: "TS_X1", 6: "TS_NF", 7: "TS_O1"}))
S5.add(Part("R504", "R", "10k", (X + 95, Y + 25), rotation=90, nets={1: "TS_O1", 2: "TS_ND"}))
S5.add(Part("U502", "MCP41HV51", "MCP41HV51-104 (Drive)", (X + 140, Y + 40),
            nets={1: "+3V3", 2: "SPI_SCK", 3: "CS_DRIVE", 4: "SPI_MOSI", 5: None, 6: "GND", 7: "+3V3",
                  14: "+15V", 13: "TS_ND", 12: "TS_NF", 11: "TS_NF", 10: "-15V", 9: "GND", 8: "GND"}))
two(S5, "C503", "C", "270p", X + 185, Y + 30, "TS_O1", "TS_NF")
two(S5, "R505", "R", "1k", X + 200, Y + 30, "TS_NF", "TS_NG")
two(S5, "C504", "C", "220n", X + 200, Y + 58, "TS_NG", "GND")
S5.add(Part("K501", "RELAY_2C", "G6K-2 5 V", (X + 225, Y + 40), unit=1, nets={1: "TS_O1", 2: "DS_TOP", 3: "DL_TOP"}))
S5.add(Part("K501", "RELAY_2C", "G6K-2 5 V", (X + 225, Y + 95), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("D501", "D", "1N914", (X + 255, Y + 25), nets={1: "DS_TOP", 2: "TS_NF"}))
S5.add(Part("D502", "D", "1N914", (X + 255, Y + 45), nets={1: "TS_NF", 2: "DS_ASY"}))
S5.add(Part("D505", "D", "1N914", (X + 280, Y + 45), nets={1: "DS_ASY", 2: "DS_TOP"}))
S5.add(Part("K502", "RELAY_2C", "G6K-2 5 V", (X + 270, Y + 70), unit=1, nets={1: "DS_ASY", 2: "DS_TOP", 3: None}))
S5.add(Part("K502", "RELAY_2C", "G6K-2 5 V", (X + 270, Y + 95), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("D503", "D", "LED rouge", (X + 240, Y + 65), nets={1: "DL_TOP", 2: "TS_NF"}))
S5.add(Part("D504", "D", "LED rouge", (X + 240, Y + 85), nets={1: "TS_NF", 2: "DL_TOP"}))
S5.note("K501 au repos : diodes silicium ; activé : LED. K502 activé : écrêtage asymétrique (D505 en série).", X + 5, Y + 105, 1.4)

X, Y = 15, 135
S5.frame(X, Y, X + 230, Y + 110, "Tone (numérique 10 k) et level (numérique 100 k)")
S5.add(Part("R506", "R", "1k", (X + 15, Y + 30), rotation=90, nets={1: "TS_O1", 2: "TS_TA"}))
two(S5, "C505", "C", "220n", X + 30, Y + 60, "TS_TA", "GND")
S5.add(Part("U503", "MCP41HV51", "MCP41HV51-103 (Tone)", (X + 75, Y + 50),
            nets={1: "+3V3", 2: "SPI_SCK", 3: "CS_TONE", 4: "SPI_MOSI", 5: None, 6: "GND", 7: "+3V3",
                  14: "+15V", 13: "TS_TA", 12: "TS_TWP", 11: "TS_TN", 10: "-15V", 9: "GND", 8: "GND"}))
two(S5, "R507", "R", "150", X + 115, Y + 50, "TS_TWP", "TS_TC")
two(S5, "C506", "C", "220n", X + 115, Y + 78, "TS_TC", "GND")
S5.add(Part("U504", "OPA2134", "OPA2134", (X + 150, Y + 35), unit=1, nets={3: "TS_TA", 2: "TS_TN", 1: "TS_O2"}))
two(S5, "R508", "R", "1k", X + 175, Y + 60, "TS_O2", "TS_TN")
S5.add(Part("C507", "C", "1µ film", (X + 190, Y + 30), rotation=90, nets={1: "TS_O2", 2: "TS_LV"}))
S5.add(Part("U505", "MCP41HV51", "MCP41HV51-104 (Level)", (X + 170, Y + 95),
            nets={1: "+3V3", 2: "SPI_SCK", 3: "CS_LEVEL", 4: "SPI_MOSI", 5: None, 6: "GND", 7: "+3V3",
                  14: "+15V", 13: "TS_LV", 12: "TS_LVW", 11: "GND", 10: "-15V", 9: "GND", 8: "GND"}))
S5.add(Part("U504", "OPA2134", "OPA2134", (X + 215, Y + 75), unit=2, nets={5: "TS_LVW", 6: "TS_OUT", 7: "TS_OUT"}))
S5.add(Part("U504", "OPA2134", "OPA2134", (X + 215, Y + 40), unit=3, nets={8: "+15V", 4: "-15V"}))

X, Y = 255, 135
S5.frame(X, Y, X + 220, Y + 110, "Bypass du TS et boucle d'insertion HM-2")
S5.add(Part("K503", "RELAY_2C", "G6K-2 5 V", (X + 25, Y + 35), unit=1, nets={1: "FX1", 2: "BUF_OUT", 3: "TS_OUT"}))
S5.add(Part("K503", "RELAY_2C", "G6K-2 5 V", (X + 25, Y + 80), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("K504", "RELAY_2C", "G6K-2 5 V", (X + 75, Y + 35), unit=1, nets={1: "FX1", 2: "FX_DIRECT", 3: "SEND_A"}))
S5.add(Part("K504", "RELAY_2C", "G6K-2 5 V", (X + 75, Y + 70), unit=2, nets={4: "FX2", 5: "FX_DIRECT", 6: "RET_IN"}))
S5.add(Part("R509", "R", "100", (X + 120, Y + 25), rotation=90, nets={1: "SEND_A", 2: "SEND_T"}))
S5.add(Part("J502", "JACK_TS", "Send", (X + 150, Y + 30), nets={"T": "SEND_T", "S": "GND"}))
S5.add(Part("J503", "JACK_TS", "Return", (X + 150, Y + 60), nets={"T": "RET_IN", "S": "GND"}))
two(S5, "R510", "R", "100k", X + 185, Y + 75, "RET_IN", "GND")
S5.note("Au repos : TS contourné, insert contourné (FX1 relié à FX2).", X + 5, Y + 105, 1.4)

X, Y = 15, 255
S5.frame(X, Y, X + 320, Y + 120, "Noise gate : +12 dB, VCA THAT 2181, I/V à −12 dB")
S5.add(Part("U506", "OPA2134", "OPA2134", (X + 30, Y + 40), unit=1, nets={3: "FX2", 2: "G_FB", 1: "G_PRE"}))
two(S5, "R511", "R", "30k", X + 50, Y + 70, "G_PRE", "G_FB")
two(S5, "R512", "R", "10k", X + 35, Y + 85, "G_FB", "GND")
S5.add(Part("C508", "C", "10µ bipolaire", (X + 70, Y + 35), rotation=90, nets={1: "G_PRE", 2: "VCA_INC"}))
S5.add(Part("R513", "R", "20k", (X + 95, Y + 35), rotation=90, nets={1: "VCA_INC", 2: "VCA_IN"}))
S5.add(Part("U507", "THAT2181", "THAT2181AS08", (X + 135, Y + 45),
            nets={1: "VCA_IN", 2: "VCA_EC", 3: "GND", 4: "VCA_SYM", 7: "+15V", 8: "VCA_OUT", 6: "GND", 5: "VCA_VM"}))
two(S5, "R514", "R", "5.1k", X + 165, Y + 80, "VCA_VM", "-15V")
S5.add(Part("RV501", "POT", "50k trim (SYM)", (X + 115, Y + 95), nets={3: "+15V", 2: "SYM_W", 1: "-15V"}))
S5.add(Part("R515", "R", "680k", (X + 140, Y + 95), rotation=90, nets={1: "SYM_W", 2: "VCA_SYM"}))
S5.add(Part("U506", "OPA2134", "OPA2134", (X + 215, Y + 45), unit=2, nets={5: "GND", 6: "VCA_OUT", 7: "GATE_OUT"}))
two(S5, "R516", "R", "5.1k", X + 240, Y + 75, "GATE_OUT", "VCA_OUT")
two(S5, "C509", "C", "82p", X + 255, Y + 75, "GATE_OUT", "VCA_OUT")
S5.add(Part("R519", "R", "100", (X + 285, Y + 40), rotation=90, nets={1: "GATE_OUT", 2: "IN_V1"}))
S5.add(Part("U506", "OPA2134", "OPA2134", (X + 300, Y + 85), unit=3, nets={8: "+15V", 4: "-15V"}))
S5.note("Sortie IN_V1 vers la grille de V1B par câble blindé (feuille Préampli).", X + 5, Y + 115, 1.4)

X, Y = 345, 255
S5.frame(X, Y, X + 230, Y + 120, "Commande du VCA et détection d'enveloppe")
S5.add(Part("U508", "MCP4822", "MCP4822", (X + 30, Y + 35),
            nets={1: "+3V3", 2: "CS_DAC", 3: "SPI_SCK", 4: "SPI_MOSI", 8: "DAC_A", 6: None, 5: "GND", 7: "GND"}))
S5.add(Part("R517", "R", "4.7k", (X + 70, Y + 25), rotation=90, nets={1: "DAC_A", 2: "VCA_EC"}))
two(S5, "R518", "R", "680", X + 90, Y + 50, "VCA_EC", "GND")
two(S5, "C510", "C", "100n", X + 105, Y + 50, "VCA_EC", "GND")
S5.add(Part("C511", "C", "1µ", (X + 25, Y + 80), rotation=90, nets={1: "BUF_OUT", 2: "ENV_INB"}))
two(S5, "R524", "R", "100k", X + 45, Y + 100, "ENV_INB", "VREF")
S5.add(Part("U509", "MCP6002", "MCP6002", (X + 80, Y + 85), unit=1, nets={3: "ENV_INB", 2: "ENV_FB", 1: "ENV_ADC"}))
two(S5, "R522", "R", "100k", X + 110, Y + 100, "ENV_ADC", "ENV_FB")
two(S5, "R523", "R", "10k", X + 125, Y + 100, "ENV_FB", "VREF")
two(S5, "R520", "R", "10k", X + 150, Y + 75, "+3V3", "VREF")
two(S5, "R521", "R", "10k", X + 150, Y + 100, "VREF", "GND")
two(S5, "C512", "CP", "10µ", X + 165, Y + 100, "VREF", "GND")
S5.add(Part("U509", "MCP6002", "MCP6002", (X + 195, Y + 85), unit=2, nets={5: "VREF", 6: "ENV_SPARE", 7: "ENV_SPARE"}))
S5.add(Part("U509", "MCP6002", "MCP6002", (X + 215, Y + 40), unit=3, nets={8: "+3V3", 4: "GND"}))
S5.note("Gain 11 autour de 1,65 V ; l'enveloppe et le seuil sont calculés en firmware.", X + 5, Y + 115, 1.4)

X, Y = 15, 385
S5.frame(X, Y, X + 300, Y + 50, "Découplage ±15 V")
for i in range(5):
    two(S5, f"C{513 + 2 * i}", "C", "100n", X + 15 + i * 30, Y + 25, "+15V", "GND")
    two(S5, f"C{514 + 2 * i}", "C", "100n", X + 30 + i * 30, Y + 25, "GND", "-15V")
two(S5, "C523", "CP", "10µ 25 V", X + 170, Y + 25, "+15V", "GND")
two(S5, "C524", "CP", "10µ 25 V", X + 190, Y + 25, "GND", "-15V")

# =================================================================================================
# 6. Pilotage
# =================================================================================================
S6 = P.sheet(Sheet("Pilotage", "pilotage.kicad_sch", "A1", "Alimentation BT, microcontrôleur, interface"))
X, Y = 15, 15
S6.frame(X, Y, X + 280, Y + 120, "Alimentation ±15 V du boîtier d'entrée (transfo séparé 2 × 15 V, 10 VA)")
S6.add(Part("T601", "T_LV", "2 × 15 V 10 VA", (X + 30, Y + 50),
            nets={1: "N_SW", 2: "L_SW", 3: "LV_A", 4: "GND", 5: "GND", 6: "LV_B"}))
S6.add(Part("D601", "D", "1N4007", (X + 70, Y + 35), nets={1: "LV_A", 2: "+V_BRUT"}))
S6.add(Part("D602", "D", "1N4007", (X + 70, Y + 50), nets={1: "LV_B", 2: "+V_BRUT"}))
S6.add(Part("D603", "D", "1N4007", (X + 70, Y + 70), nets={1: "-V_BRUT", 2: "LV_A"}))
S6.add(Part("D604", "D", "1N4007", (X + 70, Y + 85), nets={1: "-V_BRUT", 2: "LV_B"}))
two(S6, "C601", "CP", "1000µ 35 V", X + 95, Y + 40, "+V_BRUT", "GND")
two(S6, "C602", "CP", "1000µ 35 V", X + 95, Y + 80, "GND", "-V_BRUT")
S6.add(Part("U601", "78XX", "LM7815", (X + 135, Y + 35), nets={1: "+V_BRUT", 3: "+15V", 2: "GND"}))
two(S6, "C603", "C", "330n", X + 115, Y + 60, "+V_BRUT", "GND")
two(S6, "C604", "CP", "22µ 25 V", X + 160, Y + 60, "+15V", "GND")
S6.add(Part("D614", "D", "1N4007", (X + 180, Y + 60), rotation=90, nets={1: "GND", 2: "+15V"}))
S6.add(Part("U602", "79XX", "LM7915", (X + 135, Y + 85), nets={2: "-V_BRUT", 3: "-15V", 1: "GND"}))
two(S6, "C605", "CP", "2.2µ 35 V", X + 115, Y + 105, "GND", "-V_BRUT")
two(S6, "C606", "CP", "22µ 25 V", X + 160, Y + 105, "GND", "-15V")
S6.add(Part("D615", "D", "1N4007", (X + 180, Y + 105), rotation=90, nets={1: "-15V", 2: "GND"}))
for i, (n, x) in enumerate((("GND", X + 200), ("+V_BRUT", X + 215), ("-V_BRUT", X + 230))):
    S6.add(Part(f"#FLG06{i + 1:02d}", "PWR_FLAG", "PWR_FLAG", (x, Y + 100), nets={1: n}))
S6.note("Transfo réservé aux ±15 V analogiques (≈ 60 mA) ; le 5 V et le robot viennent du module 24 V.", X + 5, Y + 115, 1.4)

X, Y = 305, 15
S6.frame(X, Y, X + 270, Y + 200, "Microcontrôleur (NUCLEO-G474RE)")
nuc = {n: n for n in NUC_L + NUC_R}
nuc.update({"E5V": "+5V", "3V3": "+3V3", "GND": "GND", "SCL": "I2C_SCL", "SDA": "I2C_SDA", "SCK": "SPI_SCK",
            "MOSI": "SPI_MOSI", "MISO": None, "ENV": "ENV_ADC"})
for i in range(1, 10):
    nuc[f"SENSE{i}"] = f"SENSE{i}"
for i in range(1, 5):
    nuc[f"BIAS{i}"] = f"BIAS_ADC{i}"
S6.add(Part("A601", "NUCLEO_G474RE", "NUCLEO-G474RE", (X + 130, Y + 90), nets=nuc))
two(S6, "R601", "R", "4.7k", X + 20, Y + 160, "+3V3", "I2C_SCL")
two(S6, "R602", "R", "4.7k", X + 40, Y + 160, "+3V3", "I2C_SDA")
two(S6, "R618", "R", "10k", X + 60, Y + 160, "+3V3", "MOT_FAULT")
two(S6, "R619", "R", "10k", X + 80, Y + 160, "+3V3", "PCA_OE")
S6.note("USB : la traversée de façade NAUSB-W relie le port ST-LINK de la NUCLEO (programmation et port série).",
        X + 5, Y + 195, 1.4)

X, Y = 15, 145
S6.frame(X, Y, X + 280, Y + 120, "Interface : écran, encodeur, pédalier")
S6.add(Part("J601", "TFT_ST7789", "TFT 2,4\" SPI", (X + 40, Y + 45),
            nets={1: "GND", 2: "+3V3", 3: "SPI_SCK", 4: "SPI_MOSI", 5: "TFT_RST", 6: "TFT_DC", 7: "CS_TFT", 8: "+3V3"}))
S6.add(Part("SW601", "EC11", "EC11", (X + 110, Y + 40), nets={"A": "ENC_A", "C": "GND", "B": "ENC_B", "S1": "ENC_SW", "S2": "GND"}))
for i, n in enumerate(("ENC_A", "ENC_B", "ENC_SW")):
    two(S6, f"R{603 + i}", "R", "10k", X + 140 + i * 15, Y + 30, "+3V3", n)
    two(S6, f"C{607 + i}", "C", "10n", X + 140 + i * 15, Y + 60, n, "GND")
S6.add(Part("J602", "JACK_TRS", "Pédalier", (X + 25, Y + 95), nets={"T": "FS1_IN", "R": "FS2_IN", "S": "GND"}))
for i, (a, b) in enumerate((("FS1_IN", "FS1"), ("FS2_IN", "FS2"))):
    S6.add(Part(f"R{608 + i}", "R", "1k", (X + 60 + i * 50, Y + 92), rotation=90, nets={1: a, 2: b}))
    two(S6, f"R{606 + i}", "R", "10k", X + 80 + i * 50, Y + 75, "+3V3", b)
    two(S6, f"C{610 + i}", "C", "100n", X + 80 + i * 50, Y + 105, b, "GND")

X, Y = 15, 275
S6.frame(X, Y, X + 280, Y + 120, "MIDI IN et THRU")
S6.add(Part("J603", "DIN5", "MIDI IN", (X + 20, Y + 45), nets={4: "MIDI_4", 2: None, 5: "MIDI_IN_K"}))
S6.add(Part("R610", "R", "220", (X + 45, Y + 42), rotation=90, nets={1: "MIDI_4", 2: "MIDI_IN_A"}))
S6.add(Part("D605", "D", "1N4148", (X + 60, Y + 70), nets={1: "MIDI_IN_K", 2: "MIDI_IN_A"}))
S6.add(Part("U605", "6N138", "6N138", (X + 110, Y + 50),
            nets={2: "MIDI_IN_A", 3: "MIDI_IN_K", 1: None, 4: None, 8: "+5V", 7: "OPTO_B", 6: "MIDI_RX", 5: "GND"}))
two(S6, "R611", "R", "10k", X + 150, Y + 80, "OPTO_B", "GND")
two(S6, "R612", "R", "1k", X + 165, Y + 30, "+3V3", "MIDI_RX")
S6.add(Part("J604", "DIN5", "MIDI THRU", (X + 200, Y + 45), nets={4: "THRU_4", 2: "GND", 5: "THRU_5"}))
two(S6, "R613", "R", "33", X + 235, Y + 30, "+3V3", "THRU_4")
two(S6, "R614", "R", "10", X + 250, Y + 60, "MIDI_TX", "THRU_5")
S6.note("Sortie MIDI en 3,3 V (33 Ω et 10 Ω, spécification MIDI 1.0 à 3,3 V).", X + 5, Y + 115, 1.4)

X, Y = 305, 225
S6.frame(X, Y, X + 270, Y + 170, "Mesure du courant des 6L6GC (gain 21)")
for i, t in enumerate(("V7", "V8", "V9", "V10")):
    x = X + 15 + i * 65
    n = 615 + i * 6
    S6.add(Part(f"R{n}", "R", "10k", (x + 5, Y + 30), rotation=90, nets={1: f"{t}_K", 2: f"BS{i + 1}_F"}))
    two(S6, f"C{612 + i}", "C", "100n", x + 10, Y + 60, f"BS{i + 1}_F", "GND")
    S6.add(Part(f"D{606 + 2 * i}", "D", "BAT54", (x + 25, Y + 50), rotation=90, nets={1: f"BS{i + 1}_F", 2: "+3V3"}))
    S6.add(Part(f"D{607 + 2 * i}", "D", "BAT54", (x + 40, Y + 50), rotation=90, nets={1: "GND", 2: f"BS{i + 1}_F"}))
    u = {0: (1, {3: "BS1_F", 2: "BS1_N", 1: "BIAS_ADC1"}), 1: (2, {5: "BS2_F", 6: "BS2_N", 7: "BIAS_ADC2"}),
         2: (3, {10: "BS3_F", 9: "BS3_N", 8: "BIAS_ADC3"}), 3: (4, {12: "BS4_F", 13: "BS4_N", 14: "BIAS_ADC4"})}[i]
    S6.add(Part("U606", "MCP6004", "MCP6004", (x + 25, Y + 95), unit=u[0], nets=u[1]))
    two(S6, f"R{n + 1}", "R", "1k", x + 10, Y + 130, f"BS{i + 1}_N", "GND")
    two(S6, f"R{n + 2}", "R", "20k", x + 30, Y + 130, f"BIAS_ADC{i + 1}", f"BS{i + 1}_N")
S6.add(Part("U606", "MCP6004", "MCP6004", (X + 250, Y + 150), unit=5, nets={4: "+3V3", 11: "GND"}))

X, Y = 585, 15
S6.frame(X, Y, X + 238, Y + 120, "Alimentation 24 V : robot et 5 V (module secteur)")
S6.add(Part("F601", "FUSE", "T1 A", (X + 30, Y + 35), nets={1: "L_SW", 2: "SMPS_L"}))
S6.add(Part("U604", "SMPS_MOD", "IRM-60-24ST", (X + 85, Y + 45), nets={"L": "SMPS_L", "N": "N_SW", "V+": "+24V", "V-": "GND"}))
two(S6, "C620", "CP", "470µ 35 V", X + 130, Y + 50, "+24V", "GND")
S6.add(Part("U603", "BUCK_MOD", "LM2596 → 5,0 V", (X + 190, Y + 50), nets={1: "+24V", 2: "GND", 3: "+5V", 4: "GND"}))
S6.note("+5V : moteurs des pots, LED des LDR, relais, NUCLEO (E5V). +3V3 : sortie de la NUCLEO (≈ 300 mA sur 500 mA).",
        X + 5, Y + 108, 1.4)
S6.note("Le 0 V du module rejoint la masse de commande : aucun courant de moteur ne passe par la masse audio.", X + 5, Y + 115, 1.4)

X, Y = 585, 145
S6.frame(X, Y, X + 238, Y + 120, "Ethernet vers la régie (W5500 sur SPI2)")
S6.add(Part("U608", "W5500_MOD", "Module W5500", (X + 80, Y + 50),
            nets={1: "+3V3", 2: "GND", 3: "ETH_RST", 4: "ETH_INT", 5: "ETH_SCK", 6: "ETH_MOSI", 7: "ETH_MISO", 8: "ETH_CS"}))
two(S6, "R620", "R", "10k", X + 150, Y + 40, "+3V3", "ETH_INT")
two(S6, "C621", "CP", "47µ 10 V", X + 170, Y + 55, "+3V3", "GND")
two(S6, "C622", "C", "100n", X + 185, Y + 55, "+3V3", "GND")
S6.note("RJ45 du module relié par un cordon court à la traversée etherCON NE8FDP de la face arrière.", X + 5, Y + 108, 1.4)
S6.note("Câble UTP vers la régie : l'Ethernet est isolé par transformateur, sans boucle de masse avec l'audio.", X + 5, Y + 115, 1.4)

X, Y = 585, 275
S6.frame(X, Y, X + 238, Y + 120, "Bus CAN et 24 V vers le robot (M12, brochage CANopen)")
S6.add(Part("U607", "CAN_MOD", "SN65HVD230", (X + 55, Y + 50),
            nets={1: "+3V3", 2: "GND", 3: "CAN_TX", 4: "CAN_RX", 5: "CAN_H", 6: "CAN_L"}))
S6.add(Part("F602", "FUSE", "PTC 2,5 A", (X + 120, Y + 30), nets={1: "+24V", 2: "ROBOT_24V"}))
S6.add(Part("J605", "M12_5", "Robot", (X + 185, Y + 55),
            nets={1: "CHASSIS", 2: "ROBOT_24V", 3: "GND", 4: "CAN_H", 5: "CAN_L"}))
S6.note("500 kbit/s ; 120 Ω sur le module et sur le dernier servo. Adresses : 1 radial, 2 distance, 3 angle.", X + 5, Y + 108, 1.4)
S6.note("Blindage du câble à la face arrière par le corps de l'embase ; paire torsadée pour CAN_H et CAN_L.", X + 5, Y + 115, 1.4)

# =================================================================================================
# 7. Commandes : moteurs, capteurs, LED des LDR, bobines des relais
# =================================================================================================
S7 = P.sheet(Sheet("Commandes", "commandes.kicad_sch", "A1", "Moteurs des pots, capteurs de position, LDR et relais"))
POTS = [("RV201", "ALPS_2G", "OD Gain"), ("RV202", "ALPS_2G", "Normal Gain"), ("RV301", "ALPS_2G", "Treble"),
        ("RV302", "ALPS_2G", "Bass"), ("RV303", "ALPS_2G", "Mid"), ("RV304", "ALPS_2G", "Master OD"),
        ("RV305", "ALPS_2G", "Master Normal"), ("RV306", "ALPS_2G", "Presence"), ("RV307", "ALPS_2G", "Depth")]
VALS = {"RV201": "100k lin (OD Gain)", "RV202": "100k lin (Normal Gain)", "RV301": "20k lin (Treble)",
        "RV302": "100k log (Bass)", "RV303": "10k log (Mid)", "RV304": "100k log (Master OD)",
        "RV305": "100k log (Master Normal)", "RV306": "20k lin (Presence)", "RV307": "100k lin (Depth)"}
X, Y = 15, 15
S7.frame(X, Y, X + 560, Y + 175, "Pilotage des moteurs : 2 × PCA9685 (PWM I²C) et 5 × DRV8833")
pca_out = {}
for k in range(2):
    ch = {}
    for j in range(16):
        g = k * 16 + j
        m, side = g // 2 + 1, g % 2 + 1
        ch[{0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 15, 9: 16, 10: 17, 11: 18, 12: 19, 13: 20, 14: 21, 15: 22}[j]] = \
            f"MOT{m}_IN{side}" if m <= 9 else None
    nets = {28: "+3V3", 26: "I2C_SCL", 27: "I2C_SDA", 23: "PCA_OE", 25: "GND", 1: "+3V3" if k else "GND", 2: "GND", 3: "GND",
            4: "GND", 5: "GND", 24: "GND", 14: "GND"}
    nets.update(ch)
    S7.add(Part(f"U70{1 + k}", "PCA9685", "PCA9685", (X + 50 + k * 110, Y + 75), nets=nets))
for d in range(5):
    ma, mb = 2 * d + 1, 2 * d + 2
    nets = {1: "+5V", 2: "GND", 3: f"MOT{ma}_IN1", 4: f"MOT{ma}_IN2", 5: f"MOT{mb}_IN1" if mb <= 9 else "GND",
            6: f"MOT{mb}_IN2" if mb <= 9 else "GND", 7: "MOT_EN", 8: "MOT_FAULT", 9: f"MOT{ma}_A", 10: f"MOT{ma}_B",
            11: f"MOT{mb}_A" if mb <= 9 else None, 12: f"MOT{mb}_B" if mb <= 9 else None}
    S7.add(Part(f"U70{3 + d}", "DRV8833_MOD", "DRV8833", (X + 285 + (d % 3) * 92, Y + 50 + (d // 3) * 70), nets=nets))
S7.note("MOTn_IN1/IN2 : canaux PCA9685 2n-2 et 2n-1 ; MOT_EN coupe les ponts au repos (moteurs en roue libre).", X + 5, Y + 170, 1.4)

X, Y = 15, 200
S7.frame(X, Y, X + 560, Y + 120, "Moteurs (100 nF aux bornes) et pistes capteur (filtre 1 k / 100 nF vers l'ADC)")
for m, (ref, sym, name) in enumerate(POTS, start=1):
    x = X + 15 + (m - 1) * 60
    mot_unit = 6 if sym == "ALPS_5G" else 3
    sense_unit = 5 if sym == "ALPS_5G" else 2
    sp = {2: (4, 5, 6), 5: (13, 14, 15)}[sense_unit]
    S7.add(Part(ref, sym, VALS[ref], (x + 5, Y + 30), unit=mot_unit, nets={"M+": f"MOT{m}_A", "M-": f"MOT{m}_B"}))
    two(S7, f"C{700 + m}", "C", "100n", x + 22, Y + 30, f"MOT{m}_A", f"MOT{m}_B")
    S7.add(Part(ref, sym, VALS[ref], (x + 5, Y + 80), unit=sense_unit, nets={sp[2]: "+3V3", sp[1]: f"POT{m}_S", sp[0]: "GND"}))
    two(S7, f"R{700 + m}", "R", "1k", x + 25, Y + 75, f"POT{m}_S", f"SENSE{m}")
    two(S7, f"C{710 + m}", "C", "100n", x + 40, Y + 95, f"SENSE{m}", "GND")
    S7.note(name, x, Y + 112, 1.3)

X, Y = 15, 330
S7.frame(X, Y, X + 560, Y + 230, "LED des LDR et bobines des relais : 2 × MCP23017 et 3 × ULN2803")
LDRS = [("LDR201", "Crunch"), ("LDR202", "Clean"), ("LDR203", "Bright"), ("LDR204", "Canal clair coupé"),
        ("LDR205", "Liaison directe"), ("LDR206", "Étage sup."), ("LDR207", "LDR1 (clean)"), ("LDR208", "Clipper 10 k"),
        ("LDR209", "Clipper 4,4 k"), ("LDR210", "LDR2 (OD)"), ("LDR301", "Poussée"), ("LDR302", "LDR3 master OD"),
        ("LDR303", "LDR4 master N"), ("LDR304", "Mute")]
RELS = [("K201", "Découplages réduits"), ("K202", "Liaison 2,2 nF"), ("K501", "Diodes LED"), ("K502", "Asymétrique"),
        ("K503", "TS en service"), ("K504", "Insert en service")]
loads = [(r, "LDR") for r, _ in LDRS] + [(r, "REL") for r, _ in RELS]
gp = [21, 22, 23, 24, 25, 26, 27, 28, 1, 2, 3, 4, 5, 6, 7, 8]
for k in range(2):
    nets = {9: "+3V3", 12: "I2C_SCL", 13: "I2C_SDA", 15: "+3V3" if k else "GND", 16: "GND", 17: "GND", 18: "+3V3",
            20: None, 19: None, 11: None, 14: None, 10: "GND"}
    for j in range(16):
        g = k * 16 + j
        nets[gp[j]] = f"DRV{g + 1}" if g < 24 else None
    S7.add(Part(f"U70{8 + k}", "MCP23017", "MCP23017", (X + 45, Y + 60 + k * 110), nets=nets))
for u in range(3):
    nets = {9: "GND", 10: "+5V"}
    for i in range(1, 9):
        g = u * 8 + i
        nets[i] = f"DRV{g}"
        nets[19 - i] = f"SINK{g}" if g <= len(loads) else None
    S7.add(Part(f"U71{u}", "ULN2803A", "ULN2803A", (X + 140, Y + 45 + u * 65), nets=nets))
for g, (ref, kind) in enumerate(loads, start=1):
    col, rr = (g - 1) % 10, (g - 1) // 10
    x, y = X + 210 + col * 34, Y + 40 + rr * 70
    if kind == "LDR":
        two(S7, f"R{720 + g}", "R", "220", x, y, "+5V", f"LED{g}_A")
        S7.add(Part(ref, "VTL5C1", "VTL5C1", (x + 14, y + 22), unit=2, nets={1: f"LED{g}_A", 2: f"SINK{g}"}))
    else:
        S7.add(Part(ref, "RELAY_2C", "G6K-2 5 V", (x + 8, y + 15), unit=3, nets={7: "+5V", 8: f"SINK{g}"}))
names = dict(LDRS + RELS)
legend = "  ".join(f"{g}:{ref} {names[ref]}" for g, (ref, _) in enumerate(loads, start=1))
S7.note("Affectation DRVn / SINKn : " + legend[:150], X + 5, Y + 215, 1.25)
S7.note(legend[150:], X + 5, Y + 222, 1.25)

P.root_texts += [
    ("Tête 100 W pilotable — famille SLO-100", 20, 25, 3.0, True),
    ("Révision 0.1 du 7 novembre 2026, générée par slo_sch.py et vérifiée contre la simulation (check_sch.py).", 20, 33, 1.6, False),
    ("Les feuilles sont reliées par des étiquettes globales : B+1 à B+5, B+BUF, B+WCF, B+EXT, HEAT_*, BIAS_*, signaux de pilotage.", 20, 39, 1.6, False),
    ("Chaque broche porte le nom de son nœud ; les noms suivent la simulation SPICE (voir NETMAP dans check_sch.py).", 20, 45, 1.6, False),
    ("Haute tension mortelle (jusqu'à 535 V à vide). Ne pas intervenir sous tension ; décharger les condensateurs.", 20, 262, 2.0, True),
]

if __name__ == "__main__":
    P.write(sys.argv[1] if len(sys.argv) > 1 else "out")
    print("written", sum(len(s.parts) for s in P.sheets), "placed units on", len(P.sheets), "sheets")
