"""Primary mission unavailable mass ratio for first stage recovery."""
import numpy as np

def unavail_mass(H, P, z_m, E_1):
    """Primary mission unavailable mass ratio for first stage recovery.

    Arguments:
        H (scalar): Fraction of the recovery vehicle dry mass which is added recovery
            hardware [units: dimensionless].
        P (scalar): Propulsion exponent recovery maneuver (e.g. Delta v / c) [units: dimensionless].
        z_m (scalar): Fraction of baseline dry mass which is to be recovered [units: dimensionless].
        E_1 (scalar): Structural mass ratio w/o reuse hardware [units: dimensionless].

    Returns:
        scalar: unavailable mass ratio [units: dimensionless].
    """
    chi_r = H * z_m / (1 - H)
    epsilon_1_prime = ((1 + chi_r + z_m / (1 - H) * (np.exp(P) - 1))
                       / (1 + chi_r + (1 - E_1) / E_1))
    return epsilon_1_prime


def inert_masses(m_1, H, z_m, E_1):
    """First stage inert masses.

    Arguments:
        m_1 (scalar): First stage wet mass [units: kilogram].
        H (scalar): Fraction of the recovery vehicle dry mass which is added recovery
            hardware [units: dimensionless].
        z_m (scalar): Fraction of baseline dry mass which is to be recovered [units: dimensionless].
        E_1 (scalar): Structural mass ratio w/o reuse hardware [units: dimensionless].

    Returns:
        scalar: First stage inert mass
        scalar: Recovery vehicle inert mass
    """
    chi_r = H * z_m / (1 - H)
    m_inert_1 = m_1 * ((1 + chi_r)
                       / (1 + chi_r + (1 - E_1) / E_1))
    m_inert_recov_1 = m_1 * ((z_m + chi_r)
                             / (1 + chi_r + (1 - E_1) / E_1))
    return m_inert_1, m_inert_recov_1
