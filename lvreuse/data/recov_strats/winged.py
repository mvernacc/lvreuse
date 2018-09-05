import pandas
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.stats import triang

data = pandas.read_csv('winged.csv', index_col=0)

for x in ['a, glider', 'a, powered']:
    print('\n' + x + ' triangular distribution parameters')
    print('min = {:.3f}, mode = {:.3f}, max = {:.3f}'.format(
        np.nanmin(data[x]),
        np.nanmean(data[x]),
        np.nanmax(data[x]),
        ))

sns.set(style='whitegrid')

plt.figure(figsize=(8, 5))
plt.subplot(3, 1, 1)
sns.stripplot(data=data, x='a, glider', y='Estimate type',
              jitter=False, dodge=False)
plt.xlim([0, 1])
plt.title('Recovery hardware factor for glider winged boosters')

plt.subplot(3, 1, 2)
sns.stripplot(data=data, x='a, powered', y='Estimate type',
              jitter=False, dodge=False)
plt.xlim([0, 1])
plt.title('Recovery hardware factor for air-breathing powered winged boosters')


plt.subplot(3, 1, 3)
sns.stripplot(data=data, x='P', hue='Recovery fuel', y='Estimate type',
              jitter=False, dodge=False)
plt.title('Recovery propellant factor for air-breathing powered winged boosters')
plt.xlim([0, plt.xlim()[1]])
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title='Recov. fuel')

plt.tight_layout()
plt.savefig('winged_perf_factors.png')
plt.show()
