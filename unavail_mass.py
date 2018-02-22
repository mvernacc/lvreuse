"""Primary mission unavailable mass ratio for first stage recovery."""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

import payload

def unavail_mass(a, P, z_m, E_1):
    """Primary mission unavailable mass ratio for first stage recovery.

    Arguments:
        a (scalar): Fraction of the recovery vehicle dry mass which is added recovery
            hardware [units: dimensionless].
        P (scalar): Propulsion exponent recovery maneuver (e.g. Delta v / c) [units: dimensionless].
        z_m (scalar): Fraction of baseline dry mass which is to be recovered [units: dimensionless].
        E_1 (scalar): Structural mass ratio w/o reuse hardware [units: dimensionless].

    Returns:
        scalar: unavailable mass ratio [units: dimensionless].
    """
    chi_r = a * z_m / (1 - a)
    epsilon_1_prime = ((1 + chi_r + z_m / (1 - a) * (np.exp(P) - 1))
        / (1 + chi_r + (1 - E_1) / E_1))
    return epsilon_1_prime


def main():
    a = np.linspace(0, 0.99)
    P = np.linspace(0, 1.5)
    a_grid, P_grid = np.meshgrid(a, P)

    E_1 = 0.08
    z_m = [1, 0.25]

    gs = gridspec.GridSpec(1, len(z_m))


    # Plot results
    plt.figure(figsize=(12,6))

    for i in range(len(z_m)):
        e_grid = unavail_mass(a_grid, P_grid, z_m[i], E_1)

        plt.subplot(gs[0, i])
        cs = plt.contour(a_grid, P_grid, e_grid, np.logspace(-1, 0, 15))
        plt.clabel(cs, inline=1, fontsize=10)
        plt.xlabel('Recov. h/w mass ratio $a = m_{rh,1}/(m_{rh,1} + m_{hv,1})$ [-]')
        plt.ylabel('Propulsion exponent $P$ [-]')
        plt.title("Unavailable mass ratio $\\epsilon_1'$\n"
                  + 'for $E_1$={:.2f}, $z_m$={:.2f}'.format(E_1, z_m[i]))

    plt.tight_layout()
    plt.savefig('unavail_mass.png')

    # plt.figure(figsize=(6,6))
    # cs = plt.contour(chi_r_grid, dv_r_grid, r_p_grid)
    # plt.clabel(cs, inline=1, fontsize=10)
    # plt.xlabel('Recov. h/w mass ratio $\\chi_r = m_{rh,1}/m_{s,1}$ [-]')
    # plt.ylabel('Recov. $\\Delta v_r$ [m/s]')
    # plt.title("Recov. / Expend payload ratio $r_p$\n" +
    #           'for $c_1/g_0$={:.0f} s, $c_2/g_0$={:.0f} s $E_1=E_2$={:.2f}, $\\Delta v_*$={:.0f} m/s'.format(
    #             c_1/g_0, c_2/g_0, E, dv_mission))
    plt.show()


if __name__ == '__main__':
    main()
