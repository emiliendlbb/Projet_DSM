import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.integrate import cumulative_trapezoid

current_dir = os.path.dirname(__file__)

freq_path = os.path.join(current_dir, 'files', 'P2024_frf_acc.txt')
acc_path = os.path.join(current_dir, 'files', 'P2024_irf_acc.txt')

data_freq = np.loadtxt(freq_path)
freq = data_freq[:, 0]
Re_FRF = data_freq[:, 1]
Im_FRF = data_freq[:, 2]
data_acc = np.loadtxt(acc_path)
time = data_acc[:, 0]
acc = data_acc[:, 1]

plt.plot(time, data_acc)
plt.show()


def damped_natural_frequency(data_acc):
    time = data_acc[:, 0]
    acc = data_acc[:, 1]

    peaks, _ = find_peaks(acc)

    time_peaks = time[peaks]
    # print(time_peaks)

    time_peaks_difference = np.diff(time_peaks)
    # print(time_peaks_difference)

    time_peaks_difference = time_peaks_difference[7:]
    # print(time_peaks_difference)

    avg_time_peaks_difference = np.mean(time_peaks_difference)

    damped_natural_frequency = 1/avg_time_peaks_difference

    return damped_natural_frequency


def integrate_acc(data_acc):
    time = data_acc[:, 0]
    acc = data_acc[:, 1]

    velocity = cumulative_trapezoid(acc, time, initial=0)

    displacement = cumulative_trapezoid(velocity, time, initial=0)

    return displacement, velocity

def log_method(displacement):
    peaks, _ = find_peaks(displacement)

    displacement_peaks = displacement[peaks]
    # print(displacement_peaks)

    displacement_peaks = displacement_peaks[1:6]
    # print(displacement_peaks)

    log_quotient = np.log(np.abs(displacement_peaks[:-1] / displacement_peaks[1:]))
    # print(log_quotient)

    mean_log = np.mean(log_quotient)

    damping_ratio = mean_log / (2 * np.pi)

    return damping_ratio

    



natural_freq_peaks = damped_natural_frequency(data_acc)
print(f"Estimated natural frequency from peaks: {natural_freq_peaks} Hz")

natural_omega_peaks = 2*np.pi*natural_freq_peaks
print(f"Estimated natural pulsation from peaks: {natural_omega_peaks} Hz")

displacement, velocity = integrate_acc(data_acc)
# print(displacement)

damping_ratio_log_method = log_method(displacement)
print(f"Estimated natural frequency from Bode plot: {damping_ratio_log_method} Hz")

plt.plot(time, displacement)
plt.show()


# Construire la fonction de transfert complexe
fonction_transfert = Re_FRF + 1j * Im_FRF

# Calculer l'amplitude (module) et la phase (argument)
amplitude = np.abs(fonction_transfert)
phase = np.angle(fonction_transfert)

# Tracer l'amplitude et la phase
plt.figure()

# Amplitude
plt.subplot(2, 1, 1)
plt.plot(freq, amplitude)
plt.title("Amplitude de la fonction de transfert")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")

# Phase
plt.subplot(2, 1, 2)
plt.plot(freq, phase)
plt.title("Phase de la fonction de transfert")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Phase (radians)")

plt.tight_layout()
plt.show()

# natural frequency at the resonance peak
peak_idx = np.argmax(amplitude)
natural_frequency_bode = freq[peak_idx]

print(f"Estimated natural frequency from Bode plot: {natural_frequency_bode} Hz")

#half-power method
half_power_amplitude = amplitude[peak_idx] / np.sqrt(2)
half_power_indices = np.where(amplitude >= half_power_amplitude)[0]
bandwidth_freqs = freq[half_power_indices]

delta_f = bandwidth_freqs[-1] - bandwidth_freqs[0]
print(f"Bandwidth Δf: {delta_f} Hz")

Q_factor = natural_frequency_bode / delta_f
print(f"Estimated Quality Factor (Q): {Q_factor}")

damping_ratio_half_power = 1 / (2 * Q_factor)
print(f"Estimated Damping Ratio using Half-Power Method: {damping_ratio_half_power}")


#nyquist

# Tracer le diagramme de Nyquist
plt.figure()

plt.plot(Re_FRF/(natural_omega_peaks)**2, Im_FRF/(natural_omega_peaks)**2, label='Nyquist Plot')
# plt.plot(Re_FRF, -Im_FRF, linestyle='--', label='Conjugate symmetry')

# Ajout des axes pour plus de clarté
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)

# Titres et légendes
plt.title("Diagramme de Nyquist")
plt.xlabel("Partie réelle")
plt.ylabel("Partie imaginaire")
plt.legend()

plt.grid(True)
plt.axis('equal')  # Pour avoir des échelles identiques sur les deux axes
plt.show()
