import abc
import os.path
import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import rhodium as rdm
import seaborn as sns
import pandas

from lvreuse.cost.tools import cost_reduction_factor
from lvreuse.cost.CER_values import CERValues
from lvreuse.cost.cost_factors import ElementCostFactors, VehicleCostFactors, OperationsCostFactors
from lvreuse.cost.indirect_ops import indirect_ops_cost
from lvreuse.data.propellants import propellant_cost_list
from lvreuse.data.vehicle_cpf_data import ariane5G, falcon9, atlasV, deltaIV, electron, antares230
from lvreuse.cost.elements import VTOStageFlybackVehicle
    
wyr_conversion = .3674

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

def get_props_cost(vehicle_props_dict):
    """Get the cost of propellants for a vehicle.

    Arguments:
        vehicle_props_dict: dictionary specifiying propellants and there respective masses in kg, 
            i.e. {'propellant': mass}

    Returns:
        vehicle propellants cost [WYr]"""

    total_prop_cost = 0

    for prop in vehicle_props_dict:

        total_prop_cost += propellant_cost_list[prop] * vehicle_props_dict[prop]

    return total_prop_cost


class VehicleArchitecture(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list, 
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list, 
                 dev_cost_unc_list):
        """Create a vehicle architecture for cost analysis.

        Arguments:
            launch_vehicle: instance of the LaunchVehicle class describing launch vehicle
            vehicle_prod_nums_list: list of consecutive vehicle production numbers to consider
            vehicle_launch_nums_list: list of consecutive flight numbers to evaluate
            num_engines_dict: dictionary mapping engine/booster element names to the number of 
            identical units per vehicle, i.e. {element_name: num_identical_units}
            f8_dict: dictionary mapping element names to their respective country productivity 
                correction factor, i.e. {element_name: f8_value}
            fv (positive scalar): cost factor for impact of launch vehicle type [units: dimensionless].
            fc (positive scalar): cost factor for impact of assembly and integration mode 
                [units: dimensionless]. 
            sum_QN: sum of vehicle stage type factors Q, see vehicle class for more info
            launch_provider_type: letter designation indicating the launch provider type
            vehicle_props_dict: dictionary specifiying propellants and there respective masses in kg, 
                i.e. {'propellant': mass}
            prod_cost_facs_unc_list: list of Rhodium uncertainty objects specifying production cost uncertainties
            ops_cost_unc_list: list of Rhodium uncertainty objects specifying operations cost uncertainties
            dev_cost_unc_list: list of Rhodium uncertainty objects specifying development cost uncertainties
        """

        self.launch_vehicle = launch_vehicle
        self.vehicle_prod_nums_list = vehicle_prod_nums_list
        self.vehicle_launch_nums_list = vehicle_launch_nums_list
        self.num_engines_dict = num_engines_dict
        self.f8_dict = f8_dict
        self.fv = fv
        self.fc = fc
        self.sum_QN = sum_QN
        self.launch_provider_type = launch_provider_type
        self.vehicle_props_dict = vehicle_props_dict
        self.prod_cost_facs_unc_list = prod_cost_facs_unc_list
        self.ops_cost_unc_list = ops_cost_unc_list
        self.dev_cost_unc_list = dev_cost_unc_list
        self.uncertainties = []
        self.cost_model = rdm.Model(self.evaluate_cost)
        
    def setup_cost_model(self):

        self.cost_model.parameters = [rdm.Parameter(u.name) for u in self.uncertainties]
        self.cost_model.uncertainties = self.uncertainties
        self.cost_model.responses = [
            rdm.Response('prod_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('ops_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('dev_cost', rdm.Response.MAXIMIZE),
            rdm.Response('price_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('stage1_avg_prod_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('stage2_avg_prod_cost_per_flight', rdm.Response.MAXIMIZE),
            rdm.Response('veh_int_checkout_per_flight', rdm.Response.MAXIMIZE),
        ]

    @abc.abstractmethod
    def evaluate_cost(self):
        pass

    def sample_cost_model(self, nsamples=1000):
        """Draw samples from the cost models"""
        scenarios = rdm.sample_lhs(self.cost_model, nsamples)
        results = rdm.evaluate(self.cost_model, scenarios)
        return results

    def update_masses(self, masses_dict):
        """Update take-off weight, element masses, and propellant masses."""

        self.launch_vehicle.M0 = masses_dict['m0']/1000. # convert from kg to Mg

        for element in self.launch_vehicle.element_list:

            if isinstance(element, VTOStageFlybackVehicle):
                owe = masses_dict['s1'] + self.num_engines_dict['e1'] * masses_dict['e1']

                if 'ab' in masses_dict:
                    owe += self.num_engines_dict['ab'] * masses_dict['ab']

                element.m = owe

            else:
                element.m = masses_dict[element.name]

        for prop in self.vehicle_props_dict:
            self.vehicle_props_dict[prop] = masses_dict[prop]



class TwoLiquidStageTwoEngine(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one type of engine per stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(TwoLiquidStageTwoEngine, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                      vehicle_launch_nums_list, num_engines_dict,
                                                      f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                      vehicle_props_dict, prod_cost_facs_unc_list,
                                                      ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()

    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f1_e2=1.0, f2_e2=1.0, f3_e2=1.0, dev_a_e2=1.0, dev_x_e2=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                      f5_s1=0, f5_e1=0, f11_ops=1.0, p_ops=1.0,
                      num_reuses_s1=1.0, num_reuses_e1=1.0,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

        s1_CER_vals = CERValues(dev_a=dev_a_s1, dev_x=dev_x_s1, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=dev_a_e1, dev_x=dev_x_e1, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=dev_a_s2, dev_x=dev_x_s2, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=dev_a_e2, dev_x=dev_x_e2, prod_a=prod_a_e2, prod_x=prod_x_e2)

        s1_cost_factors = ElementCostFactors(f1=f1_s1, f2=f2_s1, f3=f3_s1, f8=self.f8_dict['s1'],
                                             f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=f1_e1, f2=f2_e1, f3=f3_e1, f8=self.f8_dict['e1'],
                                             f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=f1_s2, f2=f2_s2, f3=f3_s2, f8=self.f8_dict['s2'],
                                             f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=f1_e2, f2=f2_e2, f3=f3_e2, f8=self.f8_dict['e2'],
                                             f10=f10_e2, f11=f11_e2, p=p_e2)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=f0_dev_veh, f0_prod=f0_prod_veh, f6=f6_veh,
                                              f7=f7_veh, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, 
                                                                        self.vehicle_prod_nums_list, 
                                                                        element_map)

        f5_dict = {'s1': f5_s1, 'e1': f5_e1}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1}

        # import ipdb; ipdb.set_trace()

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1', 'e1'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)


class TwoLiquidStageTwoEnginePartial(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one type of engine per stage, partial recovery of first stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(TwoLiquidStageTwoEnginePartial, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                      vehicle_launch_nums_list, num_engines_dict,
                                                      f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                      vehicle_props_dict, prod_cost_facs_unc_list,
                                                      ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()

    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f1_e2=1.0, f2_e2=1.0, f3_e2=1.0, dev_a_e2=1.0, dev_x_e2=1.0,
                      f1_d1=1.0, f2_d1=1.0, f3_d1=1.0, dev_a_d1=1.0, dev_x_d1=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                      f10_d1=1.0, f11_d1=1.0, p_d1=1.0, prod_a_d1=1.0, prod_x_d1=1.0,
                      f5_s1=0, f5_e1=0, f11_ops=1.0, p_ops=1.0,
                      num_reuses_s1=1, num_reuses_e1=1,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

        s1_CER_vals = CERValues(dev_a=dev_a_s1, dev_x=dev_x_s1, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=dev_a_e1, dev_x=dev_x_e1, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=dev_a_s2, dev_x=dev_x_s2, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=dev_a_e2, dev_x=dev_x_e2, prod_a=prod_a_e2, prod_x=prod_x_e2)
        d1_CER_vals = CERValues(dev_a=dev_a_d1, dev_x=dev_x_d1, prod_a=prod_a_d1, prod_x=prod_x_d1)

        s1_cost_factors = ElementCostFactors(f1=f1_s1, f2=f2_s1, f3=f3_s1, f8=self.f8_dict['s1'],
                                             f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=f1_e1, f2=f2_e1, f3=f3_e1, f8=self.f8_dict['e1'],
                                             f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=f1_s2, f2=f2_s2, f3=f3_s2, f8=self.f8_dict['s2'],
                                             f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=f1_e2, f2=f2_e2, f3=f3_e2, f8=self.f8_dict['e2'],
                                             f10=f10_e2, f11=f11_e2, p=p_e2)
        d1_dost_factors = ElementCostFactors(f1=f1_d1, f2=f2_d1, f3=f3_d1, f8=self.f8_dict['d1'],
                                             f10=f10_d1, f11=f11_d1, p=p_d1)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']],
                       'd1': [d1_CER_vals, d1_dost_factors, 1]}

        veh_cost_factors = VehicleCostFactors(f0_dev=f0_dev_veh, f0_prod=f0_prod_veh, f6=f6_veh,
                                              f7=f7_veh, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, 
                                                                        self.vehicle_prod_nums_list, 
                                                                        element_map)

        f5_dict = {'s1': f5_s1, 'e1': f5_e1}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1}

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1', 'e1', 'd1'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)

class TwoLiquidStageTwoEnginePlusAirbreathing(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one rocket engine and one airbreathing engine on first stage, 
    one engine on second stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(TwoLiquidStageTwoEnginePlusAirbreathing, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                      vehicle_launch_nums_list, num_engines_dict,
                                                      f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                      vehicle_props_dict, prod_cost_facs_unc_list,
                                                      ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()

    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f1_e2=1.0, f2_e2=1.0, f3_e2=1.0, dev_a_e2=1.0, dev_x_e2=1.0,
                      f1_ab=1.0, f2_ab=1.0, f3_ab=1.0, dev_a_ab=1.0, dev_x_ab=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                      f10_ab=1.0, f11_ab=1.0, p_ab=1.0, prod_a_ab=1.0, prod_x_ab=1.0,
                      f5_s1=0, f5_e1=0, f5_ab=0, f11_ops=1.0, p_ops=1.0,
                      num_reuses_s1=1, num_reuses_e1=1, num_reuses_ab=1,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

        s1_CER_vals = CERValues(dev_a=dev_a_s1, dev_x=dev_x_s1, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=dev_a_e1, dev_x=dev_x_e1, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=dev_a_s2, dev_x=dev_x_s2, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=dev_a_e2, dev_x=dev_x_e2, prod_a=prod_a_e2, prod_x=prod_x_e2)
        ab_CER_vals = CERValues(dev_a=dev_a_ab, dev_x=dev_x_ab, prod_a=prod_a_ab, prod_x=prod_x_ab)

        s1_cost_factors = ElementCostFactors(f1=f1_s1, f2=f2_s1, f3=f3_s1, f8=self.f8_dict['s1'],
                                             f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=f1_e1, f2=f2_e1, f3=f3_e1, f8=self.f8_dict['e1'],
                                             f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=f1_s2, f2=f2_s2, f3=f3_s2, f8=self.f8_dict['s2'],
                                             f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=f1_e2, f2=f2_e2, f3=f3_e2, f8=self.f8_dict['e2'],
                                             f10=f10_e2, f11=f11_e2, p=p_e2)
        ab_cost_factors = ElementCostFactors(f1=f1_ab, f2=f2_ab, f3=f3_ab, f8=self.f8_dict['ab'],
                                             f10=f10_ab, f11=f11_ab, p=p_ab)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']],
                       'ab': [ab_CER_vals, ab_cost_factors, self.num_engines_dict['ab']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=f0_dev_veh, f0_prod=f0_prod_veh, f6=f6_veh,
                                              f7=f7_veh, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, 
                                                                        self.vehicle_prod_nums_list, 
                                                                        element_map)
        f5_dict = {'s1': f5_s1, 'e1': f5_e1, 'ab': f5_ab}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1, 'ab': num_reuses_ab}

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1', 'e1', 'ab'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)

class TwoLiquidStagePartialPlusAirbreathing(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one rocket engine and one airbreathing engine on first stage, 
    one engine on second stage, partial recovery of first stage."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(TwoLiquidStagePartialPlusAirbreathing, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                      vehicle_launch_nums_list, num_engines_dict,
                                                      f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                      vehicle_props_dict, prod_cost_facs_unc_list,
                                                      ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()

    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f1_e2=1.0, f2_e2=1.0, f3_e2=1.0, dev_a_e2=1.0, dev_x_e2=1.0,
                      f1_d1=1.0, f2_d1=1.0, f3_d1=1.0, dev_a_d1=1.0, dev_x_d1=1.0,
                      f1_ab=1.0, f2_ab=1.0, f3_ab=1.0, dev_a_ab=1.0, dev_x_ab=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                      f10_d1=1.0, f11_d1=1.0, p_d1=1.0, prod_a_d1=1.0, prod_x_d1=1.0,
                      f10_ab=1.0, f11_ab=1.0, p_ab=1.0, prod_a_ab=1.0, prod_x_ab=1.0,
                      f5_s1=0, f5_e1=0, f5_ab=0, f11_ops=1.0, p_ops=1.0,
                      num_reuses_s1=1, num_reuses_e1=1, num_reuses_ab=1,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

        s1_CER_vals = CERValues(dev_a=dev_a_s1, dev_x=dev_x_s1, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=dev_a_e1, dev_x=dev_x_e1, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=dev_a_s2, dev_x=dev_x_s2, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=dev_a_e2, dev_x=dev_x_e2, prod_a=prod_a_e2, prod_x=prod_x_e2)
        d1_CER_vals = CERValues(dev_a=dev_a_d1, dev_x=dev_x_d1, prod_a=prod_a_d1, prod_x=prod_x_d1)
        ab_CER_vals = CERValues(dev_a=dev_a_ab, dev_x=dev_x_ab, prod_a=prod_a_ab, prod_x=prod_x_ab)

        s1_cost_factors = ElementCostFactors(f1=f1_s1, f2=f2_s1, f3=f3_s1, f8=self.f8_dict['s1'],
                                             f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=f1_e1, f2=f2_e1, f3=f3_e1, f8=self.f8_dict['e1'],
                                             f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=f1_s2, f2=f2_s2, f3=f3_s2, f8=self.f8_dict['s2'],
                                             f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=f1_e2, f2=f2_e2, f3=f3_e2, f8=self.f8_dict['e2'],
                                             f10=f10_e2, f11=f11_e2, p=p_e2)
        d1_dost_factors = ElementCostFactors(f1=f1_d1, f2=f2_d1, f3=f3_d1, f8=self.f8_dict['d1'],
                                             f10=f10_d1, f11=f11_d1, p=p_d1)
        ab_cost_factors = ElementCostFactors(f1=f1_ab, f2=f2_ab, f3=f3_ab, f8=self.f8_dict['ab'],
                                             f10=f10_ab, f11=f11_ab, p=p_ab)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']],
                       'd1': [d1_CER_vals, d1_dost_factors, 1],
                       'ab': [ab_CER_vals, ab_cost_factors, self.num_engines_dict['ab']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=f0_dev_veh, f0_prod=f0_prod_veh, f6=f6_veh,
                                              f7=f7_veh, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, 
                                                                        self.vehicle_prod_nums_list, 
                                                                        element_map)


        f5_dict = {'s1': f5_s1, 'e1': f5_e1, 'ab': f5_ab}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1, 'ab': num_reuses_ab}

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1', 'e1', 'd1', 'ab'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)

class OneSolidOneLiquid(VehicleArchitecture):
    """Two stage vehicle, first stage liquid with one engine type, second stage solid."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(OneSolidOneLiquid, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                vehicle_launch_nums_list, num_engines_dict,
                                                f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                vehicle_props_dict, prod_cost_facs_unc_list,
                                                ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()


    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f5_s1=0, f5_e1=0, f11_ops=1.0, p_ops=1.0,
                      num_reuses_s1=1, num_reuses_e1=1,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

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

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, self.vehicle_prod_nums_list, element_map)

        f5_dict = {'s1': f5_s1, 'e1': f5_e1}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1}

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(num_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)

class TwoLiquidStageTwoEngineWithBooster(VehicleArchitecture):
    """Two stage vehicle, liquid stages, one type of engine per stage, with solid rocket boosters."""

    def __init__(self, launch_vehicle, vehicle_prod_nums_list, vehicle_launch_nums_list,
                 num_engines_dict, f8_dict, fv, fc, sum_QN, launch_provider_type,
                 vehicle_props_dict, prod_cost_facs_unc_list, ops_cost_unc_list,
                 dev_cost_unc_list):
        super(TwoLiquidStageTwoEngineWithBooster, self).__init__(launch_vehicle, vehicle_prod_nums_list,
                                                vehicle_launch_nums_list, num_engines_dict,
                                                f8_dict, fv, fc, sum_QN, launch_provider_type,
                                                vehicle_props_dict, prod_cost_facs_unc_list,
                                                ops_cost_unc_list, dev_cost_unc_list)
        self.uncertainties += prod_cost_facs_unc_list
        self.uncertainties += ops_cost_unc_list
        self.uncertainties += dev_cost_unc_list
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_prod_dist(element)]
        self.uncertainties += [unc for element in self.launch_vehicle.element_list for unc in
                               get_dev_dist(element)]
        self.setup_cost_model()

    def evaluate_cost(self, f0_prod_veh=1.0, f0_dev_veh = 1.0, f6_veh=1.0, f7_veh=1.0, f9_veh=1.0,
                      f1_s1=1.0, f2_s1=1.0, f3_s1=1.0, dev_a_s1=1.0, dev_x_s1=1.0,
                      f1_e1=1.0, f2_e1=1.0, f3_e1=1.0, dev_a_e1=1.0, dev_x_e1=1.0,
                      f1_s2=1.0, f2_s2=1.0, f3_s2=1.0, dev_a_s2=1.0, dev_x_s2=1.0,
                      f1_e2=1.0, f2_e2=1.0, f3_e2=1.0, dev_a_e2=1.0, dev_x_e2=1.0,
                      f1_b1=1.0, f2_b1=1.0, f3_b1=1.0, dev_a_b1=1.0, dev_x_b1=1.0,
                      f10_s1=1.0, f11_s1=1.0, p_s1=1.0, prod_a_s1=1.0, prod_x_s1=1.0,
                      f10_e1=1.0, f11_e1=1.0, p_e1=1.0, prod_a_e1=1.0, prod_x_e1=1.0,
                      f10_s2=1.0, f11_s2=1.0, p_s2=1.0, prod_a_s2=1.0, prod_x_s2=1.0,
                      f10_e2=1.0, f11_e2=1.0, p_e2=1.0, prod_a_e2=1.0, prod_x_e2=1.0,
                      f10_b1=1.0, f11_b1=1.0, p_b1=1.0, prod_a_b1=1.0, prod_x_b1=1.0,
                      f5_s1=0, f5_e1=0, f11_ops=1.0, p_ops=1.0, 
                      num_reuses_s1 = 1, num_reuses_e1 = 1,
                      num_program_flights=1, profit_multiplier=1.0, launch_rate=None, fees=0,
                      insurance=0, recovery_cost=0, frac_dev_paid=0):

        s1_CER_vals = CERValues(dev_a=dev_a_s1, dev_x=dev_x_s1, prod_a=prod_a_s1, prod_x=prod_x_s1)
        e1_CER_vals = CERValues(dev_a=dev_a_e1, dev_x=dev_x_e1, prod_a=prod_a_e1, prod_x=prod_x_e1)
        s2_CER_vals = CERValues(dev_a=dev_a_s2, dev_x=dev_x_s2, prod_a=prod_a_s2, prod_x=prod_x_s2)
        e2_CER_vals = CERValues(dev_a=dev_a_e2, dev_x=dev_x_e2, prod_a=prod_a_e2, prod_x=prod_x_e2)
        b1_CER_vals = CERValues(dev_a=dev_a_b1, dev_x=dev_x_b1, prod_a=prod_a_b1, prod_x=prod_x_b1)

        s1_cost_factors = ElementCostFactors(f1=f1_s1, f2=f2_s1, f3=f3_s1, f8=self.f8_dict['s1'], f10=f10_s1, f11=f11_s1, p=p_s1)
        e1_cost_factors = ElementCostFactors(f1=f1_e1, f2=f2_e1, f3=f3_e1, f8=self.f8_dict['e1'], f10=f10_e1, f11=f11_e1, p=p_e1)
        s2_cost_factors = ElementCostFactors(f1=f1_s2, f2=f2_s2, f3=f3_s2, f8=self.f8_dict['s2'], f10=f10_s2, f11=f11_s2, p=p_s2)
        e2_cost_factors = ElementCostFactors(f1=f1_e2, f2=f2_e2, f3=f3_e2, f8=self.f8_dict['e2'], f10=f10_e2, f11=f11_e2, p=p_e2)
        b1_cost_factors = ElementCostFactors(f1=f1_b1, f2=f2_b1, f3=f3_b1, f8=self.f8_dict['b1'], f10=f10_b1, f11=f11_b1, p=p_b1)

        element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                       'e1': [e1_CER_vals, e1_cost_factors, self.num_engines_dict['e1']],
                       's2': [s2_CER_vals, s2_cost_factors, 1],
                       'e2': [e2_CER_vals, e2_cost_factors, self.num_engines_dict['e2']],
                       'b1': [b1_CER_vals, b1_cost_factors, self.num_engines_dict['b1']]}

        veh_cost_factors = VehicleCostFactors(f0_dev=f0_dev_veh, f0_prod=f0_prod_veh, f6=f6_veh, f7=f7_veh, f8=self.f8_dict['veh'], f9=f9_veh, p=None)

        prod_cost = self.launch_vehicle.average_vehicle_production_cost(veh_cost_factors, self.vehicle_prod_nums_list, element_map)

        f5_dict = {'s1': f5_s1, 'e1': f5_e1}
        element_reuses_dict = {'s1': num_reuses_s1, 'e1': num_reuses_e1}

        prod_cost_per_flight = self.launch_vehicle.average_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list)

        stage1_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s1', 'e1', 'b1'])
        stage2_avg_prod_cost_per_flight = self.launch_vehicle.average_portion_prod_cost_per_flight(element_reuses_dict, element_map, veh_cost_factors, self.vehicle_prod_nums_list, ['s2', 'e2'])

        veh_int_checkout_per_flight = prod_cost_per_flight - stage1_avg_prod_cost_per_flight - stage2_avg_prod_cost_per_flight

        ops_cost_factors = OperationsCostFactors(f5_dict, self.f8_dict['ops'], f11_ops, self.fv, self.fc, p_ops)

        ground_ops = self.launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        mission_ops = self.launch_vehicle.flight_mission_ops_cost(self.sum_QN, launch_rate, ops_cost_factors, self.vehicle_launch_nums_list)
        props_cost = get_props_cost(self.vehicle_props_dict)

        direct_ops_cost = ground_ops + mission_ops + props_cost + fees + insurance + recovery_cost
        indir_ops_cost = indirect_ops_cost(launch_rate=launch_rate, launch_provider_type=self.launch_provider_type)

        refurb_cost = self.launch_vehicle.total_refurbishment_cost(ops_cost_factors, element_map, element_reuses_dict)

        ops_cost_per_flight = direct_ops_cost + indir_ops_cost + refurb_cost

        cost_per_flight = prod_cost_per_flight + ops_cost_per_flight

        dev_cost = self.launch_vehicle.vehicle_development_cost(veh_cost_factors, element_map)

        frac_dev_cost = dev_cost * frac_dev_paid

        dev_cost_per_flight = frac_dev_cost/num_program_flights

        price_per_flight = (prod_cost_per_flight + ops_cost_per_flight)*profit_multiplier + dev_cost_per_flight

        return (prod_cost_per_flight, ops_cost_per_flight, cost_per_flight, dev_cost, price_per_flight, 
                stage1_avg_prod_cost_per_flight, stage2_avg_prod_cost_per_flight, veh_int_checkout_per_flight,
                props_cost, refurb_cost)

atlasV_401_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=atlasV.atlasV_401,
    vehicle_prod_nums_list=atlasV.atlas_prod_nums,
    vehicle_launch_nums_list=atlasV.atlas_launch_nums,
    num_engines_dict=atlasV.atlasV_engines_dict,
    f8_dict=atlasV.atlasV_f8_dict,
    fv=atlasV.atlas_fv,
    fc=atlasV.atlas_fc,
    sum_QN=atlasV.atlas_sum_QN,
    launch_provider_type=atlasV.atlas_launch_provider_type,
    vehicle_props_dict=atlasV.atlas_props_dict,
    prod_cost_facs_unc_list=atlasV.atlas_uncertainty_list,
    ops_cost_unc_list=atlasV.atlas_ops_uncertainty_list,
    dev_cost_unc_list=atlasV.atlas_dev_uncertainty_list
)

falcon9_block3_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=falcon9.falcon9_block3,
    vehicle_prod_nums_list=falcon9.falcon_prod_nums,
    vehicle_launch_nums_list=falcon9.falcon_launch_nums,
    num_engines_dict=falcon9.falcon9_engines_dict,
    f8_dict=falcon9.falcon9_f8_dict,
    fv=falcon9.falcon_fv,
    fc=falcon9.falcon_fc,
    sum_QN=falcon9.falcon_sum_QN,
    launch_provider_type=falcon9.falcon_launch_provider_type,
    vehicle_props_dict=falcon9.falcon_props_dict,
    prod_cost_facs_unc_list=falcon9.falcon_uncertainty_list,
    ops_cost_unc_list=falcon9.falcon_ops_uncertainty_list,
    dev_cost_unc_list=falcon9.falcon_dev_uncertainty_list,
)
"""
electron_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=electron.electron,
    vehicle_prod_nums_list=electron.electron_prod_nums,
    num_engines_dict=electron.electron_engines_dict,
    f8_dict=electron.electron_f8_dict,
    prod_cost_facs_unc_list=electron.electron_uncertainty_list
)
"""
deltaIV_40_architecture = TwoLiquidStageTwoEngine(
    launch_vehicle=deltaIV.deltaIV_medium,
    vehicle_prod_nums_list=deltaIV.delta_prod_nums,
    vehicle_launch_nums_list=deltaIV.delta_launch_nums,
    num_engines_dict=deltaIV.delta_engines_dict,
    f8_dict=deltaIV.delta_f8_dict,
    fv=deltaIV.delta_fv,
    fc=deltaIV.delta_fc,
    sum_QN=deltaIV.delta_sum_QN,
    launch_provider_type=deltaIV.delta_launch_provider_type,
    vehicle_props_dict=deltaIV.delta_props_dict,
    prod_cost_facs_unc_list=deltaIV.delta_uncertainty_list,
    ops_cost_unc_list=deltaIV.delta_ops_uncertainty_list,
    dev_cost_unc_list=deltaIV.delta_dev_uncertainty_list,
)
"""
antares230_architecture = OneSolidOneLiquid(
    launch_vehicle=antares230.antares230,
    vehicle_prod_nums_list=antares230.antares_prod_nums,
    vehicle_launch_nums_list=antares230.antares_launch_nums,
    num_engines_dict=antares230.antares_engines_dict,
    f8_dict=antares230.antares_f8_dict,
    fv=antares230.antares_fv,
    fc=antares230.antares_fc,
    sum_QN=antares230.antares_sum_QN,
    launch_provider_type=antares230.antares_launch_provider_type,
    vehicle_props_dict=antares230.antares_props_dict,
    prod_cost_facs_unc_list=antares230.antares_uncertainty_list,
    ops_cost_unc_list=antares230.antares_ops_uncertainty_list,
)
"""
ariane5G_architecture = TwoLiquidStageTwoEngineWithBooster(
    launch_vehicle=ariane5G.ariane5G,
    vehicle_prod_nums_list=ariane5G.ariane_prod_nums_list,
    vehicle_launch_nums_list=ariane5G.ariane_launch_nums_list,
    num_engines_dict=ariane5G.ariane_engines_dict,
    f8_dict=ariane5G.ariane_f8_dict,
    fv=ariane5G.ariane_fv,
    fc=ariane5G.ariane_fc,
    sum_QN=ariane5G.ariane_sum_QN,
    launch_provider_type=ariane5G.ariane_launch_provider_type,
    vehicle_props_dict=ariane5G.ariane_props_dict,
    prod_cost_facs_unc_list=ariane5G.ariane_uncertainty_list,
    ops_cost_unc_list=ariane5G.ariane_ops_uncertainty_list,
    dev_cost_unc_list=ariane5G.ariane_dev_uncertainty_list
)

def demo():

    vehicles = [atlasV_401_architecture, ariane5G_architecture, deltaIV_40_architecture, falcon9_block3_architecture]

    results = {}
    xticks = []
    for vehicle in vehicles:
        name = vehicle.launch_vehicle.name

        res = vehicle.sample_cost_model(nsamples=1000)
        res = res.as_dataframe()
        results[name] = res

        xticks.append(name)

    """sa_results = rdm.sa(ariane5G_architecture.avg_prod_cost_model, "cost")
    print(sa_results)"""

    prod_cost_per_flight = {}
    ops_cost_per_flight = {}
    cost_per_flight = {}
    dev_cost = {}
    price_per_flight = {}
    for lv_name in results:
        prod_cost_per_flight[lv_name] = results[lv_name]['prod_cost_per_flight']
        ops_cost_per_flight[lv_name] = results[lv_name]['ops_cost_per_flight']
        cost_per_flight[lv_name] = results[lv_name]['cost_per_flight']
        dev_cost[lv_name] = results[lv_name]['dev_cost']
        price_per_flight[lv_name] = results[lv_name]['price_per_flight']
    prod_cost_per_flight = pandas.DataFrame(prod_cost_per_flight)
    ops_cost_per_flight = pandas.DataFrame(ops_cost_per_flight)
    cost_per_flight = pandas.DataFrame(cost_per_flight)
    dev_cost = pandas.DataFrame(dev_cost)
    price_per_flight = pandas.DataFrame(price_per_flight)


    plt.figure(figsize=(10, 6))
    sns.set(style='whitegrid')
    ax = sns.violinplot(data=prod_cost_per_flight)
    plt.title('Current production cost')
    plt.ylabel('Cost [WYr]')
    plt.xlabel('Launch vehicle')


    plt.figure(figsize=(10, 6))
    sns.set(style='whitegrid')
    ax = sns.violinplot(data=cost_per_flight)
    plt.title('Cost per flight')
    plt.ylabel('Cost [WYr]')
    plt.xlabel('Launch vehicle')

    plt.scatter(0, 314, marker='+', color='red', zorder=10) # atlas
    plt.scatter(2, 553, marker='+', color='red', zorder=10) # delta
    plt.scatter(3, 177, marker='+', color='red', zorder=10) # falcon 9
    plt.scatter(1, 485, marker='+', color='red', zorder=10) # ariane 5
    
    plt.figure(figsize=(10, 6))
    sns.set(style='whitegrid')
    data=price_per_flight.multiply(wyr_conversion)
    ax = sns.violinplot(data=data)
    ax.set_ylim(0, 450)
    ax.set_ylabel('Price per flight [Million US Dollars in 2018]')

    plt.title('Price distributions for LEO mission, 10.0 Mg payload \n stage 1: kerosene gas generator tech., stage 2: kerosene gas generator tech.')
    plt.xlabel('Launch vehicle')

    plt.scatter(0, 314*wyr_conversion, s=50, color='red', zorder=10) # atlas
    plt.scatter(1, 485*wyr_conversion, s=50, color='red', zorder=10) # ariane 5
    plt.scatter(3, 177*wyr_conversion, s=50, color='red', zorder=10) # falcon 9
    plt.scatter(2, 460*wyr_conversion, s=50, color='red', zorder=10) # delta, astronautix, 133million in 2004

    ax1 = ax.twinx()
    ax1.set_ylabel('Price per flight [WYr]')
    ax1.set_ylim(0, 450/wyr_conversion)
    ax1.grid(False)

    legend_item = [Line2D([0], [0], marker='o', color='w', label='Actual price per flight',
                   markerfacecolor='red', markersize=10)]
    ax.legend(handles=legend_item)
    plt.tight_layout()

    plt.savefig(os.path.join('plots', 'vehicle_ppf_validation.png'))

    plt.show()

if __name__ == '__main__':
    demo()
