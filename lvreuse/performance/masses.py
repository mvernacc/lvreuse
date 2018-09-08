"""Estimate engine masses."""
from lvreuse.constants import g_0


def booster_engine_mass(m_0, n_engines=1, propellant=None, tw=None, accel=2.):
    """Estimate the mass of booster (1st stage) engines.

    Arguments:
        m_0 (scalar): gross (wet) liftoff mass [units: kilogram].
        n_engines (scalar): number of identical engines on the first stage.
        propellant (str): Propellant used in first stage engines. If `propellant`
            is given and `tw` is not, the thrust/weight ratio will be set to a
            typical value for engines using that propellant. 
        tw (scalar): Engine thrust (sea level)/weight ratio [units: dimensionless].
             If given, overrides effect of `propellant`.
        accel (scalar): Liftoff vertical acceleration [units: meter second**-1].

    Returns:
        scalar: Engine mass (per engine) [units: kilogram].
    """
    if propellant is None and tw is None:
        raise ValueError('Must provide either tw or propellant')

    if propellant is not None:
        if 'H2' in propellant:
            tw = 50    # Typical value for H2/O2 engines
        if 'kero' in propellant:
            tw = 80    # Typical value for kero/O2 engines
    thrust = m_0 * (accel + g_0)
    engine_mass = thrust / (tw * g_0 * n_engines)
    return engine_mass


def upper_engine_mass(m_0_2, n_engines=1, propellant=None, tw=None, accel=10.):
    """Estimate the mass of upper stage (2nd-stage) engines.

    Arguments:
        m_0_2 (scalar): gross (wet) mass of vehicle at second stage ignition [units: kilogram].
        n_engines (scalar): number of identical engines on the second stage.
        propellant (str): Propellant used in first stage engines. If `propellant`
            is given and `tw` is not, the thrust/weight ratio will be set to a
            typical value for engines using that propellant. 
        tw (scalar): Engine thrust (sea level)/weight ratio [units: dimensionless].
             If given, overrides effect of `propellant`.
        accel (scalar): Acceleration at second stage ignition [units: meter second**-1].

    Returns:
        scalar: Engine mass (per engine) [units: kilogram].
    """
    if propellant is None and tw is None:
        raise ValueError('Must provide either tw or propellant')

    if propellant is not None:
        if 'H2' in propellant:
            tw = 33    # Typical value for H2/O2 engines
        if 'kero' in propellant:
            tw = 63    # Typical value for kero/O2 engines
    thrust = m_0_2 * accel
    engine_mass = thrust / (tw * g_0 * n_engines)
    return engine_mass
