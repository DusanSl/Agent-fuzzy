# fazi/pravila.py
import numpy as np
import skfuzzy as fuzz
from fazi.skupovi import (
    x_vizuelna, x_zvuk, x_pokrivenost, x_detekcija, x_ugao,
    x_ang, x_brzina, x_upornost,
    # Ulazne MF
    vizuelna_nejasna, vizuelna_delimicna, vizuelna_jasna,
    zvuk_tisina, zvuk_sum, zvuk_pucanj,
    pokr_retka, pokr_srednja, pokr_gusta,
    det_niska, det_srednja, det_visoka,
    ugao_ispred, ugao_bok, ugao_iza,
    # Izlazne MF
    ang_ignorisi, ang_trazi, ang_oznaci,
    brzina_patrolna, brzina_oprezna, brzina_fokusirana,
    upor_kratkotrajna, upor_zadrzana, upor_uporna,
    # Helper
    get_membership,
)


def fuzzifikuj(
    vizuelna:    float,
    zvuk:        float,
    pokrivenost: float,
    detekcija:   float,
    ugao:        float = 90.0,
) -> dict:
    return {
        "vizuelna": {
            "nejasna":   get_membership(x_vizuelna, vizuelna_nejasna,   vizuelna),
            "delimicna": get_membership(x_vizuelna, vizuelna_delimicna, vizuelna),
            "jasna":     get_membership(x_vizuelna, vizuelna_jasna,     vizuelna),
        },
        "zvuk": {
            "tisina": get_membership(x_zvuk, zvuk_tisina, zvuk),
            "sum":    get_membership(x_zvuk, zvuk_sum,    zvuk),
            "pucanj": get_membership(x_zvuk, zvuk_pucanj, zvuk),
        },
        "pokrivenost": {
            "retka":   get_membership(x_pokrivenost, pokr_retka,   pokrivenost),
            "srednja": get_membership(x_pokrivenost, pokr_srednja, pokrivenost),
            "gusta":   get_membership(x_pokrivenost, pokr_gusta,   pokrivenost),
        },
        "detekcija": {
            "niska":   get_membership(x_detekcija, det_niska,   detekcija),
            "srednja": get_membership(x_detekcija, det_srednja, detekcija),
            "visoka":  get_membership(x_detekcija, det_visoka,  detekcija),
        },
        "ugao": {
            "ispred": get_membership(x_ugao, ugao_ispred, ugao),
            "bok":    get_membership(x_ugao, ugao_bok,    ugao),
            "iza":    get_membership(x_ugao, ugao_iza,    ugao),
        },
    }

# Kontroler 1 — Angažovanje  (Ignorisi / Traži / Označi)

def kontroler_angazovanje(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- IGNORIŠI ---
    p01 = min(v["nejasna"], z["tisina"])
    aktivacije.append(np.fmin(p01, ang_ignorisi))
    p02 = min(v["nejasna"], p["gusta"])
    aktivacije.append(np.fmin(p02, ang_ignorisi))
    p03 = min(d["niska"], z["tisina"])
    aktivacije.append(np.fmin(p03, ang_ignorisi))
    p04 = min(u["iza"], v["nejasna"])
    aktivacije.append(np.fmin(p04, ang_ignorisi))
    p05 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p05, ang_ignorisi))

    # --- TRAŽI ---
    p06 = v["delimicna"]
    aktivacije.append(np.fmin(p06, ang_trazi))
    p07 = min(z["sum"], v["nejasna"])
    aktivacije.append(np.fmin(p07, ang_trazi))
    p08 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p08, ang_trazi))
    p09 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p09, ang_trazi))
    p10 = min(v["delimicna"], p["retka"])
    aktivacije.append(np.fmin(p10, ang_trazi))
    p11 = min(u["bok"], v["delimicna"])
    aktivacije.append(np.fmin(p11, ang_trazi))
    p12 = min(u["iza"], z["sum"])
    aktivacije.append(np.fmin(p12, ang_trazi))

    # --- OZNAČI ---
    p13 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p13, ang_oznaci))
    p14 = min(v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p14, ang_oznaci))
    p15 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p15, ang_oznaci))
    p16 = min(v["jasna"], z["sum"], d["visoka"])
    aktivacije.append(np.fmin(p16, ang_oznaci))
    p17 = z["pucanj"]
    aktivacije.append(np.fmin(p17, ang_oznaci))
    p18 = min(u["ispred"], v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p18, ang_oznaci))
    p19 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p19, ang_oznaci))

    return np.fmax.reduce(aktivacije)

# Kontroler 2 — Brzina kretanja  (Patrolna / Oprezna / Fokusirana)

def kontroler_brzina(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- PATROLNA (spora, rutinska) ---
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, brzina_patrolna))
    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, brzina_patrolna))
    p03 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p03, brzina_patrolna))
    p04 = min(u["iza"], d["niska"])
    aktivacije.append(np.fmin(p04, brzina_patrolna))
    p05 = min(v["nejasna"], p["gusta"])
    aktivacije.append(np.fmin(p05, brzina_patrolna))

    # --- OPREZNA (srednja, pažljiva) ---
    p06 = min(z["sum"], v["nejasna"])
    aktivacije.append(np.fmin(p06, brzina_oprezna))
    p07 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p07, brzina_oprezna))
    p08 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p08, brzina_oprezna))
    p09 = min(u["bok"], v["delimicna"])
    aktivacije.append(np.fmin(p09, brzina_oprezna))
    p10 = min(v["delimicna"], p["retka"])
    aktivacije.append(np.fmin(p10, brzina_oprezna))
    p11 = min(u["bok"], z["sum"])
    aktivacije.append(np.fmin(p11, brzina_oprezna))
    p12 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p12, brzina_oprezna))

    # --- FOKUSIRANA (brza, direktna) ---
    p13 = z["pucanj"]
    aktivacije.append(np.fmin(p13, brzina_fokusirana))
    p14 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p14, brzina_fokusirana))
    p15 = min(v["jasna"], p["retka"])
    aktivacije.append(np.fmin(p15, brzina_fokusirana))
    p16 = min(u["ispred"], v["jasna"])
    aktivacije.append(np.fmin(p16, brzina_fokusirana))
    p17 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p17, brzina_fokusirana))
    p18 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p18, brzina_fokusirana))
    p19 = min(u["ispred"], d["visoka"])
    aktivacije.append(np.fmin(p19, brzina_fokusirana))

    return np.fmax.reduce(aktivacije)

# Kontroler 3 — Upornost pretrage  (Kratkotrajna / Zadržana / Uporna)

def kontroler_upornost(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- KRATKOTRAJNA (brzo odustaje) ---
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, upor_kratkotrajna))
    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, upor_kratkotrajna))
    p03 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p03, upor_kratkotrajna))
    p04 = min(u["iza"], d["niska"])
    aktivacije.append(np.fmin(p04, upor_kratkotrajna))
    p05 = min(v["nejasna"], d["niska"])
    aktivacije.append(np.fmin(p05, upor_kratkotrajna))
    p06 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p06, upor_zadrzana))
    p07 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p07, upor_zadrzana))
    p08 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p08, upor_zadrzana))
    p09 = min(u["bok"], z["sum"])
    aktivacije.append(np.fmin(p09, upor_zadrzana))
    p10 = min(u["bok"], v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p10, upor_zadrzana))
    p11 = min(d["visoka"], p["srednja"])
    aktivacije.append(np.fmin(p11, upor_zadrzana))
    p12 = min(u["iza"], z["sum"])
    aktivacije.append(np.fmin(p12, upor_zadrzana))

    # --- UPORNA (ne odustaje dok ne potvrdi) ---
    p13 = z["pucanj"]
    aktivacije.append(np.fmin(p13, upor_uporna))
    p14 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p14, upor_uporna))
    p15 = min(v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p15, upor_uporna))
    p16 = min(z["pucanj"], d["visoka"])
    aktivacije.append(np.fmin(p16, upor_uporna))
    p17 = min(u["ispred"], v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p17, upor_uporna))
    p18 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p18, upor_uporna))
    p19 = min(v["jasna"], p["retka"], d["visoka"])
    aktivacije.append(np.fmin(p19, upor_uporna))

    return np.fmax.reduce(aktivacije)