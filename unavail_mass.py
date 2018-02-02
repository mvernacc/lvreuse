"""Primary mission unavailable mass ratio for first stage recovery."""
import numpy as np
from matplotlib import pyplot as plt

import payload

def unavail_mass(chi_r, dv_r, E, c_1):
    """Primary mission unavailable mass ratio for first stage recovery.

    Arguments:
        chi_r (scalar): ratio of recovery hardware mass to other 1st stage inert mass
            [units: dimensionless].
        dv_r (scalar): delta-V for the recovery maneuver [units: meter second**-1].
        E (scalar): Structural mass ratio w/o reuse hardware [units: dimensionless].
        c_1 (scalar): 1st stage effective exhaust velocity, e.g. Isp * g_0 
            (average over recovery burns) [units: meter second**-1].

    Returns:
        scalar: unavailable mass ratio [units: dimensionless].
    """
    epsilon_1_prime = (chi_r + 1) / ((1 - E) / E + chi_r + 1) * np.exp(dv_r / c_1)
    return epsilon_1_prime


def main():
    chi_r = np.arange(0, 0.33, 1e-2)
    dv_r = np.arange(0, 2000, 10)
    chi_r_grid, dv_r_grid = np.meshgrid(chi_r, dv_r)

    E = 0.08
    c_1 = 3000.

    e_grid = unavail_mass(chi_r_grid, dv_r_grid, E, c_1)

    c_2 = 3200.   # Stage 2 exhaust velocity [units: meter second**-1].
    y = 0.10    # Stage mass ratio.
    dv_mission = 12e3    # Mission delta-v [units: meter second**-1].

    # Payload mass fraction for expendable rocket
    pi_star_expend = payload.payload_fixed_stages(c_1, c_2, E, E, y, dv_mission)
    print 'Expendable payload fraction = {:.3f}'.format(pi_star_expend)
    
    # Compute the payload mass fraction ratio for each recovery strategy
    r_p_grid = np.zeros(chi_r_grid.shape)
    for i in range(len(chi_r)):
        for j in range(len(dv_r)):
            pi_star = payload.payload_fixed_stages(c_1, c_2, e_grid[j, i], E,
                                                   y, dv_mission)
            r_p_grid[j, i] = pi_star / pi_star_expend

    # Plot results
    plt.figure()
    cs = plt.contour(chi_r_grid, dv_r_grid, e_grid)
    plt.clabel(cs, inline=1, fontsize=10)
    plt.xlabel('Recov. h/w mass ratio $\\chi_r = m_{r1}/m_{s1}$ [-]')
    plt.ylabel('Recov. $\\Delta v_r$ [m/s]')
    plt.title("Unavailable mass ratio $\\epsilon_1'$\n" +
              'for $c_1$={:.0f} m/s, $E$={:.2f}'.format(c_1, E))

    plt.figure()
    cs = plt.contour(chi_r_grid, dv_r_grid, r_p_grid)
    plt.clabel(cs, inline=1, fontsize=10)
    plt.xlabel('Recov. h/w mass ratio $\\chi_r = m_{r1}/m_{s1}$ [-]')
    plt.ylabel('Recov. $\\Delta v_r$ [m/s]')
    plt.title("Recov. / Expend payload ratio $r_p$\n" +
              'for $c_1$={:.0f} m/s, $c_2$={:.0f} m/s $E$={:.2f}, $\\Delta v_*$={:.0f} m/s'.format(
                c_1, c_2, E, dv_mission))
    plt.show()


if __name__ == '__main__':
    main()
