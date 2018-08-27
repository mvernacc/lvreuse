class LaunchVehicleStage(object):

    def __init__(self, name, element_list):
        self.name = name
        self.element_list = element_list


    def stage_development_cost(self, element_map):

        """Find total developemnt cost for the launch vehicle stage.

        Arguments:
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_values, 
                element_cost_factors, num_elements_per_vehicle]}

        Returns:
            Launch vehicle stage development cost [units: work-year]"""

        stage_dev_cost = 0
        for element in self.element_list:
            CER_vals, element_cost_factors, n = element_map[element.name]
            element_dev_cost = element.element_development_cost(CER_vals, element_cost_factors)
            stage_dev_cost += element_dev_cost

        return stage_dev_cost

    def average_stage_production_cost(self, stage_prod_nums_list, element_map):
        """Find the average stage production cost for a given set of unit production numbers.

        Arguments:
            stage_prod_nums_list: list of consecutive stage production numbers to consider
            element_map: dictionary mapping element names to CER values, element-specific cost factors, 
                and number of identical elements per vehicle i.e. {element_name: [CER_vals, 
                element_cost_factors, num_elements_per_vehicle]}

        Returns:
            Average stage production cost [units: work-year]"""

        sum_prod_cost = 0
        for element in self.element_list:
            CER_vals, element_cost_factors, n = element_map[element.name]
            element_prod_nums_list = range(stage_prod_nums_list[0] * n - n + 1,
                                           stage_prod_nums_list[-1] * n + 1)
            element_prod_cost = element.average_element_production_cost(CER_vals, element_cost_factors, element_prod_nums_list)
            sum_prod_cost += n * element_prod_cost

        num_stages = len(stage_prod_nums_list)
        avg_vehicle_prod_cost = (1./num_stages) * vehicle_cost_factors.f0_prod**self.N * sum_prod_cost * \
                                    vehicle_cost_factors.f9
        return avg_vehicle_prod_cost

    def stage_mass(self):

        mass = 0

        for element in self.element_list:
            mass += element.m

        return mass

    def stage_prop_cost(self):

        pass