class SystemProductionValues(object):

    def __init__(self, prod_a, prod_x):
        """Create a propellant properties object. 
        
        Args:
            prod_a (positive scalar): production CER model coefficient [units: kg**(-prod_x)]
            prod_x (positive scalar): production CER model exponent [units: dimensionless]"""

        self.prod_a = prod_a
        self.prod_x = prod_x