"""Create class for storage of CER coefficient values."""

class CERValues(object):

    def __init__(self, dev_a, dev_x, prod_a, prod_x):
        """Characterization of CER coefficient values for a vehicle element.

        Arguments:
            dev_a (positive scalar): multiplier for development CER
            dev_x (positive scalar): exponent for development CER
            prod_a (positive scalar): multiplier for production CER
            prod_x (positive scalar): exponent for production CER."""

        self.dev_a = dev_a
        self.dev_x = dev_x
        self.prod_a = prod_a
        self.prod_x = prod_x
