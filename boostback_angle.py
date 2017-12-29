"""Flight path angle for 1st stage boostback burn."""
import numpy as np
from matplotlib import pyplot as plt
import pint

ureg = pint.UnitRegistry() 


dz = 30 * ureg.km    # Boostback traj altitude loss
dx = 60 * ureg.km     # Boostback trajectory horizontal distance

g = 9.8 * ureg.m * ureg.s**-2   # gravity

# Conditions at stage separation
phi_ss = np.deg2rad(30)   # Flight path angle
v_ss = 1600 * ureg.m * ureg.s**-1   # Velocity magnitude

phi_bb = np.linspace(0, np.pi / 2 - 0.1)

# Boostback velocity
v_bb = (g * dx**2 / (np.cos(phi_bb)**2 * (dz + dx * np.tan(phi_bb))))**0.5
v_bb.ito(ureg.m * ureg.s**-1)

dv_bb = (v_bb**2 + v_ss**2 - 2 * v_bb * v_ss * np.cos(np.pi - phi_bb - phi_ss))**0.5
dv_bb.ito(ureg.m * ureg.s**-1)

# Entry velocity
v_e = (v_bb**2 + 2 * g *dz)**0.5
v_e.ito(ureg.m * ureg.s**-1)

# Assume there is some max. allowable entry velocity
v_e_max = 1e3
dv_e = np.array([max(0, v_e_ - v_e_max) for v_e_ in v_e.magnitude]) * ureg.m * ureg.s**-1

plt.subplot(2, 1, 1)
plt.plot(np.rad2deg(phi_bb), v_bb, label='$v_{bb}$')
plt.plot(np.rad2deg(phi_bb), v_e, label='$v_{e}$')
plt.xlabel('$\\phi_{bb}$ [deg]')
plt.ylabel('Velocity [m/s]')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(np.rad2deg(phi_bb), dv_bb, label='$\\Delta v_{bb}$')
plt.plot(np.rad2deg(phi_bb), dv_e, label='$\\Delta v_{e}$')
plt.plot(np.rad2deg(phi_bb), dv_e + dv_bb, label='$\\Delta v_{bb} + \\Delta v_{e}$', color='black')
plt.xlabel('$\\phi_{bb}$ [deg]')
plt.ylabel('Velocity [m/s]')
plt.grid(True)
plt.legend()


plt.show()
