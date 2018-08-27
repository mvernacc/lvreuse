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
import rhodium as rdm


SRB = SolidPropellantBooster("P230", 39800) # data from Isakowitz p. 31

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