import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# Ulazi

x_vizuelna    = np.arange(0, 1.01, 0.01)
x_zvuk        = np.arange(0, 1.01, 0.01)
x_pokrivenost = np.arange(0, 1.01, 0.01)
x_detekcija   = np.arange(0, 1.01, 0.01)
x_ugao        = np.arange(0, 181,  1)

# Izlazi

x_ang      = np.arange(0, 1.01, 0.01)
x_brzina   = np.arange(0, 1.01, 0.01)
x_upornost = np.arange(0, 1.01, 0.01)

# ULAZNE MF

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

# Ugaona razlika
ugao_ispred = fuzz.trapmf(x_ugao, [0,   0,  30,  60])
ugao_bok    = fuzz.trimf (x_ugao, [45,  90, 135])
ugao_iza    = fuzz.trapmf(x_ugao, [120, 150, 180, 180])

# IZLAZNE MF

# Angažovanje
ang_ignorisi = fuzz.trapmf(x_ang, [0.0, 0.0, 0.2, 0.4])
ang_trazi    = fuzz.trimf (x_ang, [0.3, 0.5, 0.7])
ang_oznaci   = fuzz.trapmf(x_ang, [0.6, 0.8, 1.0, 1.0])

# Brzina kretanja
brzina_patrolna   = fuzz.trapmf(x_brzina, [0.0, 0.0, 0.2, 0.4])
brzina_oprezna    = fuzz.trimf (x_brzina, [0.3, 0.5, 0.7])
brzina_fokusirana = fuzz.trapmf(x_brzina, [0.6, 0.8, 1.0, 1.0])

# Upornost pretrage
upor_kratkotrajna = fuzz.trapmf(x_upornost, [0.0, 0.0, 0.2, 0.4])
upor_zadrzana     = fuzz.trimf (x_upornost, [0.3, 0.5, 0.7])
upor_uporna       = fuzz.trapmf(x_upornost, [0.6, 0.8, 1.0, 1.0])

def get_membership(x_universe, mf, vrednost: float) -> float:
    return float(fuzz.interp_membership(x_universe, mf, vrednost))
