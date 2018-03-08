"""Rocket-back manuever."""
import numpy as np


g_0 = 9.81    # Acceleation due to gravity [units: meter second**-2].

def rocketback_dv(v_ss, phi_ss, phi_rb, dx, dz):
    """Delta v for the rocketback maneuver.

    Arguments:
        v_ss (scalar): Stage separation velocity [units: meter second**-1].
        phi_ss (scalar): Stage separation flight path angle [units: radian].
        phi_rb (scalar): Flight path angle jsut after rocketback burn [units: radian].
        dx (scalar): Rocketback maneuver horizontal distance [units: meter].
        dz (scalar): Rocketback maneuver vertical distance [units: meter].

    Returns:
        scalar: Delta v needed for rocketback manuever.
    """
    # Required velocity at end of rocketback maneuver.
    v_rb = (g_0 * dx**2 / (np.cos(phi_rb)**2 * (dz + dx * np.tan(phi_rb))))**0.5

    # Delta v for rocketback manuever.
    # Using law of cosines, assuming impulsive burn.
    dv_rb = (v_rb**2 + v_ss**2 - 2 * v_rb * v_ss * np.cos(np.pi - phi_rb - phi_ss))**0.5

    return dv_rb


def main():
    v_ss = 1600
    phi_ss = np.deg2rad(25)
    phi_rb = np.deg2rad(60)
    dx = 110e3
    dz = 74e3

    # Min and max dx are from McKinney, figure 2.
    print 'LEO min = {:.0f} m/s'.format(
        rocketback_dv(v_ss=1500, phi_ss=phi_ss, phi_rb=phi_rb, dx=110e3, dz=100e3))
    print 'LEO max = {:.0f} m/s'.format(
        rocketback_dv(v_ss=2000, phi_ss=phi_ss, phi_rb=phi_rb, dx=190e3, dz=50e3))

    # Min and max dx are guesses
    print 'GTO min = {:.0f} m/s'.format(
        rocketback_dv(v_ss=2100, phi_ss=phi_ss, phi_rb=phi_rb, dx=150e3, dz=100e3))
    print 'GTO max = {:.0f} m/s'.format(
        rocketback_dv(v_ss=3300, phi_ss=phi_ss, phi_rb=phi_rb, dx=250e3, dz=50e3))


if __name__ == '__main__':
    main()
