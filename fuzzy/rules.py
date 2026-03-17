import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_vizuelna, x_zvuk, x_pokrivenost, x_detekcija,
    x_ang, x_rizik, x_urgentnost,
    # Ulazne funkcije pripadnosti
    vizuelna_niska, vizuelna_srednja, vizuelna_visoka,
    zvuk_tisina, zvuk_sum, zvuk_pucanj,
    pokr_retka, pokr_srednja, pokr_gusta,
    det_niska, det_srednja, det_visoka,
    # Izlazne funkcije pripadnosti
    ang_ignorisi, ang_trazi, ang_oznaci,
    rizik_nizak, rizik_srednji, rizik_visok,
    urg_niska, urg_srednja, urg_urgentna,
    # Helper
    get_membership,
)


def fuzzifikuj(vizuelna: float, zvuk: float, pokrivenost: float, detekcija: float) -> dict:
    return {
        "vizuelna": {
            "niska":   get_membership(x_vizuelna, vizuelna_niska,   vizuelna),
            "srednja": get_membership(x_vizuelna, vizuelna_srednja, vizuelna),
            "visoka":  get_membership(x_vizuelna, vizuelna_visoka,  vizuelna),
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

    p01 = min(v["niska"], z["tisina"])
    aktivacije.append(np.fmin(p01, ang_ignorisi))

    p02 = min(v["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, ang_ignorisi))

    p03 = min(d["niska"], z["tisina"])
    aktivacije.append(np.fmin(p03, ang_ignorisi))

    # TRAŽI pravila

    p04 = v["srednja"]
    aktivacije.append(np.fmin(p04, ang_trazi))

    p05 = min(z["sum"], v["niska"])
    aktivacije.append(np.fmin(p05, ang_trazi))

    p06 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p06, ang_trazi))

    p07 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p07, ang_trazi))

    p08 = min(v["srednja"], p["retka"])
    aktivacije.append(np.fmin(p08, ang_trazi))

    # OZNAČI pravila

    p09 = min(v["visoka"], d["visoka"])
    aktivacije.append(np.fmin(p09, ang_oznaci))

    p10 = min(v["visoka"], z["pucanj"])
    aktivacije.append(np.fmin(p10, ang_oznaci))

    p11 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p11, ang_oznaci))

    p12 = min(v["visoka"], z["sum"], d["visoka"])
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

    # NIZAK rizik
    p01 = min(v["niska"], z["tisina"])
    aktivacije.append(np.fmin(p01, rizik_nizak))

    p02 = min(p["gusta"], d["niska"])
    aktivacije.append(np.fmin(p02, rizik_nizak))

    # SREDNJI rizik
    p03 = min(v["srednja"], z["sum"])
    aktivacije.append(np.fmin(p03, rizik_srednji))

    p04 = d["srednja"]
    aktivacije.append(np.fmin(p04, rizik_srednji))

    p05 = min(v["srednja"], d["srednja"])
    aktivacije.append(np.fmin(p05, rizik_srednji))

    p06 = min(z["sum"], p["retka"])
    aktivacije.append(np.fmin(p06, rizik_srednji))

    # VISOK rizik
    p07 = z["pucanj"]
    aktivacije.append(np.fmin(p07, rizik_visok))

    p08 = min(v["visoka"], d["visoka"])
    aktivacije.append(np.fmin(p08, rizik_visok))

    p09 = min(v["visoka"], p["retka"])
    aktivacije.append(np.fmin(p09, rizik_visok))

    p10 = min(z["pucanj"], v["srednja"])
    aktivacije.append(np.fmin(p10, rizik_visok))

    return np.fmax.reduce(aktivacije)


def kontroler_urgentnost(mu: dict) -> np.ndarray:

    # Mamdani kontroler 3

    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]

    aktivacije = []

    # NISKA urgentnost
    p01 = min(z["tisina"], v["niska"])
    aktivacije.append(np.fmin(p01, urg_niska))

    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, urg_niska))

    # SREDNJA urgentnost
    p03 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p03, urg_srednja))

    p04 = min(v["srednja"], z["sum"])
    aktivacije.append(np.fmin(p04, urg_srednja))

    p05 = min(d["visoka"], p["srednja"])
    aktivacije.append(np.fmin(p05, urg_srednja))

    p06 = min(v["srednja"], d["srednja"])
    aktivacije.append(np.fmin(p06, urg_srednja))

    # URGENTNO
    p07 = z["pucanj"]
    aktivacije.append(np.fmin(p07, urg_urgentna))

    p08 = min(v["visoka"], d["visoka"])
    aktivacije.append(np.fmin(p08, urg_urgentna))

    p09 = min(v["visoka"], z["pucanj"], p["retka"])
    aktivacije.append(np.fmin(p09, urg_urgentna))

    p10 = min(z["pucanj"], d["visoka"])
    aktivacije.append(np.fmin(p10, urg_urgentna))

    return np.fmax.reduce(aktivacije)
