from numpy import percentile


def get_upper_and_lower_bounds(dataset):
    upper_quartile = percentile(dataset, 75)
    lower_quartile = percentile(dataset, 25)
    interquartile_range = upper_quartile - lower_quartile
    return (lower_quartile - interquartile_range * 3), (upper_quartile + interquartile_range * 3)
