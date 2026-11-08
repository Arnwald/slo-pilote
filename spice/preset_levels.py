"""Levels of the TS808 and HM-2 models at the settings of the Line 6 reference preset.

Reference preset (Line 6 Helix, snapshot Rythm): Scream 808 Gain 0.10, Tone 0.90, Level 0.90 on path A;
Swedish Chainsaw Drive 0.60 (0.50 in other snapshots), Bass 1, Treble 1, Level 0.60 on path B; merge A 0 dB,
B -30 dB, polarity normal. Pot positions are converted with an audio (log) law for the TS drive and the levels,
linear for the TS tone and the HM-2 drive (the Boss D law is not documented).

python3 preset_levels.py   ->  output of each pedal at full level, and the HM-2 / TS ratio at the amp input
"""
import numpy as np

import hm2
import ts


def audio_law(x):
    """Fraction of the track between lug 1 and the wiper for an audio taper at rotation x."""
    return (10 ** (2 * x) - 1) / 99


def rms(y):
    return float(np.sqrt(np.mean((y - np.mean(y)) ** 2)))


def dbu(v):
    return 20 * np.log10(v / 0.775)


if __name__ == "__main__":
    ts_level = 20 * np.log10(audio_law(0.90))       # TS level pot at 0.90
    hm_level = 20 * np.log10(audio_law(0.60))       # HM-2 level pot at 0.60
    merge_b = -30.0
    rel = merge_b + hm_level - ts_level
    print(f"TS level {ts_level:+.1f} dB, HM-2 level {hm_level:+.1f} dB, merge B {merge_b:+.0f} dB "
          f"-> HM-2 path {rel:+.1f} dB relative to the TS path (VCA A {ts_level:+.1f} dB, VCA B {merge_b + hm_level:+.1f} dB)")
    print("f (Hz)  input   HM-2 max   TS max   HM-2 / TS at the amp input")
    for f in (82.4, 110.0, 440.0, 1000.0):
        for a in (0.03, 0.1, 0.3):
            _, d = hm2.tran(f, a, probes=("out",), cycles=24, dist=0.55)
            _, y = ts.tran(f, a, version="ts808", drive=audio_law(0.10), tone=0.9, level=1.0, cycles=24)
            h, t = dbu(rms(d["out"])), dbu(rms(y))
            print(f"{f:7.1f} {a * 1000:4.0f} mV {h:+7.1f} dBu {t:+7.1f} dBu   {h - t + rel:+6.1f} dB")
