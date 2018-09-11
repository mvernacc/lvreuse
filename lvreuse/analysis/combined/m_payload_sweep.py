"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.utils import quantile_plot

def get_mode_values(uncerts):
    modes = {}
    for unc in uncerts:
        modes[unc.name] = unc.mode_value
    return modes

def main():
    tech_1 = strategy_models.kero_GG_boost_tech
    tech_2 = strategy_models.kero_GG_upper_tech
    mission_default = strategy_models.LEO

    strats = [strategy_models.PropulsiveLaunchSite,
              strategy_models.PropulsiveDownrange,
              strategy_models.WingedPoweredLaunchSite,
              strategy_models.WingedGlider,
              strategy_models.ParachutePartial]
    colors = ['red', 'C1', 'blue', 'magenta', 'green']

    m_payload = np.logspace(2, 5)
    cpf = np.zeros(len(m_payload))

    plt.figure(figsize=(8, 6))

    for strat, color in zip(strats, colors):
        strat_instance = strat(tech_1, tech_2, mission_default)
        label = '{:s}, {:s}\n{:s}, {:s}'.format(strat_instance.landing_method,
                                          strat_instance.recovery_prop_method,
                                          strat_instance.portion_recovered,
                                          strat_instance.recovery_location)
        modes = get_mode_values(strat_instance.uncertainties)
        for i in range(len(m_payload)):
            strat_instance.mission = strategy_models.Mission(
                mission_default.name, mission_default.dv, m_payload[i])
            results = strat_instance.evaluate(**modes)
            cpf[i] = results[4]
        plt.loglog(m_payload * 1e-3, cpf, color=color, label=label)

    # Draw typical expendable range for comparison
    expd = strategy_models.Expendable(tech_1, tech_2, mission_default)
    m_payload = np.array([100, 1e3, 10e3, 100e3])
    cpf_high = np.zeros(len(m_payload))
    cpf_median = np.zeros(len(m_payload))
    cpf_low = np.zeros(len(m_payload))
    for i in range(len(m_payload)):
        expd.mission = strategy_models.Mission(
                mission_default.name, mission_default.dv, m_payload[i])
        expd_results = expd.sample_model(nsamples=100)
        cpf_high[i] = np.percentile(expd_results['cost_per_flight'], 90)
        cpf_median[i] = np.percentile(expd_results['cost_per_flight'], 50)
        cpf_low[i] = np.percentile(expd_results['cost_per_flight'], 10)
    plt.errorbar(
        m_payload * 1e-3, cpf_median,
        yerr=np.vstack((cpf_median - cpf_low, cpf_high - cpf_median)),
        color='grey',
        label='Expendable',
        linestyle='None',
        marker='s'
        )

    plt.suptitle('Cost vs. payload capacity for {:s} mission'.format(mission_default.name)
                 + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                 + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))

    plt.xlabel('Max. payload mass [Mg]')
    plt.ylabel('Cost per flight [WYr]')
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
