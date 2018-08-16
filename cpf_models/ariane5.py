"""Cost per flight model for first stage reuse."""
import math
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath('..'))
from tools import cost_reduction_factor
from elements import SolidRocketMotor, CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    SolidPropellantBooster, ExpendableBallisticStageStorable, StorablePressureFed
from vehicle import LaunchVehicle
from CERValues import CERValues
from cost_factors import ElementCostFactors, VehicleCostFactors, OperationsCostFactors
from indirect_ops import indirect_ops_cost


SRB = SolidPropellantBooster("SRB", 39300)
SRB_CER_vals = CERValues(SRB.dev_a, SRB.dev_x, SRB.prod_a, SRB.prod_x)
SRB_cost_factors = ElementCostFactors(f1=1.1, f2=1.0, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.95)

core_vehicle = ExpendableBallisticStageLH2("core_vehicle", 13610)
core_veh_CER_vals = CERValues(core_vehicle.dev_a, core_vehicle.dev_x, core_vehicle.prod_a, core_vehicle.prod_x)
core_veh_cost_factors = ElementCostFactors(f1=1.1, f2=1.16, f3=0.85, f8=0.86, f10=1.0, f11=1.0, p=0.925)

vulcain_engine = CryoLH2TurboFed("vulcain_engine", 1685)
vulcain_engine_CER_vals = CERValues(vulcain_engine.dev_a, vulcain_engine.dev_x, vulcain_engine.prod_a, vulcain_engine.prod_x)
vulcain_engine_cost_factors = ElementCostFactors(f1=1.1, f2=0.79, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.925)

stage2 = ExpendableBallisticStageStorable("stage2", 2500)
stage2_CER_vals = CERValues(stage2.dev_a, stage2.dev_x, stage2.prod_a, stage2.prod_x)
stage2_cost_factors = ElementCostFactors(f1=0.9, f2=1.09, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.925)

aestus_engine = StorablePressureFed("aestus_engine", 119)
aestus_engine_CER_vals = CERValues(aestus_engine.dev_a, aestus_engine.dev_x, aestus_engine.prod_a, aestus_engine.prod_x)
aestus_engine_cost_factors = ElementCostFactors(f1=0.8, f2=1.0, f3=0.8, f8=0.77, f10=1.0, f11=1.0, p=0.925)

ariane5_element_list =  [SRB, core_vehicle, vulcain_engine, stage2, aestus_engine]
ariane5 = LaunchVehicle("ariane5", 777, 6, ariane5_element_list)

ariane5_element_map = {"SRB": [SRB_CER_vals, SRB_cost_factors, 2],
                       "core_vehicle": [core_veh_CER_vals, core_veh_cost_factors, 1],
                       "vulcain_engine": [vulcain_engine_CER_vals, vulcain_engine_cost_factors, 1],
                       "stage2": [stage2_CER_vals, stage2_cost_factors, 1],
                       "aestus_engine": [aestus_engine_CER_vals, aestus_engine_cost_factors, 1]}

ariane5_cost_factors = VehicleCostFactors(f0_dev=1.04**3, f0_prod=1.025, f6=1.0, f7=1.0, f8=0.86, f9=1.07, p=0.925)

ariane5_ops_cost_factors = OperationsCostFactors(f5_vehicle=0, f5_engine=0, f8=0.86, f11=1.0, fv=0.9, fc=0.85, p=0.925)


####### INPUTS #######
launch_vehicle = ariane5
launch_vehicle_cost_factors = ariane5_cost_factors
launch_vehicle_element_map = ariane5_element_map
total_num_launches = 120
fleet_size = total_num_launches
sum_QN = 1.6
M_rec = 0
ops_cost_factors = ariane5_ops_cost_factors

launch_nums_list = range(1, 61)
prod_nums = range(1, fleet_size+1)

num_crew = 0
mission_duration = 0

cost_LH2 = 2.7623 * 10 ** (-5) # [units: WYr/kg]
cost_LOX = 8.1019 * 10 ** (-7) # [units: WYr/kg]
cost_MMH = 0.0013117 # [units: WYr/kg]
cost_N2O4 = 3.3951 * 10 ** (-4) # [units: WYr/kg]

stage1_props_cost = 22777 * 1.85 * cost_LH2 + 141222 * 1.6 * cost_LOX
stage2_props_cost = 3180 * cost_MMH + 6520 * cost_N2O4

props_gasses_cost = stage1_props_cost + stage2_props_cost

ground_transport_cost = 5 # [units: WYr]
insurance = 1.5 # [units: WYr]
fees = 0

launch_provider_type = 'A'
# indirect_ops = indirect_ops_cost(6, launch_provider_type) # [WYr]

profit_multiplier = 1.07

# launch_rate = 6

cpf_v_launch_rate = []

launch_rate_range = range(3,13)

for launch_rate in launch_rate_range:

    ####### COSTS #######
    dev_cost = launch_vehicle.vehicle_development_cost(launch_vehicle_cost_factors, launch_vehicle_element_map)

    avg_prod_cost = launch_vehicle.average_vehicle_production_cost(launch_vehicle_cost_factors, prod_nums, launch_vehicle_element_map)
    # fleet_prod_cost = fleet_size * avg_prod_cost

    ground_ops_cost = launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, launch_nums_list)
    mission_ops_cost = launch_vehicle.flight_mission_ops_cost(sum_QN, launch_rate, ops_cost_factors, launch_nums_list)


    direct_ops = ground_ops_cost + mission_ops_cost + props_gasses_cost + fees + insurance

    indirect_ops = indirect_ops_cost(launch_rate, launch_provider_type)

    cost_per_flight = avg_prod_cost + direct_ops + indirect_ops + dev_cost/total_num_launches

    price_per_flight = profit_multiplier * cost_per_flight

    cpf_v_launch_rate.append(cost_per_flight)


plt.scatter(launch_rate_range, cpf_v_launch_rate)
plt.xlabel('Launch Rate [LpA]')
plt.ylabel('Cost per Flight [WYr]')
plt.show()


# print 'CpF + amortization: ' + str(cost_per_flight)


