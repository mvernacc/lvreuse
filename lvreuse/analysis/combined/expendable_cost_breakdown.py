import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.data.missions import LEO
from num_reuse_sweep import get_mode_values
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion


def main():
        
    mission = LEO
    strat = strategy_models.Expendable

    strat_instance = strat(strategy_models.kero_GG_boost_tech, strategy_models.kero_GG_upper_tech, mission)
    modes = get_mode_values(strat_instance.uncertainties)

    fontsize = 17

    results = strat_instance.evaluate(**modes)
    prod_cost_per_flight = results[2] * wyr_conversion
    s1_e1_prod_cost_per_flight = results[7] * wyr_conversion
    s2_e2_prod_cost_per_flight = results[8] * wyr_conversion
    veh_int_checkout = results[9] * wyr_conversion
    ops_cost_per_flight = results[3] * wyr_conversion
    props_cost = results[10] * wyr_conversion
    refurb_cost = results[11] * wyr_conversion
    cpf = results[4] * wyr_conversion

    width = 0.3

    plt.figure(figsize=(10,5))
    ax = plt.subplot(1,1,1)

    plt.bar(0, s1_e1_prod_cost_per_flight, width, align='edge', label='Stage 1 Production')
    plt.bar(0, s2_e2_prod_cost_per_flight, width, bottom=s1_e1_prod_cost_per_flight, align='edge', label='Stage 2 Production')
    plt.bar(0, veh_int_checkout, width, bottom=s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Vehicle Integration and Checkout')
    plt.bar(0, ops_cost_per_flight, width, bottom=veh_int_checkout+s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Operations')
    plt.bar(0, props_cost, width, bottom=ops_cost_per_flight+veh_int_checkout+s2_e2_prod_cost_per_flight+s1_e1_prod_cost_per_flight, align='edge', label='Propellants')
    
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off 

    plt.title('Cost per flight breakdown of expendable vehicle \n for LEO mission, 10.0 Mg payload \n stage 1: kerosene gas generator tech., \n stage 2: kerosene gas generator tech', loc='left', fontsize=fontsize)
    plt.ylabel('Cost [Million US Dollars in 2018]', fontsize=fontsize)
    plt.xlim(0, width)
    # ax.spines['right'].set_visible(False)

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost [WYr]', fontsize=fontsize)
    ax1.set_ylim(0, ax.get_ylim()[1]/wyr_conversion)
    ax1.grid(False)

    ax.spines['top'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    plt.xticks(fontsize=0.8*fontsize)
    plt.yticks(fontsize=0.8*fontsize)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[::-1], labels=labels[::-1], loc='center left', bbox_to_anchor=(1.4, 0.5), fontsize=0.8*fontsize)

    plt.tight_layout()

    plt.savefig(os.path.join('plots', 'expendable_cost_breakdown.png'))

    plt.show()

if __name__ == '__main__':
    main()