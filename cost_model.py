"""Cost model for 1st stage re-use."""
import numpy as np
from matplotlib import pyplot as plt


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
    n = 16
    z = 0.5
    b = np.linspace(1, 3)
    q = np.linspace(0, 1)

    b_grid, q_grid = np.meshgrid(b, q)

    r_c_grid = cost_ratio(n, z, b_grid, q_grid)

    # Find the minimum value of r_c
    r_c_min = cost_ratio(n, z, 1, 0)
    print 'r_c min = {:.3f}'.format(r_c_min)

    # Find the r_c=1 "break-even" curve
    q_be = 1/(z*b) - 1/float(n) - (1 - z) / z
    q_be[q_be < 0] = 0


    plt.figure()
    # Plot contours of r_c
    cs = plt.contour(b_grid, q_grid, r_c_grid, 16)
    plt.clabel(cs, inline=1, fontsize=10)

    # Shade the r_c > 1 bad region
    plt.fill_between(b, q_be, 1, facecolor='grey')

    plt.xlabel('Recov./Expend. prod. cost $b$ [-]')
    plt.ylabel('(Recov.+Refurb.)/prod. cost $q$ [-]')
    plt.title('Cost ratio $r_c$\nfor n={:d}, z={:.2f}'.format(n, z))
    plt.show()


if __name__ == '__main__':
    main()
