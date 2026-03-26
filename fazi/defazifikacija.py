# fazi/defazifikacija.py
import numpy as np
import skfuzzy as fuzz
from fazi.skupovi import (
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

# Fuzzy kontroler za stanje
x_stanje       = np.arange(0, 1.01, 0.01)
x_angazovanje  = np.arange(0, 1.01, 0.01)
x_brzina_ulaz  = np.arange(0, 1.01, 0.01)
x_upor_ulaz    = np.arange(0, 1.01, 0.01)

stanje_mirno      = fuzz.trapmf(x_stanje, [0.0, 0.0, 0.25, 0.45])
stanje_upozorenje = fuzz.trimf (x_stanje, [0.35, 0.50, 0.65])
stanje_potvrdjeno = fuzz.trapmf(x_stanje, [0.55, 0.75, 1.0,  1.0])

angazovanje_nisko   = fuzz.trapmf(x_angazovanje, [0.0, 0.0, 0.2, 0.4])
angazovanje_srednje = fuzz.trimf (x_angazovanje, [0.3, 0.5, 0.7])
angazovanje_visoko  = fuzz.trapmf(x_angazovanje, [0.6, 0.8, 1.0, 1.0])

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

    # Fuzzifikacija crisp izlaza kao ulaza u state kontroler
    angazovanje_mu_nisko   = _mu(x_angazovanje, angazovanje_nisko,   ang)
    angazovanje_mu_srednje = _mu(x_angazovanje, angazovanje_srednje, ang)
    angazovanje_mu_visoko  = _mu(x_angazovanje, angazovanje_visoko,  ang)

    brzina_mu_spora    = _mu(x_brzina_ulaz, brzina_spora,   brz)
    brzina_mu_srednja  = _mu(x_brzina_ulaz, brzina_srednja, brz)
    brzina_mu_brza     = _mu(x_brzina_ulaz, brzina_brza,    brz)

    upornost_mu_mala    = _mu(x_upor_ulaz, upor_mala,    upor)
    upornost_mu_srednja = _mu(x_upor_ulaz, upor_srednja, upor)
    upornost_mu_velika  = _mu(x_upor_ulaz, upor_velika,  upor)

    aktivacije = []

    # MIRNO
    aktivacije.append(np.fmin(min(angazovanje_mu_nisko, brzina_mu_spora, upornost_mu_mala), stanje_mirno))
    aktivacije.append(np.fmin(min(angazovanje_mu_nisko, brzina_mu_spora), stanje_mirno))
    aktivacije.append(np.fmin(min(angazovanje_mu_nisko, upornost_mu_mala), stanje_mirno))
    aktivacije.append(np.fmin(min(brzina_mu_spora, upornost_mu_mala), stanje_mirno))

    # UPOZORENJE
    aktivacije.append(np.fmin(min(angazovanje_mu_srednje, brzina_mu_srednja), stanje_upozorenje))
    aktivacije.append(np.fmin(min(angazovanje_mu_srednje, upornost_mu_srednja), stanje_upozorenje))
    aktivacije.append(np.fmin(min(brzina_mu_srednja, upornost_mu_srednja), stanje_upozorenje))
    aktivacije.append(np.fmin(min(angazovanje_mu_srednje, brzina_mu_srednja, upornost_mu_srednja), stanje_upozorenje))
    aktivacije.append(np.fmin(min(angazovanje_mu_nisko, upornost_mu_srednja), stanje_upozorenje))
    aktivacije.append(np.fmin(min(angazovanje_mu_srednje, brzina_mu_spora, upornost_mu_srednja), stanje_upozorenje))

    # POTVRĐENO
    aktivacije.append(np.fmin(min(angazovanje_mu_visoko, brzina_mu_brza, upornost_mu_velika),  stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(angazovanje_mu_visoko, brzina_mu_brza), stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(angazovanje_mu_visoko, upornost_mu_velika), stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(brzina_mu_brza, upornost_mu_velika), stanje_potvrdjeno))
    aktivacije.append(np.fmin(angazovanje_mu_visoko, stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(angazovanje_mu_srednje, brzina_mu_brza, upornost_mu_velika), stanje_potvrdjeno))
    aktivacije.append(np.fmin(min(angazovanje_mu_visoko, brzina_mu_brza, upornost_mu_srednja), stanje_potvrdjeno))

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
    print("  FaziAgent — Crisp izlazi")
    print("=" * 48)

    for kljuc, vrednost in izlazi.items():
        traka = "█" * int(vrednost * 20)
        print(f"  {labele[kljuc]:<14} {vrednost:.3f}  {traka}")

    ikona = ikone_stanja.get(stanje, "⚪")
    print(f"\n  Stanje Agenta:  {ikona}  {stanje}")
    print("=" * 48)