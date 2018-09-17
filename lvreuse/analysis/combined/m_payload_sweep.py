"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.data import missions
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion

fontsize = 17

def get_mode_values(uncerts):
    modes = {}
    for unc in uncerts:
        modes[unc.name] = unc.mode_value
    return modes

def main():
    tech_1 = strategy_models.kero_GG_boost_tech
    tech_2 = strategy_models.kero_GG_upper_tech
    mission_default = strategy_models.LEO

    strats = [strategy_models.Expendable,
              strategy_models.PropulsiveLaunchSite,
              strategy_models.PropulsiveDownrange,
              strategy_models.WingedPoweredLaunchSite,
              strategy_models.WingedGlider,
              strategy_models.ParachutePartial]
    colors = ['black', 'red', 'C1', 'blue', 'magenta', 'green']
    jitters = np.logspace(-0.05, 0.05, len(strats))
    m_payload = np.array([100, 1e3, 10e3, 100e3])

    plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)
    ax.set_xscale('log')
    ax.set_yscale('log')

    for strat, color, jitter in zip(strats, colors, jitters):
        cpm_high = np.zeros(len(m_payload))
        cpm_median = np.zeros(len(m_payload))
        cpm_low = np.zeros(len(m_payload))
        strat_instance = strat(tech_1, tech_2, mission_default)
        label = '{:s}, {:s}\n{:s}, {:s}'.format(strat_instance.landing_method,
                                          strat_instance.recovery_prop_method,
                                          strat_instance.portion_recovered,
                                          strat_instance.recovery_location)
        for i in range(len(m_payload)):
            strat_instance.mission = missions.Mission(
                mission_default.name, mission_default.dv, m_payload[i])
            results = strat_instance.sample_model(nsamples=100)
            cpm_high[i] = np.percentile(results['cost_per_flight'], 90) * wyr_conversion \
                / m_payload[i]
            cpm_median[i] = np.percentile(results['cost_per_flight'], 50) * wyr_conversion \
                / m_payload[i]
            cpm_low[i] = np.percentile(results['cost_per_flight'], 10) * wyr_conversion\
                / m_payload[i]
        plt.errorbar(
            m_payload * 1e-3 * jitter, cpm_median,
            yerr=np.vstack((cpm_median - cpm_low, cpm_high - cpm_median)),
            color=color,
            label=label,
            linestyle='--',
            marker='s'
            )

    plt.suptitle('Cost/mass vs. payload capacity for {:s} mission'.format(mission_default.name)
                 + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                 + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle), fontsize=fontsize)

    plt.xlabel('Max. payload mass [Mg]', fontsize=fontsize)
    ax.set_ylabel('Cost per flight / payload mass \n [Million US Dollars in 2018 kg^-1]', fontsize=fontsize)
    ax.tick_params(axis='both', labelsize=0.7*fontsize)
    plt.legend(fontsize=0.8*fontsize, loc=3)
    plt.grid(True, which='major')
    plt.grid(True, which='minor', color=[0.8]*3)

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost per flight / payload mass [WYr kg^-1]', fontsize=fontsize)
    ax1.set_yscale('log') # , nonposy='clip')
    ax1.set_ylim(ax.get_ylim()[0]/wyr_conversion, ax.get_ylim()[1]/wyr_conversion)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1.grid(False)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    plt.savefig(os.path.join('plots', 'm_payload_sweep_{:s}_{:s}.png'.format(
        mission_default.name, tech_1.fuel)))
    plt.show()

if __name__ == '__main__':
    main()
