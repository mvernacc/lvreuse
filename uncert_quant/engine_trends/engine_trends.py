import pandas
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

engines = pandas.read_csv('engines.csv', index_col=0)
engines['Thrust/Weight'] = engines['Thrust (vac)'] / (engines['Mass'] * 9.81)
print(engines)

plt.figure(figsize=(10, 8))
plt.subplot(2, 2, 1)
sns.scatterplot(data=engines, x='Year of first flight', y='Isp (vac)',
                hue='Fuel', style='Cycle', legend=False)
plt.ylabel('$I_{sp}$, vacuum [s]')

plt.subplot(2, 2, 2)
sns.scatterplot(data=engines, x='Year of first flight', y='Isp (sl)',
                hue='Fuel', style='Cycle')
plt.ylabel('$I_{sp}$, sea level [s]')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.subplot(2, 2, 3)
sns.scatterplot(data=engines, x='Year of first flight', y='Chamber pressure',
                hue='Fuel', style='Cycle', legend=False)
plt.ylabel('Chamber pressure [Pa]')


plt.subplot(2, 2, 4)
sns.scatterplot(data=engines, x='Year of first flight', y='Thrust/Weight',
                hue='Fuel', style='Cycle', legend=False)
plt.ylabel('(Vacuum Thrust)/(Weight) [-]')
plt.suptitle('Historical Trends in Liquid-Propellant Rocket Engine Performance')
plt.tight_layout()
plt.subplots_adjust(top=0.95)

# Select "modern" engines, flown after 1975
engines = engines.loc[engines['Year of first flight'] >= 1975]

# Divide upper-stage and booster engines
upper_engines = engines.loc[engines['Use'] == 'Upper']
booster_engines = engines.loc[engines['Use'] == 'Booster']

# Divide H2 and kerosene engines
# kero_upper_engines = upper_engines.loc[upper_engines['Fuel'] == 'kero']
hue_order = ['GG', 'SC', 'Expander', 'Electric']
plt.figure(figsize=(8, 4))
ax1 = plt.subplot(2, 1, 1)
sns.stripplot(data=upper_engines, x='Isp (vac)', y='Fuel', hue='Cycle',
              jitter=False, dodge=True, hue_order=hue_order)
plt.title('Performance of Modern (Post-1975) Upper-Stage Engines')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.subplot(2, 1, 2, sharex=ax1)
sns.stripplot(data=booster_engines, x='Isp (vac)', y='Fuel', hue='Cycle',
              jitter=False, dodge=True,  hue_order=hue_order)
plt.title('Performance of Modern (Post-1975) Booster Engines')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.tight_layout()

# Compute the min, max, and mean vacuum Isp for each propellant and cycle
print('Performance distributions, upper stage engines:')
for fuel in ['H2', 'kero']:
    for cycle in hue_order:
        print('\tFuel = {:s}, cycle = {:s}'.format(fuel, cycle))
        x = upper_engines.loc[(upper_engines['Fuel'] == fuel) & (upper_engines['Cycle'] == cycle)]['Isp (vac)']
        if len(x) > 0:
            print('\t\tIsp vac: min={:.1f}, max={:.1f}, mean={:.1f}'.format(min(x), max(x), np.mean(x)))
        else:
            print('\t\tNo data')

plt.show()
