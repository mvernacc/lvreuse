import abc
import os.path
from collections import namedtuple

import seaborn as sns
import pandas
import numpy as np
from matplotlib import pyplot as plt
import rhodium as rdm

from lvreuse.performance import payload_fixed_stages
from lvreuse.performance.unavail_mass import unavail_mass
from lvreuse.performance.landing_dv import landing_dv
from lvreuse.performance.launch_site_return import (propulsive_ls_perf,
                                                    winged_powered_ls_perf)
from lvreuse.data import launch_vehicles

g_0 = 9.81

Technology = namedtuple('Technology',
                       ['fuel', 'oxidizer', 'of_mass_ratio',
                       'cycle', 'n_engines', 'stage', 'uncertainties'])

kero_GG_boost_tech = Technology(
    fuel='kerosene',
    oxidizer='O2',
    of_mass_ratio=2.3,
    cycle='gas generator',
    stage='booster',
    n_engines=9,
    uncertainties=[
        rdm.TriangularUncertainty('c_1', min_value=264.6 * g_0, mode_value=287.9 * g_0, max_value=305.4 * g_0),
        rdm.TriangularUncertainty('E_1', min_value=0.055, mode_value=0.060, max_value=0.065),
    ]
    )

kero_GG_upper_tech = Technology(
    fuel='kerosene',
    oxidizer='O2',
    of_mass_ratio=2.3,
    cycle='gas generator',
    stage='upper',
    n_engines=1,
    uncertainties=[
        rdm.TriangularUncertainty('c_2', min_value=335.2 * g_0, mode_value=345.0 * g_0, max_value=348.0 * g_0),
        rdm.TriangularUncertainty('E_2', min_value=0.040, mode_value=0.050, max_value=0.060),
    ]
    )

H2_SC_boost_tech = Technology(
    fuel='H2',
    oxidizer='O2',
    of_mass_ratio=6.0,
    cycle='staged combustion',
    stage='booster',
    n_engines=9,
    uncertainties=[
        rdm.TriangularUncertainty('c_1', min_value=369.5 * g_0, mode_value=398.1 * g_0, max_value=418.7 * g_0),
        rdm.TriangularUncertainty('E_1', min_value=0.11, mode_value=0.12, max_value=0.13),
    ]
    )

H2_SC_upper_tech = Technology(
    fuel='H2',
    oxidizer='O2',
    of_mass_ratio=6.0,
    cycle='staged combustion',
    stage='upper',
    n_engines=1,
    uncertainties=[
        rdm.TriangularUncertainty('c_2', min_value=444.9 * g_0, mode_value=458.0 * g_0, max_value=462.0 * g_0),
        rdm.TriangularUncertainty('E_2', min_value=0.080, mode_value=0.085, max_value=0.090),
    ]
    )

"""Defines a launch mission: taking a payload to an orbit.

Attributes:
    name (str): Orbit name.
    dv (scalar): Delta-v (incl losses) required to reach the target orbit
        [units: meter second**-1].
    m_payload (scalar): Payload mass [units: kilogram].
"""
Mission = namedtuple('Mission', ['name', 'dv', 'm_payload'])

LEO = Mission('LEO', 9.5e3, 10e3)
GTO = Mission('GTO', 12e3, 5e3)

# Common uncertainties
# Downrange distance at stage separation - model coefficient [units: meter**-1 second**2].
f_ss_uncert = rdm.TriangularUncertainty('f_ss', min_value=0.01, mode_value=0.02, max_value=0.03)
# Entry burn delta-v for propulsive recovery [units: meter second**-1].
dv_entry_uncert = rdm.TriangularUncertainty('dv_entry', min_value=0, mode_value=800, max_value=1000)
# Mass / area ratio for landing burn [units: kilogram meter**-2].
landing_m_A_large_uncert = rdm.TriangularUncertainty('landing_m_A', min_value=1500, mode_value=2000, max_value=2500)
# Landing burn acceleration for propulsive landing [units: meter second**-2].
landing_accel_uncert = rdm.TriangularUncertainty('landing_accel', min_value=20, mode_value=30, max_value=40)
# Air breathing propulsion specific impulse [units: second].
I_sp_ab_uncert = rdm.TriangularUncertainty('I_sp_ab', min_value=3200, mode_value=3600, max_value=4000)
# Recovery cruise speed [units: meter second*-1].
v_cruise_uncert = rdm.TriangularUncertainty('v_cruise', min_value=100, mode_value=200, max_value=300)
# Winged recovery vehicle L/D [units: dimensionless]
lift_drag_uncert = rdm.TriangularUncertainty('lift_drag', min_value=4, mode_value=6, max_value=8)
# Engine pod mass / booster inert mass $z_m$ for partial recovery strategies [units: dimensionless].
z_m_uncert = rdm.UniformUncertainty('z_m', min_value=0.15, mode_value=0.25, max_value=0.35)

class Strategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, landing_method, recovery_location, portion_recovered, tech_1, tech_2, mission):
        self.landing_method = landing_method
        self.recovery_location = recovery_location
        self.portion_recovered = portion_recovered
        self.tech_1 = tech_1
        self.tech_2 = tech_2
        self.uncertainties = []
        self.uncertainties += tech_1.uncertainties
        self.uncertainties += tech_2.uncertainties
        self.perf_model = rdm.Model(self.evaluate_performance)
        self.mission = mission

    def setup_model(self):
        """Setup the rhodium Monte Carlo model.

        Subclasses should call this method after filling in `self.uncertainties`.
        """
        self.perf_model.parameters = [rdm.Parameter(u.name) for u in self.uncertainties]
        self.perf_model.uncertainties = self.uncertainties
        self.perf_model.responses = [
            rdm.Response('pi_star', rdm.Response.MAXIMIZE),
        ]

    def sample_perf_model(self, nsamples=1000):
        """Draw samples from the performance model"""
        scenarios = rdm.sample_lhs(self.perf_model, nsamples)
        results = rdm.evaluate(self.perf_model, scenarios)
        return results

    @abc.abstractmethod
    def evaluate_performance(self):
        pass


class StrategyNoPropulsion(Strategy):
    __metaclass__ = abc.ABCMeta

    def __init__(self, landing_method, recovery_location, portion_recovered, 
                 tech_1, tech_2, mission):
        super(StrategyNoPropulsion, self).__init__(landing_method, recovery_location,
                                                   portion_recovered, tech_1, tech_2, mission)

    def evaluate_performance(self, c_1, c_2, E_1, E_2, a, z_m=1):
        e_1 = unavail_mass(a, P=0, z_m=z_m, E_1=E_1)
        return payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)



class Expendable(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(Expendable, self).__init__('expendable', 'N/A', 'none', tech_1, tech_2, mission)
        self.y = y
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2):
        return payload_fixed_stages(c_1, c_2, E_1, E_2, self.y, self.mission.dv)


class PropulsiveLaunchSite(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(PropulsiveLaunchSite, self).__init__('propulsive', 'launch site', 'full',
                                                   tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            f_ss_uncert,
            dv_entry_uncert,
            landing_m_A_large_uncert,
            landing_accel_uncert,
        ]
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2, a,
                       dv_entry, landing_m_A, landing_accel, f_ss):
        results = propulsive_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                       dv_entry, landing_m_A, landing_accel, f_ss)
        return results.pi_star


class WingedPoweredLaunchSite(Strategy):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedPoweredLaunchSite, self).__init__('winged powered', 'launch site', 'full',
                                                      tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            f_ss_uncert,
            I_sp_ab_uncert,
            v_cruise_uncert,
            lift_drag_uncert,
        ]
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2, a,
                       I_sp_ab, v_cruise, lift_drag, f_ss):
        results = winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss)
        return results.pi_star


class WingedPoweredLaunchSitePartial(Strategy):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedPoweredLaunchSitePartial, self).__init__('winged powered', 'launch site', 'partial',
                                                      tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            f_ss_uncert,
            I_sp_ab_uncert,
            v_cruise_uncert,
            lift_drag_uncert,
            z_m_uncert,
        ]
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2, a,
                       I_sp_ab, v_cruise, lift_drag, f_ss, z_m):
        results = winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss, z_m)
        return results.pi_star


class PropulsiveDownrange(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(PropulsiveDownrange, self).__init__('propulsive', 'downrange', 'full',
                                                   tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            dv_entry_uncert,
            landing_m_A_large_uncert,
            landing_accel_uncert,
        ]
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2, a,
                       dv_entry, landing_m_A, landing_accel):
        dv_land = landing_dv(m_A=landing_m_A, accel=landing_accel)
        P = (dv_entry + dv_land) / c_1
        propellant_margin = 0.10
        P *= 1 + propellant_margin
        e_1 = unavail_mass(a, P, z_m=1, E_1=E_1)
        return payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)


class WingedGlider(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedGlider, self).__init__('winged glider', 'downrange', 'full',
                                           tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.380, mode_value=0.426, max_value=0.540),
        ]
        self.setup_model()


class Parachute(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(Parachute, self).__init__('parachute', 'downrange', 'full',
                                        tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.15, mode_value=0.17, max_value=0.19),
        ]
        self.setup_model()


class ParachutePartial(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(ParachutePartial, self).__init__('parachute', 'downrange', 'partial',
                                               tech_1, tech_2, mission)
        self.y = y
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.15, mode_value=0.17, max_value=0.19),
            z_m_uncert,
        ]
        self.setup_model()


def demo():
    strats = [Expendable, PropulsiveLaunchSite,
                WingedPoweredLaunchSite, WingedPoweredLaunchSitePartial,
                PropulsiveDownrange, WingedGlider, Parachute, ParachutePartial]

    for tech_1, tech_2 in zip([kero_GG_boost_tech, H2_SC_boost_tech],
                              [kero_GG_upper_tech, H2_SC_upper_tech]):
        for mission in [LEO, GTO]:
            plt.figure(figsize=(10, 6))
            
            results = {}
            xticks = []
            for strat in strats:
                strat_instance = strat(tech_1, tech_2, mission)
                name = strat.__name__
                res = strat_instance.sample_perf_model(nsamples=100)
                res = res.as_dataframe()
                results[name] = res
                xticks.append('{:s}\n{:s}'.format(strat_instance.landing_method,
                                                  strat_instance.portion_recovered))

            pi_star = {}
            for strat_name in results:
                pi_star[strat_name] = results[strat_name]['pi_star']
            pi_star = pandas.DataFrame(pi_star)

            sns.set(style='whitegrid')

            ax = sns.violinplot(data=pi_star)
            plt.ylabel('Overall payload mass fraction $\\pi_*$ [-]')
            plt.title('Payload performance distributions for {:s} mission'.format(mission.name)
                + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))
            plt.ylim([0, plt.ylim()[1]])

            ax.set_xticklabels(xticks)
            plt.xticks(rotation=30)

            plt.axvline(x=0.5, color='grey')
            plt.text(x=1, y=0.0, s='Launch site recovery')
            plt.axvline(x=3.5, color='grey')
            plt.text(x=4, y=0.0, s='Downrange recovery')

            if (tech_1.fuel == 'kerosene' and tech_1.cycle == 'gas generator'
                and tech_2.fuel == 'kerosene' and tech_2.cycle == 'gas generator'):
                # Plot Falcon 9 data for comparison
                pi_star = launch_vehicles.f9_b3_e.payload_actual(mission.name)
                plt.scatter(0, pi_star, marker='+', color='red', zorder=10)
                plt.text(0.1, pi_star, 'Falcon 9', color='red', zorder=10)

                if mission.name == 'GTO':
                    pi_star = launch_vehicles.f9_b3_e.payload_actual(mission.name, recov='DR')
                    plt.scatter(4, pi_star, marker='+', color='red', zorder=10)
                    plt.text(4.1, pi_star, 'Falcon 9', color='red', zorder=10)

                if mission.name == 'LEO':
                    pi_star = launch_vehicles.f9_b3_e.payload_actual(mission.name, recov='LS')
                    plt.scatter(1, pi_star, marker='+', color='red', zorder=10)
                    plt.text(1.1, pi_star, 'Falcon 9', color='red', zorder=10)

            plt.tight_layout()
            plt.savefig(os.path.join('plots', 'strategy_perf_{:s}_{:s}.png'.format(
                mission.name, tech_1.fuel)))
    plt.show()


if __name__ == '__main__':
    demo()
