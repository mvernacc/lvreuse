"""Recovery strategy performance models."""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve

from landing_dv import landing_dv
import unavail_mass
from payload import payload_fixed_stages


def rocketback_delta_v(v_ss, f_ss=0.02, dz=50e3, dv_loss=200):
    """Estimate the delta-v for the rocket-back maneuver.
    
    Arguments:
        v_ss (positive scalar): Velocity at stage separation [units: meter second**-1].
        f_ss (positive scalar): Stage separation downrange distance model coefficient
            [units: meter**-1 second**2].
        dz (positive scalar): Altitude loss available for rocket-back maneuver & coast [units: meter].
        dv_loss (positive scalar): delta-v loss during the rocket-back maneuver
            [units: meter second**-1].
    Returns:
        delta-v for the rocket-back maneuver [units: meter second**-1].
    """
    g_0 = 9.81    # Accel due to gravity near Earth's surface [units: meter second**-2].
    phi_ss = np.deg2rad(30)    # Flight path angle at stage sep [units: radian].
    phi_rb = np.deg2rad(60)    # Flight path angle at end of rocket-back burn [units: radian].

    # Downrange distance at stage separation [units: meter].
    x_ss = f_ss * v_ss**2

    # Velocity required at end of rocket-back burn [units: meter second**-1].
    v_rb = (g_0 * x_ss**2 / (np.cos(phi_rb)**2 * (dz + x_ss * np.tan(phi_rb))))**0.5

    # Ideal delta-v for rocket-back maneuver [units: meter second**-1].
    dv_rb_ideal = (v_rb**2 + v_ss**2 - 2 * v_rb * v_ss * np.cos(np.pi - phi_rb - phi_ss))**0.5

    dv_rb = dv_rb_ideal + dv_loss
    return dv_rb


def stage_sep_velocity(c_1, e_1, pi_1, dv_loss_ascent=300):
    """Estimate the velocity at stage separation.

    Arguments:
        c_1 (scalar): 1st stage effective exhaust velocity, e.g. Isp * g_0 
            (average over ascent) [units: meter second**-1].
        e_1 (scalar): 1st stage unavailable mass ratio [units: dimensionless].
        pi_1 (scalar): 1st stage payload mass fraction [units: dimensionless].
        dv_loss_ascent (scalar): delta-v loss during ascent [units: meter second**-1].

    Returns:
        scalar: velocity at stage separation [units: meter second**-1].
    """
    dv_1_ideal = - c_1 * np.log(e_1 + (1 - e_1) * pi_1)
    v_ss = dv_1_ideal - dv_loss_ascent
    return v_ss


def propulsive_ls_perf(a, c_1, c_2, E_1, E_2, y, dv_mission):
    # Solve for the 1st stage payload mass fraction
    def root_fun(x):
        e_1_guess = x[0]
        pi_1 = x[1]
        if pi_1 < 0:
            pi_1 = 0

        v_ss = stage_sep_velocity(c_1, e_1_guess, pi_1)
        dv_rb = rocketback_delta_v(v_ss)
        dv_entry = 800.
        dv_land = landing_dv(m_A=2000., accel=30.)
        P = (dv_rb + dv_entry + dv_land) / c_1
        e_1 = unavail_mass.unavail_mass(a, P, z_m=1, E_1=E_1)

        pi_2 = (y + 1) - y / pi_1
        dv = - c_1 * np.log(e_1 + (1 - e_1) * pi_1) - c_2 * np.log(E_2 + (1 - E_2) * pi_2)
        if np.isnan(dv):
            return [1, e_1 - e_1_guess]
        return [(dv_mission - dv) / dv_mission, e_1 - e_1_guess]

    x_guess = [y, 0.5]
    x, infodict, ier, mesg = fsolve(root_fun, x_guess, full_output=True)
    if ier != 1:
        return np.nan
    pi_1 = x[1]
    if pi_1 <= 0:
        return np.nan
    pi_2 = (y + 1) - y / pi_1
    pi_star = pi_1 * pi_2

    if pi_star < 0:
        return np.nan
    return pi_star


def rocketback_delta_v_demo():
    v_ss = np.linspace(1e3, 4e3)
    dv_rb = rocketback_delta_v(v_ss)
    plt.plot(v_ss, dv_rb)
    plt.xlabel('Stage sep. velocity $v_{ss}$ [m/s]')
    plt.ylabel('Rocketback $\\Delta v_{rb}$ [m/s]')
    plt.grid(True)
    plt.show()


def propulsive_ls_perf_demo():
    print(propulsive_ls_perf(0.17, 3000, 3500, 0.06, 0.05, 0.20, 12e3))


def stage_mass_ratio_sweep():
    a = 0.17
    c_1 = 3000
    c_2 = 3500
    E_1 = 0.06
    E_2 = 0.05
    dv_mission = 9.5e3

    y = np.linspace(0.10, 0.40)
    pi_star_expend = np.zeros(len(y))
    pi_star_prop_ls = np.zeros(len(y))

    for i in range(len(y)):
        pi_star_expend[i] = payload_fixed_stages(c_1, c_2, E_1, E_2, y[i], dv_mission)
        pi_star_prop_ls[i] = propulsive_ls_perf(a, c_1, c_2, E_1, E_2, y[i], dv_mission)

    plt.plot(y, pi_star_expend, label='Expendable')
    plt.plot(y, pi_star_prop_ls, label='Propulsive launch site recov.')
    plt.xlabel('Stage 2 / stage 1 mass ratio $y$ [-]')
    plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
    plt.ylim([0, plt.ylim()[1]])
    plt.title('Effect of stage mass ratio on payload capacity'
        + '\nMission $\\Delta v_*$ = {:.1f} km/s, kerosene/O2 tech.'.format(dv_mission * 1e-3))
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    # rocketback_delta_v_demo()
    # propulsive_ls_perf_demo()
    stage_mass_ratio_sweep()
