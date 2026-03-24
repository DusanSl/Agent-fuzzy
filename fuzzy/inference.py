# fuzzy/inference.py
import numpy as np

from fuzzy.rules import (
    fuzzifikuj,
    kontroler_angazovanje,
    kontroler_brzina,
    kontroler_upornost,
)
from fuzzy.defuzz import (
    defuzzifikuj_sve,
    odredi_stanje,
    ispisi_izlaze,
)


def pokreni_fis(
    vizuelna:    float,
    zvuk:        float,
    pokrivenost: float,
    detekcija:   float,
    ugao:        float = 90.0,
    ispisi:      bool  = False,
) -> dict:

    # Korak 1 — Fuzzifikacija
    mu = fuzzifikuj(vizuelna, zvuk, pokrivenost, detekcija, ugao)

    # Korak 2 — 3 Mamdani kontrolera (agregacija pravila)
    agg_angazovanje = kontroler_angazovanje(mu)
    agg_brzina      = kontroler_brzina(mu)
    agg_upornost    = kontroler_upornost(mu)

    # Korak 3 — Defuzzifikacija (Centroid COA)
    izlazi = defuzzifikuj_sve(agg_angazovanje, agg_brzina, agg_upornost)

    # Korak 4 — Određivanje stanja Snitcha
    stanje = odredi_stanje(izlazi)

    if ispisi:
        ispisi_izlaze(izlazi, stanje)

    return {
        "angazovanje": izlazi["angazovanje"],
        "brzina":      izlazi["brzina"],
        "upornost":    izlazi["upornost"],
        "stanje":      stanje,
    }