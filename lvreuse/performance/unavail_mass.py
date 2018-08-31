"""Primary mission unavailable mass ratio for first stage recovery."""
import numpy as np

def unavail_mass(a, P, z_m, E_1):
    """Primary mission unavailable mass ratio for first stage recovery.

    Arguments:
        a (scalar): Fraction of the recovery vehicle dry mass which is added recovery
            hardware [units: dimensionless].
        P (scalar): Propulsion exponent recovery maneuver (e.g. Delta v / c) [units: dimensionless].
        z_m (scalar): Fraction of baseline dry mass which is to be recovered [units: dimensionless].
        E_1 (scalar): Structural mass ratio w/o reuse hardware [units: dimensionless].

    Returns:
        scalar: unavailable mass ratio [units: dimensionless].
    """
    chi_r = a * z_m / (1 - a)
    epsilon_1_prime = ((1 + chi_r + z_m / (1 - a) * (np.exp(P) - 1))
                       / (1 + chi_r + (1 - E_1) / E_1))
    return epsilon_1_prime
