"""Payload capability of a launch vehicle with 1st stage return."""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve

def payload_fixed_stages(c_1, c_2, e_1, e_2, y, dv_mission):
    """Get the payload capacity for a 2-stage launcher with fixed stagne mass ratio.

    Arguments:
        c_1 (scalar): 1st stage effective exhaust velocity, e.g. Isp * g_0 
            (average over recovery burns) [units: meter second**-1].
        c_2 (scalar): 2nd stage effective exhaust velocity, e.g. Isp * g_0 
            (average over recovery burns) [units: meter second**-1].
        e_1 (scalar): 1st stage unaviaible mass ratio [units: dimensionless].
        e_2 (scalar): 2nd stage unaviaible mass ratio [units: dimensionless].
        y (scalar): Stage mass ratio (m_p2 + m_s2)/(m_p1 + m_s1) [units: dimensionless].

    Returns:
        scalar: Overall payload mass ratio pi* [units: dimensionless].
    """
    # Solve for the 1st stage payload fraction which matches the mission dv
    def root_fun(pi_1):
        """Delta-v capability error as a function of 1st stage paylaod fraction."""
        pi_2 = (y + 1) - y / pi_1
        dv = - c_1 * np.log(e_1 + (1 - e_1) * pi_1) - c_2 * np.log(e_2 + (1 - e_2) * pi_2)
        if np.isnan(dv):
            return dv_mission
        return dv_mission - dv
    x, infodict, ier, mesg = fsolve(root_fun, y, full_output=True)
    if ier != 1:
        return np.nan
    pi_1 = x[0]
    pi_2 = (y + 1) - y / pi_1
    return pi_1 * pi_2


def main():
    
    g_0 = 9.81
    # Stage exahust velocities [units: meter second**-1].
    # O2/kerosene
    c_1 = 290 * g_0
    c_2 = 350 * g_0
    # O2/H2
    # c_1 = 400 * g_0
    # c_2 = 460 * g_0

    E = 0.08 # Stage inert mass fraction
    y = 0.15 # Stage mass ratio

    e_1_max = 0.25

    # Plot payload capacity vs 1st stage unavail mass
    plt.figure(figsize=(6, 9))
    for dv_mission in [9.5e3, 12e3]:
        pi_star_expend = payload_fixed_stages(c_1, c_2, E, E, y, dv_mission)
        e_1 = np.linspace(E, e_1_max)
        pi_star = np.zeros(e_1.shape)
        for i in range(len(e_1)):
            pi_star[i] = payload_fixed_stages(c_1, c_2, e_1[i], E, y, dv_mission)
            if pi_star[i] < 0:
                pi_star[i] = np.nan

        plt.subplot(2, 1, 1)
        plt.plot(e_1, pi_star, label='$\\Delta v_* = {:.1f}$ km/s'.format(
            dv_mission * 1e-3))
        plt.subplot(2, 1, 2)
        plt.plot(e_1, pi_star / pi_star_expend,
                 label='$\\Delta v_* = {:.1f}$ km/s'.format(
            dv_mission * 1e-3))

    plt.subplot(2, 1, 1)
    plt.xlabel("1st stage unavail. mass fraction $\\epsilon_1'$ [-]")
    plt.ylabel('Payload fraction $\\pi_*^{\\mathrm{recov}}$ [-]')
    plt.grid(True)
    plt.title("Effect of $\\epsilon_1'$ on payload capacity\n"
              + 'for $y = {:.2f}$, '.format(y)
              + '$c_1/g_0$={:.0f} s, $c_2/g_0$={:.0f} s, $E_1=E_2$={:.2f}'.format(
                c_1 / g_0, c_2 / g_0, E))
    plt.legend()
    plt.xlim(E, e_1_max)

    plt.subplot(2, 1, 2)
    plt.xlabel("1st stage unavail. mass fraction $\\epsilon_1'$ [-]")
    plt.ylabel('Payload factor $r_p = \\pi_*^{\\mathrm{recov}}/\\pi_*^{\\mathrm{expend}}$ [-]')
    plt.grid(True)
    plt.legend()
    plt.xlim(E, e_1_max)
    plt.ylim([0,1])

    plt.tight_layout()

    plt.savefig('payload.png')

    plt.show()



if __name__ == '__main__':
    main()
