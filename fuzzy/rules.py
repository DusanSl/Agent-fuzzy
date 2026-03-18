# fuzzy/rules.py
import numpy as np
import skfuzzy as fuzz
from fuzzy.membership import (
    x_vizuelna, x_zvuk, x_pokrivenost, x_detekcija, x_ugao,
    x_ang, x_rizik, x_urgentnost,
    # Ulazne MF
    vizuelna_nejasna, vizuelna_delimicna, vizuelna_jasna,
    zvuk_tisina, zvuk_sum, zvuk_pucanj,
    pokr_retka, pokr_srednja, pokr_gusta,
    det_niska, det_srednja, det_visoka,
    ugao_ispred, ugao_bok, ugao_iza,
    # Izlazne MF
    ang_ignorisi, ang_trazi, ang_oznaci,
    rizik_bezopasan, rizik_umeren, rizik_kritican,
    hitnost_mirna, hitnost_umerena, hitnost_kriticna,
    # Helper
    get_membership,
)


def fuzzifikuj(
    vizuelna:   float,
    zvuk:       float,
    pokrivenost: float,
    detekcija:  float,
    ugao:       float = 90.0,   # ugaona razlika u stepenima [0°, 180°]
) -> dict:
    """Fuzzifikacija svih pet ulaznih promenljivih."""
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


# ─────────────────────────────────────────────────────────────────
# Kontroler 1 — Angažovanje
# ─────────────────────────────────────────────────────────────────

def kontroler_angazovanje(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- IGNORIŠI ---
    # Nejasna slika + tišina → nema razloga za akciju
    p01 = min(v["nejasna"], z["tisina"])
    aktivacije.append(np.fmin(p01, ang_ignorisi))

    # Nejasna slika + gusta pokrivenost → ne može da proceni
    p02 = min(v["nejasna"], p["gusta"])
    aktivacije.append(np.fmin(p02, ang_ignorisi))

    # Niska detekcija + tišina → ignoriši
    p03 = min(d["niska"], z["tisina"])
    aktivacije.append(np.fmin(p03, ang_ignorisi))

    # Iza leđa + nejasna vizuelna → ne vidi, ignoriši
    p04 = min(u["iza"], v["nejasna"])
    aktivacije.append(np.fmin(p04, ang_ignorisi))

    # Iza leđa + tišina → potpuno bezopasno
    p05 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p05, ang_ignorisi))

    # --- TRAŽI ---
    # Delimična vizuelna → istražuje
    p06 = v["delimicna"]
    aktivacije.append(np.fmin(p06, ang_trazi))

    # Šum + nejasna slika → nešto se čuje, ali ne vidi
    p07 = min(z["sum"], v["nejasna"])
    aktivacije.append(np.fmin(p07, ang_trazi))

    # Srednja detekcija + srednja pokrivenost → moguć kontakt
    p08 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p08, ang_trazi))

    # Šum + srednja detekcija → prati zvuk
    p09 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p09, ang_trazi))

    # Delimična + retka pokrivenost → traži dalje
    p10 = min(v["delimicna"], p["retka"])
    aktivacije.append(np.fmin(p10, ang_trazi))

    # Sa boka + delimična vidljivost → kreni prema cilju
    p11 = min(u["bok"], v["delimicna"])
    aktivacije.append(np.fmin(p11, ang_trazi))

    # Iza leđa + šum → čuje ali ne vidi, traži
    p12 = min(u["iza"], z["sum"])
    aktivacije.append(np.fmin(p12, ang_trazi))

    # --- OZNAČI ---
    # Jasna slika + visoka detekcija → potvrđen kontakt
    p13 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p13, ang_oznaci))

    # Jasna slika + pucanj → hitno označi
    p14 = min(v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p14, ang_oznaci))

    # Visoka detekcija + retka pokrivenost → nema gde da se sakrije
    p15 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p15, ang_oznaci))

    # Jasna + šum + visoka detekcija → višestruka potvrda
    p16 = min(v["jasna"], z["sum"], d["visoka"])
    aktivacije.append(np.fmin(p16, ang_oznaci))

    # Pucanj uvek → označi bez obzira na ostalo
    p17 = z["pucanj"]
    aktivacije.append(np.fmin(p17, ang_oznaci))

    # Ispred + jasna + visoka detekcija → direktan kontakt
    p18 = min(u["ispred"], v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p18, ang_oznaci))

    # Ispred + pucanj → neposredna pretnja
    p19 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p19, ang_oznaci))

    return np.fmax.reduce(aktivacije)


# ─────────────────────────────────────────────────────────────────
# Kontroler 2 — Nivo rizika
# ─────────────────────────────────────────────────────────────────

def kontroler_rizik(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- BEZOPASAN ---
    # Nejasna + tišina → nema signala
    p01 = min(v["nejasna"], z["tisina"])
    aktivacije.append(np.fmin(p01, rizik_bezopasan))

    # Gusta pokrivenost + niska detekcija → dobro skriven
    p02 = min(p["gusta"], d["niska"])
    aktivacije.append(np.fmin(p02, rizik_bezopasan))

    # Iza leđa + nejasna → ne predstavlja pretnju
    p03 = min(u["iza"], v["nejasna"])
    aktivacije.append(np.fmin(p03, rizik_bezopasan))

    # Iza leđa + tišina + gusta pokrivenost → idealno skriven
    p04 = min(u["iza"], z["tisina"], p["gusta"])
    aktivacije.append(np.fmin(p04, rizik_bezopasan))

    # --- UMEREN ---
    # Delimična + šum → nešto se dešava
    p05 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p05, rizik_umeren))

    # Srednja detekcija → neutralna situacija
    p06 = d["srednja"]
    aktivacije.append(np.fmin(p06, rizik_umeren))

    # Delimična + srednja detekcija → prati razvoj
    p07 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p07, rizik_umeren))

    # Šum + retka pokrivenost → čuje se, nema zaklon
    p08 = min(z["sum"], p["retka"])
    aktivacije.append(np.fmin(p08, rizik_umeren))

    # Sa boka + delimična → delimično izložen
    p09 = min(u["bok"], v["delimicna"])
    aktivacije.append(np.fmin(p09, rizik_umeren))

    # Sa boka + srednja detekcija → može biti primećen
    p10 = min(u["bok"], d["srednja"])
    aktivacije.append(np.fmin(p10, rizik_umeren))

    # --- KRITIČAN ---
    # Pucanj uvek → kritično
    p11 = z["pucanj"]
    aktivacije.append(np.fmin(p11, rizik_kritican))

    # Jasna + visoka detekcija → direktno otkriven
    p12 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p12, rizik_kritican))

    # Jasna + retka pokrivenost → nema zaklona
    p13 = min(v["jasna"], p["retka"])
    aktivacije.append(np.fmin(p13, rizik_kritican))

    # Pucanj + delimična → i delimično otkriven uz pucanj
    p14 = min(z["pucanj"], v["delimicna"])
    aktivacije.append(np.fmin(p14, rizik_kritican))

    # Ispred + jasna + retka pokrivenost → maksimalna izloženost
    p15 = min(u["ispred"], v["jasna"], p["retka"])
    aktivacije.append(np.fmin(p15, rizik_kritican))

    # Ispred + visoka detekcija → nema šanse za skrivanje
    p16 = min(u["ispred"], d["visoka"])
    aktivacije.append(np.fmin(p16, rizik_kritican))

    return np.fmax.reduce(aktivacije)


# ─────────────────────────────────────────────────────────────────
# Kontroler 3 — Urgentnost eskalacije
# ─────────────────────────────────────────────────────────────────

def kontroler_urgentnost(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- MIRNA ---
    # Tišina + nejasna → nema uzbuđenja
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, hitnost_mirna))

    # Niska detekcija + gusta pokrivenost → daleko i skriven
    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, hitnost_mirna))

    # Iza leđa + tišina → potpuno mirno
    p03 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p03, hitnost_mirna))

    # Iza leđa + niska detekcija → nema potrebe za eskalacijom
    p04 = min(u["iza"], d["niska"])
    aktivacije.append(np.fmin(p04, hitnost_mirna))

    # --- UMERENA ---
    # Šum + srednja detekcija → prati situaciju
    p05 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p05, hitnost_umerena))

    # Delimična + šum → nešto se pomera
    p06 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p06, hitnost_umerena))

    # Visoka detekcija + srednja pokrivenost → blizu ali delimično skriven
    p07 = min(d["visoka"], p["srednja"])
    aktivacije.append(np.fmin(p07, hitnost_umerena))

    # Delimična + srednja detekcija → prati razvoj
    p08 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p08, hitnost_umerena))

    # Sa boka + šum → čuje se sa strane
    p09 = min(u["bok"], z["sum"])
    aktivacije.append(np.fmin(p09, hitnost_umerena))

    # Sa boka + srednja detekcija + delimična → umerena pretnja sa strane
    p10 = min(u["bok"], d["srednja"], v["delimicna"])
    aktivacije.append(np.fmin(p10, hitnost_umerena))

    # --- KRITIČNA ---
    # Pucanj → odmah eskalacija
    p11 = z["pucanj"]
    aktivacije.append(np.fmin(p11, hitnost_kriticna))

    # Jasna + visoka detekcija → direktan kontakt
    p12 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p12, hitnost_kriticna))

    # Jasna + pucanj + retka pokrivenost → trojna potvrda
    p13 = min(v["jasna"], z["pucanj"], p["retka"])
    aktivacije.append(np.fmin(p13, hitnost_kriticna))

    # Pucanj + visoka detekcija → potvrđena pretnja sa zvukom
    p14 = min(z["pucanj"], d["visoka"])
    aktivacije.append(np.fmin(p14, hitnost_kriticna))

    # Ispred + jasna + pucanj → maksimalna hitnost
    p15 = min(u["ispred"], v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p15, hitnost_kriticna))

    # Ispred + visoka detekcija + retka pokrivenost → potpuno izložen ispred
    p16 = min(u["ispred"], d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p16, hitnost_kriticna))

    return np.fmax.reduce(aktivacije)