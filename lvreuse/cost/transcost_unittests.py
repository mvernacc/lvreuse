import math
import unittest
import os.path
from lvreuse.cost.tools import cost_reduction_factor
from lvreuse.cost.elements import SolidRocketMotor, CryoLH2TurboFed, ExpendableBallisticStageLH2, \
    SolidPropellantBooster, ExpendableBallisticStageStorable, StorablePressureFed
from lvreuse.cost.vehicle import LaunchVehicle
from lvreuse.cost.CER_values import CERValues
from lvreuse.cost.cost_factors import ElementCostFactors, VehicleCostFactors, OperationsCostFactors

class TestElementClass(unittest.TestCase):

    def test_element_instantiation(self):
        SRM = SolidRocketMotor("test", 100)
        self.assertEqual(SRM.name, "test")
        self.assertEqual(SRM.m, 100)
        self.assertEqual(SRM.dev_a, 16.8)

    def test_SSME_dev(self):
        SSME = CryoLH2TurboFed("ssme", 3180)
        SSME_CER_vals = CERValues(SSME.dev_a, SSME.dev_x, SSME.prod_a, SSME.prod_x)
        SSME_cost_factors = ElementCostFactors(f1=1.30, f2=1.22, f3=0.85, f8=1.0, f10=1.0, f11=1.0, p=0.9)
        SSME_dev_cost = SSME.element_development_cost(SSME_CER_vals, SSME_cost_factors)
        self.assertAlmostEqual(SSME_dev_cost, 17921, delta=1)

    def test_saturn2_prod(self):
        saturn2 = ExpendableBallisticStageLH2("saturn2", 34475)
        saturn2_CER_vals = CERValues(saturn2.dev_a, saturn2.dev_x, saturn2.prod_a, saturn2.prod_x)
        saturn2_cost_factors = ElementCostFactors(f1=1.0, f2=1.0, f3=1.0, f8=1.0, f10=1.0, f11=1.0, p=0.96)
        saturn2_prod_nums = range(11, 16)
        saturn2_prod_cost = saturn2.average_element_production_cost(saturn2_CER_vals, saturn2_cost_factors, saturn2_prod_nums)
        self.assertAlmostEqual(saturn2_prod_cost, 752.2, delta=1)
        

class TestVehicleClass(unittest.TestCase):

    def setUp(self):

        self.SRB = SolidPropellantBooster("SRB", 39300)
        self.SRB_CER_vals = CERValues(self.SRB.dev_a, self.SRB.dev_x, self.SRB.prod_a, self.SRB.prod_x)
        self.SRB_cost_factors = ElementCostFactors(f1=1.1, f2=1.0, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

        self.core_vehicle = ExpendableBallisticStageLH2("core_vehicle", 13610)
        self.core_veh_CER_vals = CERValues(self.core_vehicle.dev_a, self.core_vehicle.dev_x, self.core_vehicle.prod_a, self.core_vehicle.prod_x)
        self.core_veh_cost_factors = ElementCostFactors(f1=1.1, f2=1.16, f3=0.85, f8=0.86, f10=1.0, f11=1.0, p=0.9)

        self.vulcain_engine = CryoLH2TurboFed("vulcain_engine", 1685)
        self.vulcain_engine_CER_vals = CERValues(self.vulcain_engine.dev_a, self.vulcain_engine.dev_x, self.vulcain_engine.prod_a, self.vulcain_engine.prod_x)
        self.vulcain_engine_cost_factors = ElementCostFactors(f1=1.1, f2=0.79, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

        self.stage2 = ExpendableBallisticStageStorable("stage2", 2500)
        self.stage2_CER_vals = CERValues(self.stage2.dev_a, self.stage2.dev_x, self.stage2.prod_a, self.stage2.prod_x)
        self.stage2_cost_factors = ElementCostFactors(f1=0.9, f2=1.09, f3=0.9, f8=0.86, f10=1.0, f11=1.0, p=0.9)

        self.aestus_engine = StorablePressureFed("aestus_engine", 119)
        self.aestus_engine_CER_vals = CERValues(self.aestus_engine.dev_a, self.aestus_engine.dev_x, self.aestus_engine.prod_a, self.aestus_engine.prod_x)
        self.aestus_engine_cost_factors = ElementCostFactors(f1=0.8, f2=1.0, f3=0.8, f8=0.77, f10=1.0, f11=1.0, p=0.9)

        ariane5_element_list = [self.SRB, self.core_vehicle, self.vulcain_engine, self.stage2, self.aestus_engine]
        self.ariane5 = LaunchVehicle("ariane5", 777, 4, ariane5_element_list)

        self.ariane5_element_map = {"SRB":[self.SRB_CER_vals, self.SRB_cost_factors, 2],
                                "core_vehicle":[self.core_veh_CER_vals, self.core_veh_cost_factors, 1],
                                "vulcain_engine":[self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors, 1],
                                "stage2":[self.stage2_CER_vals, self.stage2_cost_factors, 1],
                                "aestus_engine":[self.aestus_engine_CER_vals, self.aestus_engine_cost_factors, 1]}

        self.ariane5_cost_factors = VehicleCostFactors(f0_dev=1.04**3, f0_prod=1.025, f6=1.0, f7=1.0, f8=0.86, f9=1.07, p=0.9)

        self.ariane_prod_nums = [1]
        self.ariane_prod_nums3 = [1, 2, 3]
        
        self.ariane5_ops_cost_factors = OperationsCostFactors(f5_dict={}, f8=0.86, f11=1.0, fv=0.9, fc=0.85, p=0.9)
        self.launch_rate = 7
        self.launch_nums_list = range(1,10)

        self.ariane5_sum_QN = 1.6

    def test_element_dev_costs(self):

        SRB_dev_cost = self.SRB.element_development_cost(self.SRB_CER_vals, self.SRB_cost_factors)
        self.assertAlmostEqual(SRB_dev_cost, 5025, delta=1)

        core_veh_dev_cost = self.core_vehicle.element_development_cost(self.core_veh_CER_vals, self.core_veh_cost_factors)
        self.assertAlmostEqual(core_veh_dev_cost, 18092, delta=1)

        vulcain_engine_dev_cost = self.vulcain_engine.element_development_cost(self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors)
        self.assertAlmostEqual(vulcain_engine_dev_cost, 6592, delta=1)

        stage2_dev_cost = self.stage2.element_development_cost(self.stage2_CER_vals, self.stage2_cost_factors)
        self.assertAlmostEqual(stage2_dev_cost, 5750, delta=1)

        aestus_engine_dev_cost = self.aestus_engine.element_development_cost(self.aestus_engine_CER_vals, self.aestus_engine_cost_factors)
        self.assertAlmostEqual(aestus_engine_dev_cost, 438, delta=1)

    def test_vehicle_dev_cost(self):

        ariane5_dev_cost = self.ariane5.vehicle_development_cost(self.ariane5_cost_factors, self.ariane5_element_map)
        self.assertAlmostEqual(ariane5_dev_cost, 40379, delta=5)

    def test_element_prod_cost(self):

        SRB_prod_cost = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, self.ariane_prod_nums)
        self.assertAlmostEqual(SRB_prod_cost, 155, delta=1)

        SRB_prod_cost2 = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [1,2])
        self.assertAlmostEqual(SRB_prod_cost2, 147, delta=1)

        core_veh_prod_cost = self.core_vehicle.average_element_production_cost(self.core_veh_CER_vals, self.core_veh_cost_factors, self.ariane_prod_nums)
        self.assertAlmostEqual(core_veh_prod_cost, 435, delta=1)

        vulcain_engine_prod_cost = self.vulcain_engine.average_element_production_cost(self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors, self.ariane_prod_nums)
        self.assertAlmostEqual(vulcain_engine_prod_cost, 144, delta=1)

        stage2_prod_cost = self.stage2.average_element_production_cost(self.stage2_CER_vals, self.stage2_cost_factors, self.ariane_prod_nums)
        self.assertAlmostEqual(stage2_prod_cost, 110, delta=1)

        aestus_engine_prod_cost = self.aestus_engine.average_element_production_cost(self.aestus_engine_CER_vals, self.aestus_engine_cost_factors, self.ariane_prod_nums)
        self.assertAlmostEqual(aestus_engine_prod_cost, 19, delta=1)

    def test_vehicle_prod_cost(self):

        ariane5_TFU_prod_cost = self.ariane5.average_vehicle_production_cost(self.ariane5_cost_factors, self.ariane_prod_nums, self.ariane5_element_map)
        self.assertAlmostEqual(ariane5_TFU_prod_cost, 1183, delta=1)

    def test_vehicle_prod_cost3(self):

        ariane5_first3_prod_cost = self.ariane5.average_vehicle_production_cost(self.ariane5_cost_factors, self.ariane_prod_nums3, self.ariane5_element_map)
        
        # vehicle1
        SRB_prod_cost = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [1])
        SRB_prod_cost2 = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [2])
        core_veh_prod_cost = self.core_vehicle.average_element_production_cost(self.core_veh_CER_vals, self.core_veh_cost_factors, [1])
        vulcain_engine_prod_cost = self.vulcain_engine.average_element_production_cost(self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors, [1])
        stage2_prod_cost = self.stage2.average_element_production_cost(self.stage2_CER_vals, self.stage2_cost_factors, [1])
        aestus_engine_prod_cost = self.aestus_engine.average_element_production_cost(self.aestus_engine_CER_vals, self.aestus_engine_cost_factors, [1])

        vehicle1_cost = SRB_prod_cost + SRB_prod_cost2 + core_veh_prod_cost + vulcain_engine_prod_cost + stage2_prod_cost + aestus_engine_prod_cost

        #vehicle2
        SRB_prod_cost = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [3])
        SRB_prod_cost2 = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [4])
        core_veh_prod_cost = self.core_vehicle.average_element_production_cost(self.core_veh_CER_vals, self.core_veh_cost_factors, [2])
        vulcain_engine_prod_cost = self.vulcain_engine.average_element_production_cost(self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors, [2])
        stage2_prod_cost = self.stage2.average_element_production_cost(self.stage2_CER_vals, self.stage2_cost_factors, [2])
        aestus_engine_prod_cost = self.aestus_engine.average_element_production_cost(self.aestus_engine_CER_vals, self.aestus_engine_cost_factors, [2])

        vehicle2_cost = SRB_prod_cost + SRB_prod_cost2 + core_veh_prod_cost + vulcain_engine_prod_cost + stage2_prod_cost + aestus_engine_prod_cost

        SRB_prod_cost = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [5])
        SRB_prod_cost2 = self.SRB.average_element_production_cost(self.SRB_CER_vals, self.SRB_cost_factors, [6])
        core_veh_prod_cost = self.core_vehicle.average_element_production_cost(self.core_veh_CER_vals, self.core_veh_cost_factors, [3])
        vulcain_engine_prod_cost = self.vulcain_engine.average_element_production_cost(self.vulcain_engine_CER_vals, self.vulcain_engine_cost_factors, [3])
        stage2_prod_cost = self.stage2.average_element_production_cost(self.stage2_CER_vals, self.stage2_cost_factors, [3])
        aestus_engine_prod_cost = self.aestus_engine.average_element_production_cost(self.aestus_engine_CER_vals, self.aestus_engine_cost_factors, [3])

        vehicle3_cost = SRB_prod_cost + SRB_prod_cost2 + core_veh_prod_cost + vulcain_engine_prod_cost + stage2_prod_cost + aestus_engine_prod_cost

        vehicle_avg = (vehicle1_cost + vehicle2_cost + vehicle3_cost)/3. * self.ariane5_cost_factors.f0_prod**self.ariane5.N * self.ariane5_cost_factors.f9

        self.assertAlmostEqual(ariane5_first3_prod_cost, vehicle_avg, delta=1)

    def test_preflight_ground_ops_cost(self):

        ariane5_preflight_ops_cost = self.ariane5.preflight_ground_ops_cost(self.launch_rate, self.ariane5_ops_cost_factors, self.launch_nums_list)
        self.assertAlmostEqual(ariane5_preflight_ops_cost, 169, delta=1)

    def test_flight_mission_ops_cost(self):

        ariane5_mission_ops_cost = self.ariane5.flight_mission_ops_cost(self.ariane5_sum_QN, self.launch_rate, self.ariane5_ops_cost_factors, self.launch_nums_list)
        self.assertAlmostEqual(ariane5_mission_ops_cost, 6.3, delta=0.1)

    def test_recovery_ops_cost(self):

        ariane5_booster_rec_cost = self.ariane5.recovery_ops_cost(37, self.launch_rate, self.ariane5_ops_cost_factors)
        self.assertAlmostEqual(ariane5_booster_rec_cost, 8.7, delta=0.1)

if __name__ == '__main__':
    unittest.main()
