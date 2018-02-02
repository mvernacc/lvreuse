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
        return dv_mission - dv
    pi_1 = fsolve(root_fun, y)[0]
    pi_2 = (y + 1) - y / pi_1
    return pi_1 * pi_2


def main():
    # Stage exahust velocities [units: meter second**-1].
    c_1 = 290 * 9.8
    c_2 = 320 * 9.8

    e = 0.10 # Stage inert mass fraction
    y = 0.10 # Stage mass ratio

    dv_mission = 9.5e3    # Mission delta-v [units: meter second**-1].

    pi_star = payload_fixed_stages(c_1, c_2, e, e, y, dv_mission)
    print pi_star


if __name__ == '__main__':
    main()
