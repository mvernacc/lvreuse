import pandas
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')

# Load engines data from csv file
engines = pandas.read_csv('engines.csv', index_col=0)
engines.sort_values(by='Engine', inplace=True)

# Compute thurst/weight for each engine [units: dimensionless]
engines['Thrust/Weight'] = engines['Thrust (vac)'] / (engines['Mass'] * 9.81)

# Convert chamber pressure from pascals to megapascals.
engines['Chamber pressure'] = engines['Chamber pressure'] * 1e-6

print(engines)

# Save engines data as a latex table
with open('engine_historical_trends.tex', 'w') as f:
    tex = engines.to_latex(
        columns=['Use', 'Fuel', 'Cycle', 'Isp (vac)', 'Isp (sl)', 'Chamber pressure', 'Thrust/Weight', 'Year of first flight'],
        formatters={
            'Use': '{:s}'.format,
            'Fuel': '{:s}'.format,
            'Cycle': '{:s}'.format,
            'Isp (vac)': '{:.0f}'.format,
            'Isp (sl)': '{:.0f}'.format,
            'Chamber pressure': '{:.1f}'.format,
            'Thrust/Weight': '{:.0f}'.format,
            'Year of first flight': '{:d}'.format,
            }
        )
    tex = tex.replace('nan', '-')
    # Fix up column titles
    tex = tex.replace('Isp (vac)', '\\head{1.5cm}{$I_{sp}$, vacuum [s]}')
    tex = tex.replace('Isp (sl)', '\\head{1.5cm}{$I_{sp}$, sea level [s]}')
    tex = tex.replace('Chamber pressure', '\\head{1.5cm}{Chamber pressure [MPa]}')
    tex = tex.replace('Thrust/Weight', '\\head{1.5cm}{Thrust \\slash Weight [-]}')
    tex = tex.replace('Year of first flight', '\\head{1.5cm}{Year of first flight}')
    f.write(tex)


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
plt.savefig('engine_historical_trends.png')

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

plt.savefig('engine_isp_dist.png')

# Compute the min, max, and mean vacuum Isp for each propellant and cycle
print('Performance statistics, upper stage engines:')
for fuel in ['H2', 'kero']:
    for cycle in hue_order:
        print('\tFuel = {:s}, cycle = {:s}'.format(fuel, cycle))
        x = upper_engines.loc[(upper_engines['Fuel'] == fuel) & (upper_engines['Cycle'] == cycle)]['Isp (vac)']
        if len(x) > 0:
            print('\t\tIsp vac: min={:.1f}, max={:.1f}, mean={:.1f}'.format(min(x), max(x), np.mean(x)))
        else:
            print('\t\tNo data')

print('Performance statistics, booster engines:')
for fuel in ['H2', 'kero']:
    for cycle in hue_order:
        print('\tFuel = {:s}, cycle = {:s}'.format(fuel, cycle))
        x = booster_engines.loc[(booster_engines['Fuel'] == fuel) & (booster_engines['Cycle'] == cycle)]['Isp (vac)']
        if len(x) > 0:
            print('\t\tIsp vac: min={:.1f}, max={:.1f}, mean={:.1f}'.format(min(x), max(x), np.mean(x)))
        else:
            print('\t\tNo data')

# isp_dist_params
print('Triangular distribution parameters, upper stage engines:')
for fuel in ['H2', 'kero']:
    for cycle in hue_order:
        print('\tFuel = {:s}, cycle = {:s}'.format(fuel, cycle))
        x = upper_engines.loc[(upper_engines['Fuel'] == fuel) & (upper_engines['Cycle'] == cycle)]['Isp (vac)']
        if len(x) > 0 and not np.isnan(x).all():
            print('\t\tIsp: min={:.1f}, max={:.1f}, mean={:.1f}'.format(
                0.98 * min(x), max(x), np.mean(x)))
        else:
            print('\t\tNo data')

print('Triangular distribution parameters, booster stage engines:')
for fuel in ['H2', 'kero']:
    for cycle in hue_order:
        print('\tFuel = {:s}, cycle = {:s}'.format(fuel, cycle))
        engine_sample = booster_engines.loc[(booster_engines['Fuel'] == fuel) & (booster_engines['Cycle'] == cycle)]
        x = (engine_sample['Isp (vac)'] + engine_sample['Isp (sl)']) / 2
        if len(x) > 0 and not np.isnan(x).all():
            print('\t\tIsp: min={:.1f}, max={:.1f}, mean={:.1f}'.format(
                0.95 * np.nanmin(x), 1.03* np.nanmax(x), np.nanmean(x)))
        else:
            print('\t\tNo data')

plt.show()
