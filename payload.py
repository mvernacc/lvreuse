"""Payload capability of a launch vehicle with 1st stage return."""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve


def main():
    # Stage inert masses [arb units].
    m_i1 = 1.
    m_i2 = 0.1 * m_i1
    # Stage maximum propellant loads [arb units].
    m_p1_max = 10 * m_i1
    m_p2_max = 10 * m_i2

    # Payload masses to examine [arb units].
    m_pay = np.linspace(0, m_i2)

    # Stage exahust velocities [units: meter second**-1].
    c_1 = 290 * 9.8
    c_2 = 320 * 9.8

    # Return delta-v's to plot [units: meter second**-1].
    dv_r = [1e3, 2e3]

    def get_dv_pay_no_return(m_pay):
        """Payload delta-v, no first stage return."""
        m_initial_1 = m_p1_max + m_i1 + m_p2_max + m_i2 + m_pay
        m_final_1 = m_i1 + m_p2_max + m_i2 + m_pay
        m_initial_2 = m_p2_max + m_i2 + m_pay
        m_final_2 = m_i2 + m_pay
        dv_pay = c_1 * np.log((m_initial_1 / m_final_1)) + c_2 * np.log((m_initial_2 / m_final_2))
        return dv_pay

    def get_dv_pay_return(m_pay, dv_r):
        """Payload delta-v, with first stage return."""
        m_initial_1 = m_p1_max + m_i1 + m_p2_max + m_i2 + m_pay
        m_final_1 = m_i1 * np.exp(dv_r / c_1) + m_p2_max + m_i2 + m_pay
        m_initial_2 = m_p2_max + m_i2 + m_pay
        m_final_2 = m_i2 + m_pay
        dv_pay = c_1 * np.log((m_initial_1 / m_final_1)) + c_2 * np.log((m_initial_2 / m_final_2))
        return dv_pay

    def get_payload_ratio(dv_pay, dv_r):
        """return / no return payload mass ratio"""
        # Max. possible dv with return
        dv_pay_max_return = get_dv_pay_return(0, dv_r)
        # Max. possible dv with return
        dv_pay_max_no_return = get_dv_pay_no_return(0)
        # Check if dv is too high
        if dv_pay >= dv_pay_max_no_return:
            # This dv is not achievable, even with no return.
            return np.nan
        elif dv_pay >= dv_pay_max_return:
            # This dv is achievable w/o return, but not with return.
            return 0

        m_pay_return = fsolve(lambda m_pay: dv_pay - get_dv_pay_return(m_pay, dv_r), x0=0.05)[0]
        m_pay_no_return = fsolve(lambda m_pay: dv_pay - get_dv_pay_no_return(m_pay), x0=0.05)[0]
        return m_pay_return / m_pay_no_return


    dv_pay_no_return = get_dv_pay_no_return(m_pay)
    plt.plot(dv_pay_no_return, m_pay, label='No return', linestyle='--', color='black')

    for dv_r_ in dv_r:
        dv_pay_return = get_dv_pay_return(m_pay, dv_r_)
        plt.plot(dv_pay_return, m_pay, label='$\\Delta v_r$ = {:.0f} m/s'.format(dv_r_))

    plt.xlabel('Payload  $\\Delta v$ [m/s]')
    plt.ylabel('Payload mass [arb.]')
    plt.grid(True)
    plt.legend()
    plt.title('Payload capability of 2-stage launch vehicle')

    # Find the return / no return payload mass ratio for some dv's
    plt.figure()
    for dv_r_ in dv_r:
        dv_pay_max = get_dv_pay_return(0, dv_r_)
        dv_pay = np.linspace(9e3, dv_pay_max)
        payload_ratio = [get_payload_ratio(dv_pay_, dv_r_) for dv_pay_ in dv_pay]
        plt.plot(dv_pay, payload_ratio, label='$\\Delta v_r$ = {:.0f} m/s'.format(dv_r_))
    plt.xlabel('Payload  $\\Delta v$ [m/s]')
    plt.ylabel('Payload / (payload w/o return) [-]')
    plt.grid(True)
    plt.legend()
    plt.title('Payload mass reduction due to 1st stage return')

    plt.show()


if __name__ == '__main__':
    main()
