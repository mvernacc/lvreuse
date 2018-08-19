"""Recovery strategy performance models."""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve, minimize_scalar

from landing_dv import landing_dv
import unavail_mass
from payload import payload_fixed_stages


def stage_sep_range(v_ss, f_ss=0.02):
    """Estimate the downrange distance at stage separation.
    
    Arguments:
        v_ss (positive scalar): Velocity at stage separation [units: meter second**-1].
        f_ss (positive scalar): Stage separation downrange distance model coefficient
            [units: meter**-1 second**2].
    Returns:
        scalar: downrange distance at stage separation [units: meter].
    """
    return f_ss * v_ss**2


def rocketback_delta_v(v_ss, f_ss=0.02, dz=50e3, dv_loss=200, phi_rb=None):
    """Estimate the delta-v for the rocket-back maneuver.
    
    Arguments:
        v_ss (positive scalar): Velocity at stage separation [units: meter second**-1].
        f_ss (positive scalar): Stage separation downrange distance model coefficient
            [units: meter**-1 second**2].
        dz (positive scalar): Altitude loss available for rocket-back maneuver & coast [units: meter].
        dv_loss (positive scalar): delta-v loss during the rocket-back maneuver
            [units: meter second**-1].
        phi_rb (scalar): Flight path angle just after rocket-back burn. If `None`, the
            dv-minimizing phi_rb will be computed and used. [units: radian].
    Returns:
        delta-v for the rocket-back maneuver [units: meter second**-1].
    """
    g_0 = 9.81    # Accel due to gravity near Earth's surface [units: meter second**-2].
    phi_ss = np.deg2rad(30)    # Flight path angle at stage sep [units: radian].

    # Downrange distance at stage separation [units: meter].
    x_ss = stage_sep_range(v_ss, f_ss)

    # Minimize dv over phi_rb
    def dv_rb_ideal_func(phi_rb):
        """Minimize this to find the optimal rocket-back flight path angle.

        Arguments:
            phi_rb (scalar): Flight path angle at end of rocket-back burn [units: radian].

        Returns:
            scalar: Ideal delta-v for the rocket-back maneuver [units: meter second**-1].
        """
        # Velocity required at end of rocket-back burn [units: meter second**-1].
        v_rb = (g_0 * x_ss**2 / (np.cos(phi_rb)**2 * (dz + x_ss * np.tan(phi_rb))))**0.5

        # Ideal delta-v for rocket-back maneuver [units: meter second**-1].
        dv_rb_ideal = (v_rb**2 + v_ss**2 - 2 * v_rb * v_ss * np.cos(np.pi - phi_rb - phi_ss))**0.5
        return dv_rb_ideal

    if phi_rb is None:
        res = minimize_scalar(dv_rb_ideal_func,
                              bounds=(np.deg2rad(5), np.deg2rad(85)),
                              method='Bounded',
                              options={'disp': 0}
                              )
        dv_rb_ideal = res.fun
    else:
        dv_rb_ideal = dv_rb_ideal_func(phi_rb)

    dv_rb = dv_rb_ideal + dv_loss
    return dv_rb


def stage_sep_velocity(c_1, e_1, pi_1, dv_loss_ascent=1000):
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


def coupled_perf_solver(a, c_1, c_2, E_1, E_2, y, dv_mission, recovery_propellant_func):
    # Solve for the 1st stage payload mass fraction
    def root_fun(x):
        e_1_guess = x[0]
        pi_1 = x[1]
        if pi_1 < 0:
            pi_1 = 1e-6

        v_ss = stage_sep_velocity(c_1, e_1_guess, pi_1)
        P = recovery_propellant_func(v_ss)
        e_1 = unavail_mass.unavail_mass(a, P, z_m=1, E_1=E_1)

        pi_2 = (y + 1) - y / pi_1
        dv = - c_1 * np.log(e_1 + (1 - e_1) * pi_1) - c_2 * np.log(E_2 + (1 - E_2) * pi_2)
        if np.isnan(dv):
            return [1, e_1 - e_1_guess]
        return [(dv_mission - dv) / dv_mission, e_1 - e_1_guess]

    x_guess = [y, 0.5]
    x, infodict, ier, mesg = fsolve(root_fun, x_guess, full_output=True)
    if ier != 1:
        return (np.nan, np.nan)
    e_1 = x[0]
    pi_1 = x[1]
    if pi_1 <= 0 or e_1 <= 0:
        return (np.nan, np.nan)
    pi_2 = (y + 1) - y / pi_1
    pi_star = pi_1 * pi_2

    if pi_star < 0:
        return (np.nan, np.nan)

    v_ss = stage_sep_velocity(c_1, e_1, pi_1)
    return (pi_star, v_ss)


def propulsive_ls_perf(a, c_1, c_2, E_1, E_2, y, dv_mission):
    propellant_margin = 0.10
    def recovery_propellant_func(v_ss):
        dv_rb = rocketback_delta_v(v_ss)
        dv_entry = 800.
        dv_land = landing_dv(m_A=2000., accel=30.)
        P = (dv_rb + dv_entry + dv_land) / c_1
        return P * (1 + propellant_margin)

    results = coupled_perf_solver(a, c_1, c_2, E_1, E_2, y,
                                  dv_mission, recovery_propellant_func)
    return results


def breguet_propellant_winged_powered(R_cruise, v_cruise, lift_drag, I_sp_ab):
    """Recovery propellant factor P for winged vehicle with air-breathing propulsion.

    See Breguet range equation http://web.mit.edu/16.unified/www/FALL/thermodynamics/notes/node98.html

    Arguments:
        R_cruise (scalar): cruise range [units: meter].
        v_crusie (scalar): cruise speed [units: meter second**-1].
        lift_drag (scalar): Vehicle lift/drag ratio [units: dimensionless].
        I_sp_ab (scalar): Air-breathing propulsion specific impulse [units: second].

    Returns:
        scalar: propellant factor P. The recovery vehicle will burn `e**P -1` times its inert mass
            in propellant during the recovery cruise.
    """
    return R_cruise / (v_cruise * lift_drag * I_sp_ab)


def winged_powered_ls_perf(a, c_1, c_2, E_1, E_2, y, dv_mission):
    I_sp_ab = 3600    # Specific impulse of air-breathing propulsion [units: second].
    v_cruise = 150    # Recovery cruise speed [units: meter second**-1].
    lift_drag = 4    # Recovery vehicle lift/drag ratio [units: dimensionless].
    propellant_margin = 0.10
    def recovery_propellant_func(v_ss):
        # Recovery cruise range [units: meter].
        R_cruise = stage_sep_range(v_ss)
        P = breguet_propellant_winged_powered(R_cruise, v_cruise, lift_drag, I_sp_ab)
        return P * (1 + propellant_margin)

    results = coupled_perf_solver(a, c_1, c_2, E_1, E_2, y,
                                  dv_mission, recovery_propellant_func)
    return results


def rocketback_delta_v_demo():
    v_ss = np.linspace(1e3, 4e3)
    dv_rb = np.array([rocketback_delta_v(v) for v in v_ss])
    plt.plot(v_ss, dv_rb)
    plt.xlabel('Stage sep. velocity $v_{ss}$ [m/s]')
    plt.ylabel('Rocketback $\\Delta v_{rb}$ [m/s]')
    plt.grid(True)


def propulsive_ls_perf_demo():
    print(propulsive_ls_perf(0.17, 3000, 3500, 0.06, 0.05, 0.20, 12e3))


def stage_mass_ratio_sweep():
    a_prop = 0.17
    a_wing_pwr = 0.57
    c_1 = 3000
    c_2 = 3500
    E_1 = 0.06
    E_2 = 0.04
    dv_mission = 9.5e3

    y = np.linspace(0.10, 0.40)
    pi_star_expend = np.zeros(len(y))
    pi_star_prop_ls = np.zeros(len(y))
    pi_star_wing_pwr_ls = np.zeros(len(y))
    v_ss_prop_ls = np.zeros(len(y))
    v_ss_wing_pwr_ls = np.zeros(len(y))

    for i in range(len(y)):
        pi_star_expend[i] = payload_fixed_stages(c_1, c_2, E_1, E_2, y[i], dv_mission)
        (pi_star_prop_ls[i], v_ss_prop_ls[i]) = \
            propulsive_ls_perf(a_prop, c_1, c_2, E_1, E_2, y[i], dv_mission)
        (pi_star_wing_pwr_ls[i], v_ss_wing_pwr_ls[i]) = \
            winged_powered_ls_perf(a_wing_pwr, c_1, c_2, E_1, E_2, y[i], dv_mission)

    plt.figure(figsize=(6, 8))
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(y, pi_star_expend, label='Expendable', color='black')
    plt.plot(y, pi_star_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(y, pi_star_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Stage 2 / stage 1 mass ratio $y$ [-]')
    plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
    plt.ylim([0, plt.ylim()[1]])
    plt.title('Effect of stage mass ratio on payload capacity'
        + '\nMission $\\Delta v_*$ = {:.1f} km/s, kerosene/O2 tech.'.format(dv_mission * 1e-3))
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2, sharex=ax1)
    plt.plot(y, v_ss_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(y, v_ss_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Stage 2 / stage 1 mass ratio $y$ [-]')
    plt.ylabel('Velocity at stage separation $v_{{ss}}$ [m/s]')
    plt.ylim([0, plt.ylim()[1]])
    plt.legend()
    plt.grid(True)

    plt.tight_layout()


def dv_mission_sweep():
    a_prop = 0.17
    a_wing_pwr = 0.57
    c_1 = 3000
    c_2 = 3500
    E_1 = 0.06
    E_2 = 0.04
    y = 0.20
    dv_mission = 9.5e3

    dv_mission = np.linspace(9e3, 14e3)
    pi_star_expend = np.zeros(len(dv_mission))
    pi_star_prop_ls = np.zeros(len(dv_mission))
    pi_star_wing_pwr_ls = np.zeros(len(dv_mission))
    v_ss_prop_ls = np.zeros(len(dv_mission))
    v_ss_wing_pwr_ls = np.zeros(len(dv_mission))

    for i in range(len(dv_mission)):
        pi_star_expend[i] = payload_fixed_stages(c_1, c_2, E_1, E_2, y, dv_mission[i])
        (pi_star_prop_ls[i], v_ss_prop_ls[i]) = \
            propulsive_ls_perf(a_prop, c_1, c_2, E_1, E_2, y, dv_mission[i])
        (pi_star_wing_pwr_ls[i], v_ss_wing_pwr_ls[i]) = \
            winged_powered_ls_perf(a_wing_pwr, c_1, c_2, E_1, E_2, y, dv_mission[i])

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
    plt.plot(dv_mission * 1e-3, v_ss_prop_ls, label='Propulsive launch site recov.', color='red')
    plt.plot(dv_mission * 1e-3, v_ss_wing_pwr_ls, label='Winged powered launch site recov.', color='C0')
    plt.xlabel('Mission $\\Delta v_*$ [km/s]')
    plt.ylabel('Velocity at stage separation $v_{{ss}}$ [m/s]')
    plt.ylim([0, plt.ylim()[1]])
    plt.legend()
    plt.grid(True)

    plt.tight_layout()


if __name__ == '__main__':
    # rocketback_delta_v_demo()
    # propulsive_ls_perf_demo()
    stage_mass_ratio_sweep()
    dv_mission_sweep()
    plt.show()
