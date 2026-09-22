def interpolate(x0, y0, x1, y1, x):
    """
    Linear interpolation between two values.
    """
    y_renamed = (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

    return y_renamed