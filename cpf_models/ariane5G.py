"""Cost per flight model for Ariane 5G rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import sys
import os
sys.path.append(os.path.abspath('..'))
from tools import cost_reduction_factor
from elements import SolidRocketMotor, CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    SolidPropellantBooster, ExpendableBallisticStageStorable, StorablePressureFed
from vehicle import LaunchVehicle

SRB = SolidPropellantBooster("b1", 39800) # data from Isakowitz p. 31
core_vehicle = ExpendableBallisticStageLH2("s1", 12200 - 1300) # data from Isakowitz, less engine
vulcain_engine = CryoLH2TurboFed("e1", 1300)
stage2 = ExpendableBallisticStageStorable("s2", 1200 + 1500 + 2025 + 716 - 111) # data from Isakowitz, including VEB, short fairing, SPELTRA, less engine
aestus_engine = StorablePressureFed("e2", 111) 

ariane5_element_list =  [SRB, core_vehicle, vulcain_engine, stage2, aestus_engine]

ariane5G = LaunchVehicle(name="ariane5G", M0=746, N=4, element_list=ariane5_element_list)
ariane_engines_dict = {'e1': 1, 'e2': 1, 'b1': 2}
ariane_f8_dict = {'s1': 0.86, 'e1': 0.86, 's2':0.86, 'e2': 0.77, 'b1': 0.86, 'veh': 0.86, 'ops': 0.86}

ariane_uncertainty_list = [
    rdm.TriangularUncertainty('p_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_b1', min_value=0.8, mode_value=0.85, max_value=0.9),
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    rdm.TriangularUncertainty('f9_veh', min_value=1.05, mode_value=1.08, max_value=1.15),
]

ariane_ops_uncertainty_list = [
    rdm.TriangularUncertainty('launch_rate', min_value=5, mode_value=6, max_value=7),
    rdm.TriangularUncertainty('p_ops', min_value=0.8, mode_value=0.85, max_value = 0.9),
    rdm.TriangularUncertainty('insurance', min_value=1, mode_value=2, max_value=3),
]

ariane_prod_nums_list = range(89, 100)
ariane_launch_nums_list = ariane_prod_nums_list
ariane_fv = 0.6
ariane_fc = 0.85
ariane_sum_QN = 1.6
ariane_launch_provider_type = 'A'

ariane_props_dict = {'LH2': 22777 * 1.85, 'LOX': 141222 * 1.6, 'MMH': 3180, 'N2O4': 6520}