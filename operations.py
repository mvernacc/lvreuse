"""Create operations costs model."""

class DirectOperations(object):

    def __init__(self, launch_vehicle, L, N, fv, fc, p, f8, f11):
        """Characterization of the direct operations cost for a launch vehicle.

        Arguments:
            launch_vehicle: launch vehicle of interest, an instance of the LaunchVehicle class.
            L (positive integer): launch rate [units: launches/year or LpA].
            N (positive integer): number of stages or major vehicle elements
            fv (positive scalar): TODO [units: dimensionless]
            fc (positive scalar): TODO [units: dimensionless]
            p: TODO [units: dimensionless]
            f8 (positive scalar): TODO [units: dimensionless]
            f11 (positive scalar): TODO [units: dimensionless]"""

            self.launch_vehicle = launch_vehicle
            self.L = L
            self.fv = fv
            self.fc = fc
            self.p = p
            self.f8 = f8
            self.f11 = f11

    def preflight_ground_ops_cost(self):
        """Find pre-flight ground operations costs.

        Returns:
            Pre-flight ground oeperations cost [units: person-year]"""
    
        C_ops = 8 * self.launch_vehicle.M0**0.67 * self.L**-0.9 * N**0.7 * self.fv * self.fc * f4 * self.f8 * self.f11 ##### CHECK N
        return C_ops

    def flight_mission_ops_cost(self, is_crewed=False, Tm=None, Na=None):
        """Find crewed launch, flight, and mission operations cost.

        Arguments:
            is_crewed (boolean): True if vehicle is crewed, False otherwise
            Tm: Mission duration in orbit [units: days]
            Na: Number of crew members

        Returns:
            Total crewed launch, flight, and mission operations cost [units: person-year"""


        C_m = 20 * sum_QN * self.L**-0.65 * f4 * self.f8

        if is_crewed:
            C_ma = 75. * Tm**0.5 * Na**0.5 * self.L**-0.8 * f4 * self.f8 * self.f11
            C_m += C_ma

        return C_m

    def recovery_ops_cost(self, M_rec):
        """Find recovery operations cost.

        Arguments:
            M_rec: recovery mass [units: Mg]

        Returns:
            Recovery operations cost [units: person-year]"""

        C_rec = 1.5 / self.L * (7. * self.L**0.7 + M_rec**0.83) * self.f8 * self.f11
        return C_rec

    def total_operations_cost(self, props_gasses_cost, maintenance_cost, ground_transport_cost, fees):
        """Find the total per-flight operations cost.

        Arguments:
            props_gasses_cost: TODO [units: person-year]
            maintenance_cost: TODO [units: person-year]
            ground_transport_cost: TODO [units: person-year]
            fees: TODO [units: person-year]

        Returns:
            Per-flight operations cost [units: person-year]"""

        









