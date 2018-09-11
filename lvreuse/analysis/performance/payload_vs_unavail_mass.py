import numpy as np
from matplotlib import pyplot as plt

from lvreuse.performance import payload_fixed_stages
from lvreuse.data import launch_vehicles
from lvreuse.data.missions import LEO, GTO


def main():
    fig, axes = plt.subplots(ncols=2, nrows=2)
    fig.set_size_inches(12, 9)
    plot_payload('H2', axes, 0)
    plot_payload('kerosene', axes, 1)
    plt.suptitle("Effect of $\\epsilon_1'$ on payload capacity")
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.savefig('payload.png')
    plt.show()


def plot_payload(technology, axes, which_column):
    g_0 = 9.81

    if technology == 'H2':
        # Hydrogen-fuel technology, based on Delta IV
        # Stage exahust velocities [units: meter second**-1].
        c_1 = 386 * g_0
        c_2 = 462 * g_0

        # Stage inert mass fraction [units: dimensionless].
        E_1 = 0.120
        E_2 = 0.120

        # Stage mass ratio [units: dimensionless].
        # Approx the payload-optimal value
        y = 0.18
    elif technology == 'kerosene':
        # Kerosene-fuel technology, based on Falcon 9 Block 3
        # Stage exahust velocities [units: meter second**-1].
        c_1 = 297 * g_0
        c_2 = 350 * g_0

        # Stage inert mass fraction [units: dimensionless].
        E_1 = 0.060
        E_2 = 0.039

        # Stage mass ratio [units: dimensionless].
        # F9 value
        y = 0.265

    e_1_max = 0.40

    # Plot payload capacity vs 1st stage unavail mass
    for mission in [LEO, GTO]:
        pi_star_expend = payload_fixed_stages(c_1, c_2, E_1, E_2, y, mission.dv)
        e_1 = np.linspace(E_1, e_1_max)
        pi_star = np.zeros(e_1.shape)
        for i in range(len(e_1)):
            pi_star[i] = payload_fixed_stages(c_1, c_2, e_1[i], E_2, y, mission.dv)

        plt.sca(axes[0, which_column])
        plt.plot(e_1, pi_star, label='{:s}'.format(mission.name))

        plt.sca(axes[1, which_column])
        plt.plot(e_1, pi_star / pi_star_expend,
                 label='{:s}'.format(mission.name))

    if technology == 'kerosene':
        # Plot actual r_p values for Falcon 9
        r_p_acutal_gto_dr = (launch_vehicles.f9_b3_e.masses['m_star_GTO_DR']
            / launch_vehicles.f9_b3_e.masses['m_star_GTO'])
        r_p_acutal_leo_ls = (launch_vehicles.f9_b3_e.masses['m_star_LEO_LS']
            / launch_vehicles.f9_b3_e.masses['m_star_LEO'])
        plt.sca(axes[1, which_column])
        plt.axhline(y=r_p_acutal_gto_dr, color='C1', linestyle='--')
        plt.text(0.15, r_p_acutal_gto_dr + 0.02, 'F9 GTO downrange')
        plt.axhline(y=r_p_acutal_leo_ls, color='C0', linestyle='--')
        plt.text(0.15, r_p_acutal_leo_ls + 0.02, 'F9 LEO launch site')


    plt.sca(axes[0, which_column])
    plt.xlabel("1st stage unavail. mass fraction $\\epsilon_1'$ [-]")
    plt.ylabel('Payload fraction $\\pi_*^{\\mathrm{recov}}$ [-]')
    plt.grid(True)
    plt.title('{:s} technology\n'.format(technology)
              + '$y = {:.2f}$, '.format(y)
              + '$c_1/g_0$={:.0f} s, $c_2/g_0$={:.0f} s, $E_1$={:.2f}, $E_2$={:.2f}'.format(
                  c_1 / g_0, c_2 / g_0, E_1, E_2))
    plt.legend()
    plt.xlim(E_1, e_1_max)
    plt.ylim([0, 0.05])

    plt.sca(axes[1, which_column])
    plt.xlabel("1st stage unavail. mass fraction $\\epsilon_1'$ [-]")
    plt.ylabel('Payload factor $r_p = \\pi_*^{\\mathrm{recov}}/\\pi_*^{\\mathrm{expend}}$ [-]')
    plt.grid(True)
    plt.legend()
    plt.xlim(E_1, e_1_max)
    plt.ylim([0, 1])


if __name__ == '__main__':
    main()
