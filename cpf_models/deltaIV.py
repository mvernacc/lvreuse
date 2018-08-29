"""Cost per flight model for Delta IV rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import sys
import os
sys.path.append(os.path.abspath('..'))
from tools import cost_reduction_factor
from elements import ExpendableBallisticStageStorable, ModernTurboFed, ExpendableBallisticStageLH2, CryoLH2TurboFed
from vehicle import LaunchVehicle

core = ExpendableBallisticStageLH2("s1", 26760 - 6600) # stage + interstage - engine , from Isakowitz,
core_engine = ModernTurboFed("e1", 6600) # RS-68, from Wikipedia
stage2 = ExpendableBallisticStageLH2("s2", 2850 + 1677 - 277) # stage + fairing - engine, from Isakowitz
stage2_engine = CryoLH2TurboFed("e2", 277) # RL-10B-2, from Wikipedia

delta_elements = [core, core_engine, stage2, stage2_engine]

deltaIV_medium = LaunchVehicle(name='deltaIV_medium', M0=1257, N=2, element_list=delta_elements) # mass from Isakowitz
delta_engines_dict = {'e1': 1, 'e2': 1}
delta_f8_dict = {'s1': 1.0, 'e1': 1.0, 's2': 1.0, 'e2': 1.0, 'veh': 1.0, 'ops': 1.0}
delta_uncertainty_list = [
    rdm.TriangularUncertainty('p_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    rdm.TriangularUncertainty('f9_veh', min_value=1.05, mode_value=1.08, max_value=1.15),
    rdm.TriangularUncertainty('f10_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
]

delta_ops_uncertainty_list = [
    rdm.TriangularUncertainty('launch_rate', min_value=3, mode_value=3.5, max_value=4),
    rdm.TriangularUncertainty('p_ops', min_value=0.8, mode_value=0.85, max_value=0.9),
    rdm.TriangularUncertainty('insurance', min_value=1, mode_value=2, max_value=3),
]

delta_prod_nums = range(27, 38)
delta_launch_nums = delta_prod_nums
delta_fv = 1.0
delta_fc = 0.85
delta_sum_QN = 0.8
delta_launch_provider_type = 'B'

delta_props_dict = {'LOX':(171086 +17261) * 1.6, 'LH2':(28514 + 3138) * 1.85}

