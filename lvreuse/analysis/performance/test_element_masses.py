from strategy_perf_models import (Expendable, WingedPoweredLaunchSite,
                                  WingedPoweredLaunchSitePartial,
                                  ParachutePartial,
                                  kero_GG_boost_tech,
                                  kero_GG_upper_tech,
                                  LEO, GTO)

def main():
    tech_1 = kero_GG_boost_tech
    tech_2 = kero_GG_upper_tech
    mission = LEO

    expd = Expendable(tech_1, tech_2, mission)
    print(expd.get_masses(pi_star=0.02, a=0, E_1=0.06, E_2=0.04))

    wingpwr = WingedPoweredLaunchSite(tech_1, tech_2, mission)
    print(wingpwr.get_masses(pi_star=0.01, a=0.60, E_1=0.06, E_2=0.04))

    wingpwr_part = WingedPoweredLaunchSitePartial(tech_1, tech_2, mission)
    print(wingpwr_part.get_masses(pi_star=0.01, a=0.60, E_1=0.06, E_2=0.04))

    parachute_part = ParachutePartial(tech_1, tech_2, mission)
    print(parachute_part.get_masses(pi_star=0.01, a=0.20, E_1=0.06, E_2=0.04))


if __name__ == '__main__':
    main()
