import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import statsmodels.api as sm
from CER_data import CER_data_list
import math

data_set = CER_data_list[-2]

x_data = data_set.x_data
y_data = data_set.y_data

log_x = []
log_y = []
for index in range(len(x_data)):
    log_x.append(math.log10(x_data[index]))
    log_y.append(math.log10(y_data[index]))


def func(x, a, b):
    return a * x + b

popt, pcov = curve_fit(func, log_x, log_y)

print('regression fit: ', [popt[0], 10**popt[1]])

log_x = sm.add_constant(log_x)
mod = sm.OLS(log_y, log_x)
res = mod.fit()
#print(res.params)
conf_int = res.conf_int(alpha=0.1)

exp_conf_int = []
for bound in conf_int[0]:
    exp_conf_int.append(10**(bound))


print('x confidence interval: ', conf_int[1])
print('a confidence interval: ', exp_conf_int)




