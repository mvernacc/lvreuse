"""Useful tools and methods"""
import math

def cost_reduction_factor(p, prod_nums_list):
    """Calculate the average cost reduction factor for a given production run.

    Arguments:
        p: learning factor, p<=1
        prod_nums_list: list of consecutive production numbers to consider 

    Returns:
        Average cost reduction factor."""

    f4_sum = 0
    for prod_num in prod_nums_list:
        f4_sum += prod_num**(math.log(p)/math.log(2.))
    num_prod_units = len(prod_nums_list)
    f4_avg = f4_sum/num_prod_units

    return f4_avg

if __name__ == '__main__':

    f4_avg = cost_reduction_factor(0.9, range(1,10))
    print f4_avg