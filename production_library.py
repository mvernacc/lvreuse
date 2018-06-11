class SystemProductionValues(object):

    def __init__(self, prod_a, prod_x):
        """Create a propellant properties object.
        
        Args:
            prod_a (positive scalar): production CER model coefficient [units: kg**(-prod_x)]
            prod_x (positive scalar): production CER model exponent [units: dimensionless]"""

        self.prod_a = prod_a
        self.prod_x = prod_x

solid_prop_motor_booster = SystemProductionValues(
    prod_a=2.3,
    prod_x=0.399
    )

liquid_engine_cryo = SystemProductionValues(
    prod_a=5.16,
    prod_x=0.45
    )

liquid_engine_storable = SystemProductionValues(
    prod_a=1.9,
    prod_x=0.535
    )

liquid_engine_monoprop = SystemProductionValues(
    prod_a=1.13,
    prod_x=0.535
    )

airbreathing_engine = SystemProductionValues(
    prod_a=2.29,
    prod_x=0.545
    )

prop_module = SystemProductionValues(
    prod_a=4.65,
    prod_x=0.49
    )

ballistic_vehicles_storable_prop = SystemProductionValues(
    prod_a=0.83,
    prod_x=.65
    )
ballistic_vehicles_cryo_prop = SystemProductionValues(
    prod_a=1.30,
    prod_x=0.65
    )

high_speed_aircraft = SystemProductionValues(
    prod_a=.367,
    prod_x=0.747
    )

winged_first_stage = SystemProductionValues(
    prod_a=.367,
    prod_x=0.747
    )

winged_orbital_vehicle = SystemProductionValues(
    prod_a=3.75,
    prod_x=0.65
    )

crewed_space_system = SystemProductionValues(
    prod_a=0.16,
    prod_x=.98
    )

sys_prod_vals_list = [solid_prop_motor_booster, liquid_engine_cryo, liquid_engine_storable, 
                        liquid_engine_monoprop, airbreathing_engine, prop_module, 
                        ballistic_vehicles_storable_prop, ballistic_vehicles_cryo_prop, 
                        high_speed_aircraft, winged_first_stage, winged_orbital_vehicle, 
                        crewed_space_system] 