"""Create launch vehicle elements and launch vehicle."""

import math
from tools import cost_reduction_factor

class LaunchVehicle(object):

    def __init__(self, name, M0, N, element_list):
        """Characterization of total launch vehicle.

        Arguments:
            name (string): identifying name or tag for launch vehicle element
            M0 (positive scalar): gross lift-off weight of launch vehicle [units: Mg]
            N (positive scalar): number of stages or major vehicle elements. Large segmented boosters count
                as a stage, small kick-stages or attached boosters count as half.
            element_list: a list containing instances of LaunchVehicleElement class that
                characterize the launch vehicle"""

        self.name = name
        self.M0 = M0
        self.N = N
        self.element_list = element_list

    def vehicle_development_cost(self, vehicle_cost_factors, element_map):
        """Find total developemnt cost for the launch vehicle.

        Arguments:
            vehicle_cost_factors: instance of VehicleCostFactors class describing the vehicle-specific cost factors
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_values, 
                element_cost_factors, num_elements_per_vehicle]}

        Returns:
            Launch vehicle development cost [units: work-year]"""

        dev_cost = 0
        for element in self.element_list:
            CER_vals, element_cost_factors, n = element_map[element.name]
            element_dev_cost = element.element_development_cost(CER_vals, element_cost_factors)
            dev_cost += element_dev_cost

        vehicle_dev_cost = vehicle_cost_factors.f0_dev * dev_cost * vehicle_cost_factors.f6 * vehicle_cost_factors.f7
        return vehicle_dev_cost

    def average_vehicle_production_cost(self, vehicle_cost_factors, vehicle_prod_nums_list, element_map):
        """Find the average vehicle production cost for a given set of unit production numbers.

        Arguments:
            vehicle_cost_factors: instance of VehicleCostFactors class describing the vehicle-specific cost factors
            vehicle_prod_nums_list: list of consecutive vehicle production numbers to consider
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_vals, 
                element_cost_factors, num_elements_per_vehicle]}

        Returns:
            Average vehicle production cost [units: work-year]"""

        sum_prod_cost = 0
        for element in self.element_list:
            CER_vals, element_cost_factors, n = element_map[element.name]
            element_prod_nums_list = range(vehicle_prod_nums_list[0] * n - n + 1,
                                           vehicle_prod_nums_list[-1] * n + 1)
            element_prod_cost = element.average_element_production_cost(CER_vals, element_cost_factors, element_prod_nums_list)
            sum_prod_cost += n * element_prod_cost

        avg_vehicle_prod_cost = vehicle_cost_factors.f0_prod**self.N * sum_prod_cost * \
                                    vehicle_cost_factors.f9
        return avg_vehicle_prod_cost 


    def preflight_ground_ops_cost(self, launch_rate, ops_cost_factors, launch_nums_list):
        """Find pre-flight ground operations costs.

        Arguments:
            launch_rate (positive scalar): launch rate [units: launches/year]
            ops_cost_factors: instance of OperationsCostFactors class describing the operations-specific cost fators
            launch_nums_list: list of consecutive flight numbers to evaluate

        Returns:
            Pre-flight ground oeperations cost [units: work-year]"""

        if launch_rate < 3:
            print("Warning: Pre-launch ground operations cost model is only valid for launch rates of 3 or more per year.")

        f4_avg = cost_reduction_factor(ops_cost_factors.p, launch_nums_list)
    
        C_ops = 8 * self.M0**0.67 * launch_rate**-0.9 * self.N**0.7 * ops_cost_factors.fv * ops_cost_factors.fc * \
                f4_avg * ops_cost_factors.f8 * ops_cost_factors.f11
        return C_ops

    def flight_mission_ops_cost(self, sum_QN, launch_rate, ops_cost_factors, launch_nums_list, num_crew=0, mission_duration=0):
        ##### TODO UPDATE
        """Find launch, flight, and mission operations cost.

        Arguments:
            sum_QN: TODO
            launch_rate (positive scalar): launch rate [units: launches/year]
            ops_cost_factors: instance of OperationsCostFactors class describing the operations-specific cost fators
            num_crew (positive integer): number of crew members on a crewed mission
            mission_duration (positive scalar): duration of a crewed mission [units: days]

        Returns:
            Total launch, flight, and mission operations cost [units: person-year]"""

        f4_avg = cost_reduction_factor(ops_cost_factors.p, launch_nums_list)

        C_m = 20 * sum_QN * launch_rate**-0.65 * f4_avg * ops_cost_factors.f8

        if num_crew > 0:
            C_ma = 75. * mission_duration**0.5 * num_crew**0.5 * launch_rate**-0.8 * f4_avg * ops_cost_factors.f8 * ops_cost_factors.f11
            C_m += C_ma

        return C_m

    def recovery_ops_cost(self, M_rec, launch_rate, ops_cost_factors):
        """Find recovery operations cost.

        Arguments:
            M_rec: recovery mass [units: Mg]
            launch_rate: launch rate [units: launches/year]
            ops_cost_factors: instance of OperationsCostFactors class describing the operations-specific cost fators

        Returns:
            Recovery operations cost [units: Work Year]"""

        C_rec = 1.5 / launch_rate * (7. * launch_rate**0.7 + M_rec**0.83) * ops_cost_factors.f8 * ops_cost_factors.f11

        return C_rec

    def vehicle_refurbishment_cost(self, ops_cost_factors, vehicle_cost_factors, element_map):
        """Find refurbishment cost for vehicle.

        Arguments:
            ops_cost_factors: instance of OperationsCostFactors class describing the operations-specific cost fators
            vehicle_cost_factors: instance of VehicleCostFactors class describing the vehicle-specific cost factors
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_vals, 
                element_cost_factors, num_elements_per_vehicle]}

        Returns:
            Vehicle refurbishment cost [units: Work Year]"""

        TFU = self.average_vehicle_production_cost(vehicle_cost_factors, [1], element_map)

        vehicle_refurb_cost = ops_cost_factors.f5_vehicle * TFU

        return vehicle_refurb_cost

    def engines_refurbishment_cost(self, ops_cost_factors, engine_element, element_map):
        """Find refurbishment cost for engine.

        Arguments:
            ops_cost_factors: instance of OperationsCostFactors class describing the operations-specific cost fators
            engine_element: instance of LaunchVehicleElement class or subclass describing the relavant engine
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_vals, 
                element_cost_factors, num_elements_per_vehicle]}            

        Returns:
            Engine refurbishment cost [units: Work Year]"""

        CER_vals, element_cost_factors, n = element_map[engine_element.name]
        TFU = engine_element.average_element_production_cost(CER_vals, element_cost_factors, [1])

        engines_refurb_cost = n * ops_cost_factors.f5_engine * TFU
        
        return engines_refurb_cost

    def total_refurbishment_cost(self):

        pass

    def indirect_operations_cost(self):

        pass
