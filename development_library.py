class SystemDevelopmentValues(object):

    def __init__(self, dev_a, dev_x):
        """Create a propellant properties object.
        
        Args:
            dev_a (positive saclar): development CER model coefficient [units: kg**(-dev_x)]
            dev_x (positive scalar): development CER model exponent [units: dimensionless]"""

        self.dev_a = dev_a
        self.dev_x = dev_x


solid_motor = SystemDevelopmentValues(
    dev_a=16.3,
    dev_x=0.54,
    )

turbo_fed_engine = SystemDevelopmentValues(
    dev_a=277.,
    dev_x=0.48
    )

pressure_fed_engine = SystemDevelopmentValues(
    dev_a=167.,
    dev_x=0.35,
    )

air_breathing_engine = SystemDevelopmentValues(
    dev_a=1380.,
    dev_x=0.295,
    )

large_solid_booster = SystemDevelopmentValues(
    dev_a=10.4,
    dev_x=0.60,
    )

liquid_propulsion_module = SystemDevelopmentValues(
    dev_a=14.2,
    dev_x=0.577,
    )

expendable_ballastic_vehicle = SystemDevelopmentValues(
    dev_a=100.,
    dev_x=0.555,
    )

reusable_ballistic_vehicle = SystemDevelopmentValues(
    dev_a=803.5,
    dev_x=0.385,
    )

winged_orbital_vehicle = SystemDevelopmentValues(
    dev_a=1421.,
    dev_x=0.35,
    )

advanced_aircraft = SystemDevelopmentValues(
    dev_a=2880.,
    dev_x=0.241,
    )

VTO_flyback = SystemDevelopmentValues(
    dev_a=1462.,
    dev_x=0.325,
    )

crewed_ballistic_capsule = SystemDevelopmentValues(
    dev_a=436.,
    dev_x=0.408,
    )

crewed_space_system = SystemDevelopmentValues(
    dev_a=1113.,
    dev_x=0.383,
    )

sys_dev_vals_list = [solid_motor, turbo_fed_engine, pressure_fed_engine, air_breathing_engine, 
                        large_solid_booster, liquid_propulsion_module, expendable_ballastic_vehicle, 
                        reusable_ballistic_vehicle, winged_orbital_vehicle, advanced_aircraft, 
                        VTO_flyback, crewed_ballistic_capsule, crewed_space_system]