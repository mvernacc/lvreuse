"""TRANSCOST Cost Exponential Relationship (CER) models."""

class LaunchVehicleElement():

    def __init__(self, dev_vals, prod_vals, m, f1=1.0, f3=1.0, f4=1.0, f8=1.0, f2=1.0):
        """Characterization of a system/element in a launch vehicle system.

        Arguments:
            m: vehicle element reference mass [units: kg].
            f1 (positive scalar): development standard factor as defined by TRANSCOST p. 31
                    [units: dimensionless]. Probably in range of 0.4 - 1.4.
            f2 (positive scalar): technical qualify factor as defined by TRANSCOST p. 40
                    [units: dimensionless]. Probably in the range of 0.5 - 1.4.
            f3 (positive scalar): team experience factor as defined by TRANSCOST p. 32
                    [units: dimensionless]. Probably in range of 0.7 - 1.4.
            """

        self.dev_vals = dev_vals
        self.dev_a = dev_vals.a
        self.dev_x = dev_vals.x
        self.prod_vals = prod_vals
        self.prod_a = prod_vals.a
        self.prod_x = prod_vals.x
        self.m = m
        self.f1 = f1
        self.f3 = f3
        self.f4 = f4
        self.f8 = f8
        self.f2 = f2

    def element_development_cost(self):

        dev_cost = self.f1*self.f2*self.f3*self.f8*self.dev_a*self.m**self.dev_x
        return dev_cost

    def element_production_cost(self):
        pass

class LaunchVehicle():

    def __init__(self, element_list, f0=1.0):
        self.element_list = element_list
        self.f0 = f0

    def vehicle_development_cost(self):

        dev_cost = 0
        for element in self.element_list:
            element_dev_cost = element.element_development_cost()
            dev_cost += element_dev_cost

        vehicle_dev_cost = self.f0*dev_cost
        return vehicle_dev_cost       
