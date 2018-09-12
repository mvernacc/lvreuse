"""Plot payload vs delta-v to target orbit."""
import os.path

import numpy as np
from matplotlib import pyplot as plt

from lvreuse.data.missions import LEO, GTO
from lvreuse.performance import payload_fixed_stages
from lvreuse.data import launch_vehicles


def plot_lv(lv, color='C0'):
    """Plot the payload capacity vs mission delta-v for a given launch vehicle."""
    # Scatter-plot the actual payload capacities for LEO and GTO
    pi_star_actual = []
    dv = []
    for mission in [LEO, GTO]:
        pi_star_actual.append(lv.payload_actual(mission.name))
        dv.append(mission.dv)
    dv = np.array(dv); pi_star_actual = np.array(pi_star_actual)
    plt.scatter(dv * 1e-3, pi_star_actual, color=color, marker='+', s=64,
        label=lv.name + ', advertised')

    # Plot the modeled paylaod vs dv
    # Stage inert mass fractions [units: dimensionless]
    e_1 = lv.stage_inert_mass_fraction(1)
    e_2 = lv.stage_inert_mass_fraction(2)
    # Stage mass ratio [units: dimensionless]
    y = lv.stage_mass_ratio()

    dv = np.linspace(9e3, 14e3)
    pi_star_model = np.zeros(len(dv))
    for i in range(len(dv)):
        pi_star_model[i] = payload_fixed_stages(
            c_1=lv.c_1, c_2=lv.c_2,
            e_1=e_1, e_2=e_2,
            y=y, dv_mission=dv[i])
    plt.plot(dv * 1e-3, pi_star_model, color=color,
             label=lv.name + ', model')


def main():
    lvs = [launch_vehicles.delta_iv_m, launch_vehicles.f9_b3_e]
    colors = ['C0', 'C1']
    plt.figure()
    for lv, color in zip(lvs, colors):
        plot_lv(lv, color)
    plt.xlabel('$\\Delta v_*$ to target orbit [km s^-1]')
    plt.text(LEO.dv * 1e-3, 0.005, 'LEO', rotation=90)
    plt.text(GTO.dv * 1e-3, 0.005, 'GTO', rotation=90)
    plt.ylabel('Payload mass fraction $\\pi_*$ [-]')
    plt.ylim([0, plt.ylim()[1]])
    plt.grid(True)
    plt.legend()
    plt.title('Payload performance vs. $\\Delta v$')
    plt.text(11.1, 0.026, '$\\mathrm{H_2} / \\mathrm{O_2}$', color='C0')
    plt.text(10, 0.017, 'kerosene$/ \\mathrm{O_2}$', color='C1')
    plt.savefig(os.path.join('plots', 'payload_vs_dv.png'), dpi=200)
    plt.show()

if __name__ == '__main__':
    main()
