"""Delta-v estimation for propulsive landing."""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve


# Speed of sound in air at 290 K [units: meter second**-1].
a = 342

# Graviational acceleration [units: meter second**-2].
g_0 = 9.81

# Atmosphere scale height [units: meter].
# At 290 K, near surface
H_0 = 8500.

# Atmosphere sea level density [units: kilogram meter**-3].
# At 290 K
rho_0 = 1.20


def drag(M):
    """Drag coefiicient of a cylinder in transonic flight.

    Reference: S. F. Hoerner, "Fluid-Dynamic Drag" Ch 16.3

    Arguments:
        M (scalar): Mach number [units: dimensionless].

    """
    # Hoerner says K_fore = 0.9. The formula below is a hack to
    # make the curve match Hoerner ch 16 figure 14.
    K_fore = 0.9 if M > 1 else 0.8
    # Stagnation pressure increment / dynamic pressure
    qq = 1 + M**2/4 + M**4/10    # Eqn 15.4
    if M >= 1:
        # Include pressure loss due to normal shock
        qq = 1.84 - 0.76/M**2 + 0.166/M**4 + 0.035/M**6    # Eqn 16.4
    C_D = K_fore * qq
    return C_D


def terminal_velocity(m_A, H):
    """Terminal velocity of a falling cylinder.

    Arguments:
        m_A (scalar): mass/area ratio [units: kilogram meter**-2].
        H (scalar): altitude [units: meter].

    Returns:
        Terminal velocity [units: meter second**-1].
    """
    def root_fun(v):
        M = v / a
        v_t = (2 * m_A * g_0 / (drag(M) * rho_0))**0.5 * np.exp(H / (2 * H_0))
        return v - v_t
    v_t = fsolve(root_fun, 300.)[0]
    return v_t


def landing_dv(m_A, accel):
    """Landing dv.

    Arguments:
        m_A (scalar): mass/area ratio [units: kilogram meter**-2].
        accel (scalar): landing acceleartion [units: meter second**-2].

    Returns:
        Terminal velocity [units: meter second**-1].
    """
    def root_fun(v):
        M = v / a
        t_b = v / accel
        H = 0.5 * accel * t_b**2
        v_t = (2 * m_A * g_0 / (drag(M) * rho_0))**0.5 * np.exp(H / (2 * H_0))
        return v - v_t
    v_t = fsolve(root_fun, 300.)[0]
    return v_t * (1 + g_0 / accel)


def main():
    # Plot the drag model
    M = np.linspace(0, 4)
    C_D = [drag(M_) for M_ in M]
    plt.plot(M, C_D)
    plt.grid(True)
    plt.xlabel('$M$')
    plt.ylabel('$C_D$')

    # Range of mass/area ratios to consider
    m_A = np.linspace(300, 4000)

    # Compute and plot delta-v for landing
    plt.figure()
    accels = [2*g_0, 3*g_0, 4*g_0]
    colors = ['C0', 'C1', 'C2']
    for accel, color in zip(accels, colors):
        dv_land = np.array([landing_dv(m_A_, accel) for m_A_ in m_A])
        v_t = dv_land / (1 + g_0 / accel)
        plt.plot(m_A, dv_land,
                 label='$\Delta v_{{land}}, a={:.0f} g_0$'.format(accel / g_0),
                 color=color, linestyle='-')
        plt.plot(m_A, v_t,
                 label='$v_t, a={:.0f} g_0$'.format(accel / g_0),
                 color=color, linestyle='--')
    
    plt.axhline(y=a, color='grey', label='sonic')
    plt.xlabel('Mass / frontal area ratio [kg/m^2]')
    plt.ylabel('Velocity [m/s]')
    plt.legend()
    plt.savefig('landing_dv.png')

    plt.show()

if __name__ == '__main__':
    main()
