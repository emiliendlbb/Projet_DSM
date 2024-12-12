import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy import integrate
from scipy.linalg import eig
import sympy 
import matplotlib as mpl

def load_data():
    current_dir = os.path.dirname(__file__)

    freq_path = os.path.join(current_dir, 'files', 'P2024_f_Part4.txt')
    modes_path = os.path.join(current_dir, 'files', 'P2024_Modes_Part4.txt')

    freq_data = np.loadtxt(freq_path)
    modes_data = np.loadtxt(modes_path)

    mode1 = modes_data[:, 0]
    mode2 = modes_data[:, 1]
    mode3 = modes_data[:, 2]
    mode4 = modes_data[:, 3]

    return freq_data, modes_data, mode1, mode2, mode3, mode4


x = sympy.symbols("x")

#Paramètres
E= 210e9
rho= 7850
l = 1.2 
e = 0.15
t = 0.01
A = e**2-(e-2*t)**2
I = ((e**4)/12)-((e-2*t)**4)/12
M_mot = 0.4*188
M_dv = 75
J_B = 1
J_D = 10
k1l = 10**4 
k1r = 10**9 
k2l = 10**5
k2r = 10**4
d_B = 0.25 #distance entre le chassis et la masse B
L = 0.8
a = 0.2

#Fonctions de Ritz
def phi(x,l,n):
    f = (x/l)**(n)
    return f

# N = nombre de fonctions d'approximation de Rayleigh
#Matrice des raideurs
def Stiff(N):
    K = np.zeros((N,N))
    for i in range(0,N):
        for j in range(0,N):
            phi_i = phi(x,l,i)
            phi_j = phi(x,l,j)
            phi_i_0 = phi_i.evalf(subs={x: 0})
            phi_j_0 = phi_j.evalf(subs={x: 0})
            phi_i_L = phi_i.evalf(subs={x: L})
            phi_j_L = phi_j.evalf(subs={x: L})
            
            dphi_i = sympy.diff(phi_i,x)
            dphi_j = sympy.diff(phi_j,x)
            dphi_i_0 = dphi_i.evalf(subs={x: 0})
            dphi_j_0 = dphi_j.evalf(subs={x: 0})
            dphi_i_L = dphi_i.evalf(subs={x: L})
            dphi_j_L = dphi_j.evalf(subs={x: L})
            
            d2phi_i = sympy.diff(phi_i,x,x)
            d2phi_j = sympy.diff(phi_j,x,x)
    
            kij = sympy.integrate(E*I*d2phi_i*d2phi_j, (x, 0, l)) \
                + k1l * phi_i_0*phi_j_0 + k1r * dphi_i_0 * dphi_j_0  \
                + k2l * phi_i_L * phi_j_L + k2r * dphi_i_L * dphi_j_L
        
            K[i,j] = kij
    return K

#Matrice des masses
def Mass(N):
    M = np.zeros((N,N))
    for i in range(0,N):
        for j in range(0,N):
            phi_i = phi(x,l,i)
            phi_j = phi(x,l,j)
            phi_i_B = phi_i.evalf(subs={x: L/2})
            phi_j_B = phi_j.evalf(subs={x: L/2})
            phi_i_D = phi_i.evalf(subs={x: L+a})
            phi_j_D = phi_j.evalf(subs={x: L+a})
            
            dphi_i = sympy.diff(phi_i,x)
            dphi_j = sympy.diff(phi_j,x)
            dphi_i_B = dphi_i.evalf(subs={x: L/2})
            dphi_j_B = dphi_j.evalf(subs={x: L/2})
            dphi_i_D = dphi_i.evalf(subs={x: L+a})
            dphi_j_D = dphi_j.evalf(subs={x: L+a})
            
            mij = sympy.integrate(rho*A*phi_i*phi_j, (x, 0, l)) + M_mot * phi_i_B * phi_j_B + M_dv * phi_i_D * phi_j_D + (J_B+M_mot*(d_B)**2)*dphi_i_B*dphi_j_B+J_D*dphi_i_D*dphi_j_D
            M[i,j] = mij
    return M

def frequency_convergence(nth_frequency, freq_num):
    Nritz = 13 #  = Nombre de fonctions jusqu'auquel on teste la convergence
    OM = np.zeros(Nritz-nth_frequency+1)
    relative_errors = np.zeros_like(OM)
    N_range = np.zeros(Nritz-nth_frequency+1)
    
    for N in range(nth_frequency,Nritz+1): # Au moins nth_frequency pour avoir la freq correspondante
        K = Stiff(N)
        M = Mass(N)
        omegas_squared, eigen_vects = eig(K,M)
        ind = np.argsort(np.abs(np.sqrt(omegas_squared)))
        omegas = np.sort(np.abs(np.sqrt(omegas_squared)))/2/np.pi
        eigen_vects = eigen_vects[:, ind]
        OM[N-nth_frequency] = omegas[nth_frequency-1]
        print(N,'omega :', OM[N-nth_frequency])
        N_range[N-nth_frequency]=N
    

        
    plt.plot(N_range, OM, 'b')
    plt.plot(N_range, OM, 'bo')
    plt.title(f"Convergence de la fréquence propre {nth_frequency}")
    plt.xlabel("Nombre de fonctions d'approximation")
    plt.ylabel("Fréquence naturelle approximée [Hz]")
    plt.grid('True')
    plt.show()
    
    
    relative_errors = 100*(OM - freq_num[nth_frequency-1])/freq_num[nth_frequency-1]

    plt.plot(N_range, relative_errors, 'b')
    plt.plot(N_range, relative_errors, 'bo')
    plt.title(f"Erreur de la fréquence propre {nth_frequency}")
    plt.xlabel("Nombre de fonctions d'approximation")
    plt.ylabel("Erreur relative [%]")
    plt.grid('True')
    plt.show()


def modeshape(num_mode, Nritz, eigen_vects, points_distances, npoints):
    Ritz_mode = np.zeros(npoints)
    for i in range(0, Nritz):
        for j in range(0,npoints):
            # print("eigen_vects[i, num_mode - 1] : ", eigen_vects[i, num_mode - 1])
            # print("phi(points_distances[j],l,i) : ", phi(points_distances[j],l,i))
            Ritz_mode[j] = Ritz_mode[j] + eigen_vects[i, num_mode - 1]*phi(points_distances[j],l,i)

    print(Ritz_mode)
    return Ritz_mode


def plot_mode(num_mode, mode, points_distances):
    Npoints = 14
    Nritz = 13
    K = Stiff(Nritz)
    M = Mass(Nritz)
    omegas_squared, eigen_vects = eig(K,M)
    ind = np.argsort(omegas_squared)
    eigen_vects = eigen_vects[:,ind]
    W_ritz = modeshape(num_mode,Nritz,eigen_vects, points_distances, Npoints)
    
    plt.plot(range(len(W_ritz)), W_ritz, 'b')
    plt.plot(range(len(W_ritz)), W_ritz, 'bo')
    plt.plot(range(len(mode)), mode, 'r')
    plt.plot(range(len(mode)), mode, 'ro')
    plt.show()

    return W_ritz

def MAC(modes_1, modes_2):
    n_modes_1 = modes_1.shape[1]
    n_modes_2 = modes_2.shape[1]
    mac_matrix = np.zeros((n_modes_1, n_modes_2))

    for i in range(n_modes_1):
        for j in range(n_modes_2):
            phi_i = modes_1[:, i]
            psi_j = modes_2[:, j]
            numerator = np.abs(np.dot(phi_i.T, psi_j))**2
            denominator = np.dot(phi_i.T, phi_i) * np.dot(psi_j.T, psi_j)
            mac_matrix[i, j] = numerator / denominator

    return mac_matrix

if __name__ == "__main__":
    freqs_pitch_modes, modes, mode1, mode2, mode3, mode4 = load_data()
    exact_modes = np.column_stack((mode1, mode2, mode3, mode4))
    points_distances = np.array([0, 100, 200, 300, 400, 400, 500, 600, 700, 800, 901, 1000, 1101, 1200])
    points_distances = points_distances/1000
    # eigen_vects_1 = frequency_convergence(1, freqs_pitch_modes)
    # eigen_vects_2 = frequency_convergence(2, freqs_pitch_modes)
    # eigen_vects_3 = frequency_convergence(3, freqs_pitch_modes)
    # eigen_vects_4 = frequency_convergence(4, freqs_pitch_modes)

    W_ritz1 = plot_mode(1, mode1, points_distances)
    W_ritz2 = plot_mode(2, mode2, points_distances)
    W_ritz3 = plot_mode(3, mode3, points_distances)
    W_ritz4 = plot_mode(4, mode4, points_distances)

    Ritz_modes = np.column_stack((W_ritz1, W_ritz2, W_ritz3, W_ritz4))

    MAC_matrix = MAC(exact_modes, Ritz_modes)

    print("MAC Matrix:")
    print(MAC_matrix)

    # Optional: Visualize the MAC matrix
    plt.imshow(MAC_matrix, cmap="viridis", interpolation="nearest")
    plt.colorbar(label="MAC Value")
    plt.title("MAC Matrix")
    plt.xlabel("Mode Shapes (Set 2)")
    plt.ylabel("Mode Shapes (Set 1)")
    plt.show()