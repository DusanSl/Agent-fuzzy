# fuzzy/inference.py
import numpy as np

from fuzzy.rules import (
    fuzzifikuj,
    kontroler_angazovanje,
    kontroler_rizik,
    kontroler_urgentnost,
)
from fuzzy.defuzz import (
    defuzzifikuj_sve,
    odredi_stanje,
    ispisi_izlaze,
)

def pokreni_fis(
    vizuelna: float,
    zvuk: float,
    pokrivenost: float,
    detekcija: float,
    ugao: float = 90.0,        # ← dodaj ovo
    ispisi: bool = False,
) -> dict:

    # Korak 1 — Fuzzifikacija
    mu = fuzzifikuj(vizuelna, zvuk, pokrivenost, detekcija, ugao)

    # Korak 2 — 3 Mamdani kontrolera (agregacija pravila)
    agg_angazovanje = kontroler_angazovanje(mu)
    agg_rizik       = kontroler_rizik(mu)
    agg_urgentnost  = kontroler_urgentnost(mu)

    # Korak 3 — Defuzzifikacija (Centroid COA)
    izlazi = defuzzifikuj_sve(agg_angazovanje, agg_rizik, agg_urgentnost)

    # Korak 4 — Određivanje stanja Snitcha
    stanje = odredi_stanje(izlazi)

    if ispisi:
        ispisi_izlaze(izlazi, stanje)

    return {
        "angazovanje": izlazi["angazovanje"],
        "rizik":       izlazi["rizik"],
        "urgentnost":  izlazi["urgentnost"],
        "stanje":      stanje,
    }