"""Cost per flight model for Atlas V 401 rocket."""
import math
import matplotlib.pyplot as plt
import rhodium as rdm
import sys
import os
sys.path.append(os.path.abspath('..'))
from tools import cost_reduction_factor
from elements import SolidRocketMotor, CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    SolidPropellantBooster, ExpendableBallisticStageStorable, StorableTurboFed
from vehicle import LaunchVehicle

core = ExpendableBallisticStageStorable("s1", 20743 + 420 + 375 - 5480) # CCB, data from Isakowitz, p. 77, includes core, booster and interstage adapter
core_engine = StorableTurboFed("e1", 5480) # RD-180
stage2 = ExpendableBallisticStageLH2("s2", 1914 + 2085 - 168) # centaur, data from Isakowitz, stage + short fairing - engine
stage2_engine = CryoLH2TurboFed("e2", 168) # RL-10A

atlas_elements = [core, core_engine, stage2, stage2_engine]

atlasV_401 = LaunchVehicle(name='AtlasV_401', M0=334.5, N=2, element_list=atlas_elements)
atlasV_engines_dict = {'e1': 1, 'e2': 1}
atlasV_f8_dict = {'s1': 1.0, 'e1': 1.49, 's2': 1.0, 'e2': 1.0, 'veh': 1.0}
atlas_uncertainty_list = [
    rdm.TriangularUncertainty('p_s1', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_e1', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_s2', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('p_e2', min_value=0.85, mode_value=0.9, max_value=0.95),
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    rdm.TriangularUncertainty('f9_veh', min_value=1.05, mode_value=1.08, max_value=1.15)
]

