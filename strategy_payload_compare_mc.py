import numpy as np
from matplotlib import pyplot as plt
from collections import namedtuple
import rhodium as rdm
import seaborn as sns
import pandas

import payload
import unavail_mass
import launch_vehicles

g_0 = 9.81

Technology = namedtuple('Technology', ['name', 'c_1', 'c_2', 'E_1', 'E_2', 'y'])
kerosene_tech = Technology(name='kerosene',
    c_1=297*g_0, E_1=0.060, c_2=350*g_0, E_2=0.040, y=0.265)
hydrogen_tech = Technology(name='hydrogen',
    c_1=386*g_0, E_1=0.121, c_2=462*g_0, E_2=0.120, y=0.18)


def monte_carlo():
    # GTO Mission delta-v [units: meter second**-1]
    dv_mission = 12e3
    mission = 'GTO'
    dv_prop_ls = np.array([2930 + 800 + 150, 4360 + 800 + 350])
    # Assume kerosene technology
    tech = kerosene_tech

    strategy_uncerts = {
        'prop_ls': [
            rdm.UniformUncertainty('a', min_value=0.05, max_value=0.07),
            rdm.UniformUncertainty('P', min_value=dv_prop_ls[0] / tech.c_1, max_value=dv_prop_ls[1] / tech.c_1)
        ],
        'wing_ls': [
            rdm.UniformUncertainty('a', min_value=0.28, max_value=0.52),
            rdm.UniformUncertainty('P', min_value=0.17, max_value=0.26),
        ],
        'wing_ls_partial': [
            rdm.UniformUncertainty('a', min_value=0.28, max_value=0.52),
            rdm.UniformUncertainty('P', min_value=0.17, max_value=0.26),
            rdm.UniformUncertainty('z_m', min_value=0.2, max_value=0.3),
        ],
        'prop_dr': [
            rdm.UniformUncertainty('a', min_value=0.05, max_value=0.07),
            rdm.UniformUncertainty('P', min_value=800 / tech.c_1, max_value=1150 / tech.c_1)
        ],
        'wing_dr': [
            rdm.UniformUncertainty('a', min_value=0.18, max_value=0.37),
        ],
        'parachute_dr_partial': [
            rdm.UniformUncertainty('a', min_value=0.15, max_value=0.19),
            rdm.UniformUncertainty('z_m', min_value=0.2, max_value=0.3),
        ],
    }

    def perf_model_func(a=0, P=0, z_m=1):
        e_1 = unavail_mass.unavail_mass(a=a, P=P, z_m=z_m, E_1=tech.E_1)
        pld_frac_recov = payload.payload_fixed_stages(
            c_1=tech.c_1,
            c_2=tech.c_2,
            e_1=e_1,
            e_2=tech.E_2,
            y=tech.y,
            dv_mission=dv_mission
            )
        return pld_frac_recov

    perf_model = rdm.Model(perf_model_func)

    perf_model.parameters = [
        rdm.Parameter('a'),
        rdm.Parameter('P'),
        rdm.Parameter('z_m')
    ]

    perf_model.responses = [
        rdm.Response('pld_frac_recov', rdm.Response.MAXIMIZE)
    ]

    results_dict = {}

    for strat, uncerts in strategy_uncerts.items():
        perf_model.uncertainties = uncerts

        scenarios = rdm.sample_lhs(perf_model, nsamples=1000)

        results = rdm.evaluate(perf_model, scenarios)
        results_dict[strat] = results['pld_frac_recov']

    pld_frac_recov = pandas.DataFrame(results_dict)

    pld_frac_expend = payload.payload_fixed_stages(
        c_1=tech.c_1,
        c_2=tech.c_2,
        e_1=tech.E_1,
        e_2=tech.E_2,
        y=tech.y,
        dv_mission=dv_mission
        )

    r_p = pld_frac_recov / pld_frac_expend

    sns.violinplot(data=r_p, width=1)

    # Plot actual Falcon 9 data
    if tech.name == 'kerosene' and mission == 'GTO':
        r_p_acutal_gto_dr = (launch_vehicles.f9_b3_e.masses['m_star_GTO_DR']
            / launch_vehicles.f9_b3_e.masses['m_star_GTO'])
        x = r_p.columns.get_loc('prop_dr')
        plt.scatter(x, r_p_acutal_gto_dr, marker='+', color='black')
        plt.text(x, r_p_acutal_gto_dr-0.05, 'Falcon 9')


    plt.ylim([0, 1])
    plt.ylabel('$r_p$, payload mass frac. relative to expendable')
    plt.xticks(rotation=30)    
    plt.title('Recovery strategies: performance estimates\nGTO mission, {:s} technology'.format(
        tech.name))
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    monte_carlo()