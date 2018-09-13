"""Cost per flight model for Delta IV rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import os.path
from lvreuse.cost.tools import cost_reduction_factor
from lvreuse.cost.elements import ExpendableBallisticStageStorable, ModernTurboFed, ExpendableBallisticStageLH2, CryoLH2TurboFed
from lvreuse.cost.vehicle import LaunchVehicle
from lvreuse.cost.indirect_ops import indirect_ops_cost

core = ExpendableBallisticStageLH2("s1", 26760 - 6600) # stage + interstage - engine , from Isakowitz,
core_engine = ModernTurboFed("e1", 6600) # RS-68, from Wikipedia
stage2 = ExpendableBallisticStageLH2("s2", 2850 + 1677 - 277) # stage + fairing - engine, from Isakowitz
stage2_engine = CryoLH2TurboFed("e2", 277) # RL-10B-2, from Wikipedia

delta_elements = [core, core_engine, stage2, stage2_engine]

deltaIV_medium = LaunchVehicle(name='Delta IV Medium (4,0)', M0=257, N=2, element_list=delta_elements) # mass from Isakowitz
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
    rdm.TriangularUncertainty('launch_rate', min_value=3, mode_value=4, max_value=5),
    rdm.TriangularUncertainty('p_ops', min_value=0.8, mode_value=0.85, max_value=0.9),
    rdm.TriangularUncertainty('insurance', min_value=1, mode_value=2, max_value=3),
]

delta_dev_uncertainty_list = [
    rdm.TriangularUncertainty('f2_s1', min_value=0.9, mode_value=1.0, max_value=1.1), # guess
    rdm.TriangularUncertainty('f2_s2', min_value=0.9, mode_value=1.0, max_value=1.1), # guess
    rdm.TriangularUncertainty('f3_s1', min_value=1.0, mode_value=1.1, max_value=1.2), # transcost p. 111
    rdm.TriangularUncertainty('f3_e1', min_value=1.0, mode_value=1.1, max_value=1.2), # guess
    rdm.TriangularUncertainty('f3_s2', min_value=1.0, mode_value=1.1, max_value=1.2), # guess
    rdm.TriangularUncertainty('f3_e2', min_value=1.0, mode_value=1.1, max_value=1.2), # guess
    rdm.TriangularUncertainty('f0_dev_veh', min_value=1.03**2, mode_value=1.04**2, max_value=1.05**2),
    rdm.TriangularUncertainty('num_program_flights', min_value=100, mode_value=120, max_value=150),
    rdm.TriangularUncertainty('profit_multiplier', min_value=1.05, mode_value=1.07, max_value=1.09),
]

delta_prod_nums = range(27, 38)
delta_launch_nums = delta_prod_nums
delta_fv = 1.0
delta_fc = 0.85
delta_sum_QN = 0.8
delta_launch_provider_type = 'B'

delta_props_dict = {'O2':(171086 + 17261) * 1.6, 'H2':(28514 + 3138) * 1.85}

