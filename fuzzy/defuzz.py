# fuzzy/defuzz.py
import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_ang, x_rizik, x_urgentnost,
)


def defuzzifikuj_centroid(x_universe: np.ndarray, agg_mf: np.ndarray) -> float:

    # Centroid (COA) metoda defuzzifikacije.
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


def odredi_stanje(izlazi: dict) -> str:

    ang = izlazi["angazovanje"]
    riz = izlazi["rizik"]
    urg = izlazi["urgentnost"]

    if ang > 0.60 or riz > 0.65:
        return "POTVRĐENO"
    elif ang > 0.35 or riz > 0.35 or urg > 0.40:
        return "UPOZORENJE"
    else:
        return "MIRNO"


def ispisi_izlaze(izlazi: dict, stanje: str) -> None:
    # Formatiran ispis crisp izlaza i stanja u konzoli.

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