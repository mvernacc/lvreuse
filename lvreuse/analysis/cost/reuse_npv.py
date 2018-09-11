"""Present value of cost savings due to reuse."""
import os.path

import numpy as np
from matplotlib import pyplot as plt

def main():
    # Sweep over
    # (cost per flight w/ 1st stage reuse)
    # / (cost per flight of all-expendable launch vehicle)
    # [units: dimensionless].
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
    plt.axvspan(xmin=0.33, xmax=1, color='green', alpha=0.1)
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
    plt.xlabel('Cost p.f. w/ 1st stage reuse / cost p.f. expendable [-]')
    plt.ylabel('Present value of savings / cost p.f. expendable [-]')
    plt.title('Present value of reuse cost per flight savings'
              + '\n {:.0f} %/year discount rate, {:.0f} year horizon'.format(
                  discount_rate_annual * 100, horizon))
    plt.tight_layout()
    plt.savefig(os.path.join('plots', 'reuse_npv.png'), dpi=200)

    plt.legend(title='Launch rate / year')
    plt.show()

if __name__ == '__main__':
    main()
