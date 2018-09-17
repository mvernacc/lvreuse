import os.path

from matplotlib import pyplot as plt
import numpy as np

from lvreuse.analysis.combined import strategy_models
from lvreuse.analysis.cost.strategy_cost_models import wyr_conversion
from lvreuse.data.missions import LEO, LEO_smallsat
from num_reuse_sweep import get_mode_values


def main():

    fontsize = 17

    strat = strategy_models.PropulsiveDownrange

    strat_instance = strat(strategy_models.kero_GG_boost_tech, strategy_models.kero_GG_upper_tech, LEO)
    modes = get_mode_values(strat_instance.uncertainties)

    ###

    num_reuses = np.arange(1, 101)
    s1_e1_prod_cost_per_flight = np.zeros(len(num_reuses))
    s2_e2_prod_cost_per_flight = np.zeros(len(num_reuses))
    veh_int_checkout = np.zeros(len(num_reuses))
    ops_cost_per_flight = np.zeros(len(num_reuses))
    prod_cost_per_flight = np.zeros(len(num_reuses))
    cpf = np.zeros(len(num_reuses))
    props_cost = np.zeros(len(num_reuses))
    refurb_cost = np.zeros(len(num_reuses))

    for i in range(len(num_reuses)):
        modes['num_reuses_s1'] = num_reuses[i]
        modes['num_reuses_e1'] = num_reuses[i]
        results = strat_instance.evaluate(**modes)
        prod_cost_per_flight[i] = results[2]
        s1_e1_prod_cost_per_flight[i] = results[7]
        s2_e2_prod_cost_per_flight[i] = results[8]
        veh_int_checkout[i] = results[9]
        ops_cost_per_flight[i] = results[3]
        props_cost[i] = results[10]
        refurb_cost[i] = results[11]
        cpf[i] = results[4]

    print('min cpf: ', min(cpf))
    print('min use num: ', np.argmin(cpf))

    labels = ['Stage 1 Production', 'Stage 2 Production', 'Vehicle Integration and Checkout',
              'Operations', 'Propellants', 'Refurbishment']
    plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)
    plt.stackplot(num_reuses, s1_e1_prod_cost_per_flight*wyr_conversion, s2_e2_prod_cost_per_flight*wyr_conversion,
                  veh_int_checkout*wyr_conversion, ops_cost_per_flight*wyr_conversion - props_cost*wyr_conversion - 
                  refurb_cost*wyr_conversion, props_cost*wyr_conversion, refurb_cost*wyr_conversion, labels=labels)
    plt.xlabel('Number of 1st stage uses', fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.ylabel('Cost [Million US Dollars in 2018]', fontsize=fontsize)
    plt.title('Cost per flight breakdown vs. vehicle life for LEO mission, 10.0 Mg payload \n stage 1: kerosene gas generator tech., stage 2: kerosene gas generator tech', fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    ax.set_xscale('log')
    ax.set_ylim(0,60)
    ax.tick_params(axis='y', labelsize=0.8*fontsize)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], fontsize=fontsize*0.8)
    plt.xlim(1e0, 1e2)

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost [WYr]', fontsize=fontsize)
    ax1.set_ylim(0, 60/wyr_conversion)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1.grid(False)

    plt.savefig(os.path.join('plots', 'cpf_stackplot_reuses_sweep.png'))

    ### 

    modes = get_mode_values(strat_instance.uncertainties)
    launch_rate = np.array([3, 5, 10, 20, 40])
    cpf = np.zeros((len(launch_rate),len(num_reuses)))

    plt.figure(figsize=(10, 10))
    ax = plt.subplot(1, 1, 1)

    for j in range(len(launch_rate)):
        for i in range(len(num_reuses)):
            modes['num_reuses_s1'] = num_reuses[i]
            modes['num_reuses_e1'] = num_reuses[i]
            modes['launch_rate'] = launch_rate[j]
            results = strat_instance.evaluate(**modes)
            cpf[j, i] = results[4]
        plt.semilogx(num_reuses, cpf[j, :]*wyr_conversion)

    plt.title('Cost per flight vs. vehicle life for LEO mission, 10.0 Mg payload \n stage 1: kerosene gas generator tech., stage 2: kerosene gas generator tech', fontsize=fontsize)
    plt.xlabel('Number of 1st stage uses', fontsize=fontsize)
    #plt.xticks(fontsize=fontsize)
    plt.ylabel('Cost per flight [Million US Dollars in 2018]', fontsize=fontsize)
    labels = [str(i) for i in launch_rate]
    plt.legend(labels=labels, title='Launch rate', fontsize=fontsize*0.8)
    plt.xlim(1e0, 1e2)
    plt.ylim(0, 75)
    ax.tick_params(axis='both', labelsize=0.8*fontsize)
    plt.grid(True, which='both')

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost per flight [WYr]', fontsize=fontsize)
    ax1.set_ylim(0, 75/wyr_conversion)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1.grid(False)

    plt.savefig(os.path.join('plots', 'cpf_reuses_sweep_vary_launch_rate.png'))

    ###

    modes = get_mode_values(strat_instance.uncertainties)

    launch_rate = np.arange(1, 31)
    s1_e1_prod_cost_per_flight = np.zeros(len(launch_rate))
    s2_e2_prod_cost_per_flight = np.zeros(len(launch_rate))
    veh_int_checkout = np.zeros(len(launch_rate))
    ops_cost_per_flight = np.zeros(len(launch_rate))
    prod_cost_per_flight = np.zeros(len(launch_rate))
    cpf = np.zeros(len(launch_rate))
    props_cost = np.zeros(len(launch_rate))
    refurb_cost = np.zeros(len(launch_rate))


    for i in range(len(launch_rate)):
        modes['launch_rate'] = launch_rate[i]
        results = strat_instance.evaluate(**modes)
        prod_cost_per_flight[i] = results[2]
        s1_e1_prod_cost_per_flight[i] = results[7]
        s2_e2_prod_cost_per_flight[i] = results[8]
        veh_int_checkout[i] = results[9]
        ops_cost_per_flight[i] = results[3]
        cpf[i] = results[4]
        props_cost[i] = results[10]
        refurb_cost[i] = results[11]

    labels = ['Stage 1 Production', 'Stage 2 Production', 'Vehicle Integration and Checkout',
              'Operations', 'Propellants', 'Refurbishment']
    plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1)
    plt.stackplot(launch_rate, s1_e1_prod_cost_per_flight*wyr_conversion, s2_e2_prod_cost_per_flight*wyr_conversion, 
                  veh_int_checkout*wyr_conversion, ops_cost_per_flight*wyr_conversion - props_cost*wyr_conversion - 
                  refurb_cost*wyr_conversion, props_cost*wyr_conversion, refurb_cost*wyr_conversion, labels=labels)
    plt.xlabel('Annual launch rate', fontsize=fontsize)
    plt.ylabel('Cost [Million US Dollars in 2018]', fontsize=fontsize)
    plt.title('Cost per flight breakdown vs. launch rate for LEO mission, 10.0 Mg payload \n stage 1: kerosene gas generator tech., stage 2: kerosene gas generator tech', fontsize=fontsize)
    ax.set_xscale('log')
    ax.tick_params(axis='both',labelsize=fontsize)
    ax.set_ylim(0, 75)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], fontsize=0.8*fontsize)
    plt.xlim(1, 30)

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost [WYr]', fontsize=fontsize)
    ax1.set_ylim(0, 75/wyr_conversion)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1.grid(False)

    plt.savefig(os.path.join('plots', 'cpf_stackplot_launch_rate_sweep.png'))

    ### small sat

    strat_instance = strat(strategy_models.kero_GG_boost_tech, strategy_models.kero_GG_upper_tech, LEO_smallsat)
    modes = get_mode_values(strat_instance.uncertainties)

    num_reuses = np.arange(1, 101)
    s1_e1_prod_cost_per_flight = np.zeros(len(num_reuses))
    s2_e2_prod_cost_per_flight = np.zeros(len(num_reuses))
    veh_int_checkout = np.zeros(len(num_reuses))
    ops_cost_per_flight = np.zeros(len(num_reuses))
    prod_cost_per_flight = np.zeros(len(num_reuses))
    cpf = np.zeros(len(num_reuses))
    props_cost = np.zeros(len(num_reuses))
    refurb_cost = np.zeros(len(num_reuses))

    for i in range(len(num_reuses)):
        modes['num_reuses_s1'] = num_reuses[i]
        modes['num_reuses_e1'] = num_reuses[i]
        results = strat_instance.evaluate(**modes)
        prod_cost_per_flight[i] = results[2]
        s1_e1_prod_cost_per_flight[i] = results[7]
        s2_e2_prod_cost_per_flight[i] = results[8]
        veh_int_checkout[i] = results[9]
        ops_cost_per_flight[i] = results[3]
        props_cost[i] = results[10]
        refurb_cost[i] = results[11]
        cpf[i] = results[4]

    print('min cpf: ', min(cpf))
    print('min use num: ', np.argmin(cpf))

    labels = ['Stage 1 Production', 'Stage 2 Production', 'Vehicle Integration and Checkout',
              'Operations', 'Propellants', 'Refurbishment']
    plt.figure(figsize=(10, 9))
    ax = plt.subplot(1, 1, 1)
    plt.stackplot(num_reuses, s1_e1_prod_cost_per_flight*wyr_conversion, s2_e2_prod_cost_per_flight*wyr_conversion,
                  veh_int_checkout*wyr_conversion, ops_cost_per_flight*wyr_conversion - props_cost*wyr_conversion - 
                  refurb_cost*wyr_conversion, props_cost*wyr_conversion, refurb_cost*wyr_conversion, labels=labels)
    plt.xlabel('Number of 1st stage uses', fontsize=fontsize)
    plt.ylabel('Cost [Million US Dollars in 2018]', fontsize=fontsize)
    plt.title('Cost per flight breakdown vs. vehicle life for LEO mission, 100 kg payload \n stage 1: kerosene gas generator tech., stage 2: kerosene gas generator tech', fontsize=fontsize)
    ax.set_xscale('log')
    ax.set_ylim(0,12)
    ax.tick_params(axis='both', labelsize=0.8*fontsize)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], fontsize=fontsize)
    plt.xlim(1e0, 1e2)

    ax1 = ax.twinx()
    ax1.set_ylabel('Cost [WYr]', fontsize=fontsize)
    ax1.set_ylim(0, 12/wyr_conversion)
    ax1.tick_params(axis='y', labelsize=0.8*fontsize)
    ax1.grid(False)

    plt.savefig(os.path.join('plots', 'cpf_stackplot_reuses_sweep_small_sat.png'))

    plt.show()


if __name__ == '__main__':
    main()