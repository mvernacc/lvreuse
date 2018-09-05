"""Payload capability of a 2-stage launch vehicle."""
import numpy as np
from scipy.optimize import fsolve


def payload_fixed_stages(c_1, c_2, e_1, e_2, y, dv_mission, return_all_pis=False):
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
    pi_1_guess = y / (y + 1)
    x, infodict, ier, mesg = fsolve(root_fun, pi_1_guess, full_output=True)
    if ier != 1:
        return np.nan
    pi_1 = x[0]
    pi_2 = (y + 1) - y / pi_1
    pi_star = pi_1 * pi_2

    if pi_star < 0:
        return np.nan
    if return_all_pis:
        return (pi_star, pi_1, pi_2)
    return pi_star

