"""examine the variation of performance with inert mass fraction."""

import seaborn as sns
import pandas
import numpy as np
from matplotlib import pyplot as plt
import os.path

import rhodium as rdm
import perf
import payload
from landing_dv import landing_dv
from unavail_mass import unavail_mass
import strategy_perf_models
from lessons.quantile_plot import quantile_plot


def main():
    # Replace the uncertainty in first stage inert mass with a wider range
    strategy_perf_models.kero_GG_boost_tech.uncertainties.pop(1)
    strategy_perf_models.kero_GG_boost_tech.uncertainties.append(
        rdm.UniformUncertainty('E_1', min_value=0.02, max_value=0.07))
    tech_1 = strategy_perf_models.kero_GG_boost_tech

    tech_2 = strategy_perf_models.kero_GG_upper_tech
    mission = strategy_perf_models.GTO


    plt.figure(figsize=(8,6))
    strats = [strategy_perf_models.Expendable, strategy_perf_models.PropulsiveLaunchSite,
                strategy_perf_models.WingedPoweredLaunchSite]
    colors = ['grey', 'red', 'blue']
    for strat, color in zip(strats, colors):
        strat_instance = strat(tech_1, tech_2, mission)
        res = strat_instance.sample_perf_model(nsamples=1000)
        res = res.as_dataframe()
        label = '{:s}'.format(strat_instance.landing_method)
        quantile_plot(res['E_1'], res['pi_star'], color=color, scatter=False, label=label)

    plt.xlabel('First stage baseline inert mass fraction $E_1$ [-]')
    plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
    plt.title('Payload performance for {:s} mission'.format(mission.name)
                + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))
    plt.ylim([0, plt.ylim()[1]])
    plt.text(x=0.060, y=plt.ylim()[1]/2, s='Al alloy tanks', rotation=90)
    plt.text(x=0.035, y=plt.ylim()[1]/2, s='Composite tanks?', rotation=90)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join('plots', 'inert_mass_sweep.png'))

    plt.show()

if __name__ == '__main__':
    main()
