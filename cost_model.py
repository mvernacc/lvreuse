"""Cost model for 1st stage re-use."""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec


def cost_ratio(n, z, b, q):
    """Cost ratio r_c.

    Arguments:
        n (positive integer): Reusable component lifetime, number of flights.
        z (scalar in (0,1)): recovered cost fraction [units: dimensionless].
            The ratio of the cost of the recovered 1st stage components to the
            total production cost of a recoverable 1st stage.
        b (positive scalar): Recoverable / expendable 1st stage production cost
            ratio [units: dimensionless]. Probably > 1.
        q (positive scalar): Recovery and refurbishment cost ratio [units: dimensionless].
            (cost of recovering and refurbishing the recoverable components) /
            (production cost of the recoverable components). Probably < 1.
    """
    r_c = z * b * (1/float(n) + (1 - z)/z + q)
    return r_c


def main():
    n = (4, 16, 64)
    z = (1, 0.5)
    b = np.linspace(1, 3)
    q = np.linspace(0, 0.5)

    b_grid, q_grid = np.meshgrid(b, q)

    gs = gridspec.GridSpec(len(n), len(z))
    plt.figure(figsize=(8, 10))

    for i in range(len(n)):
        for j in range(len(z)):
            r_c_grid = cost_ratio(n[i], z[j], b_grid, q_grid)

            # Find the minimum value of r_c
            r_c_min = cost_ratio(n[i], z[j], 1, 0)
            print 'r_c min = {:.3f}'.format(r_c_min)

            # Find the r_c=1 "break-even" curve
            q_be = 1/(z[j]*b) - 1/float(n[i]) - (1 - z[j]) / z[j]
            q_be[q_be < 0] = 0

            plt.subplot(gs[i, j])
            # Plot contours of r_c
            cs = plt.contour(b_grid, q_grid, r_c_grid,
                             np.linspace(0, 1, 11))
            plt.clabel(cs, inline=1, fontsize=8)

            # Shade the r_c > 1 bad region
            plt.fill_between(b, q_be, 1, facecolor='grey')

            plt.xlabel('Prod. cost ratio $b$ [-]')
            plt.ylabel('Refurb. ratio $q$ [-]')
            plt.title('n={:d}, z={:.2f}'.format(n[i], z[j]))
            plt.ylim([0, 0.5])
    plt.suptitle('Cost factor $r_c$')
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    plt.show()


if __name__ == '__main__':
    main()
