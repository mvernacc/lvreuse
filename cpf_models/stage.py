class LaunchVehicleStage(object):

    def __init__(self, name, element_list):
        self.name = name
        self.element_list = element_list


    def development_cost(self, element_map):

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

    def production_cost(self):

        pass

    def stage_mass(self):

        mass = 0

        for element in self.element_list:
            mass += element.m

        return mass

    def stage_prop_cost(self):

        pass