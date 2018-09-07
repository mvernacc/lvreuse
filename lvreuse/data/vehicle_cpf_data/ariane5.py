"""Cost per flight model for Ariane 5 rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import os.path
from lvreuse.cost.tools import cost_reduction_factor
from lvreuse.cost.elements import SolidRocketMotor, CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    SolidPropellantBooster, ExpendableBallisticStageStorable, StorablePressureFed
from lvreuse.cost.vehicle import LaunchVehicle
from lvreuse.cost.indirect_ops import indirect_ops_cost

### Ariane 5 ECA

SRB = SolidPropellantBooster("P240", 40300) # data from Isakowitz p. 31
SRB_CER_vals = CERValues(SRB.dev_a, SRB.dev_x, SRB.prod_a, SRB.prod_x)
SRB_cost_factors = ElementCostFactors(f1=1.1, f2=1.0, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.95)

core_vehicle = ExpendableBallisticStageLH2("H173", 16000 - 1800) # data from Isakowitz, less engine
core_veh_CER_vals = CERValues(core_vehicle.dev_a, core_vehicle.dev_x, core_vehicle.prod_a, core_vehicle.prod_x)
core_veh_cost_factors = ElementCostFactors(f1=1.1, f2=1.16, f3=0.85, f8=0.86, f10=1.0, f11=1.0, p=0.9)

vulcain_engine = CryoLH2TurboFed("vulcain2", 1800)
vulcain_engine_CER_vals = CERValues(vulcain_engine.dev_a, vulcain_engine.dev_x, vulcain_engine.prod_a, vulcain_engine.prod_x)
vulcain_engine_cost_factors = ElementCostFactors(f1=1.1, f2=0.79, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

stage2 = ExpendableBallisticStageStorable("ESC-A", 3418 + 950 + 2025 + 716 - 165) # data from Isakowitz, including VEB, short fairing, SPELTRA, less engine
stage2_CER_vals = CERValues(stage2.dev_a, stage2.dev_x, stage2.prod_a, stage2.prod_x)
stage2_cost_factors = ElementCostFactors(f1=0.9, f2=1.09, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

aestus_engine = CryoLH2TurboFed("HM7B", 165) 
aestus_engine_CER_vals = CERValues(aestus_engine.dev_a, aestus_engine.dev_x, aestus_engine.prod_a, aestus_engine.prod_x)
aestus_engine_cost_factors = ElementCostFactors(f1=0.8, f2=1.0, f3=0.8, f8=0.77, f10=1.0, f11=1.0, p=0.9)

ariane5_element_list =  [SRB, core_vehicle, vulcain_engine, stage2, aestus_engine]
ariane5ECA = LaunchVehicle(name="ariane5ECA", M0=791, N=4, element_list=ariane5_element_list)

ariane5ECA_element_map = {"P240": [SRB_CER_vals, SRB_cost_factors, 2],
                       "H173": [core_veh_CER_vals, core_veh_cost_factors, 1],
                       "vulcain2": [vulcain_engine_CER_vals, vulcain_engine_cost_factors, 1],
                       "ESC-A": [stage2_CER_vals, stage2_cost_factors, 1],
                       "HM7B": [aestus_engine_CER_vals, aestus_engine_cost_factors, 1]}

ariane5_cost_factors = VehicleCostFactors(f0_dev=1.04**3, f0_prod=1.02, f6=1.0, f7=1.0, f8=0.86, f9=1.07, p=0.9)

ariane5_ops_cost_factors = OperationsCostFactors(f5_vehicle=0, f5_engine=0, f8=0.86, f11=1.0, fv=0.6, fc=0.85, p=0.85)


### Ariane 5G 

SRB = SolidPropellantBooster("P230", 39800) # data from Isakowitz p. 31
SRB_CER_vals = CERValues(SRB.dev_a, SRB.dev_x, SRB.prod_a, SRB.prod_x)
SRB_cost_factors = ElementCostFactors(f1=1.1, f2=1.0, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.95)

core_vehicle = ExpendableBallisticStageLH2("H158", 12200 - 1300) # data from Isakowitz, less engine
core_veh_CER_vals = CERValues(core_vehicle.dev_a, core_vehicle.dev_x, core_vehicle.prod_a, core_vehicle.prod_x)
core_veh_cost_factors = ElementCostFactors(f1=1.1, f2=1.16, f3=0.85, f8=0.86, f10=1.0, f11=1.0, p=0.9)

vulcain_engine = CryoLH2TurboFed("vulcain1", 1300)
vulcain_engine_CER_vals = CERValues(vulcain_engine.dev_a, vulcain_engine.dev_x, vulcain_engine.prod_a, vulcain_engine.prod_x)
vulcain_engine_cost_factors = ElementCostFactors(f1=1.1, f2=0.79, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

stage2 = ExpendableBallisticStageStorable("EPS-L9", 1200 + 1500 + 2025 + 716 - 111) # data from Isakowitz, including VEB, short fairing, SPELTRA, less engine
stage2_CER_vals = CERValues(stage2.dev_a, stage2.dev_x, stage2.prod_a, stage2.prod_x)
stage2_cost_factors = ElementCostFactors(f1=0.9, f2=1.09, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

aestus_engine = StorablePressureFed("Aestus", 111) 
aestus_engine_CER_vals = CERValues(aestus_engine.dev_a, aestus_engine.dev_x, aestus_engine.prod_a, aestus_engine.prod_x)
aestus_engine_cost_factors = ElementCostFactors(f1=0.8, f2=1.0, f3=0.8, f8=0.77, f10=1.0, f11=1.0, p=0.9)

ariane5_element_list =  [SRB, core_vehicle, vulcain_engine, stage2, aestus_engine]
ariane5G = LaunchVehicle(name="ariane5G", M0=746, N=4, element_list=ariane5_element_list)

ariane5G_element_map = {"P230": [SRB_CER_vals, SRB_cost_factors, 2],
                       "H158": [core_veh_CER_vals, core_veh_cost_factors, 1],
                       "vulcain1": [vulcain_engine_CER_vals, vulcain_engine_cost_factors, 1],
                       "EPS-L9": [stage2_CER_vals, stage2_cost_factors, 1],
                       "Aestus": [aestus_engine_CER_vals, aestus_engine_cost_factors, 1]}

ariane5_cost_factors = VehicleCostFactors(f0_dev=1.04**3, f0_prod=1.02, f6=1.0, f7=1.0, f8=0.86, f9=1.07, p=0.9)

ariane5_ops_cost_factors = OperationsCostFactors(f5_vehicle=0, f5_engine=0, f8=0.86, f11=1.0, fv=0.6, fc=0.85, p=0.85)


####### INPUTS #######
launch_vehicle = ariane5ECA
launch_vehicle_cost_factors = ariane5_cost_factors
launch_vehicle_element_map = ariane5ECA_element_map
total_num_launches = 120
fleet_size = total_num_launches
sum_QN = 1.6
M_rec = 0
ops_cost_factors = ariane5_ops_cost_factors

launch_nums_list = [60]
prod_nums = [60]

num_crew = 0
mission_duration = 0

cost_LH2 = 2.7623 * 10 ** (-5) # [units: WYr/kg]
cost_LOX = 8.1019 * 10 ** (-7) # [units: WYr/kg]
cost_MMH = 0.0013117 # [units: WYr/kg]
cost_N2O4 = 3.3951 * 10 ** (-4) # [units: WYr/kg]

stage1_props_cost = 22777 * 1.85 * cost_LH2 + 141222 * 1.6 * cost_LOX
stage2_props_cost = 3180 * cost_MMH + 6520 * cost_N2O4

props_gasses_cost = stage1_props_cost + stage2_props_cost
# print(props_gasses_cost)

ground_transport_cost = 0 # [units: WYr]
insurance = 1.5 # [units: WYr]
fees = 0

launch_provider_type = 'A'
# indirect_ops = indirect_ops_cost(6, launch_provider_type) # [WYr]

profit_multiplier = 1.0

# launch_rate = 6

cpf_v_launch_rate = []
cpf_v_launch_rate_2010avg = []

launch_rate_range = range(3,13)

def run():

### P1 Production Batch
    P1_prod_nums = range(1, 15)
    avg_prod_cost_P1 = ariane5G.average_vehicle_production_cost(ariane5_cost_factors, P1_prod_nums, ariane5G_element_map)
    print('P1 Average Production Cost: ', avg_prod_cost_P1)

    for launch_rate in launch_rate_range:

        ####### COSTS #######
        dev_cost = 0 #launch_vehicle.vehicle_development_cost(launch_vehicle_cost_factors, launch_vehicle_element_map)

        avg_prod_cost1 = launch_vehicle.average_vehicle_production_cost(launch_vehicle_cost_factors, prod_nums, launch_vehicle_element_map)
        # print(avg_prod_cost)
        # fleet_prod_cost = fleet_size * avg_prod_cost
        avg_prod_cost2 = launch_vehicle.average_vehicle_production_cost(launch_vehicle_cost_factors, prod_nums, launch_vehicle_element_map)

        ground_ops_cost = launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, launch_nums_list)
        # print(ground_ops_cost)
        mission_ops_cost = launch_vehicle.flight_mission_ops_cost(sum_QN, launch_rate, ops_cost_factors, launch_nums_list)
        # print(mission_ops_cost)

        direct_ops = ground_ops_cost + mission_ops_cost + props_gasses_cost + fees + insurance

        indirect_ops = indirect_ops_cost(launch_rate, launch_provider_type)

        cost_per_flight = avg_prod_cost1 + direct_ops + indirect_ops + dev_cost/total_num_launches
        cost_per_flight_2010avg = avg_prod_cost2 + direct_ops + indirect_ops + dev_cost/total_num_launches
        
        price_per_flight = profit_multiplier * cost_per_flight

        cpf_v_launch_rate.append(price_per_flight)
        cpf_v_launch_rate_2010avg.append(cost_per_flight_2010avg)

    f1 = plt.figure(1)
    plt.scatter(launch_rate_range, cpf_v_launch_rate)
    plt.xlabel('Launch Rate [LpA]')
    plt.ylabel('Cost per Flight [WYr]')
    plt.title('CpF, Launch 60')

    """f2 = plt.figure(2)
    plt.scatter(launch_rate_range, cpf_v_launch_rate_2010avg)
    plt.xlabel('Launch Rate [LpA]')
    plt.ylabel('Cost per Flight [WYr]')
    plt.title('CpF, 2010 Average')"""

    plt.show()

    # print 'CpF + amortization: ' + str(cost_per_flight)
    """
    launch_rate = 6

    dev_cost = launch_vehicle.vehicle_development_cost(launch_vehicle_cost_factors, launch_vehicle_element_map)

    avg_prod_cost = launch_vehicle.average_vehicle_production_cost(launch_vehicle_cost_factors, prod_nums, launch_vehicle_element_map)
    print(avg_prod_cost)
        # fleet_prod_cost = fleet_size * avg_prod_cost

    ground_ops_cost = launch_vehicle.preflight_ground_ops_cost(launch_rate, ops_cost_factors, launch_nums_list)
    mission_ops_cost = launch_vehicle.flight_mission_ops_cost(sum_QN, launch_rate, ops_cost_factors, launch_nums_list)


    direct_ops = ground_ops_cost + mission_ops_cost + props_gasses_cost + fees + insurance

    indirect_ops = indirect_ops_cost(launch_rate, launch_provider_type)

    cpf_v_num_launces = []

    total_launch_nums_list = range(10, 200, 10)

    for total_num_launches in total_launch_nums_list:

        cost_per_flight = avg_prod_cost + direct_ops + indirect_ops + dev_cost/total_num_launches

        price_per_flight = profit_multiplier * cost_per_flight

        cpf_v_num_launces.append(price_per_flight)

    f2 = plt.figure(2)
    plt.scatter(total_launch_nums_list, cpf_v_num_launces)
    plt.xlabel('Total Number of Launches in Program')
    plt.ylabel('Cost per Flight [WYr]')

    plt.show()
    """
if __name__ == '__main__':
    run()