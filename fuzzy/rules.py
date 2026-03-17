import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_vizuelna, x_zvuk, x_pokrivenost, x_detekcija,
    x_ang, x_rizik, x_urgentnost,
    # Ulazne funkcije pripadnosti
    vizuelna_nejasna, vizuelna_delimicna, vizuelna_jasna,
    zvuk_tisina, zvuk_sum, zvuk_pucanj,
    pokr_retka, pokr_srednja, pokr_gusta,
    det_niska, det_srednja, det_visoka,
    # Izlazne funkcije pripadnosti
    ang_ignorisi, ang_trazi, ang_oznaci,
    rizik_bezopasan, rizik_umeren, rizik_kritican,
    hitnost_mirna, hitnost_umerena, hitnost_kriticna,
    # Helper
    get_membership,
)


def fuzzifikuj(vizuelna: float, zvuk: float, pokrivenost: float, detekcija: float) -> dict:
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
    }


def kontroler_angazovanje(mu: dict) -> np.ndarray:

    # Mamdani kontroler 1 — Angažovanje

    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]

    aktivacije = []

    # IGNORIŠI pravila

    p01 = min(v["nejasna"], z["tisina"])
    aktivacije.append(np.fmin(p01, ang_ignorisi))

    p02 = min(v["nejasna"], p["gusta"])
    aktivacije.append(np.fmin(p02, ang_ignorisi))

    p03 = min(d["niska"], z["tisina"])
    aktivacije.append(np.fmin(p03, ang_ignorisi))

    # TRAŽI pravila

    p04 = v["delimicna"]
    aktivacije.append(np.fmin(p04, ang_trazi))

    p05 = min(z["sum"], v["nejasna"])
    aktivacije.append(np.fmin(p05, ang_trazi))

    p06 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p06, ang_trazi))

    p07 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p07, ang_trazi))

    p08 = min(v["delimicna"], p["retka"])
    aktivacije.append(np.fmin(p08, ang_trazi))

    # OZNAČI pravila

    p09 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p09, ang_oznaci))

    p10 = min(v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p10, ang_oznaci))

    p11 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p11, ang_oznaci))

    p12 = min(v["jasna"], z["sum"], d["visoka"])
    aktivacije.append(np.fmin(p12, ang_oznaci))

    p14 = z["pucanj"]
    aktivacije.append(np.fmin(p14, ang_oznaci))

    return np.fmax.reduce(aktivacije)


def kontroler_rizik(mu: dict) -> np.ndarray:

    # Mamdani kontroler 2 — Nivo rizika

    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]

    aktivacije = []

    # BEZOPASAN rizik
    p01 = min(v["nejasna"], z["tisina"])
    aktivacije.append(np.fmin(p01, rizik_bezopasan))

    p02 = min(p["gusta"], d["niska"])
    aktivacije.append(np.fmin(p02, rizik_bezopasan))

    # UMEREN rizik
    p03 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p03, rizik_umeren))

    p04 = d["srednja"]
    aktivacije.append(np.fmin(p04, rizik_umeren))

    p05 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p05, rizik_umeren))

    p06 = min(z["sum"], p["retka"])
    aktivacije.append(np.fmin(p06, rizik_umeren))

    # KRITIČAN rizik
    p07 = z["pucanj"]
    aktivacije.append(np.fmin(p07, rizik_kritican))

    p08 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p08, rizik_kritican))

    p09 = min(v["jasna"], p["retka"])
    aktivacije.append(np.fmin(p09, rizik_kritican))

    p10 = min(z["pucanj"], v["delimicna"])
    aktivacije.append(np.fmin(p10, rizik_kritican))

    return np.fmax.reduce(aktivacije)


def kontroler_urgentnost(mu: dict) -> np.ndarray:

    # Mamdani kontroler 3

    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]

    aktivacije = []

    # MIRNA hitnost
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, hitnost_mirna))

    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, hitnost_mirna))

    # UMERENA hitnost
    p03 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p03, hitnost_umerena))

    p04 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p04, hitnost_umerena))

    p05 = min(d["visoka"], p["srednja"])
    aktivacije.append(np.fmin(p05, hitnost_umerena))

    p06 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p06, hitnost_umerena))

    # KRITIČNA hitnost
    p07 = z["pucanj"]
    aktivacije.append(np.fmin(p07, hitnost_kriticna))

    p08 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p08, hitnost_kriticna))

    p09 = min(v["jasna"], z["pucanj"], p["retka"])
    aktivacije.append(np.fmin(p09, hitnost_kriticna))

    p10 = min(z["pucanj"], d["visoka"])
    aktivacije.append(np.fmin(p10, hitnost_kriticna))

    return np.fmax.reduce(aktivacije)