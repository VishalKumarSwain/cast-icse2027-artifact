def interpolate(x0, y0, x1, y1, x):
    """
    Linear interpolation between two values.
    """
    y = (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

    return y
