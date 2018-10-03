"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import numpy as np
import rhodium as rdm

from lvreuse.analysis.combined import strategy_models
from lvreuse.data import missions
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion


def get_mode_values(uncerts):
    modes = {}
    for unc in uncerts:
        modes[unc.name] = unc.mode_value
    return modes

def main(fig_format='presentation'):
    """Plot cost/kg vs. payload mass

    Arguments:
        fig_format (string):  Figure format switch - paper or presentation?
    """
    tech_1 = strategy_models.kero_GG_boost_tech
    tech_2 = strategy_models.kero_GG_upper_tech
    mission_default = strategy_models.LEO

    if fig_format == 'paper':
        fontsize = 21
        strats = [strategy_models.Expendable,
                  strategy_models.PropulsiveLaunchSite,
                  strategy_models.PropulsiveDownrange,
                  strategy_models.WingedPoweredLaunchSite,
                  strategy_models.WingedGlider,
                  strategy_models.ParachutePartial]
        colors = ['black', 'red', 'C1', 'blue', 'magenta', 'green']
        jitters = np.logspace(-0.05, 0.05, len(strats))

    elif fig_format == 'presentation':
        fontsize = 18
        strats = [strategy_models.Expendable,
                  strategy_models.PropulsiveDownrange]
        colors = ['black', 'C1']
        jitters = np.logspace(-0.01, 0.01, len(strats))
    else:
        raise ValueError()

    expend = strategy_models.Expendable(tech_1, tech_2, mission_default)

    m_payload = np.array([100, 1e3, 10e3, 100e3])

    plt.figure(figsize=(10, 11))
    ax1 = plt.subplot(2, 1, 1)
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    ax2 = plt.subplot(2, 1, 2, sharex=ax1)


    for strat, color, jitter in zip(strats, colors, jitters):
        cpm_high = np.zeros(len(m_payload))
        cpm_median = np.zeros(len(m_payload))
        cpm_low = np.zeros(len(m_payload))
        ratio_low = np.zeros(len(m_payload))
        ratio_median = np.zeros(len(m_payload))
        ratio_high = np.zeros(len(m_payload))
        strat_instance = strat(tech_1, tech_2, mission_default)
        label = '{:s}, {:s}\n{:s}, {:s}'.format(strat_instance.landing_method,
                                          strat_instance.recovery_prop_method,
                                          strat_instance.portion_recovered,
                                          strat_instance.recovery_location)
        for i in range(len(m_payload)):
            current_mission = missions.Mission(
                mission_default.name, mission_default.dv, m_payload[i])
            strat_instance.mission = current_mission
            expend.mission = current_mission
            
            scenarios = rdm.sample_lhs(strat_instance.model, 100)
            results = rdm.evaluate(strat_instance.model, scenarios).as_dataframe()

            cpm_high[i] = np.percentile(results['cost_per_flight'], 90) * wyr_conversion \
                / m_payload[i]
            cpm_median[i] = np.percentile(results['cost_per_flight'], 50) * wyr_conversion \
                / m_payload[i]
            cpm_low[i] = np.percentile(results['cost_per_flight'], 10) * wyr_conversion\
                / m_payload[i]

            if strat.__name__ != 'Expendable':
                results_expend = rdm.evaluate(expend.model, scenarios).as_dataframe()
                cost_ratio = results['cost_per_flight'] / results_expend['cost_per_flight']
                ratio_low[i], ratio_median[i], ratio_high[i] = np.percentile(cost_ratio, [10, 50, 90])


        ax1.errorbar(
            m_payload * 1e-3 * jitter, cpm_median,
            yerr=np.vstack((cpm_median - cpm_low, cpm_high - cpm_median)),
            color=color,
            label=label,
            linestyle='--',
            marker='s'
            )
        if strat.__name__ != 'Expendable':
            ax2.errorbar(
                m_payload * 1e-3 * jitter, ratio_median,
                yerr=np.vstack((ratio_median - ratio_low, ratio_high - ratio_median)),
                color=color,
                label=label,
                linestyle='--',
                marker='s'
                )


    plt.suptitle('Cost/mass vs. payload capacity for {:s} mission'.format(mission_default.name)
                 + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                 + '\nstage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle), fontsize=fontsize)

    ax1.set_ylabel('Cost per flight / payload mass \n [Million US Dollars in 2018 kg^-1]', fontsize=fontsize)
    ax1.legend(fontsize=0.8*fontsize, loc=3)

    ax2.set_xlabel('Max. payload mass [Mg]', fontsize=fontsize)
    ax2.set_ylabel('Cost w/ reuse / expendable [-]', fontsize=fontsize)
    ax2.set_ylim([0, 1])

    for ax in [ax1, ax2]:
        ax.grid(True, which='major')
        ax.grid(True, which='minor', color=[0.8]*3)
        ax.tick_params(axis='both', labelsize=0.7*fontsize)

    plt.setp(ax1.get_xticklabels(), visible=False)

    ax1_alt = ax1.twinx()
    ax1_alt.set_ylabel('Cost per flight / payload mass [WYr kg^-1]', fontsize=fontsize)
    ax1_alt.set_yscale('log') # , nonposy='clip')
    ax1_alt.set_ylim(ax1.get_ylim()[0]/wyr_conversion, ax1.get_ylim()[1]/wyr_conversion)
    ax1_alt.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1_alt.grid(False)

    plt.tight_layout()
    plt.subplots_adjust(top=0.85, hspace=0.03)

    plt.savefig(os.path.join('plots', 'm_payload_sweep_{:s}_{:s}.png'.format(
        mission_default.name, tech_1.fuel)))
    plt.show()

if __name__ == '__main__':
    main()
