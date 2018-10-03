from lvreuse.cost.tools import cost_reduction_factor

class LaunchVehicleElement(object):

    def __init__(self, name, m):
        """General characterization of a system/element in a launch vehicle system.

        Arguments:
            name (string): identifying name or tag for launch vehicle element
            m: vehicle element reference mass [units: kg].
            """

        self.name = name
        self.m = m

    def element_development_cost(self, CER_vals, element_cost_factors):
        """Calculate development cost of vehicle element or system.

        Arguments: 
            CER_vals: instance of CERValues class describing the CER coefficient values
            element_cost_factors: instance of ElementCostFactors class describing element-specific
                cost factors

        Returns:
            Development cost of launch vehicle element [units: work-year]"""

        dev_cost = element_cost_factors.f1 * element_cost_factors.f2 * element_cost_factors.f3 * \
                    element_cost_factors.f8 * CER_vals.dev_a * self.m**CER_vals.dev_x
        return dev_cost

    def average_element_production_cost(self, CER_vals, element_cost_factors, element_prod_nums_list):
        """Calculate average production cost per vehicle element unit.

        Arguments:
            CER_vals: instance of CERValues class describing the CER coefficient values
            element_cost_factors: instance of ElementCostFactors class describing element-specific
                cost factors 
            element_prod_nums_list: list of consecutive vehicle element production numbers to consider

        Returns:
            Average production cost of launch vehicle element [units: person-year]."""

        f4_avg = cost_reduction_factor(element_cost_factors.p, element_prod_nums_list)

        avg_prod_cost = CER_vals.prod_a * self.m**CER_vals.prod_x * f4_avg * element_cost_factors.f8 * \
                        element_cost_factors.f10 * element_cost_factors.f11

        return avg_prod_cost


class ComplexElement(LaunchVehicleElement):
    """General characterization of element requiring additional cost factors for development cost"""

    def __init__(self, name, m):
        super(ComplexElement, self).__init__(name, m)

    def element_development_cost(self, CER_vals, element_cost_factors):

        dev_cost = element_cost_factors.f1 * element_cost_factors.f2 * element_cost_factors.f3 * \
                    element_cost_factors.f8 * element_cost_factors.f10 * element_cost_factors.f11 * \
                    CER_vals.dev_a * self.m**CER_vals.dev_x
        return dev_cost


class TurboFedEngine(LaunchVehicleElement):
    """General characterization of a turbo fed engine element."""

    def __init__(self, name, m):
        super(TurboFedEngine, self).__init__(name, m)

    def element_development_cost(self, CER_vals, element_cost_factors):

        dev_cost = element_cost_factors.f1 * element_cost_factors.f2 * element_cost_factors.f3 * \
                    element_cost_factors.f8 * CER_vals.dev_a * self.m**CER_vals.dev_x
        return dev_cost


class SolidRocketMotor(LaunchVehicleElement):

    def __init__(self, name, m):
        super(SolidRocketMotor, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [16.8, 0.54, 2.3, 0.412]
        self.dev_a_conf_int = [7.742346255021625, 30.026586675011707]
        self.dev_x_conf_int = [0.4772495, 0.62277953]
        self.prod_a_conf_int = [1.9209268723712933, 2.7710185782712706]
        self.prod_x_conf_int = [0.38625392, 0.43420692]


class SolidPropellantBooster(LaunchVehicleElement):

    def __init__(self, name, m):
        super(SolidPropellantBooster, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [19.5, 0.54, 2.3, 0.412]
        self.dev_a_conf_int = [19.5, 26.8] # [21.068, 26.8]
        self.dev_x_conf_int = [0.4772495, 0.62277953]
        self.prod_a_conf_int = [1.9209268723712933, 2.7710185782712706]
        self.prod_x_conf_int = [0.38625392, 0.43420692]


class SolidPropellantVehicleStage(LaunchVehicleElement):

    def __init__(self, name, m):
        super(SolidPropellantVehicleStage, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [22.4, 0.54, 2.75, 0.412]
        self.dev_a_conf_int = [12.823, 52.119]
        self.dev_x_conf_int = [0.4772495, 0.62277953]
        self.prod_a_conf_int = [2.288, 2.771]
        self.prod_x_conf_int = [0.38625392, 0.43420692]


class CryoLH2TurboFed(TurboFedEngine):

    def __init__(self, name, m):
        super(CryoLH2TurboFed, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [277., 0.48, 3.15, 0.535]
        self.dev_a_conf_int = [195.1340728668754, 389.01133900679804]
        self.dev_x_conf_int = [0.42853851, 0.52827748]
        self.prod_a_conf_int = [2.764, 4.128]
        self.prod_x_conf_int = [0.49908152, 0.57606891] # from StorableTurboFed


class StorableTurboFed(TurboFedEngine):

    def __init__(self, name, m):
        super(StorableTurboFed, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [277., 0.48, 1.9, 0.535]
        self.dev_a_conf_int = [195.1340728668754, 389.01133900679804]
        self.dev_x_conf_int = [0.42853851, 0.52827748]
        self.prod_a_conf_int = [1.438868469813962, 2.29113324341886]
        self.prod_x_conf_int = [0.49908152, 0.57606891]


class StorablePressureFed(LaunchVehicleElement):

    def __init__(self, name, m):
        super(StorablePressureFed, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [167., 0.35, 1.9, 0.535]
        self.dev_a_conf_int = [149.75335940452638, 181.67568396416385]
        self.dev_x_conf_int = [0.3273087, 0.37139749]
        self.prod_a_conf_int = [1.438868469813962, 2.29113324341886]
        self.prod_x_conf_int = [0.49908152, 0.57606891]


class ModernPressureFed(LaunchVehicleElement):

    def __init__(self, name, m):
        super(ModernPressureFed, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [167., 0.35, 1.2, 0.535]
        self.dev_a_conf_int = [149.75335940452638, 181.67568396416385]
        self.dev_x_conf_int = [0.3273087, 0.37139749]
        self.prod_a_conf_int = [0.729, 2.089]
        self.prod_x_conf_int = [0.49908152, 0.57606891]

    def average_element_production_cost(self, CER_vals, element_cost_factors, element_prod_nums_list):

        f4_avg = cost_reduction_factor(element_cost_factors.p, element_prod_nums_list)

        avg_prod_cost = CER_vals.prod_a * self.m**CER_vals.prod_x * f4_avg * \
                            element_cost_factors.f8 * element_cost_factors.f11
        return avg_prod_cost


class ModernTurboFed(TurboFedEngine):

    def __init__(self, name, m):
        super(ModernTurboFed, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [277., 0.48, 1.2, 0.535]
        self.dev_a_conf_int = [195.1340728668754, 389.01133900679804]
        self.dev_x_conf_int = [0.42853851, 0.52827748]
        self.prod_a_conf_int = [0.729, 2.089]
        self.prod_x_conf_int = [0.49908152, 0.57606891]

    def average_element_production_cost(self, CER_vals, element_cost_factors, element_prod_nums_list):

        f4_avg = cost_reduction_factor(element_cost_factors.p, element_prod_nums_list)

        avg_prod_cost = CER_vals.prod_a * self.m**CER_vals.prod_x * f4_avg * element_cost_factors.f8 * \
                        element_cost_factors.f11
        return avg_prod_cost


class TurboJetEngine(LaunchVehicleElement):

    def __init__(self, name, m):
        super(TurboJetEngine, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [1380., 0.295, 2.29, 0.545]
        self.dev_a_conf_int = [462.492874820969, 3640.1151895792027]
        self.dev_x_conf_int = [0.16479322, 0.43652455]
        self.prod_a_conf_int = [1.484, 3.021]
        self.prod_x_conf_int = [0.5125299122673098, 0.6584429840182615]


class RamjetEngine(LaunchVehicleElement):

    def __init__(self, name, m):
        super(RamjetEngine, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [355., 0.295, None, None]


class LiquidPropulsionModule(LaunchVehicleElement):

    def __init__(self, name, m):
        super(LiquidPropulsionModule, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [14.2, 0.577, 3.04, 0.581]
        self.dev_a_conf_int = [6.489031194474779, 28.212166317456276]
        self.dev_x_conf_int = [0.4810022, 0.69573074]


class ExpendableBallisticStageStorable(ComplexElement):

    def __init__(self, name, m):
        super(ExpendableBallisticStageStorable, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [98.5, 0.555, 1.265, 0.59]
        self.dev_a_conf_int = [50.043972009639276, 198.97130393516127]
        self.dev_x_conf_int = [0.47663718, 0.63094232]
        self.prod_a_conf_int = [0.6424330247666832, 3.0449842761799766]
        self.prod_x_conf_int = [0.50440936, 0.68569942]


class ExpendableBallisticStageLH2(ComplexElement):

    def __init__(self, name, m):
        super(ExpendableBallisticStageLH2, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [98.5, 0.555, 1.84, 0.59]
        self.dev_a_conf_int = [50.043972009639276, 198.97130393516127]
        self.dev_x_conf_int = [0.47663718, 0.63094232]
        self.prod_a_conf_int = [1.84, 2.484] # [1.987, 2.484]
        self.prod_x_conf_int = [0.50440936, 0.68569942] # from ExpendableBallisticStageStorable


class ReusableBallisticStageStorable(ComplexElement): 

    def __init__(self, name, m):
        super(ReusableBallisticStageStorable, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [803.5, 0.385, 1.265, 0.59]
        self.dev_a_conf_int = [490.10542138922403, 1341.7410849306882]
        self.dev_x_conf_int = [0.34053124, 0.4265368]
        self.prod_a_conf_int = [0.6424330247666832, 3.0449842761799766]
        self.prod_x_conf_int = [0.50440936, 0.68569942]


class ReusableBallisticStageLH2(ComplexElement): 

    def __init__(self, name, m):
        super(ReusableBallisticStageLH2, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [803.5, 0.385, 1.84, 0.59]
        self.dev_a_conf_int = [490.10542138922403, 1341.7410849306882]
        self.dev_x_conf_int = [0.34053124, 0.4265368]
        self.prod_a_conf_int = [1.84, 2.484] # [1.987, 2.484]
        self.prod_x_conf_int = [0.50440936, 0.68569942] # from ExpendableBallisticStageStorable


class WingedOrbitalVehicle(ComplexElement):

    def __init__(self, name, m):
        super(WingedOrbitalVehicle, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [1420., 0.35, 5.83, 0.606]
        self.dev_a_conf_int = [833.5406027210969, 2373.8200128800067]
        self.dev_x_conf_int = [0.30198781, 0.40052414]


class AdvancedAircraft(ComplexElement):

    def __init__(self, name, m):
        super(AdvancedAircraft, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [2169., 0.262, 0.357, 0.762]
        self.dev_a_conf_int = [1138.1882040647638, 3996.4441371072517]
        self.dev_x_conf_int = [0.20291993, 0.3229399]


class VTOStageFlybackVehicle(LaunchVehicleElement):

    def __init__(self, name, m):
        super(VTOStageFlybackVehicle, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [1462., 0.325, 0.357, 0.762]
        self.dev_a_conf_int = [135.34253464446792, 15336.623033405793]
        self.dev_x_conf_int = [0.10541958, 0.5443403]
        # Note: the following are 90% confidence intervals, not 95% as used elsewhere.
        self.prod_a_conf_int = [0.0350, 3.32]
        self.prod_x_conf_int = [0.545, 0.987]

    def element_development_cost(self, CER_vals, element_cost_factors):

        dev_cost = element_cost_factors.f1 * element_cost_factors.f3 * element_cost_factors.f8 * \
                    element_cost_factors.f10 * element_cost_factors.f11 * CER_vals.dev_a * \
                    self.m**CER_vals.dev_x
        return dev_cost


class CrewedBallisticReentryCapsule(ComplexElement):

    def __init__(self, name, m):
        super(CrewedBallisticReentryCapsule, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [436., 0.408, 0.16, 0.98]
        self.dev_a_conf_int = [0.000228800100628152, 772048685.9231286]
        self.dev_x_conf_int = [0, 1] #[-1.46338225, 2.2841254]


class CrewedSpaceSystem(LaunchVehicleElement):

    def __init__(self, name, m):
        super(CrewedSpaceSystem, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [1113., 0.383, 0.16, 0.98]
        self.dev_a_conf_int = [448.81060831506323, 2704.1854749425434]
        self.dev_x_conf_int = [0.29281118, 0.47303145]

    def element_development_cost(self, CER_vals, element_cost_factors):

        dev_cost = element_cost_factors.f1 * element_cost_factors.f3 * element_cost_factors.f8 * \
                    element_cost_factors.f10 * element_cost_factors.f11 * CER_vals.dev_a * \
                    self.m**CER_vals.dev_x
        return dev_cost

class ExpendableTank(ComplexElement):
    """An expendable liquid propellant tank, with little other equipment (e.g. avionics)

    Notes:
    Production exponent taken from ExpendableBallisticStageStorable. Production coefficient
    calibrated to Space Shuttle Super Lightweight Tank.
    Shuttle SLWT values:
        mass = 26.5 Mg [https://en.wikipedia.org/wiki/Space_Shuttle_external_tank#Super_Lightweight_Tank]
        cost = $34M in 2002 dollars at 10 units/year [https://www.nasa.gov/sites/default/files/atoms/files/29_2016_nasa_cost_symp-learn_rate_curves_webb_tagged.pdf]
                We assume the 10/year production rate most accurately reflects the true production costs; the production costs at lower rates
                are inflated by "dedicated people producing at less than full capacity"
             = 153 WYr
                We expect the first unit cost to be about 2x this value, due to learning effects. (0.9**(log_2(100)) = ~0.5)
        first unit cost = ~300 WYr
        Slide 15 of Webb indicates 450k touch labor hours (216 WYr) for the first unit in 1978-79.
        Plus materials & equipment, this agrees w/ the 300 WYr first unit cost.

    a = c_fu * m**-x
    a = (300) * (26.5e3)**-0.59 = 0.76
    """

    def __init__(self, name, m):
        super(ExpendableTank, self).__init__(name, m)
        self.dev_a, self.dev_x, self.prod_a, self.prod_x = [98.5, 0.555, 0.76, 0.59]
        self.dev_a_conf_int = [50.043972009639276, 198.97130393516127] # Copied from ExpendableBallisticStageStorable
        self.dev_x_conf_int = [0.47663718, 0.63094232] # Copied from ExpendableBallisticStageStorable
        self.prod_a_conf_int = [0.76 / 2, 0.76 * 2]
        self.prod_x_conf_int = [0.50440936, 0.68569942] # Copied from ExpendableBallisticStageStorable
