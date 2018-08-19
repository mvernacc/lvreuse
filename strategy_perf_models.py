import abc
from collections import namedtuple
import seaborn as sns
import pandas
import numpy as np
from matplotlib import pyplot as plt

import rhodium as rdm
import perf


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


class Strategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, landing_method, recovery_location, tech, mission):
        self.landing_method = landing_method
        self.recovery_location = recovery_location
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
            rdm.Response('pld_frac_recov', rdm.Response.MAXIMIZE),
        ]

    def sample_perf_model(self, nsamples=1000):
        """Draw samples from the performance model"""
        scenarios = rdm.sample_lhs(self.perf_model, nsamples)
        results = rdm.evaluate(self.perf_model, scenarios)
        return results

    @abc.abstractmethod
    def evaluate_performance():
        pass


class PropulsiveLaunchSite(Strategy):

    def __init__(self, tech, mission):
        super(PropulsiveLaunchSite, self).__init__('propulsive', 'launch site', tech, mission)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
        ]
        self.setup_model()


    def evaluate_performance(self, c_1, c_2, E_1, E_2, y=0.2, a=0):
        return perf.propulsive_ls_perf(c_1, c_2, E_1, E_2, y, self.mission.dv, a)[0]


def demo():
    prop_ls = PropulsiveLaunchSite(kero_GG_tech, GTO)
    res = prop_ls.sample_perf_model(nsamples=100)
    res = res.as_dataframe()
    print(res)

    sns.set(style='whitegrid')

    sns.violinplot(data=res, y='pld_frac_recov')
    plt.show()


if __name__ == '__main__':
    demo()
