from matplotlib import pyplot as plt
from CER_data import liquid_storable_prod
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion
from lvreuse.cost.elements import StorableTurboFed
import math
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats
import statsmodels.api as sm
import os.path

element = StorableTurboFed
element_data = liquid_storable_prod
y_data_wyr = [y*wyr_conversion for y in element_data.y_data]

log_y = [math.log10(y) for y in element_data.y_data]
log_x = [math.log10(x) for x in element_data.x_data]

def func(x, a, b):
    return a * x + b

popt, pcov = curve_fit(func, log_x, log_y)

x_prod = popt[0]
a_prod = 10**popt[1]

log_x = sm.add_constant(log_x)
mod = sm.OLS(log_y, log_x)
res = mod.fit()
conf_int = res.conf_int(alpha=0.05)


a_prod_conf_int = [10**bound for bound in conf_int[0]]
x_prod_conf_int = [bound for bound in conf_int[1]]

prod_a = 1.9
prod_x = 0.535

y_transcost = [wyr_conversion*prod_a*M**prod_x for M in element_data.x_data]

y_upper = [wyr_conversion*a_prod_conf_int[1]*M**x_prod_conf_int[1] for M in element_data.x_data]
y_lower = [wyr_conversion*a_prod_conf_int[0]*M**x_prod_conf_int[0] for M in element_data.x_data]

plt.figure()
ax = plt.subplot(1, 1, 1)

plt.plot(element_data.x_data, y_transcost)
plt.fill_between(element_data.x_data, y_lower, y_upper, color='blue', alpha='0.2')
plt.scatter(element_data.x_data, y_data_wyr, zorder=10)
plt.title('First unit production costs \n Liquid rocket engines with storable propellants')
plt.xlabel('Engine dry mass [kg]')
plt.ylabel('Production cost [Million US Dollars in 2018]')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([30, 1e4])
ax.set_ylim([3, 2e2])
ax.grid(which='both', axis='both', zorder=5)

plt.savefig(os.path.join('plots', 'storable_engine_uncertainty.png'))


plt.figure()
ax = plt.subplot(1, 1, 1)

plt.plot(element_data.x_data, y_transcost)
plt.scatter(element_data.x_data, y_data_wyr, zorder=10)
plt.title('First unit production costs \n Liquid rocket engines with storable propellants')
plt.xlabel('Engine dry mass [kg]')
plt.ylabel('Production cost [Million US Dollars in 2018]')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([30, 1e4])
ax.set_ylim([3, 2e2])
ax.grid(which='both', axis='both', zorder=5)

plt.savefig(os.path.join('plots', 'storable_engine.png'))


plt.show()