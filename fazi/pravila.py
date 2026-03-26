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
    ugao:        float = 90.0,   # ugaona razlika u stepenima [0°, 180°]
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
# Kontroler 1 — Angažovanje  (Ignorisi / Traži / Označi)
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
# Kontroler 2 — Brzina kretanja  (Patrolna / Oprezna / Fokusirana)
# ─────────────────────────────────────────────────────────────────

def kontroler_brzina(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- PATROLNA (spora, rutinska) ---
    # Tišina + nejasna → nema razloga za ubrzanje
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, brzina_patrolna))

    # Niska detekcija + gusta pokrivenost → situacija pod kontrolom
    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, brzina_patrolna))

    # Iza leđa + tišina → nema razloga za promenu tempa
    p03 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p03, brzina_patrolna))

    # Iza leđa + niska detekcija → rutinska patrola
    p04 = min(u["iza"], d["niska"])
    aktivacije.append(np.fmin(p04, brzina_patrolna))

    # Nejasna + gusta pokrivenost → ne može da proceni, ostaje spor
    p05 = min(v["nejasna"], p["gusta"])
    aktivacije.append(np.fmin(p05, brzina_patrolna))

    # --- OPREZNA (srednja, pažljiva) ---
    # Šum + nejasna → čuje nešto, usporava i sluša
    p06 = min(z["sum"], v["nejasna"])
    aktivacije.append(np.fmin(p06, brzina_oprezna))

    # Delimična + srednja detekcija → prati signal oprezno
    p07 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p07, brzina_oprezna))

    # Šum + srednja detekcija → prati zvuk pažljivo
    p08 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p08, brzina_oprezna))

    # Sa boka + delimična vidljivost → polako kruži ka cilju
    p09 = min(u["bok"], v["delimicna"])
    aktivacije.append(np.fmin(p09, brzina_oprezna))

    # Delimična + retka pokrivenost → istražuje ali ne juri
    p10 = min(v["delimicna"], p["retka"])
    aktivacije.append(np.fmin(p10, brzina_oprezna))

    # Sa boka + šum → orijentiše se prema zvuku
    p11 = min(u["bok"], z["sum"])
    aktivacije.append(np.fmin(p11, brzina_oprezna))

    # Srednja detekcija + srednja pokrivenost → prati uz oprez
    p12 = min(d["srednja"], p["srednja"])
    aktivacije.append(np.fmin(p12, brzina_oprezna))

    # --- FOKUSIRANA (brza, direktna) ---
    # Pucanj → maksimalna brzina reakcije
    p13 = z["pucanj"]
    aktivacije.append(np.fmin(p13, brzina_fokusirana))

    # Jasna + visoka detekcija → direktan kontakt, kreće se brzo
    p14 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p14, brzina_fokusirana))

    # Jasna + retka pokrivenost → nema zaklona, treba brzo delovati
    p15 = min(v["jasna"], p["retka"])
    aktivacije.append(np.fmin(p15, brzina_fokusirana))

    # Ispred + jasna → direktna linija vidljivosti, maksimalna brzina
    p16 = min(u["ispred"], v["jasna"])
    aktivacije.append(np.fmin(p16, brzina_fokusirana))

    # Ispred + pucanj → neposredna pretnja direktno ispred
    p17 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p17, brzina_fokusirana))

    # Visoka detekcija + retka pokrivenost → meta izložena, brzo reaguje
    p18 = min(d["visoka"], p["retka"])
    aktivacije.append(np.fmin(p18, brzina_fokusirana))

    # Ispred + visoka detekcija → potvrđena meta ispred, fokusirano napreduje
    p19 = min(u["ispred"], d["visoka"])
    aktivacije.append(np.fmin(p19, brzina_fokusirana))

    return np.fmax.reduce(aktivacije)


# ─────────────────────────────────────────────────────────────────
# Kontroler 3 — Upornost pretrage  (Kratkotrajna / Zadržana / Uporna)
# ─────────────────────────────────────────────────────────────────

def kontroler_upornost(mu: dict) -> np.ndarray:
    v = mu["vizuelna"]
    z = mu["zvuk"]
    p = mu["pokrivenost"]
    d = mu["detekcija"]
    u = mu["ugao"]

    aktivacije = []

    # --- KRATKOTRAJNA (brzo odustaje) ---
    # Tišina + nejasna → nema signala, nema razloga da ostane
    p01 = min(z["tisina"], v["nejasna"])
    aktivacije.append(np.fmin(p01, upor_kratkotrajna))

    # Niska detekcija + gusta pokrivenost → ne može da pronađe, odustaje
    p02 = min(d["niska"], p["gusta"])
    aktivacije.append(np.fmin(p02, upor_kratkotrajna))

    # Iza leđa + tišina → signal iza + tiho = lažni alarm
    p03 = min(u["iza"], z["tisina"])
    aktivacije.append(np.fmin(p03, upor_kratkotrajna))

    # Iza leđa + niska detekcija → slab signal iza, ne vredi pratiti
    p04 = min(u["iza"], d["niska"])
    aktivacije.append(np.fmin(p04, upor_kratkotrajna))

    # Nejasna + niska detekcija → premalo informacija za dalju pretragu
    p05 = min(v["nejasna"], d["niska"])
    aktivacije.append(np.fmin(p05, upor_kratkotrajna))

    # --- ZADRŽANA (kruži, verifikuje) ---
    # Šum + srednja detekcija → ima nešto, ali nije potvrđeno — ostaje da provjeri
    p06 = min(z["sum"], d["srednja"])
    aktivacije.append(np.fmin(p06, upor_zadrzana))

    # Delimična + šum → nešto se pomera, kruži oko zone
    p07 = min(v["delimicna"], z["sum"])
    aktivacije.append(np.fmin(p07, upor_zadrzana))

    # Delimična + srednja detekcija → delimično otkrivena meta, nastavlja pretragu
    p08 = min(v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p08, upor_zadrzana))

    # Sa boka + šum → signal sa strane, kruži da potvrdi
    p09 = min(u["bok"], z["sum"])
    aktivacije.append(np.fmin(p09, upor_zadrzana))

    # Sa boka + delimična + srednja detekcija → delimično otkriveno sa strane
    p10 = min(u["bok"], v["delimicna"], d["srednja"])
    aktivacije.append(np.fmin(p10, upor_zadrzana))

    # Visoka detekcija + srednja pokrivenost → blizu ali zaklonjeno, traga dalje
    p11 = min(d["visoka"], p["srednja"])
    aktivacije.append(np.fmin(p11, upor_zadrzana))

    # Iza leđa + šum → čuje iza, okreće se i verifikuje
    p12 = min(u["iza"], z["sum"])
    aktivacije.append(np.fmin(p12, upor_zadrzana))

    # --- UPORNA (ne odustaje dok ne potvrdi) ---
    # Pucanj → odmah uporna potraga, ne napušta zonu
    p13 = z["pucanj"]
    aktivacije.append(np.fmin(p13, upor_uporna))

    # Jasna + visoka detekcija → potvrđena meta, traga dok ne označi
    p14 = min(v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p14, upor_uporna))

    # Jasna + pucanj → vizuelno + zvučno potvrđeno, maximalna upornost
    p15 = min(v["jasna"], z["pucanj"])
    aktivacije.append(np.fmin(p15, upor_uporna))

    # Pucanj + visoka detekcija → dvostruka potvrda, ne napušta zonu
    p16 = min(z["pucanj"], d["visoka"])
    aktivacije.append(np.fmin(p16, upor_uporna))

    # Ispred + jasna + visoka detekcija → direktan kontakt, uporno prati
    p17 = min(u["ispred"], v["jasna"], d["visoka"])
    aktivacije.append(np.fmin(p17, upor_uporna))

    # Ispred + pucanj → pucanj direktno ispred, ne povlači se
    p18 = min(u["ispred"], z["pucanj"])
    aktivacije.append(np.fmin(p18, upor_uporna))

    # Jasna + retka pokrivenost + visoka detekcija → meta bez zaklona, sigurno otkrivena
    p19 = min(v["jasna"], p["retka"], d["visoka"])
    aktivacije.append(np.fmin(p19, upor_uporna))

    return np.fmax.reduce(aktivacije)