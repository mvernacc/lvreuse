"""Effect of stage mass ratio on payload capacity."""

import numpy as np
from matplotlib import pyplot as plt
from itertools import cycle

import payload
import launch_vehicles


def main():
    g_0 = 9.81

    lv = launch_vehicles.atlas_v_401

    # Stage exahust velocities [units: meter second**-1].
    # O2/kerosene
    c_1 = lv.c_1
    c_2 = lv.c_2

    # Stage inert mass fractions
    e_1_actual = lv.stage_inert_mass_fraction(1)
    e_1_steps = np.concatenate(([e_1_actual], np.linspace(0.10, 0.25, 4)))
    e_2 = lv.stage_inert_mass_fraction(2)

    # Stage mass ratio [units: dimensionless].
    y = np.linspace(0.05, 0.50)

    # Mission delta-v [units: meter second**-1].
    mission = 'GTO'
    dv_mission = 0
    if mission == 'GTO':
        dv_mission = 12e3    # GTO
    elif mission == 'LEO':
        dv_mission = 9.5e3    # LEO

    #colors
    color_cycle = cycle(['C' + str(i) for i in range(len(e_1_steps))])

    for e_1 in  e_1_steps:
        pi_star = np.zeros(y.shape)
        for i in range(len(y)):
            pi_star[i] = payload.payload_fixed_stages(
                c_1, c_2, e_1, e_2, y[i], dv_mission)
        if e_1 == e_1_actual:
            color='black'
            label="$\\epsilon_1'=${:.2f} (actual)".format(e_1)
        else:
            color = next(color_cycle)
            label="$\\epsilon_1'=${:.2f}".format(e_1)

        plt.plot(y, pi_star, label=label, color=color)

        # Mark the maxium, if there is one
        i_max = np.nanargmax(pi_star)
        if (i_max != 0) and (i_max != len(y) - 1):
            plt.scatter(y[i_max], pi_star[i_max], color=color)

    # Mark actual values
    pi_star_actual = lv.payload_actual(mission)
    y_actual = lv.stage_mass_ratio()
    plt.axhline(y=pi_star_actual, color='black')
    plt.axvline(x=y_actual, color='black')
    plt.text(y_actual*1.02, pi_star_actual*1.02, lv.name)

    plt.legend()
    plt.xlabel("2nd/1st stage mass ratio $y$ [-]")
    plt.ylabel('Payload mass fraction $\\pi_*$ [-]')
    plt.title("Effect of $\\epsilon_1'$ on optimal stage mass ratio\n"
        + 'for $c_1/g_0$={:.0f} s, $c_2/g_0$={:.0f} s,'.format(c_1/g_0, c_2/g_0)
        + '$\\epsilon_2$={:.2f}, $\Delta v_*$={:.1f} km/s'.format(e_2, dv_mission * 1e-3))
    # Start plot at 0,0
    ax = plt.gca()
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    plt.show()


if __name__ == '__main__':
    main()
