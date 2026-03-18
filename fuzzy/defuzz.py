# fuzzy/defuzz.py
import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_ang, x_rizik, x_urgentnost,
)


def defuzzifikuj_centroid(x_universe: np.ndarray, agg_mf: np.ndarray) -> float:
    if agg_mf.max() == 0:
        return 0.0
    return float(fuzz.defuzz(x_universe, agg_mf, "centroid"))


def defuzzifikuj_sve(
    agg_angazovanje: np.ndarray,
    agg_rizik: np.ndarray,
    agg_urgentnost: np.ndarray,
) -> dict:
    return {
        "angazovanje": defuzzifikuj_centroid(x_ang,        agg_angazovanje),
        "rizik":       defuzzifikuj_centroid(x_rizik,      agg_rizik),
        "urgentnost":  defuzzifikuj_centroid(x_urgentnost, agg_urgentnost),
    }


# ─────────────────────────────────────────
# Fuzzy kontroler za stanje
# ─────────────────────────────────────────
x_stanje        = np.arange(0, 1.01, 0.01)
x_angazovanje   = np.arange(0, 1.01, 0.01)   # ulaz kontrolera stanja
x_rizik_ulaz    = np.arange(0, 1.01, 0.01)   # ulaz kontrolera stanja
x_urgentnost_ulaz = np.arange(0, 1.01, 0.01) # ulaz kontrolera stanja

stanje_mirno      = fuzz.trapmf(x_stanje, [0.0, 0.0, 0.25, 0.45])
stanje_upozorenje = fuzz.trimf (x_stanje, [0.35, 0.50, 0.65])
stanje_potvrdjeno = fuzz.trapmf(x_stanje, [0.55, 0.75, 1.0, 1.0])

angazovanje_nisko   = fuzz.trapmf(x_angazovanje, [0.0, 0.0, 0.2, 0.4])
angazovanje_srednje = fuzz.trimf (x_angazovanje, [0.3, 0.5, 0.7])
angazovanje_visoko  = fuzz.trapmf(x_angazovanje, [0.6, 0.8, 1.0, 1.0])

rizik_nizak   = fuzz.trapmf(x_rizik_ulaz, [0.0, 0.0, 0.2, 0.4])
rizik_srednji = fuzz.trimf (x_rizik_ulaz, [0.3, 0.5, 0.7])
rizik_visok   = fuzz.trapmf(x_rizik_ulaz, [0.6, 0.8, 1.0, 1.0])

urgentnost_niska   = fuzz.trapmf(x_urgentnost_ulaz, [0.0, 0.0, 0.2, 0.4])
urgentnost_srednja = fuzz.trimf (x_urgentnost_ulaz, [0.3, 0.5, 0.7])
urgentnost_visoka  = fuzz.trapmf(x_urgentnost_ulaz, [0.6, 0.8, 1.0, 1.0])


def _mu(universe, mf, val):
    return float(fuzz.interp_membership(universe, mf, val))


def odredi_stanje(izlazi: dict) -> str:
    ang = izlazi["angazovanje"]
    riz = izlazi["rizik"]
    urg = izlazi["urgentnost"]

    a_n = _mu(x_angazovanje,     angazovanje_nisko,   ang)
    a_s = _mu(x_angazovanje,     angazovanje_srednje, ang)
    a_v = _mu(x_angazovanje,     angazovanje_visoko,  ang)
    r_n = _mu(x_rizik_ulaz,      rizik_nizak,         riz)
    r_s = _mu(x_rizik_ulaz,      rizik_srednji,       riz)
    r_v = _mu(x_rizik_ulaz,      rizik_visok,         riz)
    u_n = _mu(x_urgentnost_ulaz, urgentnost_niska,    urg)
    u_s = _mu(x_urgentnost_ulaz, urgentnost_srednja,  urg)
    u_v = _mu(x_urgentnost_ulaz, urgentnost_visoka,   urg)

    aktivacije = []

    # MIRNO
    aktivacije.append(np.fmin(min(a_n, r_n),      stanje_mirno))
    aktivacije.append(np.fmin(min(a_n, u_n),      stanje_mirno))
    aktivacije.append(np.fmin(min(r_n, u_n),      stanje_mirno))
    aktivacije.append(np.fmin(min(a_n, r_n, u_n), stanje_mirno))

    # UPOZORENJE
    aktivacije.append(np.fmin(a_s,                stanje_upozorenje))
    aktivacije.append(np.fmin(r_s,                stanje_upozorenje))
    aktivacije.append(np.fmin(min(a_s, u_s),      stanje_upozorenje))
    aktivacije.append(np.fmin(min(r_s, u_s),      stanje_upozorenje))
    aktivacije.append(np.fmin(min(a_n, r_s),      stanje_upozorenje))
    aktivacije.append(np.fmin(min(a_s, r_n, u_s), stanje_upozorenje))

    # POTVRĐENO
    aktivacije.append(np.fmin(a_v,                stanje_potvrdjeno))
    aktivacije.append(np.fmin(r_v,                stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(a_v, r_v),      stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(a_v, u_v),      stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(r_v, u_v),      stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(a_v, r_v, u_v), stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(a_s, r_v),      stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(a_v, r_s),      stanje_potvrdjeno))

    agg = np.fmax.reduce(aktivacije)

    if agg.max() == 0:
        return "MIRNO"

    crisp = float(fuzz.defuzz(x_stanje, agg, "centroid"))

    if crisp >= 0.55:
        return "POTVRĐENO"
    elif crisp >= 0.35:
        return "UPOZORENJE"
    else:
        return "MIRNO"


def ispisi_izlaze(izlazi: dict, stanje: str) -> None:
    ikone_stanja = {
        "MIRNO":      "🟢",
        "UPOZORENJE": "🟡",
        "POTVRĐENO":  "🔴",
    }

    print("\n" + "=" * 48)
    print("  FuzzySnitch — Crisp izlazi")
    print("=" * 48)

    labele = {
        "angazovanje": "Angažovanje",
        "rizik":       "Rizik",
        "urgentnost":  "Urgentnost",
    }

    for kljuc, vrednost in izlazi.items():
        traka = "█" * int(vrednost * 20)
        print(f"  {labele[kljuc]:<14} {vrednost:.3f}  {traka}")

    ikona = ikone_stanja.get(stanje, "⚪")
    print(f"\n  Stanje Snitcha:  {ikona}  {stanje}")
    print("=" * 48)