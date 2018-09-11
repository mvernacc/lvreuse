import abc
import os.path
from collections import namedtuple

import seaborn as sns
import pandas
import numpy as np
from matplotlib import pyplot as plt
import rhodium as rdm

from lvreuse.performance import payload_fixed_stages
from lvreuse.performance.unavail_mass import unavail_mass, inert_masses
from lvreuse.performance.landing_dv import landing_dv
from lvreuse.performance.launch_site_return import (propulsive_ls_perf,
                                                    winged_powered_ls_perf)
from lvreuse.data import launch_vehicles
from lvreuse.performance import masses
from lvreuse.constants import g_0
import lvreuse.cost as cost
from lvreuse.analysis.cost import strategy_cost_models
from lvreuse.analysis.combined.construct_launch_vehicle import construct_launch_vehicle

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
GTO = Mission('GTO', 12e3, 10e3)

# Common uncertainties - performance
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

# Common uncertainties - cost
prod_cost_uncerts = [
    # Learning factors for serial production/operations.
    rdm.TriangularUncertainty('p_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
    # System management factor for vehicle production
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    # Subcontractor cost factor - these values assume only 20% of the project is subcontracted
    rdm.TriangularUncertainty('f9_veh', min_value=1.01, mode_value=1.02, max_value=1.03),
    # cost reduction factor by past experience, technical progress and application of cost engineering
    rdm.TriangularUncertainty('f10_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
    # cost reduction factor by independent development without government contracts' requirements and customer interference
    rdm.TriangularUncertainty('f11_s1', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_e1', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_s2', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_e2', min_value=0.45, mode_value=0.5, max_value=0.55),
]
ops_cost_uncerts = [
    rdm.TriangularUncertainty('launch_rate', min_value=10, mode_value=15, max_value=20),
    rdm.TriangularUncertainty('p_ops', min_value=0.8, mode_value=0.85, max_value=0.9),
    rdm.TriangularUncertainty('insurance', min_value=1, mode_value=2, max_value=3),
    # cost reduction factor by independent development without government contracts' requirements and customer interference
    rdm.TriangularUncertainty('f11_ops', min_value=0.45, mode_value=0.5, max_value=0.55),
]
dev_cost_uncerts = [
    # systems engineering/integration factor for vehicle development
    rdm.TriangularUncertainty('f0_dev_veh', min_value=1.03**2, mode_value=1.04**2, max_value=1.05**2),
    rdm.TriangularUncertainty('num_program_flights', min_value=100, mode_value=120, max_value=150),
    # Development standard factors for 2nd stage -  assumes 2nd stage is a variant of an existing system
    rdm.TriangularUncertainty('f1_s2', min_value=0.3, mode_value=0.4, max_value=0.5),
    rdm.TriangularUncertainty('f1_e2', min_value=0.3, mode_value=0.4, max_value=0.5),
]
vehicle_prod_nums_list = list(range(20, 60))
vehicle_launch_nums_list = vehicle_prod_nums_list
# country productivity correction factor as defined by TRANSCOST 8.2 p. 25
f8_dict = {'s1': 1.0, 'e1': 1.0, 's2': 1.0, 'e2': 1.0, 'veh': 1.0, 'ops': 1.0, 'ab': 1.0, 'd1': 1.0}
# Assembly and integration cost factor, assuming horizontal assembly and checkout, transport to pad, erection.
fc = 0.7
# Launch provider type (see Transcost 8.2 pg 173).
# Type C assumes the launch service provider and the launch vehicle
# manufacturer are the same company, and that only a small portion of the
# work is subcontracted.
launch_provider_type = 'C'
reuse_cost_uncerts = [
    # Reusable vehicle lifetime
    # rdm.TriangularUncertainty('num_reuses', min_value=5, mode_value=10, max_value=25),
    rdm.TriangularUncertainty('num_reuses_e1', min_value=5, mode_value=10, max_value=25),
    rdm.TriangularUncertainty('num_reuses_s1', min_value=5, mode_value=10, max_value=25),
    # Refurbishment cost factors
    rdm.TriangularUncertainty('f5_e1', min_value=0.5e-2, mode_value=1e-2, max_value=3e-2),
    rdm.TriangularUncertainty('f5_s1', min_value=0.008e-2, mode_value=1e-2, max_value=2.3e-2),
]
reuse_cost_ab_uncerts = [
    rdm.TriangularUncertainty('num_reuses_ab', min_value=100, mode_value=700, max_value=1000),
    rdm.TriangularUncertainty('f5_ab', min_value=0.001e-2, mode_value=0.1e-2, max_value=0.5e-2),
]
# Learning factor for disposed stage 1 tank (partial reuse strats)
p_d1 = rdm.TriangularUncertainty('p_d1', min_value=0.75, mode_value=0.8, max_value=0.85)
# Recovery cost [WYr] for launch site recovery
recov_cost_launch_site = rdm.TriangularUncertainty('recovery_cost', min_value=0.5, mode_value=0.7, max_value=1.0)
# Recovery cost [WYr] for downrange recovery
recov_cost_downrange = rdm.TriangularUncertainty('recovery_cost', min_value=1, mode_value=1.5, max_value=2)

class Strategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, landing_method, recovery_prop_method, recovery_location, portion_recovered,
                 tech_1, tech_2, mission, y):
        self.landing_method = landing_method
        self.recovery_prop_method = recovery_prop_method
        self.recovery_location = recovery_location
        self.portion_recovered = portion_recovered
        self.tech_1 = tech_1
        self.tech_2 = tech_2
        self.uncertainties = []
        self.uncertainties += tech_1.uncertainties
        self.uncertainties += tech_2.uncertainties
        self.model = rdm.Model(self.evaluate)
        self.mission = mission
        self.y = y

        if recovery_location == 'launch site':
            self.uncertainties += [recov_cost_launch_site]
        elif recovery_location == 'downrange':
            self.uncertainties += [recov_cost_downrange]
        elif recovery_location == 'N/A':
            pass
        else:
            raise ValueError('Invalid recovery recovery_location "{:s}"'.format(
                recovery_location))

        # Construct LaunchVehicle Object for cost modeling
        if landing_method == 'winged':
            stage_type = 'winged'
        else:
            stage_type = 'ballistic'
        self.launch_vehicle = construct_launch_vehicle(
            stage_type,
            prop_choice=tech_1.fuel,
            portion_reused=portion_recovered,
            ab_rec=(recovery_prop_method == 'air-breathing'),
            num_rocket_engines=tech_1.n_engines
            )
        # Cost model (defined in subclasses)
        self.cost_model = None

    def setup_model(self):
        """Setup the rhodium Monte Carlo model.

        Subclasses should call this method after filling in `self.uncertainties`.
        """
        self.model.parameters = [rdm.Parameter(u.name) for u in self.uncertainties]
        self.model.uncertainties = self.uncertainties
        self.model.responses = [
            rdm.Response('pi_star', rdm.Response.MAXIMIZE),
            rdm.Response('e_1', rdm.Response.MAXIMIZE),
            rdm.Response('prod_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('ops_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('dev_cost', rdm.Response.MAXIMIZE),
            rdm.Response('price_per_flight', rdm.Response.MAXIMIZE),
        ]

    def sample_model(self, nsamples=1000):
        """Draw samples from the performance model"""
        scenarios = rdm.sample_lhs(self.model, nsamples)
        results = rdm.evaluate(self.model, scenarios)
        return results

    @abc.abstractmethod
    def evaluate(self):
        pass

    def get_z_m_engine_pod(self, E_1):
        """Estimate the mass of an engines-only recovery pod, relative to
            the baseline mass of the first stage.

        Returns:
            scalar: z_m = (engines-only recovery pod mass)
                / (stage 1 baseline inert mass) [units: dimensionless].
        """
        # Engine mass (per engine), as a fraction of gross liftoff mass
        m_eng = masses.booster_engine_mass(1, n_engines=self.tech_1.n_engines,
                                             propellant=self.tech_1.fuel + '/' + self.tech_1.oxidizer)
        # First stage baseline inert mass, as a fraction of gross liftoff mass
        # (approx)
        m_inert_1 = (1 - self.y - 0.02) * E_1

        # Engine mass (total), as a fraction of first stage baseline inert mass
        z_m = (m_eng * self.tech_1.n_engines) / m_inert_1

        # Add a few percent to z_m to account for thrust structure, etc
        z_m += 0.05

        return z_m

    def get_masses(self, pi_star, a, E_1, E_2):
        # Gross liftoff mass [units: kilogram].
        m_0 = self.mission.m_payload / pi_star
        # Stage 1 wet mass [units: kilogram].
        m_1 = 1 / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 2 wet mass [units: kilogram].
        m_2 = self.y / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage inert masses [units: kilogram].
        m_inert_1 = inert_masses(m_1, a, z_m=1, E_1=E_1)[0]
        m_inert_2 = E_2 * m_2
        # Stage engine masses [units: kilogram].
        m_eng_1 = masses.booster_engine_mass(m_0, n_engines=self.tech_1.n_engines,
                                             propellant=self.tech_1.fuel + '/' + self.tech_1.oxidizer)
        m_eng_2 = masses.upper_engine_mass(m_2 + self.mission.m_payload,
                                           n_engines=self.tech_2.n_engines,
                                           propellant=self.tech_2.fuel + '/' + self.tech_2.oxidizer)

        # Stage propellant masses [units: kilogram].
        m_p_1 = m_1 - m_inert_1
        m_fuel_1 = 1 / (1 + self.tech_1.of_mass_ratio) * m_p_1
        m_oxidizer_1 = m_p_1 - m_fuel_1
        m_p_2 = m_2 - m_inert_2
        m_fuel_2 = 1 / (1 + self.tech_2.of_mass_ratio) * m_p_2
        m_oxidizer_2 = m_p_2 - m_fuel_2

        mass_dict = {
            'm0': m_0,
            's1': m_inert_1 - (m_eng_1 * self.tech_1.n_engines),
            's2': m_inert_2 - (m_eng_2 * self.tech_2.n_engines),
            'e1': m_eng_1,
            'e2': m_eng_2,
        }

        if self.tech_1.fuel == self.tech_2.fuel:
            mass_dict[self.tech_1.fuel] = m_fuel_1 + m_fuel_2
        else:
            mass_dict[self.tech_1.fuel] = m_fuel_1
            mass_dict[self.tech_2.fuel] = m_fuel_2
        if self.tech_1.oxidizer == self.tech_2.oxidizer:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1 + m_oxidizer_2
        else:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1
            mass_dict[self.tech_2.oxidizer] = m_oxidizer_2

        for key in mass_dict:
            assert mass_dict[key] > 0

        return mass_dict


class StrategyNoPropulsion(Strategy):
    __metaclass__ = abc.ABCMeta

    def __init__(self, landing_method, recovery_prop_method, recovery_location, portion_recovered, 
                 tech_1, tech_2, mission, y):
        assert recovery_prop_method == 'none'
        super(StrategyNoPropulsion, self).__init__(landing_method, recovery_prop_method, recovery_location,
                                                   portion_recovered, tech_1, tech_2, mission, y)

    def evaluate(self, c_1, c_2, E_1, E_2, a, **kwargs):
        e_1 = unavail_mass(a, P=0, z_m=1, E_1=E_1)
        pi_star = payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)
        element_masses = self.get_masses(pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (pi_star, e_1, *cost_results)


class Expendable(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(Expendable, self).__init__('expendable', 'N/A', 'N/A', 'none',
                                         tech_1, tech_2, mission, y)
        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For expendable, assume this is a standard project w state-of-the-art technology.
            rdm.TriangularUncertainty('f1_s1', min_value=0.9, mode_value=1.0, max_value=1.1),
            rdm.TriangularUncertainty('f1_e1', min_value=0.9, mode_value=1.0, max_value=1.1),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEngine(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=2 * 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, **kwargs):
        pi_star = payload_fixed_stages(c_1, c_2, E_1, E_2, self.y, self.mission.dv)
        element_masses = self.get_masses(pi_star, a=0, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (pi_star, E_1, *cost_results)


class PropulsiveLaunchSite(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(PropulsiveLaunchSite, self).__init__('propulsive', 'rocket', 'launch site', 'full',
                                                   tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            f_ss_uncert,
            dv_entry_uncert,
            landing_m_A_large_uncert,
            landing_accel_uncert,
        ]

        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For propulsive landing, rocket return to launch site, assume this is "new technical and/or operational features".
            rdm.TriangularUncertainty('f1_s1', min_value=1.1, mode_value=1.15, max_value=1.2),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEngine(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, a,
                       dv_entry, landing_m_A, landing_accel, f_ss, **kwargs):
        results = propulsive_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                       dv_entry, landing_m_A, landing_accel, f_ss)
        element_masses = self.get_masses(results.pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (results.pi_star, results.e_1, *cost_results)


class WingedPoweredLaunchSite(Strategy):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedPoweredLaunchSite, self).__init__('winged', 'air-breathing', 'launch site', 'full',
                                                      tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            f_ss_uncert,
            I_sp_ab_uncert,
            v_cruise_uncert,
            lift_drag_uncert,
        ]
        self.n_ab_engines = 4    #  Number of air breathing engines for recovery.
        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For winged landing, air-breathing return to launch site, assume this is "new concept
            # approach, involving new techniques and new technologies" for the stage, and
            # "new technical and/or operational features" for the engines.
            rdm.TriangularUncertainty('f1_s1', min_value=1.3, mode_value=1.35, max_value=1.4),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEnginePlusAirbreathing(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines, 'ab': self.n_ab_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,
            sum_QN=1.0 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.uncertainties += reuse_cost_ab_uncerts
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, a,
                       I_sp_ab, v_cruise, lift_drag, f_ss, **kwargs):
        results = winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss)
        element_masses = self.get_masses(results.pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (results.pi_star, results.e_1, *cost_results)

    def get_masses(self, pi_star, a, E_1, E_2):
        # Gross liftoff mass [units: kilogram].
        m_0 = self.mission.m_payload / pi_star
        # Stage 1 wet mass [units: kilogram].
        m_1 = 1 / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 2 wet mass [units: kilogram].
        m_2 = self.y / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage inert masses [units: kilogram].
        m_inert_1 = inert_masses(m_1, a, z_m=1, E_1=E_1)[0]
        m_inert_2 = E_2 * m_2
        # Stage rocket engine masses [units: kilogram].
        m_eng_1 = masses.booster_engine_mass(m_0, n_engines=self.tech_1.n_engines,
                                             propellant=self.tech_1.fuel + '/' + self.tech_1.oxidizer)
        m_eng_2 = masses.upper_engine_mass(m_2 + self.mission.m_payload,
                                           n_engines=self.tech_2.n_engines,
                                           propellant=self.tech_2.fuel + '/' + self.tech_2.oxidizer)
        # Stage 1 air-breathing engine mass [units: kilogram].
        # Model: air-breathing engines typically make up 10% of the mass of
        # winged, powered vehicles.
        m_ab_engine = m_inert_1 * 0.10 / self.n_ab_engines
        # Stage propellant masses [units: kilogram].
        m_p_1 = m_1 - m_inert_1
        m_fuel_1 = 1 / (1 + self.tech_1.of_mass_ratio) * m_p_1
        m_oxidizer_1 = m_p_1 - m_fuel_1
        m_p_2 = m_2 - m_inert_2
        m_fuel_2 = 1 / (1 + self.tech_2.of_mass_ratio) * m_p_2
        m_oxidizer_2 = m_p_2 - m_fuel_2

        mass_dict = {
            'm0': m_0,
            's1': m_inert_1 - (m_eng_1 * self.tech_1.n_engines) \
                - (m_ab_engine * self.n_ab_engines),
            's2': m_inert_2 - (m_eng_2 * self.tech_2.n_engines),
            'e1': m_eng_1,
            'e2': m_eng_2,
            'ab': m_ab_engine
        }

        if self.tech_1.fuel == self.tech_2.fuel:
            mass_dict[self.tech_1.fuel] = m_fuel_1 + m_fuel_2
        else:
            mass_dict[self.tech_1.fuel] = m_fuel_1
            mass_dict[self.tech_2.fuel] = m_fuel_2
        if self.tech_1.oxidizer == self.tech_2.oxidizer:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1 + m_oxidizer_2
        else:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1
            mass_dict[self.tech_2.oxidizer] = m_oxidizer_2

        for key in mass_dict:
            assert mass_dict[key] > 0

        return mass_dict


class WingedPoweredLaunchSitePartial(Strategy):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedPoweredLaunchSitePartial, self).__init__('winged', 'air-breathing', 'launch site', 'partial',
                                                      tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.490, mode_value=0.574, max_value=0.650),
            f_ss_uncert,
            I_sp_ab_uncert,
            v_cruise_uncert,
            lift_drag_uncert,
        ]
        self.n_ab_engines = 2    #  Number of air breathing engines for recovery.

        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For winged landing, air-breathing return to launch site, assume this is "new concept
            # approach, involving new techniques and new technologies" for the stage, and
            # "new technical and/or operational features" for the engines.
            rdm.TriangularUncertainty('f1_s1', min_value=1.3, mode_value=1.35, max_value=1.4),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStagePartialPlusAirbreathing(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines, 'ab': self.n_ab_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts + [p_d1],
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.uncertainties += reuse_cost_ab_uncerts
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, a,
                       I_sp_ab, v_cruise, lift_drag, f_ss, **kwargs):
        z_m = self.get_z_m_engine_pod(E_1)
        results = winged_powered_ls_perf(c_1, c_2, E_1, E_2, self.y, self.mission.dv, a,
                                           I_sp_ab, v_cruise, lift_drag, f_ss, z_m)
        element_masses = self.get_masses(results.pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (results.pi_star, results.e_1, *cost_results)

    def get_masses(self, pi_star, a, E_1, E_2):
        z_m = self.get_z_m_engine_pod(E_1)
        # Gross liftoff mass [units: kilogram].
        m_0 = self.mission.m_payload / pi_star
        # Stage 1 wet mass [units: kilogram].
        m_1 = 1 / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 2 wet mass [units: kilogram].
        m_2 = self.y / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 1 inert mass [units: kilogram].
        # and Stage 1 recovered inert mass (e.g. winged engine pod) [units: kilogram]
        m_inert_1, m_inert_recov_1 = inert_masses(m_1, a, z_m, E_1)
        # Stage 1 disposed inert mass [units: kilogram].
        # e.g. tanks
        m_dispose_1 = m_inert_1 - m_inert_recov_1
        # Stage 2 inert mass [units: kilogram].
        m_inert_2 = E_2 * m_2
        # Stage rocket engine masses [units: kilogram].
        m_eng_1 = masses.booster_engine_mass(m_0, n_engines=self.tech_1.n_engines,
                                             propellant=self.tech_1.fuel + '/' + self.tech_1.oxidizer)
        m_eng_2 = masses.upper_engine_mass(m_2 + self.mission.m_payload,
                                           n_engines=self.tech_2.n_engines,
                                           propellant=self.tech_2.fuel + '/' + self.tech_2.oxidizer)
        # Stage 1 air-breathing engine mass [units: kilogram].
        # Model: air-breathing engines typically make up 15-20% of the mass of
        # winged, powered vehicles. 
        m_ab_engine = m_inert_recov_1 * 0.17 / self.n_ab_engines
        # Stage propellant masses [units: kilogram].
        m_p_1 = m_1 - m_inert_1
        m_fuel_1 = 1 / (1 + self.tech_1.of_mass_ratio) * m_p_1
        m_oxidizer_1 = m_p_1 - m_fuel_1
        m_p_2 = m_2 - m_inert_2
        m_fuel_2 = 1 / (1 + self.tech_2.of_mass_ratio) * m_p_2
        m_oxidizer_2 = m_p_2 - m_fuel_2

        mass_dict = {
            'm0': m_0,
            's1': m_inert_recov_1 - (m_eng_1 * self.tech_1.n_engines) \
                - (m_ab_engine * self.n_ab_engines),
            's2': m_inert_2 - (m_eng_2 * self.tech_2.n_engines),
            'e1': m_eng_1,
            'e2': m_eng_2,
            'ab': m_ab_engine,
            'd1': m_dispose_1,
        }

        if self.tech_1.fuel == self.tech_2.fuel:
            mass_dict[self.tech_1.fuel] = m_fuel_1 + m_fuel_2
        else:
            mass_dict[self.tech_1.fuel] = m_fuel_1
            mass_dict[self.tech_2.fuel] = m_fuel_2
        if self.tech_1.oxidizer == self.tech_2.oxidizer:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1 + m_oxidizer_2
        else:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1
            mass_dict[self.tech_2.oxidizer] = m_oxidizer_2

        for key in mass_dict:
            assert mass_dict[key] > 0

        return mass_dict


class PropulsiveDownrange(Strategy):

    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(PropulsiveDownrange, self).__init__('propulsive', 'rocket', 'downrange', 'full',
                                                   tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.09, mode_value=0.14, max_value=0.19),
            dv_entry_uncert,
            landing_m_A_large_uncert,
            landing_accel_uncert,
        ]

        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For propulsive landing, rocket to downrange, assume this is "new technical and/or operational features".
            rdm.TriangularUncertainty('f1_s1', min_value=1.1, mode_value=1.15, max_value=1.2),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEngine(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, a,
                       dv_entry, landing_m_A, landing_accel, **kwargs):
        dv_land = landing_dv(m_A=landing_m_A, accel=landing_accel)
        P = (dv_entry + dv_land) / c_1
        propellant_margin = 0.10
        P *= 1 + propellant_margin
        e_1 = unavail_mass(a, P, z_m=1, E_1=E_1)
        pi_star = payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)
        element_masses = self.get_masses(pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (pi_star, e_1, *cost_results)


class WingedGlider(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(WingedGlider, self).__init__('winged', 'none', 'downrange', 'full',
                                           tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.380, mode_value=0.426, max_value=0.540),
        ]
        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For winged landing, glide to downrange, assume this is "new technical and/or operational features".
            rdm.TriangularUncertainty('f1_s1', min_value=1.1, mode_value=1.15, max_value=1.2),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEngine(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.setup_model()


class Parachute(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(Parachute, self).__init__('parachute', 'none', 'downrange', 'full',
                                        tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.15, mode_value=0.17, max_value=0.19),
        ]

        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For parachute landing, glide to downrange, assume this is "state-of-the-art"
            # for the stage and "new technical and/or operational features".
            rdm.TriangularUncertainty('f1_s1', min_value=0.9, mode_value=1.0, max_value=1.1),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEngine(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts,
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.setup_model()


class ParachutePartial(StrategyNoPropulsion):
    def __init__(self, tech_1, tech_2, mission, y=0.20):
        super(ParachutePartial, self).__init__('parachute', 'none', 'downrange', 'partial',
                                               tech_1, tech_2, mission, y)
        self.uncertainties += [
            rdm.TriangularUncertainty('a', min_value=0.15, mode_value=0.17, max_value=0.19),
        ]
        # Cost model stuff
        # Create propellant dictionary needed by cost model
        propellants = set([tech_1.fuel, tech_1.oxidizer, tech_2.fuel, tech_2.oxidizer])
        vehicle_props_dict = {}
        for name in propellants:
            vehicle_props_dict[name] = 0

        dev_cost_stage_1_uncerts = [
            # Development standard factors for first stage.
            # For parachute landing, glide to downrange, assume this is "state-of-the-art"
            # for the stage and "new technical and/or operational features".
            rdm.TriangularUncertainty('f1_s1', min_value=0.9, mode_value=1.0, max_value=1.1),
            rdm.TriangularUncertainty('f1_e1', min_value=1.1, mode_value=1.15, max_value=1.2),
        ]

        self.cost_model = strategy_cost_models.TwoLiquidStageTwoEnginePartial(
            launch_vehicle=self.launch_vehicle,
            vehicle_prod_nums_list=vehicle_prod_nums_list,
            vehicle_launch_nums_list=vehicle_launch_nums_list,
            num_engines_dict={'e1': tech_1.n_engines, 'e2': tech_2.n_engines},
            f8_dict=f8_dict,
            fv=(1.0 if tech_1.fuel == 'H2' else 0.8),
            fc=fc,  
            sum_QN=1.0 + 0.4 + 0.4,
            launch_provider_type=launch_provider_type,
            vehicle_props_dict=vehicle_props_dict,
            prod_cost_facs_unc_list=prod_cost_uncerts + [p_d1],
            ops_cost_unc_list=ops_cost_uncerts,
            dev_cost_unc_list=dev_cost_uncerts + dev_cost_stage_1_uncerts,
            )
        self.uncertainties += self.cost_model.uncertainties
        self.uncertainties += reuse_cost_uncerts
        self.setup_model()

    def evaluate(self, c_1, c_2, E_1, E_2, a, **kwargs):
        z_m = self.get_z_m_engine_pod(E_1)
        e_1 = unavail_mass(a, P=0, z_m=z_m, E_1=E_1)
        pi_star = payload_fixed_stages(c_1, c_2, e_1, E_2, self.y, self.mission.dv)
        element_masses = self.get_masses(pi_star, a=a, E_1=E_1, E_2=E_2)
        self.cost_model.update_masses(element_masses)
        cost_results = self.cost_model.evaluate_cost(**kwargs)
        return (pi_star, e_1, *cost_results)

    def get_masses(self, pi_star, a, E_1, E_2):
        z_m = self.get_z_m_engine_pod(E_1)
        # Gross liftoff mass [units: kilogram].
        m_0 = self.mission.m_payload / pi_star
        # Stage 1 wet mass [units: kilogram].
        m_1 = 1 / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 2 wet mass [units: kilogram].
        m_2 = self.y / (1 + self.y) * (m_0 - self.mission.m_payload)
        # Stage 1 inert mass [units: kilogram].
        # and Stage 1 recovered inert mass (e.g. winged engine pod) [units: kilogram]
        m_inert_1, m_inert_recov_1 = inert_masses(m_1, a, z_m, E_1)
        # Stage 1 disposed inert mass [units: kilogram].
        # e.g. tanks
        m_dispose_1 = m_inert_1 - m_inert_recov_1
        # Stage 2 inert mass [units: kilogram].
        m_inert_2 = E_2 * m_2
        # Stage rocket engine masses [units: kilogram].
        m_eng_1 = masses.booster_engine_mass(m_0, n_engines=self.tech_1.n_engines,
                                             propellant=self.tech_1.fuel + '/' + self.tech_1.oxidizer)
        m_eng_2 = masses.upper_engine_mass(m_2 + self.mission.m_payload,
                                           n_engines=self.tech_2.n_engines,
                                           propellant=self.tech_2.fuel + '/' + self.tech_2.oxidizer)

        # Stage propellant masses [units: kilogram].
        m_p_1 = m_1 - m_inert_1
        m_fuel_1 = 1 / (1 + self.tech_1.of_mass_ratio) * m_p_1
        m_oxidizer_1 = m_p_1 - m_fuel_1
        m_p_2 = m_2 - m_inert_2
        m_fuel_2 = 1 / (1 + self.tech_2.of_mass_ratio) * m_p_2
        m_oxidizer_2 = m_p_2 - m_fuel_2

        mass_dict = {
            'm0': m_0,
            's1': m_inert_recov_1 - (m_eng_1 * self.tech_1.n_engines),
            's2': m_inert_2 - (m_eng_2 * self.tech_2.n_engines),
            'e1': m_eng_1,
            'e2': m_eng_2,
            'd1': m_dispose_1,
        }

        if self.tech_1.fuel == self.tech_2.fuel:
            mass_dict[self.tech_1.fuel] = m_fuel_1 + m_fuel_2
        else:
            mass_dict[self.tech_1.fuel] = m_fuel_1
            mass_dict[self.tech_2.fuel] = m_fuel_2
        if self.tech_1.oxidizer == self.tech_2.oxidizer:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1 + m_oxidizer_2
        else:
            mass_dict[self.tech_1.oxidizer] = m_oxidizer_1
            mass_dict[self.tech_2.oxidizer] = m_oxidizer_2

        for key in mass_dict:
            assert mass_dict[key] > 0

        return mass_dict


def demo():
    strats = [Expendable, PropulsiveLaunchSite,
        WingedPoweredLaunchSite, WingedPoweredLaunchSitePartial,
        PropulsiveDownrange, WingedGlider, Parachute, ParachutePartial]

    # strats = [Expendable, WingedPoweredLaunchSite]

    for tech_1, tech_2 in zip([kero_GG_boost_tech, H2_SC_boost_tech],
                              [kero_GG_upper_tech, H2_SC_upper_tech]):
        # for mission in [LEO]:
        for mission in [LEO, GTO]:
            plt.figure(figsize=(10, 6))
            
            results = {}
            xticks = []
            for strat in strats:
                strat_instance = strat(tech_1, tech_2, mission)
                name = strat.__name__
                res = strat_instance.sample_model(nsamples=100)
                print('finished ' + name)
                res = res.as_dataframe()
                results[name] = res
                xticks.append('{:s}\n{:s}\n{:s}'.format(strat_instance.landing_method,
                                                  strat_instance.recovery_prop_method,
                                                  strat_instance.portion_recovered))

            pi_star = {}
            cost_per_flight = {}
            for strat_name in results:
                pi_star[strat_name] = results[strat_name]['pi_star']
                cost_per_flight[strat_name] = results[strat_name]['cost_per_flight']
            pi_star = pandas.DataFrame(pi_star)
            cost_per_flight = pandas.DataFrame(cost_per_flight)

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

            plt.figure(figsize=(10, 6))
            ax = sns.violinplot(data=cost_per_flight, cut=0)

            plt.title('Cost distributions for {:s} mission'.format(mission.name)
                + ', {:.1f} Mg payload'.format(mission.m_payload * 1e-3)
                + '\nstage 1: {:s} {:s} tech.,'.format(tech_1.fuel, tech_1.cycle)
                + ' stage 2: {:s} {:s} tech.'.format(tech_2.fuel, tech_2.cycle))
            plt.ylabel('Cost per flight [WYr]')
            plt.ylim([0, 400])

            ax.set_xticklabels(xticks)
            plt.xticks(rotation=30)
            plt.axvline(x=0.5, color='grey')
            plt.text(x=1, y=0.0, s='Launch site recovery')
            plt.axvline(x=3.5, color='grey')
            plt.text(x=4, y=0.0, s='Downrange recovery')

            plt.tight_layout()
            plt.savefig(os.path.join('plots', 'strategy_cost_{:s}_{:s}.png'.format(
                mission.name, tech_1.fuel)))

    plt.show()


if __name__ == '__main__':
    demo()
