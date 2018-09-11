import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.data.missions import LEO
from num_reuse_sweep import get_mode_values


def main():

    mission = LEO
    strat = strategy_models.PropulsiveDownrange

    strat_instance = strat(strategy_models.kero_GG_boost_tech, strategy_models.kero_GG_upper_tech, mission)
    modes = get_mode_values(strat_instance.uncertainties)

    num_reuses = np.arange(1, 100)
    s1_e1_prod_cost_per_flight = np.zeros(len(num_reuses))
    s2_e2_prod_cost_per_flight = np.zeros(len(num_reuses))
    veh_int_checkout = np.zeros(len(num_reuses))
    ops_cost_per_flight = np.zeros(len(num_reuses))
    prod_cost_per_flight = np.zeros(len(num_reuses))
    cpf = np.zeros(len(num_reuses))

    for i in range(len(num_reuses)):
        modes['num_reuses_s1'] = num_reuses[i]
        modes['num_reuses_e1'] = num_reuses[i]
        results = strat_instance.evaluate(**modes)
        prod_cost_per_flight[i] = results[2]
        s1_e1_prod_cost_per_flight[i] = results[7]
        s2_e2_prod_cost_per_flight[i] = results[8]
        veh_int_checkout[i] = results[9]
        ops_cost_per_flight[i] = results[3]
        cpf[i] = results[4]


    labels = ['Stage 1 Production', 'Stage 2 Production', 'Vehicle Integration and Checkout', 'Operations']
    plt.figure(figsize=(10, 6))
    plt.stackplot(num_reuses, s1_e1_prod_cost_per_flight, s2_e2_prod_cost_per_flight, veh_int_checkout, ops_cost_per_flight, labels=labels)
    plt.xlabel('Number of 1st stage reuses')
    plt.ylabel('Cost [WYr]')
    plt.title('')
    plt.legend(loc=1)

    plt.show()

if __name__ == '__main__':
    main()