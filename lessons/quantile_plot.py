"""Plot the quantiles of an output variable against an input variable."""

import numpy as np
import matplotlib.pyplot as plt
import wquantiles

def quantile_plot(x, y, quantiles=(0.1, 0.9), ax=None, scatter=True, **kwarg):
    """ Plot the quantiles of an output variable against an input variable.

    This function visualizes the relation between two random variables x and y
    by plotting the quantiles of y against x. The median is plotted as a line
    and the interval between the lower and upper quantiles is shaded.

    This visualization is inspired by the "upside-downside curve" presented in Figure 6.12
    of Flexibility in Engineering Design by R de Neufville and S Scholtes.

    Arguments:
        x (array): samples of the input (independent) variable.
        y (array): samples of the output (dependent) variable.
        quantiles (tuple, optional): lower and upper quantiles to shade.
        ax (matplotlib axes): axes to plot on; if None create new axes.
        scatter (boolean): If true, scatter-plot the samples on the quantile plot.

    Returns:
        matplotlib axes
    """
    x = np.asarray(x)
    y = np.asarray(y)

    x_test, q_test = running_quantiles_window(x, y, (*quantiles, 0.5))

    if ax is None:
        ax = plt.subplot(1, 1, 1)

    if scatter:
        ax.scatter(x, y, marker='+', color=(0.8, 0.8, 0.8))

    ax.plot(x_test, q_test[:, 2], label='Median', **kwarg)
    ax.fill_between(x_test, q_test[:, 0], q_test[:, 1],
        label='{:.2f} to {:.2f} quantiles'.format(*quantiles), alpha=0.5, **kwarg)

    return ax


def running_quantiles_window(x, y, quantiles, window_width=None, x_test=None, npoints=50):
    """ Compute the running quantiles of y with respect to x.

    Consider a pair of random variables (x, y). This function estimates y*, where
        F(y = y* | x = x_test) = q,
        q in [0, 1] is a given quantile level,
        x_test[i] is a test point,
        and F(y|x) is the conditional cumulative distribution function of y.

    The estimation is performed by computing the sample quantiles of the subset of points whose
    x-value lies within `window_width` of `x_test`. Beware that the estimates will be poor
    if few samples lie within the window.

    Arguments:
        x (array): samples of the input (independent) variable.
        y (array): samples of the output (dependent) variable.
        quantiles (scalar or array): quantile(s) to compute, must be in [0, 1].
        x_test (scalar or array, optional): Test point(s) at which to estimate quantiles.
            If none, an array of test points spanning the range of `x` will be generated.
        window_width (scalar, optional): Width of the sub-sampling window.

    Returns:
        tuple:
            `x_test` used
            2d numpy array of quantiles with shape `(len(x_test, len(quantiles)))`.

    """
    quantiles = np.asarray(quantiles)
    if np.any(quantiles < 0) or np.any(quantiles > 1):
        raise ValueError('Quantiles must be in [0, 1]')

    if window_width is None:
        window_width = (np.nanmax(x) - np.nanmin(x)) / 16

    if x_test is None:
        x_test = np.linspace(np.nanmin(x) + window_width, np.nanmax(x) - window_width, npoints)
    else:
        x_test = np.atleast_1d(x_test)
        npoints = len(x_test)

    q_test = np.zeros((npoints, len(quantiles)))
    for i in range(npoints):
        y_subsample = y[np.abs(x_test[i] - x) < window_width]
        if len(y_subsample) == 0:
            # No data points had x within the window
            q_test[i] = np.full(len(quantiles), np.nan)
        else:
            # Compute the quantiles of y for the data points with x within the window.
            q_test[i] = np.percentile(y_subsample, quantiles * 100)
    return (x_test, q_test)



def running_quantiles_loess(x, y, quantiles, x_result=None, npoints=50):
    if x_result is None:
        x_result = np.linspace(np.nanmin(x), np.nanmax(x), npoints)
    else:
        npoints = len(x_result)
    q_result = np.zeros((npoints, len(quantiles)))

    for i in range(npoints):
        weights = loess_weights(x_result[i], x)
        print(weights)
        for j in range(len(quantiles)):
            q_result[i, j] = wquantiles.quantile(y, weights, quantiles[j])
    return (x_result, q_result)



def loess_weights(x_0, x):
    """Get the LOESS weights for an array around a given point.

    See https://en.wikipedia.org/wiki/Local_regression#Weight_function

    Arguments:
        x_0: test point
        x: array of data points

    Returns:
        array: LOESS weight from x_0 at each point in x.
    """
    normalizer = max([np.nanmax(x) - x_0, x_0 - np.nanmin(x)])
    return (1 - (np.abs(x - x_0) / normalizer)**3 )**3


def example():
    """make example quantile plots"""
    # Generate random input variable samples
    x = np.random.randn(1000)


    # Independent variables: quantiles of y should not vary with x.
    y = np.random.randn(1000)
    quantile_plot(x, y)
    plt.legend()
    plt.title('Independent')
    plt.xlabel('$x$')
    plt.ylabel('$y$')

    # Dependent but homoscedastic variables: quantiles of y should vary with
    # x, but inter-quantile spread should not vary with x.
    plt.figure()
    y = x**2 + np.random.randn(1000)
    quantile_plot(x, y)
    plt.legend()
    plt.title('Dependent but homoscedastic')
    plt.xlabel('$x$')
    plt.ylabel('$y$')

    # Dependent and heteroscedastic variables: quantiles of y should vary with
    # x, and inter-quantile spread should also vary with x.
    plt.figure()
    y = x**2 +  x * np.random.randn(1000)
    quantile_plot(x, y)
    plt.legend()
    plt.title('Dependent and heteroscedastic')
    plt.xlabel('$x$')
    plt.ylabel('$y$')

    plt.show()


if __name__ == '__main__':
    example()
