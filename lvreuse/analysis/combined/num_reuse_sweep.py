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
    mission = strategy_models.LEO

    strats = [strategy_models.PropulsiveLaunchSite,
              strategy_models.PropulsiveDownrange,
              strategy_models.WingedPoweredLaunchSite,
              strategy_models.WingedGlider,
              strategy_models.ParachutePartial]
    colors = ['red', 'C1', 'blue', 'magenta', 'green']

    num_reuses = np.arange(1, 100)
    cpf = np.zeros(len(num_reuses))

    for tech_1, tech_2 in zip([strategy_models.kero_GG_boost_tech, strategy_models.H2_SC_boost_tech],
                              [strategy_models.kero_GG_upper_tech, strategy_models.H2_SC_upper_tech]):
        for mission in [strategy_models.LEO, strategy_models.GTO]:
            plt.figure(figsize=(10, 6))
            ax1 = plt.subplot(1, 2, 1)
            ax2 = plt.subplot(1, 2, 1, sharey=ax1)

            for strat, color in zip(strats, colors):
                strat_instance = strat(tech_1, tech_2, mission)
                label = '{:s}, {:s}\n{:s}, {:s}'.format(strat_instance.landing_method,
                                                  strat_instance.recovery_prop_method,
                                                  strat_instance.portion_recovered,
                                                  strat_instance.recovery_location)
                modes = get_mode_values(strat_instance.uncertainties)
                for i in range(len(num_reuses)):
                    modes['num_reuses_s1'] = num_reuses[i]
                    modes['num_reuses_e1'] = num_reuses[i]
                    results = strat_instance.evaluate(**modes)
                    cpf[i] = results[4]
                plt.subplot(1, 2, 1)
                plt.semilogx(num_reuses, cpf, color=color)

                # Assume launch rate increase with number of reuses
                for i in range(len(num_reuses)):
                    modes['num_reuses_s1'] = num_reuses[i]
                    modes['num_reuses_e1'] = num_reuses[i]
                    modes['launch_rate'] = min([15 * num_reuses[i], 50])
                    strat_instance.cost_model.vehicle_prod_nums_list = \
                        list(range(modes['launch_rate'] * 2, modes['launch_rate'] * 3))
                    results = strat_instance.evaluate(**modes)
                    cpf[i] = results[4]
                plt.subplot(1, 2, 2)
                plt.semilogx(num_reuses, cpf, color=color, label=label)

            # Draw typical expendable range for comparison
            expd = strategy_models.Expendable(tech_1, tech_2, mission)
            expd_results = expd.sample_model(nsamples=1000)

            plt.suptitle('Cost vs. vehicle life for {:s} mission'.format(mission.name)
                         + ', {:.1f} Mg payload'.format(mission.m_payload * 1e-3)
                         + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                         + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))

            plt.subplot(1, 2, 1)
            plt.title('No effect on launch rate')

            plt.subplot(1, 2, 2)
            plt.title('Reuse increases launch rate')

            for i in [1, 2]:
                plt.subplot(1, 2, i)
                plt.axhline(y=np.percentile(expd_results['cost_per_flight'], 50), color='grey')
                plt.axhspan(ymin=np.percentile(expd_results['cost_per_flight'], 10),
                            ymax=np.percentile(expd_results['cost_per_flight'], 90),
                            color='grey', alpha=0.5)
                plt.xlabel('Number of reuses of 1st stage [-]')
                plt.ylabel('Cost per flight [WYr]')
                plt.ylim([0, plt.ylim()[1]])
                plt.legend()
                plt.grid(True, which='major')
                plt.grid(True, which='minor', color=[0.8]*3)
                plt.xlim(1, 100)

            plt.tight_layout()
            plt.subplots_adjust(top=0.85)

            plt.savefig(os.path.join('plots', 'num_reuse_sweep_{:s}_{:s}.png'.format(
                mission.name, tech_1.fuel)))
    plt.show()

if __name__ == '__main__':
    main()
