"""Examine the variation of cost with number of reuses."""
import os.path

from matplotlib import pyplot as plt
import numpy as np
import rhodium as rdm
import pandas
import seaborn as sns

from lvreuse.analysis.combined import strategy_models
from lvreuse.utils import quantile_plot
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion
from lvreuse.data import missions

def main():
    tech_1 = strategy_models.kero_GG_boost_tech
    tech_2 = strategy_models.kero_GG_upper_tech

    for mission in [missions.LEO_smallsat, missions.LEO, missions.LEO_heavy]:
        expend = strategy_models.Expendable(tech_1, tech_2, mission)
        dr_prop = strategy_models.PropulsiveDownrange(tech_1, tech_2, mission)

        scenarios = rdm.sample_lhs(dr_prop.model, 1000)
        
        results = {}
        results['expend'] = rdm.evaluate(expend.model, scenarios).as_dataframe()
        results['dr_prop'] = rdm.evaluate(dr_prop.model, scenarios).as_dataframe()
        cost_ratio = results['dr_prop']['cost_per_flight'] / results['expend']['cost_per_flight']
        
        title = 'Reuse strat: {:s}, {:s} landing, {:s} recov. prop., {:s} stage'.format(
                dr_prop.recovery_location, dr_prop.landing_method,
                dr_prop.recovery_prop_method, dr_prop.portion_recovered) \
            + '\nMission: {:s}, {:.1f} Mg payload. Technology: {:s}'.format(
                mission.name, mission.m_payload * 1e-3, tech_1.fuel)
        print('\n')
        print(title)
        print('Cost ratio 5-95% percentiles: {:.3f}, {:.3f}'.format(
            *np.percentile(cost_ratio, [5, 95])))

        plt.figure()
        sns.kdeplot(cost_ratio)
        plt.xlim([0, 1])
        plt.title(title)
        plt.xlabel('cost p.f. w/ reuse / cost p.f. expendable [-]')

    plt.show()

if __name__ == '__main__':
    main()
