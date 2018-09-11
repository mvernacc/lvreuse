"""Construct a LaunchVehicle given strategy choices and masses."""
import os.path
from lvreuse.cost.elements import CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    ExpendableBallisticStageStorable, StorableTurboFed, ReusableBallisticStageLH2, \
    VTOStageFlybackVehicle, TurboJetEngine, ReusableBallisticStageStorable, \
    ExpendableTank
from lvreuse.cost.vehicle import LaunchVehicle


def construct_launch_vehicle(stage_type, prop_choice, portion_reused, ab_rec, num_ab_engines=None, num_rocket_engines=9):
    """Create a LaunchVehicle object given strategy choices and element masses.

    Arguments:
        stage_type: type of first stage vehicle, choose from 'winged' or 'ballistic'
        prop_choice: propellant choice for first stage, choose from 'kerosene' or 'H2'
        portion_reused: portion of first stage that is reused, choose from 'full', 'partial', or 'none'
        ab_rec (boolean): specifies whether the recovery scheme is powered or not, True for powered
        masses_dict: dictionary mapping vehicle element names to their dry masses in kg,
            i.e. {'element_name': mass}

    Returns:
        instance of the LaunchVehicle class describing the launch vehicle
    """

    stage2 = ExpendableBallisticStageStorable(name='s2', m=0)
    stage2_engine = StorableTurboFed(name='e2', m=0)
    veh_element_list = [stage2, stage2_engine]

    if stage_type == 'ballistic' and prop_choice == 'H2' and portion_reused == 'none':
        stage1 = ExpendableBallisticStageLH2(name='s1', m=0)
        stage1_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_list = [stage1, stage1_engine]

    elif stage_type == 'ballistic' and prop_choice == 'H2' and portion_reused == 'full':
        stage1 = ReusableBallisticStageLH2(name='s1', m=0)
        stage1_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_list = [stage1, stage1_engine]

    elif stage_type == 'ballistic' and prop_choice == 'H2' and portion_reused == 'partial':
        stage1_rec = ReusableBallisticStageLH2(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_engine]

    elif stage_type == 'ballistic' and prop_choice == 'kerosene' and portion_reused == 'none':
        stage1 = ExpendableBallisticStageStorable(name='s1', m=0)
        stage1_engine = StorableTurboFed(name='e1', m=0)
        stage1_list = [stage1, stage1_engine]

    elif stage_type == 'ballistic' and prop_choice == 'kerosene' and portion_reused == 'full':
        stage1 = ReusableBallisticStageStorable(name='s1', m=0)
        stage1_engine = StorableTurboFed(name='e1', m=0)
        stage1_list = [stage1, stage1_engine]

    elif stage_type == 'ballistic' and prop_choice == 'kerosene' and portion_reused == 'partial':
        stage1_rec = ReusableBallisticStageStorable(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_engine = StorableTurboFed(name='e1', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_engine]

    elif stage_type == 'winged' and prop_choice == 'H2' and portion_reused == 'full' and ab_rec:
        stage1 = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_rocket_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_ab_engine = TurboJetEngine(name='ab', m=0)
        stage1_list = [stage1, stage1_rocket_engine, stage1_ab_engine]

    elif stage_type == 'winged' and prop_choice == 'H2' and portion_reused == 'full' and not ab_rec:
        stage1_rec = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_rocket_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_list = [stage1_rec, stage1_rocket_engine]

    elif stage_type == 'winged' and prop_choice == 'H2' and portion_reused == 'partial' and ab_rec:
        stage1_rec = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_rocket_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_ab_engine = TurboJetEngine(name='ab', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_rocket_engine, stage1_ab_engine]

    elif stage_type == 'winged' and prop_choice == 'H2' and portion_reused == 'partial' and not ab_rec:
        stage1_rec = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_rocket_engine = CryoLH2TurboFed(name='e1', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_rocket_engine]

    elif stage_type == 'winged' and prop_choice == 'kerosene' and portion_reused == 'full' and ab_rec:
        stage1 = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_rocket_engine = StorableTurboFed(name='e1', m=0)
        stage1_ab_engine = TurboJetEngine(name='ab', m=0)
        stage1_list = [stage1, stage1_rocket_engine, stage1_ab_engine]

    elif stage_type == 'winged' and prop_choice == 'kerosene' and portion_reused == 'full' and not ab_rec:
        stage1 = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_rocket_engine = StorableTurboFed(name='e1', m=0)
        stage1_list = [stage1, stage1_rocket_engine]

    elif stage_type == 'winged' and prop_choice == 'kerosene' and portion_reused == 'partial' and ab_rec:
        stage1_rec = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_rocket_engine = StorableTurboFed(name='e1', m=0)
        stage1_ab_engine = TurboJetEngine(name='ab', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_rocket_engine, stage1_ab_engine]

    elif stage_type == 'winged' and prop_choice == 'kerosene' and portion_reused == 'partial' and not ab_rec:
        stage1_rec = VTOStageFlybackVehicle(name='s1', m=0)
        stage1_disp = ExpendableTank(name='d1', m=0)
        stage1_rocket_engine = StorableTurboFed(name='e1', m=0)
        stage1_list = [stage1_rec, stage1_disp, stage1_rocket_engine]


    veh_element_list += stage1_list

    if portion_reused == 'partial':
        N_veh = 3
    else:
        N_veh = 2

    launch_vehicle = LaunchVehicle(name='veh', M0=0, N=N_veh, element_list=veh_element_list)
    return launch_vehicle

def demo():

    from lvreuse.analysis.performance.strategy_perf_models import (Expendable, WingedPoweredLaunchSite,
                                  WingedPoweredLaunchSitePartial,
                                  ParachutePartial,
                                  kero_GG_boost_tech,
                                  kero_GG_upper_tech,
                                  LEO, GTO)

    import abc
    import os.path
    import math
    import matplotlib.pyplot as plt
    import rhodium as rdm
    import seaborn as sns
    import pandas

    from lvreuse.cost.tools import cost_reduction_factor
    from lvreuse.cost.CER_values import CERValues
    from lvreuse.cost.cost_factors import ElementCostFactors, VehicleCostFactors, OperationsCostFactors
    from lvreuse.cost.indirect_ops import indirect_ops_cost
    from lvreuse.data.propellants import propellant_cost_list
    from lvreuse.data.vehicle_cpf_data import ariane5G, falcon9, atlasV, deltaIV, electron, antares230

    tech_1 = kero_GG_boost_tech
    tech_2 = kero_GG_upper_tech
    mission = LEO

    wingpwr_part = WingedPoweredLaunchSitePartial(tech_1, tech_2, mission)
    wingpwr_part_dict = wingpwr_part.get_masses(pi_star=0.01, a=0.60, E_1=0.06, E_2=0.04)
    print(wingpwr_part_dict)

    launch_veh = construct_launch_vehicle(stage_type='winged', prop_choice='kerosene', portion_reused='partial', ab_rec=True, num_ab_engines=2)

    s1_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)
    e1_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)
    s2_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)
    e2_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)
    d1_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)
    ab_CER_vals = CERValues(dev_a=10, dev_x=0.5, prod_a=1, prod_x=0.5)

    s1_cost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)
    e1_cost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)
    s2_cost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)
    e2_cost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)
    d1_dost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)
    ab_cost_factors = ElementCostFactors(f1=1, f2=1, f3=1, f8=1,
                                         f10=1, f11=1, p=1)

    element_map = {'s1': [s1_CER_vals, s1_cost_factors, 1],
                   'e1': [e1_CER_vals, e1_cost_factors, 9],
                   's2': [s2_CER_vals, s2_cost_factors, 1],
                   'e2': [e2_CER_vals, e2_cost_factors, 1],
                   'd1': [d1_CER_vals, d1_dost_factors, 1],
                   'ab': [ab_CER_vals, ab_cost_factors, 2]}

    veh_cost_factors = VehicleCostFactors(f0_dev=1, f0_prod=1, f6=1,
                                          f7=1, f8=1, f9=1, p=1)

    prod_nums = [1]

    prod_cost = launch_veh.average_vehicle_production_cost(veh_cost_factors, prod_nums, element_map)

    print('prod_cost: ', prod_cost)

if __name__ == '__main__':
    demo()
    print(range(4))
