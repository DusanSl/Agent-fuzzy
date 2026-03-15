# fuzzy/membership.py
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# Universum za svaki ulaz  [0.0 – 1.0]
# ─────────────────────────────────────────
x_visual  = np.arange(0, 1.01, 0.01)   # visual confidence
x_sound   = np.arange(0, 1.01, 0.01)   # sound intensity
x_cover   = np.arange(0, 1.01, 0.01)   # cover density
x_detect  = np.arange(0, 1.01, 0.01)   # detection probability

# Universum za izlaze
x_engage  = np.arange(0, 1.01, 0.01)   # engagement confidence
x_risk    = np.arange(0, 1.01, 0.01)   # risk level
x_urgency = np.arange(0, 1.01, 0.01)   # escalation urgency

# ─────────────────────────────────────────
# ULAZI
# ─────────────────────────────────────────

# Visual confidence: koliko agent "vidi" intrudera
visual_low    = fuzz.trapmf(x_visual, [0.0, 0.0, 0.2, 0.4])
visual_medium = fuzz.trimf (x_visual, [0.3, 0.5, 0.7])
visual_high   = fuzz.trapmf(x_visual, [0.6, 0.8, 1.0, 1.0])

# Sound intensity: tišina / šum / pucanj
sound_silence = fuzz.trapmf(x_sound, [0.0, 0.0, 0.1, 0.3])
sound_noise   = fuzz.trimf (x_sound, [0.2, 0.5, 0.8])
sound_gunshot = fuzz.trapmf(x_sound, [0.7, 0.9, 1.0, 1.0])

# Cover density: koliko je intruder sakriven
cover_sparse  = fuzz.trapmf(x_cover, [0.0, 0.0, 0.2, 0.4])
cover_medium  = fuzz.trimf (x_cover, [0.3, 0.5, 0.7])
cover_dense   = fuzz.trapmf(x_cover, [0.6, 0.8, 1.0, 1.0])

# Detection probability: ukupna verovatnoća detekcije
detect_low    = fuzz.trapmf(x_detect, [0.0, 0.0, 0.2, 0.4])
detect_medium = fuzz.trimf (x_detect, [0.3, 0.5, 0.7])
detect_high   = fuzz.trapmf(x_detect, [0.6, 0.8, 1.0, 1.0])

# ─────────────────────────────────────────
# IZLAZI
# ─────────────────────────────────────────

# Engagement confidence: ignore / search / mark
engage_ignore = fuzz.trapmf(x_engage, [0.0, 0.0, 0.2, 0.4])
engage_search = fuzz.trimf (x_engage, [0.3, 0.5, 0.7])
engage_mark   = fuzz.trapmf(x_engage, [0.6, 0.8, 1.0, 1.0])

# Risk level
risk_low    = fuzz.trapmf(x_risk, [0.0, 0.0, 0.2, 0.4])
risk_medium = fuzz.trimf (x_risk, [0.3, 0.5, 0.7])
risk_high   = fuzz.trapmf(x_risk, [0.6, 0.8, 1.0, 1.0])

# Escalation urgency
urgency_low    = fuzz.trapmf(x_urgency, [0.0, 0.0, 0.2, 0.4])
urgency_medium = fuzz.trimf (x_urgency, [0.3, 0.5, 0.7])
urgency_urgent = fuzz.trapmf(x_urgency, [0.6, 0.8, 1.0, 1.0])


# ─────────────────────────────────────────
# Helper: interp — uzima μ vrednost za dati x
# ─────────────────────────────────────────
def get_membership(x_universe, mf, value: float) -> float:
    return float(fuzz.interp_membership(x_universe, mf, value))


# ─────────────────────────────────────────
# Plot svih membership funkcija
# ─────────────────────────────────────────
def plot_all():
    fig, axes = plt.subplots(4, 2, figsize=(12, 14))
    fig.suptitle("FuzzySnitchAI — Membership Functions", fontsize=14)

    sets = [
        (axes[0, 0], x_visual,  [visual_low, visual_medium, visual_high],
         ["low", "medium", "high"], "Visual Confidence"),

        (axes[1, 0], x_sound,   [sound_silence, sound_noise, sound_gunshot],
         ["silence", "noise", "gunshot"], "Sound Intensity"),

        (axes[2, 0], x_cover,   [cover_sparse, cover_medium, cover_dense],
         ["sparse", "medium", "dense"], "Cover Density"),

        (axes[3, 0], x_detect,  [detect_low, detect_medium, detect_high],
         ["low", "medium", "high"], "Detection Probability"),

        (axes[0, 1], x_engage,  [engage_ignore, engage_search, engage_mark],
         ["ignore", "search", "mark"], "Engagement Confidence"),

        (axes[1, 1], x_risk,    [risk_low, risk_medium, risk_high],
         ["low", "medium", "high"], "Risk Level"),

        (axes[2, 1], x_urgency, [urgency_low, urgency_medium, urgency_urgent],
         ["low", "medium", "urgent"], "Escalation Urgency"),
    ]

    colors = ["#4A90D9", "#27AE60", "#E74C3C"]

    for ax, x_univ, mfs, labels, title in sets:
        for mf, label, color in zip(mfs, labels, colors):
            ax.plot(x_univ, mf, color=color, linewidth=2, label=label)
            ax.fill_between(x_univ, mf, alpha=0.08, color=color)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(-0.05, 1.15)
        ax.set_xlabel("x")
        ax.set_ylabel("μ(x)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    # Sakrij prazan subplot (4,2 = 8 mesta, mi imamo 7)
    axes[3, 1].set_visible(False)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Brzi test vrednosti
    test_cases = [
        ("visual_conf = 0.72", x_visual, [visual_low, visual_medium, visual_high],   ["low", "medium", "high"]),
        ("sound_level = 0.90", x_sound,  [sound_silence, sound_noise, sound_gunshot],["silence", "noise", "gunshot"]),
        ("cover        = 0.35", x_cover, [cover_sparse, cover_medium, cover_dense],  ["sparse", "medium", "dense"]),
        ("detect_prob  = 0.60", x_detect,[detect_low, detect_medium, detect_high],   ["low", "medium", "high"]),
    ]

    values = [0.72, 0.90, 0.35, 0.60]

    print("=" * 45)
    print("  Membership vrednosti — test ulazi")
    print("=" * 45)
    for (label, x_u, mfs, names), val in zip(test_cases, values):
        print(f"\n{label}")
        for mf, name in zip(mfs, names):
            mu = get_membership(x_u, mf, val)
            bar = "█" * int(mu * 20)
            print(f"  {name:<10} μ = {mu:.3f}  {bar}")

    plot_all()