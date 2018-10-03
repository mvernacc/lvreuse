"""Plot contours of first stage unvaiable mass vs recovery hardware factor and recovery propellant factor."""

import os.path
from collections import namedtuple

import numpy as np
from matplotlib import pyplot as plt

from lvreuse.performance.unavail_mass import unavail_mass

fontsize = 15

def main():
    plot_contours_ap()
    plt.figure()
    plot_effect_of_structure_mass()
    plt.show()


def plot_effect_of_structure_mass():
    E_1 = np.linspace(0.01, 0.15)
    H = 0.07
    P = 1.0
    z_m = 1.0

    Strategy = namedtuple('Strategy', ['name', 'H', 'P', 'z_m', 'style'])

    prop_ls = Strategy('Propulsive, launch site', H=0.07, P=1.2, z_m=1,
        style={'color': 'red'})
    prop_dr = Strategy('Propulsive, downrange', H=0.07, P=0.3, z_m=1,
        style={'color': 'red', 'linestyle':'--'})
    wing_ls = Strategy('Wing, launch site', H=0.45, P=0.2, z_m=1,
        style={'color': 'blue'})

    strats = (prop_ls, prop_dr, wing_ls)
    for strat in strats:
        e_1 = unavail_mass(strat.H, strat.P, z_m, E_1)
        label = '{:s} (H={:.2f}, P={:.2f})'.format(strat.name, strat.H, strat.P)
        plt.plot(E_1, e_1, label=label, **strat.style)
    plt.plot(E_1, E_1, color='grey', label='Expendable 1:1')

    ax = plt.gca()
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    plt.xlabel('First stage mass tech limit $E_1$ [-]', fontsize=fontsize)
    plt.ylabel("First stage unavail. mass $\\epsilon_1'$ [-]", fontsize=fontsize)
    plt.legend(fontsize=0.8*fontsize)
    plt.savefig('effect_of_structure_mass.png')



def plot_contours_ap():
    H = np.linspace(0, 0.99)
    P = np.linspace(0, 1.5)
    H_grid, P_grid = np.meshgrid(H, P)

    g_0 = 9.81

    Case = namedtuple('Case', ['name', 'E_1', 'c_1', 'z_m'])
    kerosene_full = Case('kerosene tech, full recovery', E_1=0.06, c_1=297*g_0, z_m=1.)
    kerosene_partial = Case('kerosene tech, partial recovery', E_1=0.06, c_1=297*g_0, z_m=0.25)
    hydrogen_full = Case('hydrogen tech, full recovery', E_1=0.12, c_1=386*g_0, z_m=1.)
    hydrogen_partial = Case('hydrogen tech, partial recovery', E_1=0.12, c_1=386*g_0, z_m=0.25)
    cases = (kerosene_full, kerosene_partial, hydrogen_full, hydrogen_partial)

    # Parameters for air-breathing powered flight return
    lift_drag = 4.    # Cruise lift/drag ratio
    Isp_ab = 3600.    # Air breathing engine specific impulse [units: second].
    v_cruise = 150.    # Cruise speed [units: meter second**-1].

    # Plot results

    for case in cases:

        e_grid = unavail_mass(H_grid, P_grid, case.z_m, case.E_1)

        # Make contour plot
        plt.figure(figsize=(8, 6))        
        host_ax = plt.subplot(111)
        cs = plt.contour(H_grid, P_grid, e_grid, np.logspace(-1, 0, 15))
        plt.clabel(cs, inline=1, fontsize=0.8*fontsize)
        host_ax.set_ylim([0, max(P)])

        host_ax.set_xlabel('Hardware factor $H = m_{hr,1}/(m_{hr,1} + m_{hv,1})$ [-]', fontsize=fontsize)
        host_ax.set_ylabel('Propellant Factor $P$ [-]')
        plt.title("Unavailable mass ratio $\\epsilon_1'$\n"
                  + 'for {:s} ($E_1$={:.2f}, $z_m$={:.2f})'.format(
                      case.name, case.E_1, case.z_m), fontsize=fontsize)

        # Add secondary axis scales
        # Delta-v axis
        dv_ax = host_ax.twinx()
        dv_ax.set_ylim(0, max(P) * case.c_1)
        dv_ax.spines['left'].set_position(('outward', 50))
        dv_ax.spines['left'].set_visible(True)
        dv_ax.yaxis.set_label_position('left')
        dv_ax.yaxis.set_ticks_position('left')
        dv_ax.set_ylabel('Recov. $\\Delta v$ [m/s]', fontsize=fontsize)
        # Air-breathing cruise range axis
        ab_ax = host_ax.twinx()
        ab_ax.set_ylim(0, max(P) * lift_drag * Isp_ab * v_cruise * 1e-3)
        # ab_ax.spines['right'].set_position(('outward', 50))
        ab_ax.set_ylabel('Recov. range $R_{{cruise}}$ (for $L/D$ = {:.0f}, $v_{{cruise}}$ = {:.0f} m/s) [km]'.format(
            lift_drag, v_cruise), fontsize=fontsize)

        plt.tight_layout()
        plt.savefig(os.path.join(
            'plots',
            'unavail_mass_{:s}.png'.format(
            case.name.replace(' ', '_').replace(',', ''))),
            dpi=200)


if __name__ == '__main__':
    main()
