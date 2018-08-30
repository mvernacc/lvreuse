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
atlasV_f8_dict = {'s1': 1.0, 'e1': 1.49, 's2': 1.0, 'e2': 1.0, 'veh': 1.0, 'ops': 1.0}
atlas_uncertainty_list = [
    rdm.TriangularUncertainty('p_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('p_e2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f0_prod_veh', min_value=1.02, mode_value=1.025, max_value=1.03),
    rdm.TriangularUncertainty('f9_veh', min_value=1.05, mode_value=1.08, max_value=1.15),
    rdm.TriangularUncertainty('f10_s1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e1', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_s2', min_value=0.75, mode_value=0.8, max_value=0.85),
    rdm.TriangularUncertainty('f10_e2', min_value=0.75, mode_value=0.8, max_value=0.85)
]

atlas_ops_uncertainty_list = [
    rdm.TriangularUncertainty('launch_rate', min_value=5, mode_value=7, max_value=9),
    rdm.TriangularUncertainty('p_ops', min_value=0.8, mode_value=0.85, max_value=0.9),
    rdm.TriangularUncertainty('insurance', min_value=1, mode_value=2, max_value=3),
]

atlas_dev_uncertainty_list = [
    rdm.TriangularUncertainty('f1_s1', min_value=0.6, mode_value=0.7, max_value=0.8), # wikipedia, 1st stage was modified from Atlas III
    rdm.TriangularUncertainty('f1_e1', min_value=0.0, mode_value=0.0, max_value=0.01), # engines previously used on Atlas III
    rdm.TriangularUncertainty('f1_s2', min_value=0.6, mode_value=0.7, max_value=0.8), # elongation of Atlas II Centaur
    rdm.TriangularUncertainty('f1_e2', min_value=0.3, mode_value=0.4, max_value=0.5), # modification of older RL-10 designs
    rdm.TriangularUncertainty('f2_s1', min_value=0.9, mode_value=1.0, max_value=1.1), # guess
    rdm.TriangularUncertainty('f2_e1', min_value=0.72, mode_value=0.78, max_value=0.84), # based on 238 firings, from incorporation-of-rd-180-failure-response-2011
    rdm.TriangularUncertainty('f2_s2', min_value=0.9, mode_value=1.0, max_value=1.1), # guess
    rdm.TriangularUncertainty('f2_e2', min_value=1.35, mode_value=1.42, max_value=1.46), # based on 1600 qual firings, from transcost
    rdm.TriangularUncertainty('f3_s1', min_value=0.7, mode_value=0.8, max_value=0.9), # team had previous experience with other variants
    rdm.TriangularUncertainty('f3_e1', min_value=0.7, mode_value=0.8, max_value=0.9),
    rdm.TriangularUncertainty('f3_s2', min_value=0.7, mode_value=0.8, max_value=0.9),
    rdm.TriangularUncertainty('f3_e2', min_value=0.7, mode_value=0.8, max_value=0.9),
    rdm.TriangularUncertainty('f0_dev_veh', min_value=1.03**2, mode_value=1.04**2, max_value=1.05**2),
    rdm.TriangularUncertainty('num_program_flights', min_value=100, mode_value=120, max_value=140),
    rdm.TriangularUncertainty('profit_multiplier', min_value=1.05, mode_value=1.07, max_value=1.09),
]

atlas_prod_nums = range(68, 79)
atlas_launch_nums = atlas_prod_nums
atlas_fv = 0.9
atlas_fc = 0.85
atlas_sum_QN = 0.8
atlas_launch_provider_type = 'B'

atlas_props_dict = {'RP-1': 76370, 'LOX': (207729 + 17625) * 1.6, 'LH2': 3204 * 1.85} # including boil-off

reference_cpf = 314