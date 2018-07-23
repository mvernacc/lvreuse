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
    tech_uncerts = [
        rdm.UniformUncertainty('c_1', min_value=260 * g_0, max_value=310 * g_0),
        rdm.UniformUncertainty('c_2', min_value=330 * g_0, max_value=350 * g_0),
        rdm.UniformUncertainty('E_1', min_value=0.04, max_value=0.08),
        rdm.UniformUncertainty('E_2', min_value=0.03, max_value=0.06),
        rdm.UniformUncertainty('y', min_value=0.2, max_value=0.3),
    ]

    c_1_recov = 260 * g_0 # TODO

    strategy_uncerts = {
        'prop_ls': [
            rdm.UniformUncertainty('a', min_value=0.05, max_value=0.07),
            rdm.UniformUncertainty('P', min_value=dv_prop_ls[0] / c_1_recov, max_value=dv_prop_ls[1] / c_1_recov)
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
            rdm.UniformUncertainty('P', min_value=800 / c_1_recov, max_value=1150 / c_1_recov)
        ],
        'wing_dr': [
            rdm.UniformUncertainty('a', min_value=0.18, max_value=0.37),
        ],
        'parachute_dr_partial': [
            rdm.UniformUncertainty('a', min_value=0.15, max_value=0.19),
            rdm.UniformUncertainty('z_m', min_value=0.2, max_value=0.3),
        ],
    }


    def perf_model_func(a=0, P=0, z_m=1, c_1=297*g_0, E_1=0.060, c_2=350*g_0, E_2=0.040, y=0.265):
        e_1 = unavail_mass.unavail_mass(a=a, P=P, z_m=z_m, E_1=E_1)
        pld_frac_recov = payload.payload_fixed_stages(
            c_1=c_1,
            c_2=c_2,
            e_1=e_1,
            e_2=E_2,
            y=y,
            dv_mission=dv_mission
            )
        pld_frac_expend = payload.payload_fixed_stages(
            c_1=c_1,
            c_2=c_2,
            e_1=E_1,
            e_2=E_2,
            y=y,
            dv_mission=dv_mission
            )
        r_p = pld_frac_recov / pld_frac_expend
        return pld_frac_recov, r_p


    perf_model = rdm.Model(perf_model_func)

    perf_model.parameters = [
        rdm.Parameter('a'),
        rdm.Parameter('P'),
        rdm.Parameter('z_m'),
        rdm.Parameter('c_1'),
        rdm.Parameter('c_2'),
        rdm.Parameter('E_1'),
        rdm.Parameter('E_2'),
        rdm.Parameter('y'),
    ]

    perf_model.responses = [
        rdm.Response('pld_frac_recov', rdm.Response.MAXIMIZE),
        rdm.Response('r_p', rdm.Response.MAXIMIZE),
    ]

    pld_frac_recov = {}
    r_p = {}

    for strat, uncerts in strategy_uncerts.items():
        perf_model.uncertainties = uncerts + tech_uncerts

        scenarios = rdm.sample_lhs(perf_model, nsamples=1000)

        results = rdm.evaluate(perf_model, scenarios)

        pld_frac_recov[strat] = results['pld_frac_recov']
        r_p[strat] = results['r_p']

    pld_frac_recov = pandas.DataFrame(pld_frac_recov)
    r_p = pandas.DataFrame(r_p)

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