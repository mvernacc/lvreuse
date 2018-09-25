"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import matplotlib.ticker
import numpy as np
import rhodium as rdm

from lvreuse.analysis.combined import strategy_models
from lvreuse.utils import quantile_plot
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion


def main():
    tech_1 = strategy_models.kero_GG_boost_tech
    tech_2 = strategy_models.kero_GG_upper_tech
    mission = strategy_models.LEO

    strats = [strategy_models.PropulsiveDownrange]
    colors = ['C1']

    num_uses = np.array([1, 2, 3, 5, 7, 10, 20, 40, 60, 80, 100])
    cpf_low = np.zeros(len(num_uses))
    cpf_median = np.zeros(len(num_uses))
    cpf_high = np.zeros(len(num_uses))

    plt.figure(figsize=(10, 6))
    ax1 = plt.subplot(1, 2, 1)
    ax1.set_xscale('log')
    ax2 = plt.subplot(1, 2, 2, sharey=ax1)
    ax2.set_xscale('log')

    for strat, color in zip(strats, colors):
        strat_instance = strat(tech_1, tech_2, mission)
        label = '{:s}, {:s}\n{:s}, {:s}'.format(strat_instance.landing_method,
                                          strat_instance.recovery_prop_method,
                                          strat_instance.portion_recovered,
                                          strat_instance.recovery_location)
        # Assuming fixed launch rate
        for i in range(len(num_uses)):
            scenarios = rdm.sample_lhs(strat_instance.model, 100)
            for s in scenarios:
                s['num_reuses_e1'] = num_uses[i]
                s['num_reuses_s1'] = num_uses[i]
            results = rdm.evaluate(strat_instance.model, scenarios).as_dataframe()

            cpf_low[i], cpf_median[i], cpf_high[i] = np.percentile(results['cost_per_flight'],
                                                                   [10, 50, 90]) * wyr_conversion
        ax1.errorbar(
            num_uses, cpf_median,
            yerr=np.vstack((cpf_median - cpf_low, cpf_high - cpf_median)),
            color=color,
            label=label,
            linestyle='--',
            marker='s'
            )

        # Assuming launch rate increase with number of reuses
        for i in range(len(num_uses)):
            scenarios = rdm.sample_lhs(strat_instance.model, 100)
            for s in scenarios:
                s['num_reuses_e1'] = num_uses[i]
                s['num_reuses_s1'] = num_uses[i]
                s['launch_rate'] = min([s['launch_rate'] * num_uses[i], 50])
            results = rdm.evaluate(strat_instance.model, scenarios).as_dataframe()

            cpf_low[i], cpf_median[i], cpf_high[i] = np.percentile(results['cost_per_flight'],
                                                                   [10, 50, 90]) * wyr_conversion
        ax2.errorbar(
            num_uses, cpf_median,
            yerr=np.vstack((cpf_median - cpf_low, cpf_high - cpf_median)),
            color=color,
            label=label,
            linestyle='--',
            marker='s'
            )

    # Draw typical expendable range for comparison
    expd = strategy_models.Expendable(tech_1, tech_2, mission)
    expd_results = expd.sample_model(nsamples=1000)
    for ax in [ax1, ax2]:
        ax.axhline(y=np.percentile(expd_results['cost_per_flight'], 50) * wyr_conversion, color='grey',
                   label='Expendable')
        ax.axhspan(ymin=np.percentile(expd_results['cost_per_flight'], 10) * wyr_conversion,
                   ymax=np.percentile(expd_results['cost_per_flight'], 90) * wyr_conversion,
                   color='grey', alpha=0.5)

    # Format & label axes
    for ax in  [ax1, ax2]:
        ax.set_xlabel('Number of uses of 1st stage [-]')
        ax.set_ylabel('Cost per flight [Million US Dollars in 2018]')
        ax.set_ylim(0, ax.get_ylim()[1])
        ax.legend()
        ax.grid(True, which='major')
        ax.grid(True, which='minor', color=[0.8]*3)
        ax.set_xlim(0.9, 100)
        # make x-axis not use exponential notation (exp. not. is de default for a log axis).
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.0f'))
        ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
        # Make alternate y-axes with scale in work-years
        ax_alt = ax.twinx()
        ax_alt.set_ylabel('Cost per flight [WYr]')
        ax_alt.set_ylim(0, ax1.get_ylim()[1]/wyr_conversion)

    ax1.set_title('No effect on launch rate')
    ax2.set_title('Reuse increases launch rate')
    plt.suptitle('Cost vs. vehicle life for {:s} mission'.format(mission.name)
                 + ', {:.1f} Mg payload'.format(mission.m_payload * 1e-3)
                 + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                 + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)

    plt.savefig(os.path.join('plots', 'num_reuse_sweep_2_{:s}_{:s}.png'.format(
                mission.name, tech_1.fuel)))

    plt.show()

if __name__ == '__main__':
    main()
