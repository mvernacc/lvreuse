import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import statsmodels.api as sm
from CER_data import CER_data_list
import math


data_set = CER_data_list[-1]

x_data = data_set.x_data
y_data = data_set.y_data

log_x = []
log_y = []
for index in range(len(x_data)):
    log_x.append(math.log10(x_data[index]))
    log_y.append(math.log10(y_data[index]))

def func(x, b):
    return 0.535 * x + b

popt, pcov = curve_fit(func, log_x, log_y)
print popt

log_x = sm.add_constant(log_x)
mod = sm.OLS(log_y, log_x)
res = mod.fit()
print(res.params)
print(res.conf_int())

