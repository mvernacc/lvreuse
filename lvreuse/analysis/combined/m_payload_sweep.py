"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.data import missions


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

    plt.figure(figsize=(8, 6))
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
            cpm_high[i] = np.percentile(results['cost_per_flight'], 90) \
                / m_payload[i]
            cpm_median[i] = np.percentile(results['cost_per_flight'], 50) \
                / m_payload[i]
            cpm_low[i] = np.percentile(results['cost_per_flight'], 10) \
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
                 + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))

    plt.xlabel('Max. payload mass [Mg]')
    plt.ylabel('Cost per flight / payload mass [WYr kg^-1]')
    plt.legend()
    plt.grid(True, which='major')
    plt.grid(True, which='minor', color=[0.8]*3)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    plt.savefig(os.path.join('plots', 'm_payload_sweep_{:s}_{:s}.png'.format(
        mission_default.name, tech_1.fuel)))
    plt.show()

if __name__ == '__main__':
    main()
