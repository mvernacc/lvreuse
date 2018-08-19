import abc
from collections import namedtuple
import seaborn as sns
import pandas
import numpy as np
from matplotlib import pyplot as plt

import rhodium as rdm
import perf
import payload
from landing_dv import landing_dv
from unavail_mass import unavail_mass


g_0 = 9.81

Technology = namedtuple('Technology', ['fuel', 'cycle', 'uncertainties'])

kero_GG_tech = Technology(
    fuel='kerosene',
    cycle='gas generator',
    uncertainties=[
        rdm.TriangularUncertainty('c_1', min_value=264.6 * g_0, mode_value=287.9 * g_0, max_value=305.4 * g_0),
        rdm.TriangularUncertainty('c_2', min_value=335.2 * g_0, mode_value=345.0 * g_0, max_value=348.0 * g_0),
        rdm.TriangularUncertainty('E_1', min_value=0.055, mode_value=0.060, max_value=0.065),
        rdm.TriangularUncertainty('E_2', min_value=0.040, mode_value=0.050, max_value=0.060),
    ]
    )

Mission = namedtuple('Mission', ['name', 'dv'])

GTO = Mission('GTO', 12e3)

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

    def __init__(self, landing_method, recovery_location, portion_recovered, tech, mission):
        self.landing_method = landing_method
        self.recovery_location = recovery_location
        self.portion_recovered = portion_recovered
        self.tech = tech
        self.uncertainties = []
        self.uncertainties += tech.uncertainties
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


class Expendable(Strategy):

    def __init__(self, tech, mission, y=0.20):
        super(Expendable, self).__init__('N/A', 'N/A', 'none', tech, mission)
        self.y = y
        self.setup_model()

    def evaluate_performance(self, c_1, c_2, E_1, E_2):
        return payload.payload_fixed_stages(c_1, c_2, E_1, E_2, self.y, self.mission.dv)


class PropulsiveLaunchSite(Strategy):

    def __init__(self, tech, mission, y=0.20):
        super(PropulsiveLaunchSite, self).__init__('propulsive', 'launch site', 'all', tech, mission)
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
        return perf.propulsive_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                       dv_entry, landing_m_A, landing_accel, f_ss)[0]


class WingedPoweredLaunchSite(Strategy):
    def __init__(self, tech, mission, y=0.20):
        super(WingedPoweredLaunchSite, self).__init__('winged powered', 'launch site', 'all', tech, mission)
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
        return perf.winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss)[0]


class WingedPoweredLaunchSitePartial(Strategy):
    def __init__(self, tech, mission, y=0.20):
        super(WingedPoweredLaunchSitePartial, self).__init__('winged powered', 'launch site', 'partial',
                                                      tech, mission)
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
        return perf.winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss, z_m)[0]

class PropulsiveDownrange(Strategy):

    def __init__(self, tech, mission, y=0.20):
        super(PropulsiveDownrange, self).__init__('propulsive', 'downrange', 'all',
                                                   tech, mission)
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
        return payload.payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)


def demo():
    strats = [Expendable, PropulsiveLaunchSite,
        WingedPoweredLaunchSite, WingedPoweredLaunchSitePartial,
        PropulsiveDownrange]
    results = {}
    for strat in strats:
        strat_instance = strat(kero_GG_tech, GTO)
        name = strat.__name__
        res = strat_instance.sample_perf_model(nsamples=100)
        res = res.as_dataframe()
        results[name] = res

    pi_star = {}
    for strat_name in results:
        pi_star[strat_name] = results[strat_name]['pi_star']
    pi_star = pandas.DataFrame(pi_star)
    print(pi_star)

    sns.set(style='whitegrid')

    sns.violinplot(data=pi_star)
    plt.show()


if __name__ == '__main__':
    demo()
