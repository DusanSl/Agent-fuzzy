# fuzzy/membership.py
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# Univerzumi za ulaze

x_vizuelna    = np.arange(0, 1.01, 0.01)   # vizuelna pouzdanost
x_zvuk        = np.arange(0, 1.01, 0.01)   # intenzitet zvuka
x_pokrivenost = np.arange(0, 1.01, 0.01)   # gustina pokrivenosti
x_detekcija   = np.arange(0, 1.01, 0.01)   # verovatnoća detekcije

# Univerzumi za izlaze
x_ang         = np.arange(0, 1.01, 0.01)   # angažovanje
x_rizik       = np.arange(0, 1.01, 0.01)   # nivo rizika
x_urgentnost  = np.arange(0, 1.01, 0.01)   # urgentnost eskalacije

# ULAZI

vizuelna_niska   = fuzz.trapmf(x_vizuelna, [0.0, 0.0, 0.2, 0.4])
vizuelna_srednja = fuzz.trimf (x_vizuelna, [0.3, 0.5, 0.7])
vizuelna_visoka  = fuzz.trapmf(x_vizuelna, [0.6, 0.8, 1.0, 1.0])

zvuk_tisina = fuzz.trapmf(x_zvuk, [0.0, 0.0, 0.1, 0.3])
zvuk_sum    = fuzz.trimf (x_zvuk, [0.2, 0.5, 0.8])
zvuk_pucanj = fuzz.trapmf(x_zvuk, [0.7, 0.9, 1.0, 1.0])

pokr_retka   = fuzz.trapmf(x_pokrivenost, [0.0, 0.0, 0.2, 0.4])
pokr_srednja = fuzz.trimf (x_pokrivenost, [0.3, 0.5, 0.7])
pokr_gusta   = fuzz.trapmf(x_pokrivenost, [0.6, 0.8, 1.0, 1.0])

det_niska   = fuzz.trapmf(x_detekcija, [0.0, 0.0, 0.2, 0.4])
det_srednja = fuzz.trimf (x_detekcija, [0.3, 0.5, 0.7])
det_visoka  = fuzz.trapmf(x_detekcija, [0.6, 0.8, 1.0, 1.0])

# IZLAZI

ang_ignorisi = fuzz.trapmf(x_ang, [0.0, 0.0, 0.2, 0.4])
ang_trazi    = fuzz.trimf (x_ang, [0.3, 0.5, 0.7])
ang_oznaci   = fuzz.trapmf(x_ang, [0.6, 0.8, 1.0, 1.0])

rizik_nizak   = fuzz.trapmf(x_rizik, [0.0, 0.0, 0.2, 0.4])
rizik_srednji = fuzz.trimf (x_rizik, [0.3, 0.5, 0.7])
rizik_visok   = fuzz.trapmf(x_rizik, [0.6, 0.8, 1.0, 1.0])

urg_niska    = fuzz.trapmf(x_urgentnost, [0.0, 0.0, 0.2, 0.4])
urg_srednja  = fuzz.trimf (x_urgentnost, [0.3, 0.5, 0.7])
urg_urgentna = fuzz.trapmf(x_urgentnost, [0.6, 0.8, 1.0, 1.0])


def get_membership(x_universe, mf, vrednost: float) -> float:
    return float(fuzz.interp_membership(x_universe, mf, vrednost))

def plot_all():
    fig, axes = plt.subplots(4, 2, figsize=(12, 14))
    fig.suptitle("FuzzySnitch — Membership funkcije", fontsize=14)

    skupovi = [
        (axes[0, 0], x_vizuelna,
         [vizuelna_niska, vizuelna_srednja, vizuelna_visoka],
         ["niska", "srednja", "visoka"],
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

        (axes[0, 1], x_ang,
         [ang_ignorisi, ang_trazi, ang_oznaci],
         ["ignoriši", "traži", "označi"],
         "Angažovanje"),

        (axes[1, 1], x_rizik,
         [rizik_nizak, rizik_srednji, rizik_visok],
         ["nizak", "srednji", "visok"],
         "Nivo rizika"),

        (axes[2, 1], x_urgentnost,
         [urg_niska, urg_srednja, urg_urgentna],
         ["niska", "srednja", "urgentna"],
         "Urgentnost eskalacije"),
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

    # Sakrij prazan subplot (4x2 = 8 mesta, imamo 7)
    axes[3, 1].set_visible(False)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_slucajevi = [
        ("Vizuelna pouzdanost = 0.72", x_vizuelna,
         [vizuelna_niska, vizuelna_srednja, vizuelna_visoka],
         ["niska", "srednja", "visoka"]),

        ("Intenzitet zvuka    = 0.90", x_zvuk,
         [zvuk_tisina, zvuk_sum, zvuk_pucanj],
         ["tišina", "šum", "pucanj"]),

        ("Pokrivenost         = 0.35", x_pokrivenost,
         [pokr_retka, pokr_srednja, pokr_gusta],
         ["retka", "srednja", "gusta"]),

        ("Verovatnoća det.    = 0.60", x_detekcija,
         [det_niska, det_srednja, det_visoka],
         ["niska", "srednja", "visoka"]),
    ]

    vrednosti = [0.72, 0.90, 0.35, 0.60]

    print("=" * 48)
    print("  FuzzySnitch — Membership vrednosti")
    print("=" * 48)
    for (labela, x_u, mfs, imena), val in zip(test_slucajevi, vrednosti):
        print(f"\n{labela}")
        for mf, ime in zip(mfs, imena):
            mu = get_membership(x_u, mf, val)
            traka = "█" * int(mu * 20)
            print(f"  {ime:<12} μ = {mu:.3f}  {traka}")

    plot_all()