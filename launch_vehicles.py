"""Example 2-stage launch vehicles."""

class LaunchVehicle(object):

    def __init__(self, name, masses, c_1, c_2):
        """Define a launch vehicle.
        Arguments:
            masses (dict): [units: megagram].
        """

        self.name = name
        self.masses = masses
        self.c_1 = c_1
        self.c_2 = c_2

    def stage_inert_mass_fraction(self, which_stage):
        """Get the inert mass fraction of a stage."""
        m_s = self.masses['m_s' + str(which_stage)]
        m_p = self.masses['m_p' + str(which_stage)]
        return m_s / (m_s + m_p)

    def stage_mass_ratio(self):
        """Get the 2nd/1st stage mass ratio y"""
        y = ((self.masses['m_s2'] + self.masses['m_p2'])
            / (self.masses['m_s1'] + self.masses['m_p1']))
        return y

    def payload_actual(self, which_orbit):
        """Get the launch vehicle's payload mass fraction."""
        assert which_orbit == 'LEO' or which_orbit == 'GTO'

        # Payload mass
        m_star = self.masses['m_star_' + which_orbit]

        # Launch vehicle wet mass
        m_lv = (self.masses['m_s1'] + self.masses['m_p1']
            + self.masses['m_s2'] + self.masses['m_p2'])

        # Payload ratio
        pi_star =  m_star / (m_star + m_lv)
        return pi_star


g_0 = 9.81

# Data from Wikipedia. c_1 is mean of listed sea level and vacuum values.
atlas_v_401 = LaunchVehicle(
    name='Atlas V 401',
    masses={
        'm_s1': 21.1,
        'm_p1': 284.,
        'm_s2': 2.32,
        'm_p2': 20.8,
        'm_star_LEO': 9.80,
        'm_star_GTO': 4.75,
    },
    c_1=325 * g_0,
    c_2=450 * g_0
    )

f9_ft_e = LaunchVehicle(
    name='Falcon 9 FT (Expendable)',
    masses={
        'm_s1': 22.2,
        'm_p1': 433.1 - 22.2,
        'm_s2': 4.0,
        'm_p2': 111.5 - 4.0,
        'm_star_LEO': 22.8,
        'm_star_GTO': 8.30,
    },
    c_1=297 * g_0,
    c_2=350 * g_0
    )

# Data from http://www.spacelaunchreport.com/delta4.html
# Delta 9040 with 4 meter second stage
delta_iv_m = LaunchVehicle(
    name='Delta IV Medium',
    masses={
        'm_s1': 28.,
        'm_p1': 204.,
        'm_s2': 2.78,
        'm_p2': 20.41,
        'm_star_LEO': 8.8,
        'm_star_GTO': 4.54,
    },
    c_1= 386 * g_0,
    c_2= 462 * g_0
    )


def main():
    lvs = (atlas_v_401, delta_iv_m, f9_ft_e)

    for lv in lvs:
        e_1 = lv.stage_inert_mass_fraction(1)
        e_2 = lv.stage_inert_mass_fraction(2)
        y = lv.stage_mass_ratio()
        pi_star_leo = lv.payload_actual('LEO')
        pi_star_gto = lv.payload_actual('GTO')

        print lv.name
        print 'e_1 = {:.3f}, e_2 = {:.3f}, y = {:.3f}, pi_leo = {:.3f}, pi_gto = {:.3f}'.format(
            e_1, e_2, y, pi_star_leo, pi_star_gto)
        print '\n'


if __name__ == '__main__':
    main()
