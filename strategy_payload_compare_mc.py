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
    # Assume technology: kerosene, gg cycle, Al alloy tanks
    tech = kerosene_tech
    tech_uncerts = [
        rdm.TriangularUncertainty('c_1', min_value=264.6 * g_0, mode_value=287.9 * g_0, max_value=305.4 * g_0),
        rdm.TriangularUncertainty('c_2', min_value=335.2 * g_0, mode_value=345.0 * g_0, max_value=348.0 * g_0),
        rdm.TriangularUncertainty('E_1', min_value=0.055, mode_value=0.060, max_value=0.065),
        rdm.TriangularUncertainty('E_2', min_value=0.040, mode_value=0.050, max_value=0.060),
        rdm.UniformUncertainty('y', min_value=0.2, max_value=0.3),
    ]

    c_1_recov = 280 * g_0 # TODO

    strategy_uncerts = {
        'prop_ls': [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            rdm.UniformUncertainty('P', min_value=dv_prop_ls[0] / c_1_recov, max_value=dv_prop_ls[1] / c_1_recov)
        ],
        'wing_pwr_ls': [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            rdm.UniformUncertainty('P', min_value=0.15, max_value=0.20),
        ],
        'wing_pwr_ls_partial': [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            rdm.UniformUncertainty('P', min_value=0.15, max_value=0.20),
            rdm.UniformUncertainty('z_m', min_value=0.2, max_value=0.3),
        ],
        'prop_dr': [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            rdm.UniformUncertainty('P', min_value=800 / c_1_recov, max_value=1150 / c_1_recov)
        ],
        'wing_glide_dr': [
            rdm.TriangularUncertainty('a', min_value=0.380, mode_value=0.426, max_value=0.540),
        ],
        'parachute_dr_partial': [
            rdm.TriangularUncertainty('a', min_value=0.15, mode_value=0.17, max_value=0.19),
            rdm.UniformUncertainty('z_m', min_value=0.2, max_value=0.3),
        ],
        'expend': [],
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


    pld_frac_recov = {}
    r_p = {}

    for strat, uncerts in strategy_uncerts.items():
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

        perf_model.uncertainties = uncerts + tech_uncerts

        scenarios = rdm.sample_lhs(perf_model, nsamples=1000)

        results = rdm.evaluate(perf_model, scenarios)

        pld_frac_recov[strat] = results['pld_frac_recov']
        r_p[strat] = results['r_p']


    pld_frac_recov = pandas.DataFrame(pld_frac_recov)
    r_p = pandas.DataFrame(r_p)

    sns.set(style='whitegrid')
    sns.violinplot(data=r_p.loc[:, r_p.columns != 'expend'], width=1)

    # Plot actual Falcon 9 data
    if tech.name == 'kerosene' and mission == 'GTO':
        r_p_acutal_gto_dr = (launch_vehicles.f9_b3_e.masses['m_star_GTO_DR']
            / launch_vehicles.f9_b3_e.masses['m_star_GTO'])
        x = r_p.columns.get_loc('prop_dr')
        plt.scatter(x, r_p_acutal_gto_dr, marker='+', color='red', zorder=10)
        plt.text(x + 0.1, r_p_acutal_gto_dr, 'Falcon 9', color='red', zorder=10)


    plt.ylim([0, 1])
    plt.ylabel('$r_p$, payload mass frac. relative to expendable')
    plt.xticks(rotation=30)
    plt.title('Recovery strategies: performance estimates\nGTO mission, {:s} technology'.format(
        tech.name))
    plt.tight_layout()

    # Plot liftoff mass distributions
    #  Example paylaod mass [units: megagram]
    m_pld = 5.
    m_0 = m_pld / pld_frac_recov

    plt.figure()
    sns.violinplot(data=m_0)

    plt.ylim([0, 3e3])
    plt.ylabel('Gross Liftoff Mass $m_0$ [Mg]')
    plt.xticks(rotation=30)
    plt.title('Recovery strategies: launch vehicle mass estimates'
        + '\n{:.1f} Mg payload to GTO, {:s} technology'.format(m_pld, tech.name))
    plt.tight_layout()

    plt.show()


if __name__ == '__main__':
    monte_carlo()