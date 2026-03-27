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
    vizuelna    = mu["vizuelna"]
    zvuk        = mu["zvuk"]
    pokrivenost = mu["pokrivenost"]
    detekcija   = mu["detekcija"]
    ugao        = mu["ugao"]

    aktivacije = []

    # IGNORIŠI
    p01 = min(vizuelna["nejasna"], zvuk["tisina"])
    aktivacije.append(np.fmin(p01, ang_ignorisi))
    p02 = min(vizuelna["nejasna"], pokrivenost["gusta"])
    aktivacije.append(np.fmin(p02, ang_ignorisi))
    p03 = min(detekcija["niska"], zvuk["tisina"])
    aktivacije.append(np.fmin(p03, ang_ignorisi))
    p04 = min(ugao["iza"], vizuelna["nejasna"])
    aktivacije.append(np.fmin(p04, ang_ignorisi))
    p05 = min(ugao["iza"], zvuk["tisina"])
    aktivacije.append(np.fmin(p05, ang_ignorisi))

    # TRAŽI
    p06 = vizuelna["delimicna"]
    aktivacije.append(np.fmin(p06, ang_trazi))
    p07 = min(zvuk["sum"], vizuelna["nejasna"])
    aktivacije.append(np.fmin(p07, ang_trazi))
    p08 = min(detekcija["srednja"], pokrivenost["srednja"])
    aktivacije.append(np.fmin(p08, ang_trazi))
    p09 = min(zvuk["sum"], detekcija["srednja"])
    aktivacije.append(np.fmin(p09, ang_trazi))
    p10 = min(vizuelna["delimicna"], pokrivenost["retka"])
    aktivacije.append(np.fmin(p10, ang_trazi))
    p11 = min(ugao["bok"], vizuelna["delimicna"])
    aktivacije.append(np.fmin(p11, ang_trazi))
    p12 = min(ugao["iza"], zvuk["sum"])
    aktivacije.append(np.fmin(p12, ang_trazi))

    # OZNAČI
    p13 = min(vizuelna["jasna"], detekcija["visoka"])
    aktivacije.append(np.fmin(p13, ang_oznaci))
    p14 = min(vizuelna["jasna"], zvuk["pucanj"])
    aktivacije.append(np.fmin(p14, ang_oznaci))
    p15 = min(detekcija["visoka"], pokrivenost["retka"])
    aktivacije.append(np.fmin(p15, ang_oznaci))
    p16 = min(vizuelna["jasna"], zvuk["sum"], detekcija["visoka"])
    aktivacije.append(np.fmin(p16, ang_oznaci))
    p17 = zvuk["pucanj"]
    aktivacije.append(np.fmin(p17, ang_oznaci))
    p18 = min(ugao["ispred"], vizuelna["jasna"], detekcija["visoka"])
    aktivacije.append(np.fmin(p18, ang_oznaci))
    p19 = min(ugao["ispred"], zvuk["pucanj"])
    aktivacije.append(np.fmin(p19, ang_oznaci))

    return np.fmax.reduce(aktivacije)

# Kontroler 2 — Brzina kretanja  (Patrolna / Oprezna / Fokusirana)

def kontroler_brzina(mu: dict) -> np.ndarray:
    vizuelna    = mu["vizuelna"]
    zvuk        = mu["zvuk"]
    pokrivenost = mu["pokrivenost"]
    detekcija   = mu["detekcija"]
    ugao        = mu["ugao"]

    aktivacije = []

    # PATROLNA
    p01 = min(zvuk["tisina"], vizuelna["nejasna"])
    aktivacije.append(np.fmin(p01, brzina_patrolna))
    p02 = min(detekcija["niska"], pokrivenost["gusta"])
    aktivacije.append(np.fmin(p02, brzina_patrolna))
    p03 = min(ugao["iza"], zvuk["tisina"])
    aktivacije.append(np.fmin(p03, brzina_patrolna))
    p04 = min(ugao["iza"], detekcija["niska"])
    aktivacije.append(np.fmin(p04, brzina_patrolna))
    p05 = min(vizuelna["nejasna"], pokrivenost["gusta"])
    aktivacije.append(np.fmin(p05, brzina_patrolna))

    # OPREZNA
    p06 = min(zvuk["sum"], vizuelna["nejasna"])
    aktivacije.append(np.fmin(p06, brzina_oprezna))
    p07 = min(vizuelna["delimicna"], detekcija["srednja"])
    aktivacije.append(np.fmin(p07, brzina_oprezna))
    p08 = min(zvuk["sum"], detekcija["srednja"])
    aktivacije.append(np.fmin(p08, brzina_oprezna))
    p09 = min(ugao["bok"], vizuelna["delimicna"])
    aktivacije.append(np.fmin(p09, brzina_oprezna))
    p10 = min(vizuelna["delimicna"], pokrivenost["retka"])
    aktivacije.append(np.fmin(p10, brzina_oprezna))
    p11 = min(ugao["bok"], zvuk["sum"])
    aktivacije.append(np.fmin(p11, brzina_oprezna))
    p12 = min(detekcija["srednja"], pokrivenost["srednja"])
    aktivacije.append(np.fmin(p12, brzina_oprezna))

    # FOKUSIRANA
    p13 = zvuk["pucanj"]
    aktivacije.append(np.fmin(p13, brzina_fokusirana))
    p14 = min(vizuelna["jasna"], detekcija["visoka"])
    aktivacije.append(np.fmin(p14, brzina_fokusirana))
    p15 = min(vizuelna["jasna"], pokrivenost["retka"])
    aktivacije.append(np.fmin(p15, brzina_fokusirana))
    p16 = min(ugao["ispred"], vizuelna["jasna"])
    aktivacije.append(np.fmin(p16, brzina_fokusirana))
    p17 = min(ugao["ispred"], zvuk["pucanj"])
    aktivacije.append(np.fmin(p17, brzina_fokusirana))
    p18 = min(detekcija["visoka"], pokrivenost["retka"])
    aktivacije.append(np.fmin(p18, brzina_fokusirana))
    p19 = min(ugao["ispred"], detekcija["visoka"])
    aktivacije.append(np.fmin(p19, brzina_fokusirana))

    return np.fmax.reduce(aktivacije)

# Kontroler 3 — Upornost pretrage  (Kratkotrajna / Zadržana / Uporna)

def kontroler_upornost(mu: dict) -> np.ndarray:
    vizuelna    = mu["vizuelna"]
    zvuk        = mu["zvuk"]
    pokrivenost = mu["pokrivenost"]
    detekcija   = mu["detekcija"]
    ugao        = mu["ugao"]

    aktivacije = []

    # KRATKOTRAJNA
    p01 = min(zvuk["tisina"], vizuelna["nejasna"])
    aktivacije.append(np.fmin(p01, upor_kratkotrajna))
    p02 = min(detekcija["niska"], pokrivenost["gusta"])
    aktivacije.append(np.fmin(p02, upor_kratkotrajna))
    p03 = min(ugao["iza"], zvuk["tisina"])
    aktivacije.append(np.fmin(p03, upor_kratkotrajna))
    p04 = min(ugao["iza"], detekcija["niska"])
    aktivacije.append(np.fmin(p04, upor_kratkotrajna))
    p05 = min(vizuelna["nejasna"], detekcija["niska"])
    aktivacije.append(np.fmin(p05, upor_kratkotrajna))

    # ZADRŽANA
    p06 = min(zvuk["sum"], detekcija["srednja"])
    aktivacije.append(np.fmin(p06, upor_zadrzana))
    p07 = min(vizuelna["delimicna"], zvuk["sum"])
    aktivacije.append(np.fmin(p07, upor_zadrzana))
    p08 = min(vizuelna["delimicna"], detekcija["srednja"])
    aktivacije.append(np.fmin(p08, upor_zadrzana))
    p09 = min(ugao["bok"], zvuk["sum"])
    aktivacije.append(np.fmin(p09, upor_zadrzana))
    p10 = min(ugao["bok"], vizuelna["delimicna"], detekcija["srednja"])
    aktivacije.append(np.fmin(p10, upor_zadrzana))
    p11 = min(detekcija["visoka"], pokrivenost["srednja"])
    aktivacije.append(np.fmin(p11, upor_zadrzana))
    p12 = min(ugao["iza"], zvuk["sum"])
    aktivacije.append(np.fmin(p12, upor_zadrzana))

    # UPORNA
    p13 = zvuk["pucanj"]
    aktivacije.append(np.fmin(p13, upor_uporna))
    p14 = min(vizuelna["jasna"], detekcija["visoka"])
    aktivacije.append(np.fmin(p14, upor_uporna))
    p15 = min(vizuelna["jasna"], zvuk["pucanj"])
    aktivacije.append(np.fmin(p15, upor_uporna))
    p16 = min(zvuk["pucanj"], detekcija["visoka"])
    aktivacije.append(np.fmin(p16, upor_uporna))
    p17 = min(ugao["ispred"], vizuelna["jasna"], detekcija["visoka"])
    aktivacije.append(np.fmin(p17, upor_uporna))
    p18 = min(ugao["ispred"], zvuk["pucanj"])
    aktivacije.append(np.fmin(p18, upor_uporna))
    p19 = min(vizuelna["jasna"], pokrivenost["retka"], detekcija["visoka"])
    aktivacije.append(np.fmin(p19, upor_uporna))

    return np.fmax.reduce(aktivacije)