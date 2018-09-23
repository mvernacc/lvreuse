"""Present value of cost savings due to reuse."""
import os.path

import numpy as np
from matplotlib import pyplot as plt

def main():
    # Sweep over
    # (cost per flight w/ 1st stage reuse)
    # / (cost per flight of all-expendable launch vehicle)
    # [units: dimensionless].
    
    # Figure format switch - paper or presentation?

    fig_format = 'presentation'
    if fig_format == 'presentation':
        fontsize = 14
    if fig_format == 'paper':
        fontsize = 17

    cpf_ratio = np.linspace(0, 1)

    # Launch rate [units: year**-1].
    launch_rates = [1, 5, 10, 20, 40]

    # Discount rate (per year)
    discount_rate_annual = 0.20

    # Horizon [units: year].
    horizon = 20

    # Present value of savings from reuse
    # [units: multiples of (cost per flight of all-expendable launch vehicle)]
    pres_val = np.zeros(len(cpf_ratio))

    plt.figure(figsize=(8, 6))
    for launch_rate in launch_rates:
        # Discount rate per "payment period", i.e. per
        # interval between launches.
        discount_rate_per_period = discount_rate_annual / launch_rate

        for i in range(len(cpf_ratio)):
            pres_val[i] = np.pv(
                rate=discount_rate_per_period,
                nper=launch_rate * horizon,
                pmt=cpf_ratio[i] - 1,
                when='begin',
                )

        plt.plot(cpf_ratio, pres_val, label='{:.0f}'.format(launch_rate))

    # Highlight credible range of cpf ratio
    # These ranges were computed by lvreuse.analysis.combined.cost_ratio.py,
    # https://github.mit.edu/mvernacc/1st-stage-return/blob/1d0a2a4421405421b4fb6cac9cb14ff232de4fd0/lvreuse/analysis/combined/cost_ratio.py
    # For downrange propulsive landing, LEO mission, kerosene technology.
    # For medium-heavy launch vehicles (10 to 100 Mg payload to LEO)
    plt.axvspan(xmin=0.39, xmax=0.68, color='green', alpha=0.1)
    # For small lauch vehicles (100 kg to LEO)
    plt.axvspan(xmin=0.80, xmax=0.96, color='green', alpha=0.1)

    # Highlight credible range of dev costs
    # e.g. for a eelv-size vehicle, cpf is likely $50M, and
    # reusability development probably costs $400M to $3B
    # so credible range is 8 to 60
    # Sources:
    #   Low bound on dev cost: https://www.nasa.gov/sites/default/files/files/Section403(b)CommercialMarketAssessmentReportFinal.pdf
    #   High bound on dev cost: guess at Blue Origin dev. spending based on J. Bezos'
    #       sales of Amazon stock.
    plt.axhspan(ymin=8, ymax=60, color='grey', alpha=0.2)

    plt.xlim([0, 1])
    plt.ylim([0, 100])
    plt.xticks(fontsize=0.8*fontsize)
    plt.yticks(fontsize=0.8*fontsize)
    plt.xlabel('Cost p.f. w/ 1st stage reuse / cost p.f. expendable [-]', fontsize=fontsize)
    plt.ylabel('Present value of savings / cost p.f. expendable [-]', fontsize=fontsize)
    plt.title('Present value of reuse cost per flight savings'
              + '\n {:.0f} %/year discount rate, {:.0f} year horizon'.format(
                  discount_rate_annual * 100, horizon), fontsize=fontsize)
    plt.tight_layout()
    plt.savefig(os.path.join('plots', 'reuse_npv.png'), dpi=200)

    plt.legend(title='Launch rate / year', fontsize=0.8*fontsize)
    plt.show()

if __name__ == '__main__':
    main()
