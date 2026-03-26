# fazi/skupovi.py
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# Univerzumi za ulaze
# ─────────────────────────────────────────
x_vizuelna    = np.arange(0, 1.01, 0.01)   # vizuelna pouzdanost   [0, 1]
x_zvuk        = np.arange(0, 1.01, 0.01)   # intenzitet zvuka      [0, 1]
x_pokrivenost = np.arange(0, 1.01, 0.01)   # gustina pokrivenosti  [0, 1]
x_detekcija   = np.arange(0, 1.01, 0.01)   # verovatnoća detekcije [0, 1]
x_ugao        = np.arange(0, 181,  1)      # ugaona razlika        [0°, 180°]

# Univerzumi za izlaze
x_ang      = np.arange(0, 1.01, 0.01)   # engagement confidence
x_brzina   = np.arange(0, 1.01, 0.01)   # brzina kretanja
x_upornost = np.arange(0, 1.01, 0.01)   # upornost / vreme pretrage

# ─────────────────────────────────────────
# ULAZNE MF
# ─────────────────────────────────────────

# Vizuelna pouzdanost
vizuelna_nejasna   = fuzz.trapmf(x_vizuelna, [0.0, 0.0, 0.2, 0.4])
vizuelna_delimicna = fuzz.trimf (x_vizuelna, [0.3, 0.5, 0.7])
vizuelna_jasna     = fuzz.trapmf(x_vizuelna, [0.6, 0.8, 1.0, 1.0])

# Intenzitet zvuka
zvuk_tisina = fuzz.trapmf(x_zvuk, [0.0, 0.0, 0.1, 0.3])
zvuk_sum    = fuzz.trimf (x_zvuk, [0.2, 0.5, 0.8])
zvuk_pucanj = fuzz.trapmf(x_zvuk, [0.7, 0.9, 1.0, 1.0])

# Pokrivenost
pokr_retka   = fuzz.trapmf(x_pokrivenost, [0.0, 0.0, 0.2, 0.4])
pokr_srednja = fuzz.trimf (x_pokrivenost, [0.3, 0.5, 0.7])
pokr_gusta   = fuzz.trapmf(x_pokrivenost, [0.6, 0.8, 1.0, 1.0])

# Verovatnoća detekcije
det_niska   = fuzz.trapmf(x_detekcija, [0.0, 0.0, 0.2, 0.4])
det_srednja = fuzz.trimf (x_detekcija, [0.3, 0.5, 0.7])
det_visoka  = fuzz.trapmf(x_detekcija, [0.6, 0.8, 1.0, 1.0])

# Ugaona razlika [0°, 180°]
ugao_ispred = fuzz.trapmf(x_ugao, [0,   0,  30,  60])   # pravo ispred
ugao_bok    = fuzz.trimf (x_ugao, [45,  90, 135])        # sa strane
ugao_iza    = fuzz.trapmf(x_ugao, [120, 150, 180, 180])  # iza leđa

# ─────────────────────────────────────────
# IZLAZNE MF
# ─────────────────────────────────────────

# Angažovanje  (Ignorisi / Traži / Označi)
ang_ignorisi = fuzz.trapmf(x_ang, [0.0, 0.0, 0.2, 0.4])
ang_trazi    = fuzz.trimf (x_ang, [0.3, 0.5, 0.7])
ang_oznaci   = fuzz.trapmf(x_ang, [0.6, 0.8, 1.0, 1.0])

# Brzina kretanja  (Patrolna / Oprezna / Fokusirana)
brzina_patrolna   = fuzz.trapmf(x_brzina, [0.0, 0.0, 0.2, 0.4])
brzina_oprezna    = fuzz.trimf (x_brzina, [0.3, 0.5, 0.7])
brzina_fokusirana = fuzz.trapmf(x_brzina, [0.6, 0.8, 1.0, 1.0])

# Upornost pretrage  (Kratkotrajna / Zadržana / Uporna)
upor_kratkotrajna = fuzz.trapmf(x_upornost, [0.0, 0.0, 0.2, 0.4])
upor_zadrzana     = fuzz.trimf (x_upornost, [0.3, 0.5, 0.7])
upor_uporna       = fuzz.trapmf(x_upornost, [0.6, 0.8, 1.0, 1.0])

# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────

def get_membership(x_universe, mf, vrednost: float) -> float:
    return float(fuzz.interp_membership(x_universe, mf, vrednost))


def plot_all():
    fig, axes = plt.subplots(5, 2, figsize=(13, 16))
    fig.suptitle("FuzzySnitch — Membership funkcije", fontsize=14)

    skupovi = [
        (axes[0, 0], x_vizuelna,
         [vizuelna_nejasna, vizuelna_delimicna, vizuelna_jasna],
         ["nejasna", "delimična", "jasna"],
         "Vizuelna pouzdanost"),

        (axes[1, 0], x_zvuk,
         [zvuk_tisina, zvuk_sum, zvuk_pucanj],
         ["tišina", "šum", "pucanj"],
         "Intenzitet zvuka"),

        (axes[2, 0], x_pokrivenost,
         [pokr_retka, pokr_srednja, pokr_gusta],
         ["retka", "srednja", "gusta"],
         "Pokrivenost"),

        (axes[3, 0], x_detekcija,
         [det_niska, det_srednja, det_visoka],
         ["niska", "srednja", "visoka"],
         "Verovatnoća detekcije"),

        (axes[4, 0], x_ugao,
         [ugao_ispred, ugao_bok, ugao_iza],
         ["ispred", "bok", "iza"],
         "Ugaona razlika [°]"),

        (axes[0, 1], x_ang,
         [ang_ignorisi, ang_trazi, ang_oznaci],
         ["ignoriši", "traži", "označi"],
         "Angažovanje"),

        (axes[1, 1], x_brzina,
         [brzina_patrolna, brzina_oprezna, brzina_fokusirana],
         ["patrolna", "oprezna", "fokusirana"],
         "Brzina kretanja"),

        (axes[2, 1], x_upornost,
         [upor_kratkotrajna, upor_zadrzana, upor_uporna],
         ["kratkotrajna", "zadržana", "uporna"],
         "Upornost pretrage"),
    ]

    boje = ["#4A90D9", "#27AE60", "#E74C3C"]

    for ax, x_univ, mfs, labele, naslov in skupovi:
        for mf, labela, boja in zip(mfs, labele, boje):
            ax.plot(x_univ, mf, color=boja, linewidth=2, label=labela)
            ax.fill_between(x_univ, mf, alpha=0.08, color=boja)
        ax.set_title(naslov, fontsize=11)
        ax.set_ylim(-0.05, 1.15)
        ax.set_xlabel("x")
        ax.set_ylabel("μ(x)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    # Sakrij prazne subplotove (5x2 = 10 mesta, imamo 8)
    axes[3, 1].set_visible(False)
    axes[4, 1].set_visible(False)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_slucajevi = [
        ("Vizuelna pouzdanost = 0.72", x_vizuelna,
         [vizuelna_nejasna, vizuelna_delimicna, vizuelna_jasna],
         ["nejasna", "delimična", "jasna"], 0.72),

        ("Intenzitet zvuka    = 0.90", x_zvuk,
         [zvuk_tisina, zvuk_sum, zvuk_pucanj],
         ["tišina", "šum", "pucanj"], 0.90),

        ("Pokrivenost         = 0.35", x_pokrivenost,
         [pokr_retka, pokr_srednja, pokr_gusta],
         ["retka", "srednja", "gusta"], 0.35),

        ("Verovatnoća det.    = 0.60", x_detekcija,
         [det_niska, det_srednja, det_visoka],
         ["niska", "srednja", "visoka"], 0.60),

        ("Ugaona razlika      = 45°", x_ugao,
         [ugao_ispred, ugao_bok, ugao_iza],
         ["ispred", "bok", "iza"], 45.0),
    ]

    print("=" * 48)
    print("  FuzzySnitch — Membership vrednosti")
    print("=" * 48)
    for (labela, x_u, mfs, imena, val) in test_slucajevi:
        print(f"\n{labela}")
        for mf, ime in zip(mfs, imena):
            mu = get_membership(x_u, mf, val)
            traka = "█" * int(mu * 20)
            print(f"  {ime:<14} μ = {mu:.3f}  {traka}")

    plot_all()