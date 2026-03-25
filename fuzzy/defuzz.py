# fuzzy/defuzz.py
import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_ang, x_brzina, x_upornost,
)


def defuzzifikuj_centroid(x_universe: np.ndarray, agg_mf: np.ndarray) -> float:
    if agg_mf.max() == 0:
        return 0.0
    return float(fuzz.defuzz(x_universe, agg_mf, "centroid"))


def defuzzifikuj_sve(
    agg_angazovanje: np.ndarray,
    agg_brzina:      np.ndarray,
    agg_upornost:    np.ndarray,
) -> dict:
    return {
        "angazovanje": defuzzifikuj_centroid(x_ang,      agg_angazovanje),
        "brzina":      defuzzifikuj_centroid(x_brzina,   agg_brzina),
        "upornost":    defuzzifikuj_centroid(x_upornost, agg_upornost),
    }


# ─────────────────────────────────────────
# Fuzzy kontroler za stanje
# ─────────────────────────────────────────
x_stanje       = np.arange(0, 1.01, 0.01)
x_angazovanje  = np.arange(0, 1.01, 0.01)
x_brzina_ulaz  = np.arange(0, 1.01, 0.01)
x_upor_ulaz    = np.arange(0, 1.01, 0.01)

stanje_mirno      = fuzz.trapmf(x_stanje, [0.0, 0.0, 0.25, 0.45])
stanje_upozorenje = fuzz.trimf (x_stanje, [0.35, 0.50, 0.65])
stanje_potvrdjeno = fuzz.trapmf(x_stanje, [0.55, 0.75, 1.0,  1.0])

# Angažovanje
angazovanje_nisko   = fuzz.trapmf(x_angazovanje, [0.0, 0.0, 0.2, 0.4])
angazovanje_srednje = fuzz.trimf (x_angazovanje, [0.3, 0.5, 0.7])
angazovanje_visoko  = fuzz.trapmf(x_angazovanje, [0.6, 0.8, 1.0, 1.0])

# Brzina
brzina_spora     = fuzz.trapmf(x_brzina_ulaz, [0.0, 0.0, 0.2, 0.4])
brzina_srednja   = fuzz.trimf (x_brzina_ulaz, [0.3, 0.5, 0.7])
brzina_brza      = fuzz.trapmf(x_brzina_ulaz, [0.6, 0.8, 1.0, 1.0])

# Upornost
upor_mala    = fuzz.trapmf(x_upor_ulaz, [0.0, 0.0, 0.2, 0.4])
upor_srednja = fuzz.trimf (x_upor_ulaz, [0.3, 0.5, 0.7])
upor_velika  = fuzz.trapmf(x_upor_ulaz, [0.6, 0.8, 1.0, 1.0])


def _mu(universe, mf, val):
    return float(fuzz.interp_membership(universe, mf, val))


def odredi_stanje(izlazi: dict) -> str:
    ang  = izlazi["angazovanje"]
    brz  = izlazi["brzina"]
    upor = izlazi["upornost"]

    # Fuzzifikacija izlaza kao ulaza u state kontroler
    a_n = _mu(x_angazovanje, angazovanje_nisko,   ang)
    a_s = _mu(x_angazovanje, angazovanje_srednje, ang)
    a_v = _mu(x_angazovanje, angazovanje_visoko,  ang)

    b_s = _mu(x_brzina_ulaz, brzina_spora,   brz)
    b_m = _mu(x_brzina_ulaz, brzina_srednja, brz)
    b_b = _mu(x_brzina_ulaz, brzina_brza,    brz)

    u_m = _mu(x_upor_ulaz, upor_mala,    upor)
    u_s = _mu(x_upor_ulaz, upor_srednja, upor)
    u_v = _mu(x_upor_ulaz, upor_velika,  upor)

    aktivacije = []

    # ── MIRNO ──────────────────────────────────────────────────────
    # Ignorisi + patrolna + kratkotrajna → potpuno mirno
    aktivacije.append(np.fmin(min(a_n, b_s, u_m), stanje_mirno))
    # Ignorisi + patrolna → nema angažovanja, sporo se kreće
    aktivacije.append(np.fmin(min(a_n, b_s),       stanje_mirno))
    # Ignorisi + kratkotrajna → brzo odustaje, nema pretnje
    aktivacije.append(np.fmin(min(a_n, u_m),       stanje_mirno))
    # Patrolna + kratkotrajna → rutinska patrola
    aktivacije.append(np.fmin(min(b_s, u_m),       stanje_mirno))

    # ── UPOZORENJE ─────────────────────────────────────────────────
    # Traži + oprezna → verifikuje signal, kruži oprezno
    aktivacije.append(np.fmin(min(a_s, b_m),       stanje_upozorenje))
    # Traži + zadržana → ostaje u zoni pretrage
    aktivacije.append(np.fmin(min(a_s, u_s),       stanje_upozorenje))
    # Oprezna + zadržana → tipičan warning obrazac
    aktivacije.append(np.fmin(min(b_m, u_s),       stanje_upozorenje))
    # Traži + oprezna + zadržana → sva tri na srednje → čisto upozorenje
    aktivacije.append(np.fmin(min(a_s, b_m, u_s),  stanje_upozorenje))
    # Ignorisi + zadržana → još uvek ne reaguje ali ostaje duže
    aktivacije.append(np.fmin(min(a_n, u_s),       stanje_upozorenje))
    # Traži + patrolna + zadržana → nešto traži ali ne ubrzava još
    aktivacije.append(np.fmin(min(a_s, b_s, u_s),  stanje_upozorenje))

    # ── POTVRĐENO ──────────────────────────────────────────────────
    # Označi + fokusirana + uporna → sva tri visoka → direktno potvrđeno
    aktivacije.append(np.fmin(min(a_v, b_b, u_v),  stanje_potvrdjeno))
    # Označi + fokusirana → visoko angažovanje i brzina
    aktivacije.append(np.fmin(min(a_v, b_b),        stanje_potvrdjeno))
    # Označi + uporna → označi i ne odustaje
    aktivacije.append(np.fmin(min(a_v, u_v),        stanje_potvrdjeno))
    # Fokusirana + uporna → brzo i uporno → meta potvrđena
    aktivacije.append(np.fmin(min(b_b, u_v),        stanje_potvrdjeno))
    # Označi sam → samo visoko angažovanje je dovoljno
    aktivacije.append(np.fmin(a_v,                  stanje_potvrdjeno))
    # Traži + fokusirana + uporna → eskalacija iz upozorenja
    aktivacije.append(np.fmin(min(a_s, b_b, u_v),  stanje_potvrdjeno))
    # Označi + zadržana + fokusirana → brzo i srednje uporno
    aktivacije.append(np.fmin(min(a_v, b_b, u_s),  stanje_potvrdjeno))

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

    labele = {
        "angazovanje": "Angažovanje",
        "brzina":      "Brzina",
        "upornost":    "Upornost",
    }

    print("\n" + "=" * 48)
    print("  FuzzySnitch — Crisp izlazi")
    print("=" * 48)

    for kljuc, vrednost in izlazi.items():
        traka = "█" * int(vrednost * 20)
        print(f"  {labele[kljuc]:<14} {vrednost:.3f}  {traka}")

    ikona = ikone_stanja.get(stanje, "⚪")
    print(f"\n  Stanje Snitcha:  {ikona}  {stanje}")
    print("=" * 48)