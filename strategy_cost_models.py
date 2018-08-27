import abc
import math
import matplotlib.pyplot as plt
from tools import cost_reduction_factor
import elements
from vehicle import LaunchVehicle
from CERValues import CERValues
from cost_factors import ElementCostFactors, VehicleCostFactors, OperationsCostFactors
from indirect_ops import indirect_ops_cost

import rhodium as rdm
import seaborn as sns
import pandas

from cpf_models import ariane5G, falcon9, atlasV, deltaIV, electron, antares230

"""
from cpf_models.atlasV import atlasV_401, atlasV_engines_dict, atlasV_f8_dict, atlas_uncertainty_list, atlas_prod_nums
from cpf_models.falcon9 import falcon9_block3, falcon9_engines_dict, falcon9_f8_dict, falcon_uncertainty_list, falcon_prod_nums
from cpf_models.electron import electron, electron_engines_dict, electron_f8_dict, electron_uncertainty_list, electron_prod_nums
from cpf_models.deltaIV import deltaIV_medium, delta_engines_dict, delta_f8_dict, delta_uncertainty_list, delta_prod_nums
from cpf_models.antares230 import antares230, antares_engines_dict, antares_f8_dict, antares_uncertainty_list, antares_prod_nums
"""

def get_prod_dist(element):
    """Get the production CER parameter distributions from an element.

    Arguments:
        element: instance of the LaunchVehicleElement class or subclass

    Returns:
        list containing Rhodium uncertainty objects for the production CER parameters."""


    tag = element.name
    tag_a = 'prod_a_' + tag
    tag_x = 'prod_x_' + tag

    prod_a_unc = rdm.TriangularUncertainty(
        name=tag_a, 
        min_value=element.prod_a_conf_int[0], 
        mode_value=element.prod_a, 
        max_value=element.prod_a_conf_int[1]
    )
    prod_x_unc = rdm.TriangularUncertainty(
        name=tag_x,
        min_value=element.prod_x_conf_int[0],
        mode_value=element.prod_x,
        max_value=element.prod_x_conf_int[1]
    )

    return [prod_a_unc, prod_x_unc]

def get_dev_dist(element):
    """Get the development CER parameter distributions from an element.

    Arguments:
        element: instance of the LaunchVehicleElement class or subclass

    Returns:
        list containing Rhodium uncertainy objects for the production CER parameters."""

    tag = element.name
    tag_a = 'dev_a_' + tag
    tag_x = 'dev_x_' + tag

    dev_a_unc = rdm.TriangularUncertainty(
        name=tag_a,
        min_value=element.dev_a_conf_int[0],
        mode_value=element.dev_a,
        max_value=element.dev_a_conf_int[1]
    )
    dev_x_unc = rdm.TriangularUncertainty(
        name=tag_x,
        min_value=element.dev_x_conf_int[0],
        mode_value=element.dev_x,
        max_value=element.dev_x_conf_int[1])

    return [dev_a_unc, dev_x_unc]


class VehicleArchitecture(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list):
        self.launch_vehicle = launch_vehicle
        self.vehicle_prod_nums_list = vehicle_prod_nums_list
        self.num_engines_dict = num_engines_dict
        self.f8_dict = f8_dict
        self.prod_cost_facs_unc_list = prod_cost_facs_unc_list
        self.prod_uncertainties = []
        self.avg_prod_cost_model = rdm.Model(self.evaluate_avg_prod_cost)

    def setup_avg_prod_cost_model(self):

        self.avg_prod_cost_model.parameters = [rdm.Parameter(u.name) for u in self.prod_uncertainties]
        self.avg_prod_cost_model.uncertainties = self.prod_uncertainties
        self.avg_prod_cost_model.responses = [
            rdm.Response('cost', rdm.Response.MINIMIZE),
        ]

    @abc.abstractmethod
    def evaluate_avg_prod_cost(self):
        pass

    def sample_avg_prod_cost_model(self, nsamples=1000):
        """Draw samples from the performance model"""
        scenarios = rdm.sample_lhs(self.avg_prod_cost_model, nsamples)
        results = rdm.evaluate(self.avg_prod_cost_model, scenarios)
        return results

    # other setup methods for each evaluate model

    def evaluate_dev_cost(self):
        pass

    def evaluate_ops_cost(self):
        pass

class TwoLiquidStageTwoEngine(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one type of engine per stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list):
        super(TwoLiquidStageTwoEngine, self).__init__(launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list)
        self.prod_uncertainties += prod_cost_facs_unc_list
        self.prod_uncertainties += [unc for element in self.launch_vehicle.element_list for unc in get_prod_dist(element)]
        self.setup_avg_prod_cost_model()

    def evaluate_avg_prod_cost(self, f0_prod_veh=1.0, f9_veh=1.0,
                               f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                               f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                               f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                               f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0):

        s1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_e2, prod_x=prod_x_e2)

        s1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s1'], f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['e1'], f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s2'], f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['e2'], f10=f10_e2, f11=f11_e2, p=p_e2)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=None, f0_prod=f0_prod_veh, f6=None, f7=None, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, self.vehicle_prod_nums_list, element_map)

        return cost

class OneSolidOneLiquid(VehicleArchitecture):
    """Two stage vehicle, first stage liquid with one engine type, second stage solid."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list):
        super(OneSolidOneLiquid, self).__init__(launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list)
        self.prod_uncertainties += prod_cost_facs_unc_list
        self.prod_uncertainties += [unc for element in self.launch_vehicle.element_list for unc in get_prod_dist(element)]
        self.setup_avg_prod_cost_model()

    def evaluate_avg_prod_cost(self, f0_prod_veh=1.0, f9_veh=1.0,
                               f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                               f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                               f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0):

        s1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s2, prod_x=prod_x_s2)

        s1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s1'], f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['e1'], f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s2'], f10=f10_s2, f11=f11_s2, p=p_s2)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1]}

        veh_cost_factors = VehicleCostFactors(f0_dev=None, f0_prod=f0_prod_veh, f6=None, f7=None, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, self.vehicle_prod_nums_list, element_map)

        return cost

class TwoLiquidStageTwoEngineWithBooster(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one type of engine per stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list):
        super(TwoLiquidStageTwoEngineWithBooster, self).__init__(launch_vehicle, vehicle_prod_nums_list, num_engines_dict, f8_dict, prod_cost_facs_unc_list)
        self.prod_uncertainties += prod_cost_facs_unc_list
        self.prod_uncertainties += [unc for element in self.launch_vehicle.element_list for unc in get_prod_dist(element)]
        self.setup_avg_prod_cost_model()

    def evaluate_avg_prod_cost(self, f0_prod_veh=1.0, f9_veh=1.0,
                               f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                               f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                               f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                               f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                               f10_b1=1.0, f11_b1=1.0, p_b1=1.0, prod_a_b1=1.0, prod_x_b1=1.0):

        s1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_e2, prod_x=prod_x_e2)
        b1_CER_vals = CERValues(dev_a=None, dev_x=None, prod_a=prod_a_b1, prod_x=prod_x_b1)

        s1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s1'], f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['e1'], f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['s2'], f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['e2'], f10=f10_e2, f11=f11_e2, p=p_e2)
        b1_cost_factors = ElementCostFactors(f1=None, f2=None, f3=None, f8=self.f8_dict['b1'], f10=f10_b1, f11=f11_b1, p=p_b1)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']],
                       'b1': [b1_CER_vals, b1_cost_factors, self.num_engines_dict['b1']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=None, f0_prod=f0_prod_veh, f6=None, f7=None, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, self.vehicle_prod_nums_list, element_map)

        return cost

prod_nums = range(1,11)

atlasV_401_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=atlasV.atlasV_401,
    vehicle_prod_nums_list=atlasV.atlas_prod_nums,
    num_engines_dict=atlasV.atlasV_engines_dict,
    f8_dict=atlasV.atlasV_f8_dict,
    prod_cost_facs_unc_list=atlasV.atlas_uncertainty_list
)

falcon9_block3_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=falcon9.falcon9_block3,
    vehicle_prod_nums_list=falcon9.falcon_prod_nums,
    num_engines_dict=falcon9.falcon9_engines_dict,
    f8_dict=falcon9.falcon9_f8_dict,
    prod_cost_facs_unc_list=falcon9.falcon_uncertainty_list
)

electron_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=electron.electron,
    vehicle_prod_nums_list=electron.electron_prod_nums,
    num_engines_dict=electron.electron_engines_dict,
    f8_dict=electron.electron_f8_dict,
    prod_cost_facs_unc_list=electron.electron_uncertainty_list
)

delta_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=deltaIV.deltaIV_medium,
    vehicle_prod_nums_list=deltaIV.delta_prod_nums,
    num_engines_dict=deltaIV.delta_engines_dict,
    f8_dict=deltaIV.delta_f8_dict,
    prod_cost_facs_unc_list=deltaIV.delta_uncertainty_list
)

antares230_architecture = OneSolidOneLiquid(
    launch_vehicle=antares230.antares230,
    vehicle_prod_nums_list=antares230.antares_prod_nums,
    num_engines_dict=antares230.antares_engines_dict,
    f8_dict=antares230.antares_f8_dict,
    prod_cost_facs_unc_list=antares230.antares_uncertainty_list
)

atlas5G_architecture = TwoLiquidStageTwoEngineWithBooster(
    launch_vehicle=ariane5G.ariane5G,
    vehicle_prod_nums_list=ariane5G.ariane_prod_nums_list,
    num_engines_dict=ariane5G.ariane_engines_dict,
    f8_dict=ariane5G.ariane_f8_dict,
    prod_cost_facs_unc_list=ariane5G.ariane_uncertainty_list
)

def demo():

    vehicles = [atlasV_401_architecture, falcon9_block3_architecture,
                delta_architecture, antares230_architecture, atlas5G_architecture]

    results_prod = {}
    xticks = []
    for vehicle in vehicles:
        name = vehicle.launch_vehicle.name
        res_prod = vehicle.sample_avg_prod_cost_model(nsamples=1000)
        res_prod = res_prod.as_dataframe()
        results_prod[name] = res_prod
        xticks.append(name)

    prod_cost = {}
    for lv_name in results_prod:
        prod_cost[lv_name] = results_prod[lv_name]['cost']
    prod_cost = pandas.DataFrame(prod_cost)

    sns.set(style='whitegrid')
    ax = sns.violinplot(data=prod_cost)
    plt.title('Current production cost')
    plt.ylabel('Cost [WYr]')
    plt.xlabel('Launch vehicle')

    plt.scatter(0, 314, marker='+', color='red', zorder=10)
    plt.scatter(1, 177, marker='+', color='red', zorder=10)
    plt.scatter(2, 553, marker='+', color='red', zorder=10)
    plt.scatter(3, 229, marker='+', color='red', zorder=10)

    plt.show()

if __name__ == '__main__':
    demo()

