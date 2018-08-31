"""Plot payload mass fraction versus mission delta-v."""

import os.path
import numpy as np
from matplotlib import pyplot as plt

from lvreuse.performance import payload_fixed_stages
from lvreuse.performance.launch_site_return import (stage_sep_velocity,
                                                    propulsive_ls_perf,
                                                    winged_powered_ls_perf)


def dv_mission_sweep():
    """Plot payload mass fraction versus mission delta-v."""
    a_prop = 0.14
    a_wing_pwr = 0.57
    c_1 = 3000
    c_2 = 3500
    E_1 = 0.06
    E_2 = 0.04
    y = 0.25
    dv_mission = 9.5e3

    dv_mission = np.linspace(9e3, 14e3)
    pi_star_expend = np.zeros(len(dv_mission))
    pi_star_prop_ls = np.zeros(len(dv_mission))
    pi_star_wing_pwr_ls = np.zeros(len(dv_mission))
    v_ss_prop_ls = np.zeros(len(dv_mission))
    v_ss_wing_pwr_ls = np.zeros(len(dv_mission))
    v_ss_expend = np.zeros(len(dv_mission))

    for i in range(len(dv_mission)):
        expend_result = payload_fixed_stages(c_1, c_2, E_1, E_2, y,
                                             dv_mission[i], return_all_pis=True)
        if not np.any(np.isnan(expend_result)):
            pi_star_expend[i] = expend_result[0]
            pi_1 = expend_result[1]
            v_ss_expend[i] = stage_sep_velocity(c_1, E_1, pi_1)
        (pi_star_prop_ls[i], v_ss_prop_ls[i]) = \
            propulsive_ls_perf(c_1, c_2, E_1, E_2, y, dv_mission[i], a_prop)
        (pi_star_wing_pwr_ls[i], v_ss_wing_pwr_ls[i]) = \
            winged_powered_ls_perf(c_1, c_2, E_1, E_2, y, dv_mission[i], a_wing_pwr)

    plt.figure(figsize=(6, 8))
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(dv_mission * 1e-3, pi_star_expend, label='Expendable', color='black')
    plt.plot(dv_mission * 1e-3, pi_star_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(dv_mission * 1e-3, pi_star_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Mission $\\Delta v_*$ [km/s]')
    plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
    plt.ylim([0, plt.ylim()[1]])
    plt.title('Effect of mission $\\Delta v$ on payload capacity'
        + '\nStage 2 / stage 1 mass ratio $y$={:.2f}, kerosene/O2 tech.'.format(y))
    plt.legend()
    plt.text(9.5, 0.005, 'LEO', rotation=90)
    plt.text(12, 0.005, 'GTO', rotation=90)
    plt.grid(True)

    plt.subplot(2, 1, 2, sharex=ax1)
    plt.plot(dv_mission * 1e-3, v_ss_expend, label='Expendable', color='black')
    plt.plot(dv_mission * 1e-3, v_ss_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(dv_mission * 1e-3, v_ss_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Mission $\\Delta v_*$ [km/s]')
    plt.ylabel('Velocity at stage separation $v_{{ss}}$ [m/s]')
    plt.ylim([0, plt.ylim()[1]])
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join('plots', 'dv_mission_sweep.png'))
    plt.show()


if __name__ == '__main__':
    dv_mission_sweep()
    
