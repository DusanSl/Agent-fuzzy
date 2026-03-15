import numpy as np
import skfuzzy as fuzzy # scikit-fuzzy biblioteka
import matplotlib.pyplot as plt

# Universum
x = np.arange(0, 1.01, 0.01)

# Membership funkcije za visual confidence
low    = fuzzy.trapmf(x, [0, 0, 0.2, 0.45])
medium = fuzzy.trimf(x,  [0.3, 0.5, 0.7])
high   = fuzzy.trapmf(x, [0.55, 0.8, 1.0, 1.0])

# Test vrednosti
test_val = 0.72
print(f"visual_conf = {test_val}")
print(f"  low:    {fuzzy.interp_membership(x, low,    test_val):.3f}")
print(f"  medium: {fuzzy.interp_membership(x, medium, test_val):.3f}")
print(f"  high:   {fuzzy.interp_membership(x, high,   test_val):.3f}")

# Plot
plt.figure(figsize=(8, 4))
plt.plot(x, low,    'b', label='low')
plt.plot(x, medium, 'g', label='medium')
plt.plot(x, high,   'r', label='high')
plt.axvline(x=test_val, color='k', linestyle='--', label=f'test = {test_val}')
plt.title('Visual Confidence — Membership Functions')
plt.legend()
plt.grid(True)
plt.show()