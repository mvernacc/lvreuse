import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.data.missions import LEO
from num_reuse_sweep import get_mode_values


def main():
        
    mission = LEO
    strat = strategy_models.Expendable

    strat_instance = strat(strategy_models.kero_GG_boost_tech, strategy_models.kero_GG_upper_tech, mission)
    modes = get_mode_values(strat_instance.uncertainties)

    results = strat_instance.evaluate(**modes)
    prod_cost_per_flight = results[2]
    s1_e1_prod_cost_per_flight = results[7]
    s2_e2_prod_cost_per_flight = results[8]
    veh_int_checkout = results[9]
    ops_cost_per_flight = results[3]
    props_cost = results[10]
    refurb_cost = results[11]
    cpf = results[4]

    width = 0.02

    plt.figure(figsize=(4,4))
    ax = plt.subplot(1,1,1)

    plt.bar(0, s1_e1_prod_cost_per_flight, width, align='edge', label='Stage 1 Production')
    plt.bar(0, s2_e2_prod_cost_per_flight, width, bottom=s1_e1_prod_cost_per_flight, align='edge', label='Stage 2 Production')
    plt.bar(0, veh_int_checkout, width, bottom=s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Vehicle Integration and Checkout')
    plt.bar(0,ops_cost_per_flight, width, bottom=veh_int_checkout+s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Operations')
    plt.bar(0, props_cost, width, bottom=ops_cost_per_flight+veh_int_checkout+s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Propellants')
    
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off 

    plt.title('Cost breakdown for \n expandable vehicle')
    plt.ylabel('Cost [WYr]')
    plt.xlim(0, width)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()