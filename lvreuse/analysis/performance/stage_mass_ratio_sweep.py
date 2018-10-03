"""Plot payload mass fraction versus stage 2/ stage 1 mass ratio."""
import os.path

import numpy as np
from matplotlib import pyplot as plt

from lvreuse.performance import payload_fixed_stages
from lvreuse.performance.launch_site_return import (stage_sep_velocity,
                                                    propulsive_ls_perf,
                                                    winged_powered_ls_perf)
from lvreuse.data.missions import LEO


def stage_mass_ratio_sweep():
    a_prop = 0.14
    a_wing_pwr = 0.57
    c_1 = 3000
    c_2 = 3500
    E_1 = 0.06
    E_2 = 0.04
    mission = LEO

    y = np.linspace(0.10, 1.)
    pi_star_expend = np.zeros(len(y))
    pi_star_prop_ls = np.zeros(len(y))
    pi_star_wing_pwr_ls = np.zeros(len(y))
    v_ss_prop_ls = np.zeros(len(y))
    v_ss_wing_pwr_ls = np.zeros(len(y))
    v_ss_expend = np.zeros(len(y))

    for i in range(len(y)):
        expend_result = payload_fixed_stages(c_1, c_2, E_1, E_2, y[i],
                                             mission.dv, return_all_pis=True)
        if not np.any(np.isnan(expend_result)):
            pi_star_expend[i] = expend_result[0]
            pi_1 = expend_result[1]
            v_ss_expend[i] = stage_sep_velocity(c_1, E_1, pi_1)
        results = propulsive_ls_perf(c_1, c_2, E_1, E_2, y[i], mission.dv, a_prop)
        (pi_star_prop_ls[i], v_ss_prop_ls[i]) = (results.pi_star, results.v_ss)
        results = winged_powered_ls_perf(c_1, c_2, E_1, E_2, y[i], mission.dv, a_wing_pwr)
        (pi_star_wing_pwr_ls[i], v_ss_wing_pwr_ls[i]) = (results.pi_star, results.v_ss)

    plt.figure(figsize=(6, 8))
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(y, pi_star_expend, label='Expendable', color='black')
    plt.plot(y, pi_star_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(y, pi_star_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Stage 2 / stage 1 mass ratio $y$ [-]')
    plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
    plt.ylim([0, plt.ylim()[1]])
    plt.title('Effect of stage mass ratio on payload capacity'
        + '\nMission $\\Delta v_*$ = {:.1f} km/s, kerosene/O2 tech.'.format(mission.dv * 1e-3))
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2, sharex=ax1)
    plt.plot(y, v_ss_expend, label='Expendable', color='black')
    plt.plot(y, v_ss_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(y, v_ss_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Stage 2 / stage 1 mass ratio $y$ [-]')
    plt.ylabel('Velocity at stage separation $v_{{ss}}$ [m/s]')
    plt.ylim([0, plt.ylim()[1]])
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join('plots', 'stage_mass_ratio_sweep.png'))
    plt.show()



if __name__ == '__main__':
    stage_mass_ratio_sweep()
