class ElementCostFactors(object):

    def __init__(self, f1, f2, f3, f8, f10, f11, p):
        """Describes vehicle element-specific cost factors for a particular vehicle element.

        Arguments:
            f1 (positive scalar): development standard factor as defined by TRANSCOST 8.2 p. 34
                    [units: dimensionless]. Probably in range of 0.4 - 1.4.
            f2 (positive scalar): technical quality factor as defined by TRANSCOST 8.2 p. 35
                    [units: dimensionless]. 
            f3 (positive scalar): team experience factor as defined by TRANSCOST 8.2 p. 35
                    [units: dimensionless]. Probably in the range of 0.5 - 1.4.
            f8 (positive scalar): country productivity correction factor as defined by TRANSCOST 8.2 p. 25
                    [units: dimensionless].
            f10 (positive scalar): cost reduction factor by past eperience, technical progress and
                    application of cost engineering [units: dimensionless]. Probably in the range of 
                    0.75 - 1.0.
            f11 (positive scalar): cost reduction factor by independent development without government 
                    contracts' requirements and customer interference [units: dimensionless]. Probably
                    in the range of 0.45 - 0.55 for applicable development efforts.
            p (positive scalar): learning factor for series production [units: dimensionless]. p <= 1
            """

        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f8 = f8
        self.f10 = f10
        self.f11 = f11
        self.p = p

class VehicleCostFactors(object):

    def __init__(self, f0_dev, f0_prod, f6, f7, f8, f9, p):
        """Describes vehicle-specific cost factors for a particular launch vehicle.

        Arguments:
            f0_dev (positive scalar): systems engineering/integration factor for vehicle development 
                    [units: dimensionless]. f0_dev >= 1
            f0_prod (positive scalar): system management factor for vehicle production 
                    [units: dimensionless]. f0_prod >= 1
            f6 (positive scalar): cost growth factor for deviation from the optimum time schedule
            f7 (positive scalar): cost growth factor for development by parallel contractors
            f8 (positive scalar): country productivity correction factor as defined by TRANSCOST 8.2 p. 25
                    [units: dimensionless].
            f9 (positive scalar): subcontractor cost factor [units: dimensionless]. 
            p (positive scalar): learning factor for series production [units: dimensionless]. p <= 1
            """

        self.f0_dev = f0_dev
        self.f0_prod = f0_prod
        self.f6 = f6
        self.f7 = f7
        self.f8 = f8
        self.f9 = f9
        self.p = p

class OperationsCostFactors(object):

    def __init__(self, f5_dict, f8, f11, fv, fc, p):
        """Describes operations-specific cost factors for vehicle operation.

        Arguments:
            f5_dict (positive scalar): dictionary mapping element names to their corresponding vehicle
                refurbishment cost factor (if applicable), i.e. {element_name: refurb_cost_factor}.
            f8 (positive scalar): country productivity correction factor as defined by TRANSCOST 8.2 p. 25
                    [units: dimensionless].
            f11 (positive scalar): cost reduction factor by independent development without government 
                    contracts' requirements and customer interference [units: dimensionless]. Probably
                    in the range of 0.45 - 0.55 for applicable development efforts. 
            fv (positive scalar): cost factor for impact of launch vehicle type [units: dimensionless].
            fc (positive scalar): cost factor for impact of assembly and integration mode 
                    [units: dimensionless].
            p (positive scalar): learning factor for series production [units: dimensionless]. p <= 1
            """

        self.f5_dict = f5_dict
        self.f8 = f8
        self.f11 = f11
        self.fv = fv
        self.fc = fc
        self.p = p
