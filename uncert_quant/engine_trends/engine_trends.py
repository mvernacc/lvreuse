import pandas
from matplotlib import pyplot as plt
import seaborn as sns

engines = pandas.read_csv('engines.csv', index_col=0)
engines['Thrust/Weight'] = engines['Thrust (vac)'] / (engines['Mass'] * 9.81)
print(engines)

plt.subplot(2, 2, 1)
sns.scatterplot(data=engines, x='Year of first flight', y='Isp (vac)', hue='Fuel', style='Cycle')
plt.ylabel('$I_{sp}$, vacuum [s]')

plt.subplot(2, 2, 2)
sns.scatterplot(data=engines, x='Year of first flight', y='Isp (sl)', hue='Fuel', style='Cycle')
plt.ylabel('$I_{sp}$, sea level [s]')

plt.subplot(2, 2, 3)
sns.scatterplot(data=engines, x='Year of first flight', y='Chamber pressure', hue='Fuel', style='Cycle')
plt.ylabel('Chamber pressure [Pa]')

plt.subplot(2, 2, 4)
sns.scatterplot(data=engines, x='Year of first flight', y='Thrust/Weight', hue='Fuel', style='Cycle')
plt.ylabel('(Vacuum Thrust)/(Weight) [-]')
plt.suptitle('Historical Trends in Liquid-Propellant Rocket Engine Performance')
plt.show()
