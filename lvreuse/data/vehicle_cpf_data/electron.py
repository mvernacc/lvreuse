"""Cost per flight model for Electron rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import os.path
from lvreuse.cost.tools import cost_reduction_factor
from lvreuse.cost.elements import ExpendableBallisticStageStorable, ModernTurboFed
from lvreuse.cost.vehicle import LaunchVehicle
from lvreuse.cost.indirect_ops import indirect_ops_cost

core = ExpendableBallisticStageStorable("s1", 950 - 9 * 35) # stage - 9 engines, from spacelaunchreport
core_engine = ModernTurboFed("e1", 35) # 
stage2 = ExpendableBallisticStageStorable("s2", 250 + 44 - 35) # stage + fairing - engine, from spacelaunchreport, rocketlabs
stage2_engine = ModernTurboFed("e2", 35) # 

electron_elements = [core, core_engine, stage2, stage2_engine]
electron = LaunchVehicle(name='Electron', M0=13.0, N=2, element_list=electron_elements) # mass from rocketlabs
electron_engines_dict = {'e1': 9, 'e2': 1}
electron_f8_dict = {'s1': 1.0, 'e1': 1.0, 's2': 1.0, 'e2': 1.0, 'veh': 1.0}
electron_uncertainty_list = [
    rdm.TriangularUncertainty('p_s1', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_e1', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_s2', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_e2', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    rdm.TriangularUncertainty('f9_veh', min_value=1.01, mode_value=1.02, max_value=1.03),
    rdm.TriangularUncertainty('f11_s1', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_e1', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_s2', min_value=0.45, mode_value=0.5, max_value=0.55),
    rdm.TriangularUncertainty('f11_e2', min_value=0.45, mode_value=0.5, max_value=0.55)
]

electron_prod_nums = range(1, 4)