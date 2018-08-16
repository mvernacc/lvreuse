def indirect_ops_cost(launch_rate, launch_provider_type):

    ioc_data = {'A': [65, 49, 42, 38, 35, 33, 31, 30, 29, 27, 26, 25],
                'B': [45, 34, 29, 27, 24, 23, 22, 21, 20, 19, 18, 17],
                'C': [32, 24, 22, 19, 18, 17, 16, 15, 14, 13, 12, 11]}

    ioc_line = ioc_data[launch_provider_type]
    ioc_cost = ioc_line[launch_rate - 1]

    return ioc_cost
