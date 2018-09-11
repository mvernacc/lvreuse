"""Typical satellite launch missions."""
from collections import namedtuple


"""Defines a launch mission: taking a payload to an orbit.

Attributes:
    name (str): Orbit name.
    dv (scalar): Delta-v (incl losses) required to reach the target orbit
        [units: meter second**-1].
    m_payload (scalar): Payload mass [units: kilogram].
"""
Mission = namedtuple('Mission', ['name', 'dv', 'm_payload'])

"""
Notes on delta-v to LEO:
Payload to LEO is reported for various different
low Earth orbits, so we should expect some disagreement between
the model and advertised values for real launch vehicles.

For the model, we assume that "LEO" is a 400 km altitude circular
orbit at 28.7 deg inclination, with launch from 28.7 deg latitude.

Prof. Martinez-Sanchez's 16.512 notes, Lecture 33 [https://ocw.mit.edu/courses/aeronautics-and-astronautics/16-512-rocket-propulsion-fall-2005/lecture-notes/lecture_33.pdf]
page 2 indicates that
this orbit requires 8.5 km/s to reach by an ideal two-impulse maneuver
with an initial flight path angle alpha of 30 deg.
Page 4 indicates that the delta-v is reduced by 0.407 km/s due to the
Earth's rotation, for a near-horizontal launch (alpha=0). For realistic
values of alpha, the reduction is probably somewhat less, perhaps 0.3 km/s.

Gravity, steering and drag losses must also be taken into account. Greg O'Neill's
report suggests that these are typically 1.65 km/s. Wikipedia agrees:
"Atmospheric and gravity drag associated with launch typically adds 1.3–1.8 km/s to
the launch vehicle delta-v required to reach normal LEO" [https://en.wikipedia.org/wiki/Low_Earth_orbit#Orbital_characteristics]

Thus, we expect the total delta-v to LEO to be
dv = 8.5 km/s - 0.3 km/s + 1.65 km/s = 9.85 km/s


Notes on delta-v to GTO:
Assume GTO is a 185 x 35 786 km altitude orbit at 28 deg inclination,
launch from 28 deg latitude.
Prof. Martinez-Sanchez's 16.512 notes, Lecture 34 [https://ocw.mit.edu/courses/aeronautics-and-astronautics/16-512-rocket-propulsion-fall-2005/lecture-notes/lecture_34.pdf]
page 7, say that the delta-v to launch into a 200x300 km parking orbit, then raise
the apogee to GTO, is
7.512 km/s + 2.605 km/s = 10.117 km/s
This includes dv savings from Earth's rotation.
A further 1.830 km/s would be required to circularize & change planes to geostationary
orbit from this GTO.

Adding losses, we expect the total dv to reach GTO to be
dv = 10.12 km/s + 1.65 km/s = 11.77 km/s
"""

LEO_smallsat = Mission('LEO', 9.85e3, 100)
LEO = Mission('LEO', 9.85e3, 10e3)
GTO = Mission('GTO', 11.77e3, 10e3)
