import pandas
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


data = pandas.read_csv('range_at_stage_sep.csv', index_col=0)
data_sim = data.loc[data['Type'] == 'Simulation']
data_flight = data.loc[data['Type'] == 'Flight data']

v_ss_model = np.linspace(1e3, 3e3)
phi_ss = np.deg2rad(30)
for f_ss in [1e-2, 1.7e-2, 3e-2]:
    x_ss_model = f_ss * v_ss_model**2
    plt.plot(v_ss_model, x_ss_model * 1e-3,
        label='Model, $f_{{ss}}$ = {:.3f} m^-1 s^2'.format(f_ss))

plt.scatter(data_sim['stage sep velocity [m/s]'], data_sim['range at stage sep [km]'],
    label='Simulations')
plt.scatter(data_flight['stage sep velocity [m/s]'], data_flight['range at stage sep [km]'],
    label='Flight data [veebay]', marker='x')
plt.xlabel('Stage sep. velocity $v_{ss}$ [m/s]')
plt.ylabel('Stage sep. downrange distance $x_{ss}$ [km]')
plt.grid(True)
plt.legend()
plt.ylim([0, 150])
plt.show()
