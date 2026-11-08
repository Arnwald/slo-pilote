"""Schematic of the pilotable SLO-family head, generated for KiCad 7+.

python3 slo_sch.py <outdir>
Net names follow the SPICE model (spice/slo.py, variant "mod") through NETMAP in check_sch.py.
"""
import sys

import kgen
from kgen import Part, Project, Sheet, ic_symbol, opamp_units, Sym, Unit, Pin, rect, poly, text, circle

P = Project("slo-pilote", "Tête 100 W pilotable, famille SLO-100", rev="0.2", date="2026-11-08",
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
P.symbol(ic_symbol("AS2164", "U",
                   [(2, "IIN1", "input"), (3, "VC1", "input"), (7, "IIN2", "input"), (6, "VC2", "input"),
                    (10, "IIN3", "input"), (11, "VC3", "input"), (15, "IIN4", "input"), (14, "VC4", "input"),
                    (1, "MODE", "input")],
                   [(4, "IOUT1", "output"), (5, "IOUT2", "output"), (12, "IOUT3", "output"), (13, "IOUT4", "output"),
                    None, (16, "VCC", "power_in"), (8, "GND", "power_in"), (9, "VEE", "power_in")], 15.24,
                   "Quadruple VCA (Alfa AS2164, brochage SSM2164/V2164), DIP-16 ; -33 mV/dB, 0 V = 0 dB"))
P.symbol(ic_symbol("MCP4822", "U", [(1, "VDD", "power_in"), (2, "CS", "input"), (3, "SCK", "input"), (4, "SDI", "input")],
                   [(8, "VOUTA", "output"), (6, "VOUTB", "output"), (5, "LDAC", "input"), (7, "VSS", "power_in")], 12.7,
                   "CNA double 12 bits SPI, DIP-8"))
P.symbol(ic_symbol("MCP3208", "U",
                   [(1, "CH0", "input"), (2, "CH1", "input"), (3, "CH2", "input"), (4, "CH3", "input"),
                    (5, "CH4", "input"), (6, "CH5", "input"), (7, "CH6", "input"), (8, "CH7", "input")],
                   [(16, "VDD", "power_in"), (15, "VREF", "input"), (13, "CLK", "input"), (11, "DIN", "input"),
                    (12, "DOUT", "output"), (10, "CS", "input"), (14, "AGND", "power_in"), (9, "DGND", "power_in")], 15.24,
                   "CAN 8 voies 12 bits SPI, DIP-16"))
P.symbol(ic_symbol("MCP23017", "U",
                   [(9, "VDD", "power_in"), (12, "SCL", "input"), (13, "SDA", "bidirectional"), (15, "A0", "input"),
                    (16, "A1", "input"), (17, "A2", "input"), (18, "RESET", "input"), (20, "INTA", "output"),
                    (19, "INTB", "output"), (11, "NC"), (14, "NC"), (10, "VSS", "power_in")],
                   [(21, "GPA0"), (22, "GPA1"), (23, "GPA2"), (24, "GPA3"), (25, "GPA4"), (26, "GPA5"), (27, "GPA6"),
                    (28, "GPA7"), (1, "GPB0"), (2, "GPB1"), (3, "GPB2"), (4, "GPB3"), (5, "GPB4"), (6, "GPB5"),
                    (7, "GPB6"), (8, "GPB7")], 20.32, "Extenseur 16 E/S I2C, MCP23017-E/SP (DIP-28)"))
P.symbol(ic_symbol("ULN2803A", "U", [(i, f"I{i}", "input") for i in range(1, 9)] + [(9, "GND", "power_in")],
                   [(19 - i, f"O{i}", "open_collector") for i in range(1, 9)] + [(10, "COM", "passive")], 15.24,
                   "8 Darlington, diodes de roue libre vers COM, DIP-18"))
P.symbol(ic_symbol("6N138", "U", [(2, "A"), (3, "K"), (1, "NC"), (4, "NC")],
                   [(8, "VCC", "power_in"), (7, "VB"), (6, "VO", "open_collector"), (5, "GND", "power_in")], 12.7,
                   "Optocoupleur MIDI, DIP-8"))
P.symbol(ic_symbol("78XX", "U", [(1, "IN", "power_in")], [(3, "OUT", "power_out"), (2, "GND", "power_in")], 10.16, "Regulateur positif TO-220"))
P.symbol(ic_symbol("79XX", "U", [(2, "IN", "power_in")], [(3, "OUT", "power_out"), (1, "GND", "power_in")], 10.16, "Regulateur negatif TO-220"))
P.symbol(ic_symbol("78L09", "U", [(3, "IN", "power_in")], [(1, "OUT", "power_out"), (2, "GND", "power_in")], 10.16,
                   "Regulateur 9 V 100 mA TO-92 (1 sortie, 2 masse, 3 entree)"))
P.symbol(ic_symbol("BUCK_MOD", "U", [(1, "IN+", "power_in"), (2, "IN-", "power_in")],
                   [(3, "OUT+", "power_out"), (4, "OUT-", "power_in")], 12.7, "Module abaisseur a picots"))
P.symbol(ic_symbol("SMPS_MOD", "PS", [("L", "AC/L", "power_in"), ("N", "AC/N", "power_in")],
                   [("V+", "+V", "power_out"), ("V-", "-V", "power_in")], 15.24,
                   "Module secteur encapsule 24 V 60 W a bornier (type Mean Well IRM-60-24ST)"))
P.symbol(ic_symbol("M12_5", "J", [(1, "SH"), (2, "V+"), (3, "V-"), (4, "CAN_H"), (5, "CAN_L")], [], 10.16,
                   "Embase M12 code A 5 points, brochage CANopen (CiA 303-1)"))
# Raspberry Pi 4 B : 40-pin header, odd pins on the left, even pins on the right
RPI_L = [(1, "3V3", "power_out"), (3, "GPIO2/SDA1"), (5, "GPIO3/SCL1"), (7, "GPIO4"), (9, "GND", "power_in"),
         (11, "GPIO17"), (13, "GPIO27"), (15, "GPIO22"), (17, "3V3", "power_out"), (19, "GPIO10/MOSI0"),
         (21, "GPIO9/MISO0"), (23, "GPIO11/SCLK0"), (25, "GND", "power_in"), (27, "ID_SD"), (29, "GPIO5"),
         (31, "GPIO6"), (33, "GPIO13"), (35, "GPIO19/MISO1"), (37, "GPIO26"), (39, "GND", "power_in")]
RPI_R = [(2, "5V", "power_in"), (4, "5V", "power_in"), (6, "GND", "power_in"), (8, "GPIO14/TXD0"), (10, "GPIO15/RXD0"),
         (12, "GPIO18"), (14, "GND", "power_in"), (16, "GPIO23"), (18, "GPIO24"), (20, "GND", "power_in"),
         (22, "GPIO25"), (24, "GPIO8/CE0"), (26, "GPIO7/CE1"), (28, "ID_SC"), (30, "GND", "power_in"),
         (32, "GPIO12"), (34, "GND", "power_in"), (36, "GPIO16"), (38, "GPIO20/MOSI1"), (40, "GPIO21/SCLK1")]
P.symbol(ic_symbol("RPI4_40P", "A", [(n, nm, t[0] if t else "bidirectional") for n, nm, *t in RPI_L],
                   [(n, nm, t[0] if t else "bidirectional") for n, nm, *t in RPI_R], 30.48,
                   "Raspberry Pi 4 modele B, connecteur 40 broches (numeros physiques)"))
P.symbol(ic_symbol("CAN_HAT", "A", [(1, "3V3", "power_in"), (2, "GND", "power_in"), (3, "SCLK"), (4, "MOSI"), (5, "MISO"),
                                    (6, "CE0"), (7, "INT", "output")],
                   [("H", "CAN_H", "bidirectional"), ("L", "CAN_L", "bidirectional"), ("G", "GND_B", "passive")], 15.24,
                   "Waveshare RS485 CAN HAT (MCP2515 12 MHz + SN65HVD230, 120 ohms) enfiche sur le Pi ; RS485 inutilise"))
P.symbol(ic_symbol("MOTORON_M2T", "U", [(1, "VIN", "power_in"), (2, "VDD", "power_in"), (3, "SDA", "bidirectional"),
                                        (4, "SCL", "input"), (5, "GND", "power_in")],
                   [(6, "M1A", "output"), (7, "M1B", "output"), (8, "M2A", "output"), (9, "M2B", "output")], 15.24,
                   "Pololu Motoron M2T256 : 2 moteurs CC, I2C, 4,5-48 V, 1,8 A ; numerotation generique, brochage a verifier"))
P.symbol(ic_symbol("DS18B20", "U", [(3, "VDD", "power_in"), (2, "DQ", "bidirectional")], [(1, "GND", "power_in")], 10.16,
                   "Sonde de temperature 1-Wire TO-92 (1 masse, 2 donnee, 3 alimentation)"))
P.symbol(ic_symbol("TFT_ST7789", "J", [(1, "GND"), (2, "VCC"), (3, "SCL"), (4, "SDA"), (5, "RES"), (6, "DC"), (7, "CS"), (8, "BLK")],
                   [], 12.7, "Ecran SPI 2,4 pouces 240 x 320"))
P.symbol(ic_symbol("EC11", "SW", [("A", "A"), ("C", "C"), ("B", "B")], [("S1", "S1"), ("S2", "S2")], 10.16,
                   "Encodeur rotatif a poussoir"))
P.symbol(Sym("OPA2134", "U", opamp_units((3, 2, 1), (5, 6, 7)), pin_names_hidden=False, ref_at=(1.27, 6.35), val_at=(1.27, -6.35),
             desc="Double ampli op JFET faible bruit, DIP-8"))
P.symbol(Sym("NJM4558", "U", opamp_units((3, 2, 1), (5, 6, 7)), pin_names_hidden=False, ref_at=(1.27, 6.35), val_at=(1.27, -6.35),
             desc="Double ampli op 4558 (NJM4558D), DIP-8 : Tube Screamer et HM-2"))
P.symbol(Sym("LM393", "U", opamp_units((3, 2, 1), (5, 6, 7)), pin_names_hidden=False, ref_at=(1.27, 6.35), val_at=(1.27, -6.35),
             desc="Double comparateur a collecteur ouvert, DIP-8"))
q4 = opamp_units((3, 2, 1), (5, 6, 7), (4, 11))
q4c = opamp_units((10, 9, 8), (12, 13, 14), (4, 11))
P.symbol(Sym("MCP6004", "U", [q4[0], q4[1], q4c[0], q4c[1], q4[2]], pin_names_hidden=False, ref_at=(1.27, 6.35),
             val_at=(1.27, -6.35), desc="Quadruple ampli op rail-a-rail 3,3 V, DIP-14"))
P.symbol(Sym("TL074", "U", [q4[0], q4[1], q4c[0], q4c[1], q4[2]], pin_names_hidden=False, ref_at=(1.27, 6.35),
             val_at=(1.27, -6.35), desc="Quadruple ampli op JFET, DIP-14"))


ADG406_S = [(19 + i if i < 8 else 11 - (i - 8), f"S{i + 1}") for i in range(16)]
P.symbol(ic_symbol("ADG406", "U", ADG406_S,
                   [(28, "D"), None, (17, "A0", "input"), (16, "A1", "input"), (15, "A2", "input"), (14, "A3", "input"),
                    (18, "EN", "input"), None, (1, "VDD", "power_in"), (27, "VSS", "power_in"), (12, "GND", "power_in"),
                    (2, "NC"), (3, "NC"), (13, "NC")], 15.24,
                   "Multiplexeur analogique 16:1, +/-15 V, entrees TTL, 50 ohms typ. (ADG406BNZ, DIP-28)"))
P.symbol(ic_symbol("ADG408", "U", [(4, "S1"), (5, "S2"), (6, "S3"), (7, "S4"), (12, "S5"), (11, "S6"), (10, "S7"), (9, "S8")],
                   [(8, "D"), None, (1, "A0", "input"), (16, "A1", "input"), (15, "A2", "input"), (2, "EN", "input"), None,
                    (13, "VDD", "power_in"), (3, "VSS", "power_in"), (14, "GND", "power_in")], 15.24,
                   "Multiplexeur analogique 8:1, +/-15 V, entrees TTL (ADG408BNZ, DIP-16)"))
P.symbol(ic_symbol("74HC595", "U", [(14, "SER", "input"), (11, "SRCLK", "input"), (12, "RCLK", "input"),
                                    (10, "~{SRCLR}", "input"), (13, "~{OE}", "input"), None, (16, "VCC", "power_in"),
                                    (8, "GND", "power_in")],
                   [(15, "QA", "output"), (1, "QB", "output"), (2, "QC", "output"), (3, "QD", "output"), (4, "QE", "output"),
                    (5, "QF", "output"), (6, "QG", "output"), (7, "QH", "output"), None, (9, "QH'", "output")], 12.7,
                   "Registre a decalage 8 bits a verrou, DIP-16"))
P.symbol(ic_symbol("HDR_2x13", "J", [(2 * i + 1, str(2 * i + 1)) for i in range(13)], [(2 * i + 2, str(2 * i + 2)) for i in range(13)],
                   7.62, "Embase IDC 2 x 13 au pas de 2,54 mm (nappe)"))
P.symbol(ic_symbol("RN_SIP9", "RN", [(1, "COM")], [(i, f"R{i - 1}") for i in range(2, 10)], 7.62,
                   "Reseau de 8 resistances a point commun, SIP-9"))


def bjt_symbol(name, pnp, desc):
    g = [circle(0.635, 0, 3.175), poly([(-0.635, 1.905), (-0.635, -1.905)], 0.508),
         poly([(-0.635, 0.762), (2.54, 2.54)], 0.254), poly([(-0.635, -0.762), (2.54, -2.54)], 0.254)]
    if pnp:
        g.append(poly([(-0.635, -0.762), (0.508, -0.889), (0.127, -1.651), (-0.635, -0.762)], 0.254, "outline"))
    else:
        g.append(poly([(2.54, -2.54), (1.397, -2.413), (1.778, -1.651), (2.54, -2.54)], 0.254, "outline"))
    return Sym(name, "Q", [Unit([Pin(1, "C", 2.54, 5.08, 270, 2.54), Pin(2, "B", -5.08, 0, 0, 4.445),
                                 Pin(3, "E", 2.54, -5.08, 90, 2.54)], g)],
               pin_names_hidden=True, ref_at=(5.08, 1.27), val_at=(5.08, -1.27), desc=desc)


P.symbol(bjt_symbol("Q_NPN", False, "Transistor NPN TO-92, brochage C-B-E (BC550C)"))
P.symbol(bjt_symbol("Q_PNP", True, "Transistor PNP TO-92, brochage C-B-E (BC560C)"))


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
S3.add(Part("C308", "C", "20n 630 V", (X + 35, Y + 45), rotation=90, nets={1: "PI_DRV", 2: "PI_GB"}))
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
S3.note("PI_IN (après LDR302/303 et le mute LDR304) passe par la VCA du gate (feuille VCA) et revient en PI_DRV.", X + 5, Y + 127, 1.4)

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
# 5. Boîtier d'entrée : buffer, Tube Screamer, HM-2, sélection des chemins
# =================================================================================================
S5 = P.sheet(Sheet("Boîtier d'entrée", "boitier_entree.kicad_sch", "A1", "Buffer, Tube Screamer TS808, clone HM-2, insert"))
X, Y = 15, 15
S5.frame(X, Y, X + 200, Y + 110, "Entrée, buffer et inverseur de polarité du chemin B")
S5.add(Part("J501", "JACK_TSN", "Entrée guitare", (X + 15, Y + 40), nets={"T": "GTR_IN", "S": "GND", "TN": "GND"}))
S5.add(Part("R501", "R", "1k", (X + 45, Y + 38), rotation=90, nets={1: "GTR_IN", 2: "BUF_IN"}))
two(S5, "C501", "C", "100p", X + 60, Y + 65, "BUF_IN", "GND")
two(S5, "R502", "R", "1M", X + 72, Y + 65, "BUF_IN", "GND")
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 105, Y + 40), unit=1, nets={3: "BUF_IN", 2: "BUF_OUT", 1: "BUF_OUT"}))
S5.add(Part("R503", "R", "10k", (X + 125, Y + 72), rotation=90, nets={1: "PB_SRC", 2: "PB_INVN"}))
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 160, Y + 75), unit=2, nets={5: "GND", 6: "PB_INVN", 7: "PB_INV"}))
S5.add(Part("R504", "R", "10k", (X + 160, Y + 58), rotation=90, nets={1: "PB_INV", 2: "PB_INVN"}))
S5.add(Part("U501", "OPA2134", "OPA2134", (X + 190, Y + 40), unit=3, nets={8: "+15V", 4: "-15V"}))
S5.note("BUF_OUT attaque la TS, la HM-2, l'envoi d'insert et la détection du gate (feuille VCA).", X + 5, Y + 105, 1.4)

X, Y = 225, 15
S5.frame(X, Y, X + 360, Y + 110, "Tube Screamer TS808 d'origine (9 V) ; niveau par la VCA du chemin A")
S5.add(Part("C506", "C", "1µ film", (X + 15, Y + 30), rotation=90, nets={1: "BUF_OUT", 2: "TS_X1"}))
two(S5, "R507", "R", "10k", X + 30, Y + 60, "TS_X1", "TS_VB")
S5.add(Part("U503", "NJM4558", "NJM4558D", (X + 60, Y + 32), unit=1, nets={3: "TS_X1", 2: "TS_NF", 1: "TS_O1"}))
S5.add(Part("R508", "R", "51k", (X + 95, Y + 20), rotation=90, nets={1: "TS_O1", 2: "TS_ND"}))
two(S5, "C507", "C", "51p", X + 140, Y + 60, "TS_O1", "TS_NF")
S5.add(Part("D501", "D", "1N914", (X + 160, Y + 25), nets={1: "TS_O1", 2: "TS_NF"}))
S5.add(Part("D502", "D", "1N914", (X + 160, Y + 40), nets={1: "TS_NF", 2: "TS_O1"}))
two(S5, "R509", "R", "4.7k", X + 180, Y + 60, "TS_NF", "TS_NG")
two(S5, "C508", "C", "47n", X + 180, Y + 85, "TS_NG", "TS_VB")
S5.add(Part("R510", "R", "1k", (X + 200, Y + 32), rotation=90, nets={1: "TS_O1", 2: "TS_TA"}))
two(S5, "C509", "C", "220n", X + 215, Y + 60, "TS_TA", "TS_VB")
two(S5, "R511", "R", "169", X + 255, Y + 75, "TS_TW", "TS_TC")
two(S5, "C510", "C", "220n", X + 255, Y + 95, "TS_TC", "TS_VB")
S5.add(Part("U503", "NJM4558", "NJM4558D", (X + 285, Y + 32), unit=2, nets={5: "TS_TA", 6: "TS_TN", 7: "TS_O2"}))
two(S5, "R512", "R", "1k", X + 300, Y + 60, "TS_O2", "TS_TN")
S5.add(Part("C511", "C", "1µ film", (X + 320, Y + 32), rotation=90, nets={1: "TS_O2", 2: "TS_OUT"}))
two(S5, "R513", "R", "100k", X + 340, Y + 60, "TS_OUT", "GND")
S5.add(Part("U503", "NJM4558", "NJM4558D", (X + 340, Y + 90), unit=3, nets={8: "+9V_TS", 4: "GND"}))
S5.note("Drive (TS_ND-TS_NF, 0 à 500 k) et tone (TS_TN-TS_TA, curseur TS_TW) : échelles à 16 positions, feuille Commandes "
        "de l'entrée. R511 : 169 Ω + 50 Ω du multiplexeur = 220 Ω d'origine.", X + 5, Y + 105, 1.4)

X, Y = 15, 135
S5.frame(X, Y, X + 570, Y + 140, "HM-2 (schéma Boss MIJ) : préampli à transistors, écrêtage, zone morte germanium (9 V)")
S5.add(Part("C517", "C", "47n film", (X + 15, Y + 40), rotation=90, nets={1: "BUF_OUT", 2: "HM_N6"}))
S5.add(Part("R517", "R", "22k", (X + 35, Y + 40), rotation=90, nets={1: "HM_N6", 2: "HM_B6"}))
two(S5, "R518", "R", "100k", X + 50, Y + 75, "HM_B6", "GND")
S5.add(Part("R519", "R", "470k", (X + 70, Y + 18), rotation=90, nets={1: "HM_C6", 2: "HM_B6"}))
S5.add(Part("C518", "C", "100p", (X + 70, Y + 28), rotation=90, nets={1: "HM_C6", 2: "HM_B6"}))
S5.add(Part("Q501", "Q_NPN", "BC550C", (X + 75, Y + 50), nets={1: "HM_C6", 2: "HM_B6", 3: "HM_E6"}))
two(S5, "R520", "R", "22", X + 78, Y + 75, "HM_E6", "GND")
two(S5, "R521", "R", "10k", X + 95, Y + 30, "HM_S", "HM_C6")
two(S5, "R522", "R", "100", X + 105, Y + 70, "HM_C6", "HM_N49")
two(S5, "C519", "CP", "10µ 16 V", X + 105, Y + 95, "HM_N49", "HM_P7")
S5.add(Part("C520", "C", "47n film", (X + 125, Y + 45), rotation=90, nets={1: "HM_C6", 2: "HM_N11"}))
S5.add(Part("R523", "R", "22k", (X + 145, Y + 45), rotation=90, nets={1: "HM_N11", 2: "HM_B7"}))
two(S5, "R524", "R", "100k", X + 160, Y + 25, "HM_S", "HM_B7")
S5.add(Part("R525", "R", "470k", (X + 180, Y + 80), rotation=90, nets={1: "HM_B7", 2: "HM_C7"}))
S5.add(Part("C521", "C", "100p", (X + 180, Y + 92), rotation=90, nets={1: "HM_B7", 2: "HM_C7"}))
S5.add(Part("Q502", "Q_PNP", "BC560C", (X + 185, Y + 50), nets={1: "HM_C7", 2: "HM_B7", 3: "HM_E7"}))
two(S5, "R526", "R", "120", X + 200, Y + 25, "HM_S", "HM_E7")
two(S5, "R527", "R", "10k", X + 210, Y + 75, "HM_C7", "GND")
two(S5, "R528", "R", "68k", X + 225, Y + 25, "+9V_HM", "HM_C7")
S5.add(Part("U505", "NJM4558", "NJM4558D", (X + 260, Y + 55), unit=2, nets={5: "HM_C7", 6: "HM_NM", 7: "HM_O1B"}))
S5.add(Part("R529", "R", "220k", (X + 265, Y + 15), rotation=90, nets={1: "HM_O1B", 2: "HM_NM"}))
S5.add(Part("C522", "C", "100p", (X + 265, Y + 24), rotation=90, nets={1: "HM_O1B", 2: "HM_NM"}))
S5.add(Part("D503", "D", "1N4148", (X + 290, Y + 15), nets={1: "HM_NM", 2: "HM_O1B"}))
S5.add(Part("D504", "D", "1N4148", (X + 290, Y + 28), nets={1: "HM_O1B", 2: "HM_D45"}))
S5.add(Part("D505", "D", "1N4148", (X + 305, Y + 28), nets={1: "HM_D45", 2: "HM_NM"}))
two(S5, "C523", "C", "47n film", X + 250, Y + 90, "HM_NM", "HM_N22")
two(S5, "R530", "R", "47k", X + 250, Y + 115, "HM_N22", "HM_P10")
S5.add(Part("C524", "CP", "1µ 50 V", (X + 315, Y + 55), rotation=90, nets={1: "HM_O1B", 2: "HM_N12"}))
S5.add(Part("R531", "R", "10k", (X + 335, Y + 55), rotation=90, nets={1: "HM_N12", 2: "HM_N23"}))
S5.add(Part("D506", "D", "1N34A", (X + 355, Y + 48), nets={1: "HM_N23", 2: "HM_N30"}))
S5.add(Part("D507", "D", "1N34A", (X + 355, Y + 62), nets={1: "HM_N30", 2: "HM_N23"}))
S5.add(Part("R532", "R", "10k", (X + 375, Y + 55), rotation=90, nets={1: "HM_N30", 2: "HM_N16"}))
S5.add(Part("D508", "D", "1N4148", (X + 395, Y + 85), nets={1: "HM_N16", 2: "GND"}))
S5.add(Part("D509", "D", "1N4148", (X + 395, Y + 100), nets={1: "GND", 2: "HM_N16"}))
two(S5, "C525", "C", "1n", X + 415, Y + 90, "HM_N16", "GND")
S5.add(Part("C526", "CP", "1µ 50 V", (X + 435, Y + 55), rotation=90, nets={1: "HM_N1A", 2: "HM_N16"}))
two(S5, "R533", "R", "68k", X + 455, Y + 85, "HM_N1A", "HM_VB")
S5.add(Part("U505", "NJM4558", "NJM4558D", (X + 490, Y + 57), unit=1, nets={3: "HM_N1A", 2: "HM_O1A", 1: "HM_O1A"}))
S5.note("Q501, Q502 : BC550C et BC560C pour 2SC2240-GR et 2SA970-GR. D503-D505, D508, D509 : 1N4148 (1S2473) ; "
        "D506, D507 : germanium 1N34A (1S188FM).", X + 5, Y + 128, 1.4)
S5.note("Dist : échelle de 250 k à 16 positions (feuille Commandes de l'entrée) entre HM_P7 et HM_P10, sortie du multiplexeur à la "
        "masse. R522 : 100 Ω + 50 Ω du multiplexeur = 150 Ω d'origine.",
        X + 5, Y + 135, 1.4)

X, Y = 15, 285
S5.frame(X, Y, X + 570, Y + 140, "HM-2 : Color Mix (gyrateurs 84 Hz, 0,95 et 1,26 kHz) et sortie au niveau maximal")
S5.add(Part("R534", "R", "3.3k", (X + 20, Y + 40), rotation=90, nets={1: "HM_O1A", 2: "HM_P14"}))
S5.add(Part("U506", "NJM4558", "NJM4558D", (X + 60, Y + 42), unit=1, nets={3: "HM_P14", 2: "HM_P13", 1: "HM_O3A"}))
S5.add(Part("R535", "R", "3.3k", (X + 65, Y + 15), rotation=90, nets={1: "HM_O3A", 2: "HM_P13"}))
S5.add(Part("C527", "C", "470p", (X + 65, Y + 25), rotation=90, nets={1: "HM_O3A", 2: "HM_P13"}))
for (cs, cv, cg, cgv, rb, rbv, rs, uref, unit, pins, xi, wiper, tag) in (
        ("C528", "1.5µ 35 V", "C529", "68n", "R536", "120k", "R537", "U506", 2, (5, 6, 7), 175, "HM_WL", "1"),
        ("C530", "0.15µ 35 V", "C531", "6.8n", "R538", "100k", "R539", "U507", 1, (3, 2, 1), 265, "HM_WH", "2"),
        ("C532", "0.1µ 35 V", "C533", "4.7n", "R540", "120k", "R541", "U507", 2, (5, 6, 7), 355, "HM_WH", "3")):
    x = X + xi
    two(S5, cs, "CP", cv, x, Y + 30, wiper, f"HM_X{tag}")
    two(S5, cg, "C", cgv + " film", x, Y + 60, f"HM_X{tag}", f"HM_G{tag}")
    two(S5, rb, "R", rbv, x + 15, Y + 90, f"HM_G{tag}", "HM_VB")
    S5.add(Part(rs, "R", "270", (x + 30, Y + 45), rotation=90, nets={1: f"HM_X{tag}", 2: f"HM_O{tag}"}))
    S5.add(Part(uref, "NJM4558", "NJM4558D", (x + 55, Y + 75), unit=unit,
                nets={pins[0]: f"HM_G{tag}", pins[1]: f"HM_O{tag}", pins[2]: f"HM_O{tag}"}))
S5.add(Part("C534", "CP", "10µ 16 V", (X + 445, Y + 42), rotation=90, nets={1: "HM_O3A", 2: "HM_N34"}))
S5.add(Part("R542", "R", "10k", (X + 465, Y + 42), rotation=90, nets={1: "HM_N34", 2: "HM_LV"}))
two(S5, "R543", "R", "10k", X + 485, Y + 70, "HM_LV", "GND")
S5.add(Part("C535", "C", "1µ film", (X + 505, Y + 42), rotation=90, nets={1: "HM_LV", 2: "HM_OUT"}))
two(S5, "R544", "R", "100k", X + 525, Y + 70, "HM_OUT", "GND")
S5.note("Color Mix : échelles de 10 k à 15 positions entre les entrées + et − de U506A (feuille Commandes de l'entrée), sorties "
        "des multiplexeurs vers les gyrateurs. Gyrateurs : 270 Ω (+ 50 Ω du multiplexeur) × 120 k / 100 k / 120 k, mêmes L et R série "
        "qu'à l'origine.",
        X + 5, Y + 121, 1.4)
S5.note("À fond (curseur côté −) : +20 dB à 84 Hz, +22 dB à 0,95 et 1,26 kHz (spice/hm2.py). Level fixé au maximum : "
        "10 k + 10 k ; le niveau passe par la VCA du chemin B.", X + 5, Y + 128, 1.4)

X, Y = 595, 15
S5.frame(X, Y, X + 230, Y + 180, "Sélection des chemins : TS, insert, polarité")
S5.add(Part("K501", "RELAY_2C", "G6K-2 5 V", (X + 30, Y + 40), unit=1, nets={1: "PA_IN", 2: "BUF_OUT", 3: "TS_OUT"}))
S5.add(Part("K501", "RELAY_2C", "G6K-2 5 V", (X + 30, Y + 70), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("K502", "RELAY_2C", "G6K-2 5 V", (X + 100, Y + 40), unit=1, nets={1: "PB_SRC", 2: "HM_OUT", 3: "RET_IN"}))
S5.add(Part("K502", "RELAY_2C", "G6K-2 5 V", (X + 100, Y + 70), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("K503", "RELAY_2C", "G6K-2 5 V", (X + 170, Y + 40), unit=1, nets={1: "PB_IN", 2: "PB_SRC", 3: "PB_INV"}))
S5.add(Part("K503", "RELAY_2C", "G6K-2 5 V", (X + 170, Y + 70), unit=2, nets={4: None, 5: None, 6: None}))
S5.add(Part("R545", "R", "100", (X + 30, Y + 110), rotation=90, nets={1: "BUF_OUT", 2: "SEND_T"}))
S5.add(Part("J502", "JACK_TS", "Send", (X + 75, Y + 112), nets={"T": "SEND_T", "S": "GND"}))
S5.add(Part("J503", "JACK_TS", "Return", (X + 75, Y + 140), nets={"T": "RET_IN", "S": "GND"}))
two(S5, "R546", "R", "100k", X + 110, Y + 150, "RET_IN", "GND")
S5.note("Au repos : chemin A = guitare tamponnée (TS hors service), chemin B = clone HM-2, polarité directe.", X + 5, Y + 166, 1.4)
S5.note("L'insert reçoit la guitare tamponnée : une HM-2 du commerce s'y compare directement au clone.", X + 5, Y + 173, 1.4)

X, Y = 595, 205
S5.frame(X, Y, X + 230, Y + 220, "Alimentations 9 V séparées (TS, HM-2) et découplage")
S5.add(Part("U502", "78L09", "78L09", (X + 40, Y + 30), nets={3: "+15V", 1: "+9V_TS", 2: "GND"}))
two(S5, "C502", "C", "330n", X + 15, Y + 55, "+15V", "GND")
two(S5, "C503", "CP", "10µ 25 V", X + 70, Y + 55, "+9V_TS", "GND")
two(S5, "C504", "C", "100n", X + 85, Y + 55, "+9V_TS", "GND")
two(S5, "R505", "R", "10k", X + 110, Y + 30, "+9V_TS", "TS_VB")
two(S5, "R506", "R", "10k", X + 110, Y + 55, "TS_VB", "GND")
two(S5, "C505", "CP", "47µ 16 V", X + 125, Y + 55, "TS_VB", "GND")
S5.add(Part("U504", "78L09", "78L09", (X + 40, Y + 100), nets={3: "+15V", 1: "+9V_HM", 2: "GND"}))
two(S5, "C512", "C", "330n", X + 15, Y + 125, "+15V", "GND")
two(S5, "C513", "CP", "10µ 25 V", X + 70, Y + 125, "+9V_HM", "GND")
two(S5, "C514", "C", "100n", X + 85, Y + 125, "+9V_HM", "GND")
two(S5, "R514", "R", "10k", X + 110, Y + 100, "+9V_HM", "HM_VB")
two(S5, "R515", "R", "10k", X + 110, Y + 125, "HM_VB", "GND")
two(S5, "C515", "CP", "47µ 16 V", X + 125, Y + 125, "HM_VB", "GND")
two(S5, "R516", "R", "1k", X + 150, Y + 100, "+9V_HM", "HM_S")
two(S5, "C516", "CP", "47µ 16 V", X + 165, Y + 125, "HM_S", "GND")
for i, (a, b) in enumerate((("+15V", "GND"), ("GND", "-15V"), ("+9V_TS", "GND"), ("+9V_HM", "GND"), ("+9V_HM", "GND"),
                            ("+9V_HM", "GND"))):
    two(S5, f"C{536 + i}", "C", "100n", X + 15 + i * 18, Y + 165, a, b)
for i, u in enumerate(("U505", "U506", "U507")):
    S5.add(Part(u, "NJM4558", "NJM4558D", (X + 140 + i * 25, Y + 180), unit=3, nets={8: "+9V_HM", 4: "GND"}))
S5.note("HM-2 : 9 V régulés, comme une pile neuve (l'adaptateur Boss ACA donnait ≈ 9 V après 330 Ω et une diode).",
        X + 5, Y + 207, 1.4)
S5.note("HM_S : alimentation filtrée du préampli à transistors (R10 1 k et C5 47 µF d'origine).", X + 5, Y + 214, 1.4)

# =================================================================================================
# 6. Pilotage
# =================================================================================================
S6 = P.sheet(Sheet("Pilotage", "pilotage.kicad_sch", "A1", "Alimentations BT, Raspberry Pi 4, interface"))
X, Y = 15, 15
S6.frame(X, Y, X + 280, Y + 120, "Alimentation ±15 V de l'entrée et des VCA (transfo séparé 2 × 15 V, 10 VA)")
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
S6.note("≈ 110 mA sur +15 V et 70 mA sur −15 V (TS, HM-2, VCA, gate) : LM7815/7915 sur une petite surface de dissipation.",
        X + 5, Y + 115, 1.4)

X, Y = 305, 15
S6.frame(X, Y, X + 280, Y + 120, "Alimentation 24 V (module secteur) : robot, +5 V des moteurs et relais, +5V_PI du Pi")
S6.add(Part("F601", "FUSE", "T1 A", (X + 20, Y + 35), nets={1: "L_SW", 2: "SMPS_L"}))
S6.add(Part("U604", "SMPS_MOD", "IRM-60-24ST", (X + 70, Y + 45), nets={"L": "SMPS_L", "N": "N_SW", "V+": "+24V", "V-": "GND"}))
two(S6, "C620", "CP", "470µ 35 V", X + 110, Y + 50, "+24V", "GND")
S6.add(Part("U603", "BUCK_MOD", "LM2596 → 5,0 V 3 A", (X + 170, Y + 40), nets={1: "+24V", 2: "GND", 3: "+5V", 4: "GND"}))
S6.add(Part("U609", "BUCK_MOD", "Pololu D36V28F5 → 5,0 V 3,2 A", (X + 170, Y + 85),
            nets={1: "+24V", 2: "GND", 3: "+5V_PI", 4: "GND"}))
two(S6, "C627", "CP", "220µ 10 V", X + 225, Y + 95, "+5V_PI", "GND")
S6.note("+5V : moteurs des pots (Motoron), relais, LED des LDR. +5V_PI : le Pi seul (jusqu'à 3 A). +3V3 : sortie du Pi.",
        X + 5, Y + 108, 1.4)
S6.note("Le 0 V du module rejoint la masse de commande : aucun courant de moteur ne passe par la masse audio.", X + 5, Y + 115, 1.4)

X, Y = 595, 15
S6.frame(X, Y, X + 230, Y + 280, "Raspberry Pi 4 B (contrôleur unique) et HAT CAN enfiché")
rpi = {1: "+3V3", 17: "+3V3", 2: "+5V_PI", 4: "+5V_PI", 3: "I2C_SDA", 5: "I2C_SCL", 7: "W1_DQ", 8: "SR_LATCH", 10: None,
       11: "CS_ADC2", 12: "CS_ADC1", 13: "CS_DAC2", 15: "FS1", 16: "FS2", 18: "TFT_DC", 19: "SPI0_MOSI", 21: "SPI0_MISO",
       22: "CAN_INT", 23: "SPI0_SCK", 24: "CAN_CS", 26: "CS_TFT", 27: None, 28: None, 29: "ENC_A", 31: "ENC_B",
       32: "MIDI_TX", 33: "MIDI_RX", 35: "SPI1_MISO", 36: "CS_DAC1", 37: "ENC_SW", 38: "SPI1_MOSI", 40: "SPI1_SCK"}
rpi.update({n: "GND" for n in (6, 9, 14, 20, 25, 30, 34, 39)})
S6.add(Part("A601", "RPI4_40P", "Raspberry Pi 4 B (2 Go)", (X + 115, Y + 85), nets=rpi))
S6.add(Part("A602", "CAN_HAT", "Waveshare RS485 CAN HAT", (X + 70, Y + 205),
            nets={1: "+3V3", 2: "GND", 3: "SPI0_SCK", 4: "SPI0_MOSI", 5: "SPI0_MISO", 6: "CAN_CS", 7: "CAN_INT",
                  "H": "CAN_H", "L": "CAN_L", "G": "GND"}))
S6.note("config.txt : dtparam=spi=on ; dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25 ; dtoverlay=spi1-3cs ;",
        X + 5, Y + 245, 1.3)
S6.note("dtoverlay=uart5 (MIDI 31 250 bauds) ; dtoverlay=w1-gpio,gpiopin=4 ; dtoverlay=disable-wifi ; dtoverlay=disable-bt.",
        X + 5, Y + 251, 1.3)
S6.note("CS_DAC2 sur GPIO27 en sélection logicielle. GPIO14 : verrou des registres de l'entrée (entrée DI du RS485 du HAT, inutilisé) ; GPIO15 reste au RS485.",
        X + 5, Y + 257, 1.3)
S6.note("Système en lecture seule (overlay), presets écrits de façon atomique sur une partition à part ; chien de garde actif.",
        X + 5, Y + 263, 1.3)
S6.note("Ethernet : RJ45 du Pi relié par un cordon court à la traversée etherCON NE8FDP de la face arrière.", X + 5, Y + 269, 1.3)

X, Y = 15, 145
S6.frame(X, Y, X + 280, Y + 120, "Interface : écran, encodeur, pédalier")
S6.add(Part("J601", "TFT_ST7789", "TFT 2,4\" SPI", (X + 40, Y + 45),
            nets={1: "GND", 2: "+3V3", 3: "SPI0_SCK", 4: "SPI0_MOSI", 5: "TFT_RES", 6: "TFT_DC", 7: "CS_TFT", 8: "+3V3"}))
two(S6, "R640", "R", "10k", X + 70, Y + 30, "+3V3", "TFT_RES")
two(S6, "C623", "C", "100n", X + 70, Y + 60, "TFT_RES", "GND")
S6.add(Part("SW601", "EC11", "EC11", (X + 120, Y + 40), nets={"A": "ENC_A", "C": "GND", "B": "ENC_B", "S1": "ENC_SW", "S2": "GND"}))
for i, n in enumerate(("ENC_A", "ENC_B", "ENC_SW")):
    two(S6, f"R{603 + i}", "R", "10k", X + 150 + i * 15, Y + 30, "+3V3", n)
    two(S6, f"C{607 + i}", "C", "10n", X + 150 + i * 15, Y + 60, n, "GND")
S6.add(Part("J602", "JACK_TRS", "Pédalier", (X + 25, Y + 95), nets={"T": "FS1_IN", "R": "FS2_IN", "S": "GND"}))
for i, (a, b) in enumerate((("FS1_IN", "FS1"), ("FS2_IN", "FS2"))):
    S6.add(Part(f"R{608 + i}", "R", "1k", (X + 60 + i * 50, Y + 92), rotation=90, nets={1: a, 2: b}))
    two(S6, f"R{606 + i}", "R", "10k", X + 80 + i * 50, Y + 75, "+3V3", b)
    two(S6, f"C{610 + i}", "C", "100n", X + 80 + i * 50, Y + 105, b, "GND")

X, Y = 15, 275
S6.frame(X, Y, X + 280, Y + 120, "MIDI IN et THRU (UART5 du Pi)")
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

X, Y = 305, 145
S6.frame(X, Y, X + 280, Y + 160, "Carte d'interface traversante : 2 × MCP3208 (SPI1), 2 × MCP4822, 1-Wire")
S6.add(Part("U610", "MCP3208", "MCP3208-CI/P", (X + 50, Y + 45),
            nets={1: "SENSE1", 2: "SENSE2", 3: "SENSE3", 4: "SENSE4", 5: "SENSE5", 6: "SENSE6", 7: "SENSE7", 8: "SENSE8",
                  16: "+3V3", 15: "+3V3", 13: "SPI1_SCK", 11: "SPI1_MOSI", 12: "SPI1_MISO", 10: "CS_ADC1", 14: "GND", 9: "GND"}))
S6.add(Part("U611", "MCP3208", "MCP3208-CI/P", (X + 50, Y + 115),
            nets={1: "SENSE9", 2: "SENSE10", 3: "BIAS_ADC1", 4: "BIAS_ADC2", 5: "BIAS_ADC3", 6: "BIAS_ADC4", 7: "ENV_MON",
                  8: "GND", 16: "+3V3", 15: "+3V3", 13: "SPI1_SCK", 11: "SPI1_MOSI", 12: "SPI1_MISO", 10: "CS_ADC2",
                  14: "GND", 9: "GND"}))
S6.add(Part("U612", "MCP4822", "MCP4822-E/P", (X + 165, Y + 40),
            nets={1: "+3V3", 2: "CS_DAC1", 3: "SPI1_SCK", 4: "SPI1_MOSI", 8: "DAC_VCA_A", 6: "DAC_VCA_B", 5: "GND", 7: "GND"}))
S6.add(Part("U613", "MCP4822", "MCP4822-E/P", (X + 165, Y + 90),
            nets={1: "+3V3", 2: "CS_DAC2", 3: "SPI1_SCK", 4: "SPI1_MOSI", 8: "DAC_THR", 6: "DAC_FADE", 5: "GND", 7: "GND"}))
two(S6, "R650", "R", "4.7k", X + 235, Y + 40, "+3V3", "W1_DQ")
for i in range(4):
    two(S6, f"C{630 + i}", "C", "100n", X + 140 + i * 15, Y + 130, "+3V3", "GND")
two(S6, "C634", "CP", "10µ 10 V", X + 215, Y + 130, "+3V3", "GND")
S6.note("Pistes capteur et VREF sur le même +3V3 : mesure ratiométrique. CNA en gain 1 (0-2,048 V), mis à l'échelle côté VCA.",
        X + 5, Y + 150, 1.3)
S6.note("Pots 1-10 : SENSE1-10 ; courant des 6L6GC : BIAS_ADC1-4 ; enveloppe du gate : ENV_MON (affichage du seuil).",
        X + 5, Y + 156, 1.3)

X, Y = 595, 435
S6.frame(X, Y, X + 230, Y + 105, "Registres des commandes de l'entrée : 3 × 74HC595 sur SPI1, nappe vers le boîtier d'entrée")
SR_BITS = [f"{t}_A{i}" for t in ("TSD", "TST", "HMD", "HML", "HMH") for i in range(4)] + [f"REL_A{i}" for i in range(3)]
qpins = [15, 1, 2, 3, 4, 5, 6, 7]
for u in range(3):
    nets = {14: ("SPI1_MOSI", "SR_D1", "SR_D2")[u], 11: "SPI1_SCK", 12: "SR_LATCH", 10: "+3V3", 13: "SR_OE",
            16: "+3V3", 8: "GND", 9: ("SR_D1", "SR_D2", None)[u]}
    for j, q in enumerate(qpins):
        b = u * 8 + j
        nets[q] = SR_BITS[b] if b < len(SR_BITS) else None
    S6.add(Part(f"U{614 + u}", "74HC595", "74HC595N", (X + 35 + u * 60, Y + 38), nets=nets))
    two(S6, f"C{635 + u}", "C", "100n", X + 20 + u * 60, Y + 68, "+3V3", "GND")
jn = {k + 1: n for k, n in enumerate(SR_BITS)}
jn.update({24: "GND", 25: "GND", 26: "GND"})
S6.add(Part("J606", "HDR_2x13", "Nappe 26 points", (X + 205, Y + 45), nets=jn))
S6.note("Écriture : 24 bits sur SPI1 sans sélection (SPI_NO_CS ; à défaut sous CS_ADC1, le MCP3208 ignore la trame), puis",
        X + 5, Y + 81, 1.2)
S6.note("impulsion sur SR_LATCH (GPIO14) : les adresses ne changent qu'au verrouillage, le trafic SPI1 ne les touche pas.",
        X + 5, Y + 86, 1.2)
S6.note("SR_OE (MCP23017, tiré à 3,3 V) : sorties en haute impédance au démarrage, adresses à 0 par les réseaux de la feuille 9.",
        X + 5, Y + 91, 1.2)
S6.note("Bits : TSD, TST (TS drive, tone), HMD, HML, HMH (HM-2 dist, Color Mix L et H) sur 4 bits, REL (gate) sur 3 bits.",
        X + 5, Y + 96, 1.2)

X, Y = 305, 315
S6.frame(X, Y, X + 270, Y + 170, "Mesure du courant des 6L6GC (gain 21) vers le MCP3208")
for i, t in enumerate(("V7", "V8", "V9", "V10")):
    x = X + 15 + i * 65
    n = 615 + i * 6
    S6.add(Part(f"R{n}", "R", "10k", (x + 5, Y + 30), rotation=90, nets={1: f"{t}_K", 2: f"BS{i + 1}_F"}))
    two(S6, f"C{612 + i}", "C", "100n", x + 10, Y + 60, f"BS{i + 1}_F", "GND")
    S6.add(Part(f"D{606 + 2 * i}", "D", "BAT85", (x + 25, Y + 50), rotation=90, nets={1: f"BS{i + 1}_F", 2: "+3V3"}))
    S6.add(Part(f"D{607 + 2 * i}", "D", "BAT85", (x + 40, Y + 50), rotation=90, nets={1: "GND", 2: f"BS{i + 1}_F"}))
    u = {0: (1, {3: "BS1_F", 2: "BS1_N", 1: "BIAS_ADC1"}), 1: (2, {5: "BS2_F", 6: "BS2_N", 7: "BIAS_ADC2"}),
         2: (3, {10: "BS3_F", 9: "BS3_N", 8: "BIAS_ADC3"}), 3: (4, {12: "BS4_F", 13: "BS4_N", 14: "BIAS_ADC4"})}[i]
    S6.add(Part("U606", "MCP6004", "MCP6004-I/P", (x + 25, Y + 95), unit=u[0], nets=u[1]))
    two(S6, f"R{n + 1}", "R", "1k", x + 10, Y + 130, f"BS{i + 1}_N", "GND")
    two(S6, f"R{n + 2}", "R", "20k", x + 30, Y + 130, f"BIAS_ADC{i + 1}", f"BS{i + 1}_N")
S6.add(Part("U606", "MCP6004", "MCP6004-I/P", (X + 250, Y + 150), unit=5, nets={4: "+3V3", 11: "GND"}))

X, Y = 595, 305
S6.frame(X, Y, X + 230, Y + 120, "Bus CAN et 24 V vers le robot (M12, brochage CANopen)")
S6.add(Part("F602", "FUSE", "PTC 2,5 A", (X + 60, Y + 30), nets={1: "+24V", 2: "ROBOT_24V"}))
S6.add(Part("J605", "M12_5", "Robot", (X + 150, Y + 55),
            nets={1: "CHASSIS", 2: "ROBOT_24V", 3: "GND", 4: "CAN_H", 5: "CAN_L"}))
S6.note("500 kbit/s ; 120 Ω sur le HAT et sur le dernier servo. Adresses : 1 radial, 2 distance, 3 angle.", X + 5, Y + 108, 1.4)
S6.note("Blindage du câble à la face arrière par le corps de l'embase ; paire torsadée pour CAN_H et CAN_L.", X + 5, Y + 115, 1.4)

# =================================================================================================
# 7. Commandes : moteurs, capteurs, LED des LDR, bobines des relais
# =================================================================================================
S7 = P.sheet(Sheet("Commandes", "commandes.kicad_sch", "A1", "Moteurs des pots, capteurs de position, LDR et relais"))
POTS = [("RV201", "OD Gain"), ("RV202", "Normal Gain"), ("RV301", "Treble"), ("RV302", "Bass"), ("RV303", "Mid"),
        ("RV304", "Master OD"), ("RV305", "Master Normal"), ("RV306", "Presence"), ("RV307", "Depth"), ("RV802", "Blend")]
VALS = {"RV201": "100k lin (OD Gain)", "RV202": "100k lin (Normal Gain)", "RV301": "20k lin (Treble)",
        "RV302": "100k log (Bass)", "RV303": "10k log (Mid)", "RV304": "100k log (Master OD)",
        "RV305": "100k log (Master Normal)", "RV306": "20k lin (Presence)", "RV307": "100k lin (Depth)",
        "RV802": "10k lin (Blend)"}
X, Y = 15, 15
S7.frame(X, Y, X + 600, Y + 120, "Moteurs des pots : 5 × Pololu Motoron M2T256 (I²C, PWM 20 kHz), sur une barrette près de la façade")
for d in range(5):
    ma, mb = 2 * d + 1, 2 * d + 2
    S7.add(Part(f"U70{1 + d}", "MOTORON_M2T", "Motoron M2T256", (X + 55 + d * 110, Y + 55),
                nets={1: "+5V", 2: "+3V3", 3: "I2C_SDA", 4: "I2C_SCL", 5: "GND",
                      6: f"MOT{ma}_A", 7: f"MOT{ma}_B", 8: f"MOT{mb}_A", 9: f"MOT{mb}_B"}))
two(S7, "C730", "CP", "470µ 10 V", X + 575, Y + 60, "+5V", "GND")
S7.note("Adresses I²C 16 à 20, programmées une carte à la fois. PWM à 20 kHz, hors bande audio ; les moteurs s'arrêtent si le Pi "
        "cesse d'émettre (délai de commande).", X + 5, Y + 108, 1.4)
S7.note("Un seul câble vers le Pi : I²C, +3V3 logique, +5V moteurs, masse. MOT1-9 : pots de l'ampli ; MOT10 : Blend.",
        X + 5, Y + 115, 1.4)

X, Y = 15, 145
S7.frame(X, Y, X + 640, Y + 120, "Moteurs (100 nF aux bornes) et pistes capteur (filtre 1 k / 100 nF vers le MCP3208)")
for m, (ref, name) in enumerate(POTS, start=1):
    x = X + 15 + (m - 1) * 62
    S7.add(Part(ref, "ALPS_2G", VALS[ref], (x + 5, Y + 30), unit=3, nets={"M+": f"MOT{m}_A", "M-": f"MOT{m}_B"}))
    two(S7, f"C{700 + m}", "C", "100n", x + 22, Y + 30, f"MOT{m}_A", f"MOT{m}_B")
    S7.add(Part(ref, "ALPS_2G", VALS[ref], (x + 5, Y + 80), unit=2, nets={6: "+3V3", 5: f"POT{m}_S", 4: "GND"}))
    two(S7, f"R{700 + m}", "R", "1k", x + 25, Y + 75, f"POT{m}_S", f"SENSE{m}")
    two(S7, f"C{710 + m}", "C", "100n", x + 40, Y + 95, f"SENSE{m}", "GND")
    S7.note(name, x, Y + 112, 1.3)
S7.add(Part("RV802", "ALPS_2G", VALS["RV802"], (X + 625, Y + 30), unit=1, nets={1: None, 2: None, 3: None}))
S7.note("RV802 : piste audio libre", X + 600, Y + 45, 1.2)

X, Y = 15, 275
S7.frame(X, Y, X + 600, Y + 230, "LED des LDR et bobines des relais : 2 × MCP23017 et 3 × ULN2803 ; GATE_OFF")
LDRS = [("LDR201", "Crunch"), ("LDR202", "Clean"), ("LDR203", "Bright"), ("LDR204", "Canal clair coupé"),
        ("LDR205", "Liaison directe"), ("LDR206", "Étage sup."), ("LDR207", "LDR1 (clean)"), ("LDR208", "Clipper 10 k"),
        ("LDR209", "Clipper 4,4 k"), ("LDR210", "LDR2 (OD)"), ("LDR301", "Poussée"), ("LDR302", "LDR3 master OD"),
        ("LDR303", "LDR4 master N"), ("LDR304", "Mute")]
RELS = [("K201", "Découplages réduits"), ("K202", "Liaison 2,2 nF"), ("K501", "TS en service"), ("K502", "Insert"),
        ("K503", "Polarité B")]
loads = [(r, "LDR") for r, _ in LDRS] + [(r, "REL") for r, _ in RELS]
gp = [21, 22, 23, 24, 25, 26, 27, 28, 1, 2, 3, 4, 5, 6, 7, 8]
for k in range(2):
    nets = {9: "+3V3", 12: "I2C_SCL", 13: "I2C_SDA", 15: "+3V3" if k else "GND", 16: "GND", 17: "GND", 18: "+3V3",
            20: None, 19: None, 11: None, 14: None, 10: "GND"}
    for j in range(16):
        g = k * 16 + j
        nets[gp[j]] = f"DRV{g + 1}" if g < len(loads) else {31: "GATE_OFF", 30: "SR_OE"}.get(g)
    S7.add(Part(f"U70{6 + k}", "MCP23017", "MCP23017-E/SP", (X + 45, Y + 60 + k * 110), nets=nets))
two(S7, "R740", "R", "10k", X + 100, Y + 210, "+3V3", "GATE_OFF")
two(S7, "R741", "R", "10k", X + 115, Y + 210, "+3V3", "SR_OE")
for u in range(3):
    nets = {9: "GND", 10: "+5V"}
    for i in range(1, 9):
        g = u * 8 + i
        nets[i] = f"DRV{g}" if g <= len(loads) else "GND"
        nets[19 - i] = f"SINK{g}" if g <= len(loads) else None
    S7.add(Part(f"U7{u + 8:02d}", "ULN2803A", "ULN2803A", (X + 140, Y + 45 + u * 65), nets=nets))
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
S7.note("Affectation DRVn / SINKn : " + legend[:160], X + 5, Y + 208, 1.25)
S7.note(legend[160:], X + 5, Y + 215, 1.25)
S7.note("GATE_OFF (U707 GPB7, tiré à 3,3 V) : gate ouvert tant que le Pi ne l'a pas activé. SR_OE (U707 GPB6, tiré à 3,3 V) : "
        "registres de l'entrée en haute impédance jusqu'à la première écriture.", X + 5, Y + 222, 1.25)

# =================================================================================================
# 8. VCA, mélange et noise gate
# =================================================================================================
S8 = P.sheet(Sheet("VCA et noise gate", "vca_gate.kicad_sch", "A1", "Mélange TS / HM-2 par VCA, noise gate analogique"))
X, Y = 15, 15
S8.frame(X, Y, X + 400, Y + 120, "Mélange : préampli ×4 du chemin A, VCA AS2164, sommation à −12 dB")
S8.add(Part("C801", "C", "2.2µ film", (X + 15, Y + 30), rotation=90, nets={1: "PA_IN", 2: "PA_X"}))
two(S8, "R801", "R", "100k", X + 30, Y + 55, "PA_X", "GND")
S8.add(Part("U801", "OPA2134", "OPA2134", (X + 60, Y + 32), unit=1, nets={3: "PA_X", 2: "PA_FB", 1: "PA_G"}))
S8.add(Part("R802", "R", "30k", (X + 65, Y + 15), rotation=90, nets={1: "PA_G", 2: "PA_FB"}))
two(S8, "R803", "R", "10k", X + 45, Y + 65, "PA_FB", "GND")
S8.add(Part("R804", "R", "30k", (X + 95, Y + 32), rotation=90, nets={1: "PA_G", 2: "VCA_IA"}))
two(S8, "R805", "R", "500", X + 110, Y + 55, "VCA_IA", "VCA_IAS")
two(S8, "C802", "C", "560p", X + 110, Y + 78, "VCA_IAS", "GND")
S8.add(Part("C803", "C", "2.2µ film", (X + 15, Y + 80), rotation=90, nets={1: "PB_IN", 2: "PB_X"}))
two(S8, "R806", "R", "100k", X + 30, Y + 96, "PB_X", "GND")
S8.add(Part("U801", "OPA2134", "OPA2134", (X + 60, Y + 82), unit=2, nets={5: "PB_X", 6: "PB_BUF", 7: "PB_BUF"}))
S8.add(Part("R807", "R", "7.5k", (X + 95, Y + 82), rotation=90, nets={1: "PB_BUF", 2: "VCA_IB"}))
two(S8, "R808", "R", "500", X + 130, Y + 90, "VCA_IB", "VCA_IBS")
two(S8, "C804", "C", "560p", X + 145, Y + 90, "VCA_IBS", "GND")
S8.add(Part("U802", "AS2164", "AS2164", (X + 205, Y + 60),
            nets={2: "VCA_IA", 3: "CV_A", 7: "VCA_IB", 6: "CV_B", 10: "GND", 11: "GND", 15: "GND", 14: "GND",
                  1: "VCA_MODE", 4: "MIX_SUM", 5: "MIX_SUM", 12: "GND", 13: "GND", 16: "+15V", 8: "GND", 9: "-15V"}))
two(S8, "R809", "R", "7.5k", X + 175, Y + 92, "VCA_MODE", "+15V")
S8.add(Part("U803", "OPA2134", "OPA2134", (X + 285, Y + 52), unit=1, nets={3: "GND", 2: "MIX_SUM", 1: "MIX_OUT"}))
S8.add(Part("R810", "R", "7.5k", (X + 290, Y + 30), rotation=90, nets={1: "MIX_OUT", 2: "MIX_SUM"}))
S8.add(Part("C805", "C", "390p", (X + 290, Y + 20), rotation=90, nets={1: "MIX_OUT", 2: "MIX_SUM"}))
S8.add(Part("R811", "R", "100", (X + 325, Y + 52), rotation=90, nets={1: "MIX_OUT", 2: "IN_V1"}))
S8.add(Part("U803", "OPA2134", "OPA2134", (X + 330, Y + 90), unit=2, nets={5: "GND", 6: "U803_SP", 7: "U803_SP"}))
S8.add(Part("U801", "OPA2134", "OPA2134", (X + 365, Y + 90), unit=3, nets={8: "+15V", 4: "-15V"}))
S8.add(Part("U803", "OPA2134", "OPA2134", (X + 385, Y + 90), unit=3, nets={8: "+15V", 4: "-15V"}))
S8.note("0 V de commande = 0 dB, +33 mV/dB d'atténuation. Chemin A : +12 dB avant la VCA, −12 dB à la sommation (bruit du VCA "
        "12 dB plus bas) ;", X + 5, Y + 108, 1.4)
S8.note("chemin B (HM-2, ≈ +3 dBu) par 7,5 k : gain unité à 0 V. Sortie IN_V1 vers la grille de V1B (câble blindé).",
        X + 5, Y + 115, 1.4)

X, Y = 425, 15
S8.frame(X, Y, X + 400, Y + 120, "Commandes des VCA (CNA 0-2,048 V × 1,62 → 0-3,3 V, soit 0 à −100 dB) et sonde de température")
S8.add(Part("R812", "R", "1k", (X + 15, Y + 32), rotation=90, nets={1: "DAC_VCA_A", 2: "CVA_F"}))
two(S8, "C806", "C", "1µ film", X + 30, Y + 60, "CVA_F", "GND")
S8.add(Part("U804", "TL074", "TL074", (X + 60, Y + 34), unit=1, nets={3: "CVA_F", 2: "CVA_FB", 1: "CV_A"}))
S8.add(Part("R813", "R", "6.2k", (X + 65, Y + 15), rotation=90, nets={1: "CV_A", 2: "CVA_FB"}))
two(S8, "R814", "R", "10k", X + 45, Y + 70, "CVA_FB", "GND")
S8.add(Part("R815", "R", "1k", (X + 115, Y + 32), rotation=90, nets={1: "DAC_VCA_B", 2: "CVB_F"}))
two(S8, "C807", "C", "1µ film", X + 130, Y + 60, "CVB_F", "GND")
S8.add(Part("U804", "TL074", "TL074", (X + 160, Y + 34), unit=2, nets={5: "CVB_F", 6: "CVB_FB", 7: "CV_B"}))
S8.add(Part("R816", "R", "6.2k", (X + 165, Y + 15), rotation=90, nets={1: "CV_B", 2: "CVB_FB"}))
two(S8, "R817", "R", "10k", X + 145, Y + 70, "CVB_FB", "GND")
S8.add(Part("U809", "DS18B20", "DS18B20", (X + 260, Y + 45), nets={3: "+3V3", 2: "W1_DQ", 1: "GND"}))
S8.add(Part("U804", "TL074", "TL074", (X + 360, Y + 60), unit=5, nets={4: "+15V", 11: "-15V"}))
S8.note("U809 collé sur U802 : la constante de commande dérive de −3300 ppm/K (kT/q) ; le Pi corrige les tensions.",
        X + 5, Y + 108, 1.4)
S8.note("Bouton Blend (logiciel) : VCA B de −∞ à −20 dB, toute la course sur −60 à −30 dB ; preset de référence : A −4 dB, B −46 dB.",
        X + 5, Y + 115, 1.4)

X, Y = 15, 145
S8.frame(X, Y, X + 810, Y + 155, "Noise gate : détection sur la guitare (U805, U806), forme et commande de la VCA du gate")
S8.add(Part("C809", "C", "100n film", (X + 15, Y + 35), rotation=90, nets={1: "BUF_OUT", 2: "ENV_X"}))
two(S8, "R825", "R", "33k", X + 30, Y + 62, "ENV_X", "GND")
S8.add(Part("U805", "TL074", "TL074", (X + 60, Y + 37), unit=1, nets={3: "ENV_X", 2: "ENV_FB", 1: "ENV_G"}))
S8.add(Part("R826", "R", "100k", (X + 65, Y + 15), rotation=90, nets={1: "ENV_G", 2: "ENV_FB"}))
two(S8, "R827", "R", "10k", X + 45, Y + 72, "ENV_FB", "GND")
S8.add(Part("R828", "R", "10k", (X + 105, Y + 40), rotation=90, nets={1: "ENV_G", 2: "HW_A"}))
S8.add(Part("U805", "TL074", "TL074", (X + 140, Y + 42), unit=2, nets={5: "GND", 6: "HW_A", 7: "HW_OUT"}))
S8.add(Part("D810", "D", "1N4148", (X + 140, Y + 20), nets={1: "HW_OUT", 2: "HW_A"}))
S8.add(Part("D811", "D", "1N4148", (X + 170, Y + 62), nets={1: "HW_B", 2: "HW_OUT"}))
S8.add(Part("R829", "R", "10k", (X + 140, Y + 78), rotation=90, nets={1: "HW_B", 2: "HW_A"}))
S8.add(Part("R830", "R", "20k", (X + 195, Y + 25), rotation=90, nets={1: "ENV_G", 2: "FW_N"}))
S8.add(Part("R831", "R", "10k", (X + 195, Y + 78), rotation=90, nets={1: "HW_B", 2: "FW_N"}))
S8.add(Part("U805", "TL074", "TL074", (X + 230, Y + 47), unit=3, nets={10: "GND", 9: "FW_N", 8: "FW_OUT"}))
S8.add(Part("R832", "R", "20k", (X + 235, Y + 25), rotation=90, nets={1: "FW_OUT", 2: "FW_N"}))
S8.add(Part("U805", "TL074", "TL074", (X + 290, Y + 47), unit=4, nets={12: "FW_OUT", 13: "ENV", 14: "PK_O"}))
S8.add(Part("D812", "D", "1N4148", (X + 320, Y + 47), nets={1: "PK_O", 2: "ENV"}))
two(S8, "C810", "C", "1µ film", X + 340, Y + 75, "ENV", "GND")
two(S8, "R833", "R", "22k", X + 355, Y + 75, "ENV", "GND")
S8.add(Part("R834", "R", "10k", (X + 380, Y + 30), rotation=90, nets={1: "DAC_THR", 2: "THR_H"}))
S8.add(Part("R835", "R", "10M", (X + 420, Y + 18), rotation=90, nets={1: "CMP_A", 2: "THR_H"}))
S8.add(Part("U806", "LM393", "LM393", (X + 430, Y + 47), unit=1, nets={3: "THR_H", 2: "ENV", 1: "CMP_A"}))
S8.add(Part("R840", "R", "470", (X + 465, Y + 47), rotation=90, nets={1: "CMP_A", 2: "GATE_CAP"}))
two(S8, "R839", "R", "47k", X + 495, Y + 25, "+15V", "REL_X")
two(S8, "C811", "C", "220n film", X + 515, Y + 85, "GATE_CAP", "GND")
two(S8, "R836", "R", "120k", X + 545, Y + 25, "+15V", "GOFF_REF")
two(S8, "R837", "R", "15k", X + 545, Y + 60, "GOFF_REF", "GND")
S8.add(Part("U806", "LM393", "LM393", (X + 580, Y + 47), unit=2, nets={5: "GOFF_REF", 6: "GATE_OFF", 7: "CMP_B"}))
S8.add(Part("R841", "R", "100", (X + 615, Y + 47), rotation=90, nets={1: "CMP_B", 2: "GATE_CAP"}))
S8.add(Part("U804", "TL074", "TL074", (X + 650, Y + 47), unit=4, nets={12: "GATE_CAP", 13: "GATE_BUF", 14: "GATE_BUF"}))
S8.add(Part("R818", "R", "30k", (X + 690, Y + 80), rotation=90, nets={1: "GATE_BUF", 2: "SUM_P"}))
S8.add(Part("R822", "R", "1k", (X + 640, Y + 100), rotation=90, nets={1: "DAC_FADE", 2: "FADE_F"}))
two(S8, "C808", "C", "1µ film", X + 655, Y + 125, "FADE_F", "GND")
S8.add(Part("R819", "R", "7.5k", (X + 690, Y + 100), rotation=90, nets={1: "FADE_F", 2: "SUM_P"}))
S8.add(Part("R850", "R", "1.5M", (X + 690, Y + 115), rotation=90, nets={1: "-15V", 2: "SUM_P"}))
S8.add(Part("U804", "TL074", "TL074", (X + 735, Y + 102), unit=3, nets={10: "SUM_P", 9: "SUM_N", 8: "SUM_O"}))
S8.add(Part("D815", "D", "1N4148", (X + 765, Y + 102), nets={1: "SUM_O", 2: "CV_G"}))
S8.add(Part("R820", "R", "2.55k", (X + 765, Y + 82), rotation=90, nets={1: "CV_G", 2: "SUM_N"}))
two(S8, "R821", "R", "10k", X + 720, Y + 130, "SUM_N", "GND")
two(S8, "R851", "R", "10k", X + 790, Y + 125, "CV_G", "GND")
S8.add(Part("R842", "R", "47k", (X + 380, Y + 110), rotation=90, nets={1: "ENV", 2: "ENV_MON"}))
two(S8, "R843", "R", "10k", X + 400, Y + 130, "ENV_MON", "GND")
two(S8, "C812", "C", "100n", X + 415, Y + 130, "ENV_MON", "GND")
S8.add(Part("U805", "TL074", "TL074", (X + 280, Y + 120), unit=5, nets={4: "+15V", 11: "-15V"}))
S8.add(Part("U806", "LM393", "LM393", (X + 580, Y + 120), unit=3, nets={8: "+15V", 4: "GND"}))
S8.note("Guitare propre ×11 (passe-haut 48 Hz), redressement double alternance de précision, crête 1 µF / 22 k (22 ms). "
        "Comparateur U806A : seuil DAC_THR, hystérésis par 10 M.", X + 5, Y + 141, 1.4)
S8.note("Ouverture par 470 Ω (0,1 ms), fermeture par 47 k + échelle de 8 positions entre REL_X et GATE_CAP (τ 10 à 450 ms, "
        "feuille Commandes de l'entrée). GATE_OFF : U806B court-circuite "
        "GATE_CAP, gate ouvert. CV_G = GATE_CAP/4 + DAC_FADE − 75 mV, bornée à 0 V par D815.", X + 5, Y + 148, 1.4)

X, Y = 15, 310
S8.frame(X, Y, X + 400, Y + 120, "VCA du gate entre masters et déphaseur (petite carte près de V5)")
two(S8, "R844", "R", "1M", X + 20, Y + 55, "PI_IN", "GND")
S8.add(Part("U807", "OPA2134", "OPA2134", (X + 50, Y + 37), unit=1, nets={3: "PI_IN", 2: "GV_BUF", 1: "GV_BUF"}))
S8.add(Part("R845", "R", "30k", (X + 85, Y + 37), rotation=90, nets={1: "GV_BUF", 2: "GV_IIN"}))
two(S8, "R846", "R", "500", X + 100, Y + 62, "GV_IIN", "GV_IS")
two(S8, "C813", "C", "560p", X + 100, Y + 85, "GV_IS", "GND")
S8.add(Part("U808", "AS2164", "AS2164", (X + 180, Y + 60),
            nets={2: "GV_IIN", 3: "CV_G", 7: "GND", 6: "GND", 10: "GND", 11: "GND", 15: "GND", 14: "GND",
                  1: "GV_MODE", 4: "GV_SUM", 5: "GND", 12: "GND", 13: "GND", 16: "+15V", 8: "GND", 9: "-15V"}))
two(S8, "R847", "R", "7.5k", X + 150, Y + 100, "GV_MODE", "+15V")
S8.add(Part("U807", "OPA2134", "OPA2134", (X + 260, Y + 52), unit=2, nets={5: "GND", 6: "GV_SUM", 7: "GV_OUT"}))
S8.add(Part("R848", "R", "30k", (X + 265, Y + 30), rotation=90, nets={1: "GV_OUT", 2: "GV_SUM"}))
S8.add(Part("C814", "C", "100p", (X + 265, Y + 20), rotation=90, nets={1: "GV_OUT", 2: "GV_SUM"}))
S8.add(Part("R849", "R", "100", (X + 300, Y + 52), rotation=90, nets={1: "GV_OUT", 2: "PI_DRV"}))
S8.add(Part("U807", "OPA2134", "OPA2134", (X + 340, Y + 90), unit=3, nets={8: "+15V", 4: "-15V"}))
S8.note("Quelques volts au plus après les masters : dans la plage d'une VCA en ±15 V. Le mute LDR304 reste en amont, sur PI_IN.",
        X + 5, Y + 108, 1.4)
S8.note("Détection sur la guitare propre, action après le préampli : coupe aussi le souffle des étages à lampes et de la HM-2.",
        X + 5, Y + 115, 1.4)

X, Y = 425, 310
S8.frame(X, Y, X + 400, Y + 120, "Découplage ±15 V")
for i in range(8):
    two(S8, f"C{816 + 2 * i}", "C", "100n", X + 15 + i * 42, Y + 40, "+15V", "GND")
    two(S8, f"C{817 + 2 * i}", "C", "100n", X + 30 + i * 42, Y + 40, "GND", "-15V")
two(S8, "C832", "CP", "22µ 25 V", X + 30, Y + 85, "+15V", "GND")
two(S8, "C833", "CP", "22µ 25 V", X + 60, Y + 85, "GND", "-15V")
S8.note("Un 100 nF par boîtier et par rail, au plus près des broches (U801-U808).", X + 5, Y + 115, 1.4)


# =================================================================================================
# 9. Commandes de l'entrée : échelles de résistances et multiplexeurs (boîtier d'entrée)
# =================================================================================================
import json
import os

STEPS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spice", "steps.json")))


def rval(v):
    if v >= 1e6:
        return f"{v / 1e6:g}M"
    if v >= 1e3:
        return f"{v / 1e3:g}k"
    return f"{v:g}"


S9 = P.sheet(Sheet("Commandes de l'entrée", "commandes_entree.kicad_sch", "A1",
                   "Échelles de la TS et de la HM-2, multiplexeurs"))
CTRL = [  # ref, sym, key, tag, start node, end node, mux output, title
    ("U901", "ADG406", "ts_drive", "TSD", "TS_ND", None, "TS_NF", "TS Drive : rhéostat 0 à 500 k, 16 positions de 21,5 à 41,5 dB par pas de 1,33 dB"),
    ("U902", "ADG406", "ts_tone", "TST", "TS_TN", "TS_TA", "TS_TW", "TS Tone : 20 k, 16 positions de −2,4 à −17,4 dB (4 kHz / 200 Hz) par pas de 1 dB"),
    ("U903", "ADG406", "hm_dist", "HMD", "HM_P7", "HM_P10", "GND", "HM-2 Dist : 250 k, 16 positions de 24 à 59 dB de gain par pas de 2,3 dB"),
    ("U904", "ADG406", "hm_low", "HML", "HM_P14", "HM_P13", "HM_WL", "HM-2 Color Mix L : 10 k, 15 positions de −20 à +20 dB à 84 Hz, plate au milieu"),
    ("U905", "ADG406", "hm_high", "HMH", "HM_P14", "HM_P13", "HM_WH", "HM-2 Color Mix H : 10 k, 15 positions de −22 à +22 dB vers 1 kHz, plate au milieu"),
    ("U906", "ADG408", "release", "REL", "GATE_CAP", None, "REL_X", "Fermeture du gate : rhéostat 0 à 2 M avec 47 k et 220 nF, 8 positions de 10 à 450 ms"),
]
nres, ncap = 901, 901
for k, (ref, sym, key, tag, start, end, out, title) in enumerate(CTRL):
    X, Y = 15 + (k % 3) * 275, 15 + (k // 3) * 185
    S9.frame(X, Y, X + 265, Y + 175, title)
    inc = STEPS[key]["inc"]
    taps = [start] + [f"{tag}_T{i}" for i in range(1, len(inc))] + [end or f"{tag}_T{len(inc)}"]
    for i, v in enumerate(inc):
        x, y = X + 95 + (i % 5) * 34, Y + 30 + (i // 5) * 40
        two(S9, f"R{nres}", "R", rval(v), x, y, taps[i], taps[i + 1])
        nres += 1
    addr = {f"A{i}": f"{tag}_A{i}" for i in range(4 if sym == "ADG406" else 3)}
    if sym == "ADG406":
        spins = [19 + i if i < 8 else 11 - (i - 8) for i in range(16)]
        nets = {1: "+15V", 27: "-15V", 12: "GND", 18: "+15V", 28: out, 17: addr["A0"], 16: addr["A1"], 15: addr["A2"],
                14: addr["A3"], 2: None, 3: None, 13: None}
    else:
        spins = [4, 5, 6, 7, 12, 11, 10, 9]
        nets = {13: "+15V", 3: "-15V", 14: "GND", 2: "+15V", 8: out, 1: addr["A0"], 16: addr["A1"], 15: addr["A2"]}
    for i, pin in enumerate(spins):
        nets[pin] = taps[i] if i < len(taps) else taps[len(taps) // 2]
    S9.add(Part(ref, sym, sym + "BNZ", (X + 40, Y + 75), nets=nets))
    two(S9, f"C{ncap}", "C", "100n", X + 95, Y + 150, "+15V", "GND")
    two(S9, f"C{ncap + 1}", "C", "100n", X + 110, Y + 150, "GND", "-15V")
    ncap += 2
    cum = STEPS[key]["cum"]
    S9.note("Prises (Ω depuis " + start + ") : " + ", ".join(rval(c) for c in cum[:9]), X + 130, Y + 148, 1.25)
    S9.note(", ".join(rval(c) for c in cum[9:]) + ("" if len(taps) == 16 else
            ("  ; S16 = prise du milieu (plat)" if sym == "ADG406" else "")), X + 130, Y + 154, 1.25)
    S9.note("Entrée Sn = prise n−1 ; adresse = position (0 = " + start + ").", X + 130, Y + 160, 1.25)

X, Y = 15, 385
S9.frame(X, Y, X + 540, Y + 120, "Nappe depuis la carte d'interface (feuille Pilotage), tirages au repos et découplage")
jn = {k + 1: n for k, n in enumerate(SR_BITS)}
jn.update({24: "GND", 25: "GND", 26: "GND"})
S9.add(Part("J901", "HDR_2x13", "Nappe 26 points", (X + 30, Y + 55), nets=jn))
for r in range(3):
    nets = {1: "GND"}
    for i in range(8):
        b = r * 8 + i
        nets[i + 2] = SR_BITS[b] if b < len(SR_BITS) else None
    S9.add(Part(f"RN{901 + r}", "RN_SIP9", "100k ×8", (X + 110 + r * 60, Y + 55), nets=nets))
two(S9, f"C{ncap}", "CP", "10µ 25 V", X + 300, Y + 55, "+15V", "GND")
two(S9, f"C{ncap + 1}", "CP", "10µ 25 V", X + 320, Y + 55, "GND", "-15V")
S9.note("Adresses en 3,3 V depuis les 74HC595 (entrées TTL des ADG4xx, seuil 2,4 V) ; lignes statiques en jeu, elles ne changent qu'au "
        "verrouillage.", X + 5, Y + 95, 1.4)
S9.note("Au repos (SR_OE haut ou nappe débranchée) : adresses à 0 par les réseaux 100 k. Changement de position sous le fondu des VCA "
        "(quelques ms) ; RON 50 Ω typ., 80 Ω max, compensés dans R511, R522 et les gyrateurs.", X + 5, Y + 102, 1.4)
S9.note("Valeurs des prises : spice/steps.py (paliers réguliers en dB, incréments E96 1 %, multiplexeur compris).", X + 5, Y + 109, 1.4)

X, Y = 565, 385
S9.frame(X, Y, X + 265, Y + 120, "Implantation")
S9.note("Sur une carte du boîtier d'entrée, près de la TS et de la HM-2 :", X + 5, Y + 20, 1.4)
S9.note("liaisons courtes vers TS_ND, TS_NF, TS_TA, TS_TW, TS_TN,", X + 5, Y + 27, 1.4)
S9.note("HM_P7, HM_P10, HM_P13, HM_P14, HM_WL, HM_WH ; U906 près de C811.", X + 5, Y + 34, 1.4)
S9.note("Brochage des ADG406 / ADG408 : celui des DG406 / DG408 (à vérifier).", X + 5, Y + 41, 1.4)

P.root_texts += [
    ("Tête 100 W pilotable — famille SLO-100", 20, 25, 3.0, True),
    ("Révision 0.2 du 8 novembre 2026 (Raspberry Pi 4, entrée TS808 ∥ HM-2 par VCA, gate analogique), générée par slo_sch.py et vérifiée contre la simulation (check_sch.py).", 20, 33, 1.6, False),
    ("Les feuilles sont reliées par des étiquettes globales : B+1 à B+5, B+BUF, B+WCF, B+EXT, HEAT_*, BIAS_*, signaux de pilotage.", 20, 39, 1.6, False),
    ("Chaque broche porte le nom de son nœud ; les noms suivent la simulation SPICE (voir NETMAP dans check_sch.py).", 20, 45, 1.6, False),
    ("Haute tension mortelle (jusqu'à 535 V à vide). Ne pas intervenir sous tension ; décharger les condensateurs.", 20, 262, 2.0, True),
]

if __name__ == "__main__":
    P.write(sys.argv[1] if len(sys.argv) > 1 else "out")
    print("written", sum(len(s.parts) for s in P.sheets), "placed units on", len(P.sheets), "sheets")
