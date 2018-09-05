"""Sensitivity analysis of performance."""

import rhodium as rdm
import strategy_perf_models


tech_1 = strategy_perf_models.kero_GG_boost_tech
tech_2 = strategy_perf_models.kero_GG_upper_tech
mission = strategy_perf_models.LEO

print('Mission: {:s}'.format(mission.name))

print('\n\n**Expendable**')
expd = strategy_perf_models.Expendable(tech_1, tech_2, mission)
results = rdm.sa(expd.perf_model, 'pi_star', method='sobol', nsamples=1000)
print(results)

print('\n\n**Propulsive Launch Site**')
prop_ls = strategy_perf_models.PropulsiveLaunchSite(tech_1, tech_2, mission)
results = rdm.sa(prop_ls.perf_model, 'pi_star', method='sobol', nsamples=1000)
print(results)

print('\n\n**Winged Powered Launch Site**')
wing_pwr_ls = strategy_perf_models.WingedPoweredLaunchSite(tech_1, tech_2, mission)
results = rdm.sa(wing_pwr_ls.perf_model, 'pi_star', method='sobol', nsamples=1000)
print(results)
