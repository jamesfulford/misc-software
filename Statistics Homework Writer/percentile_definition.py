def percentile(ds, perc):
    """
    Calculates the score that matches with the given percentile.
    """
    percentile = perc
    if perc >= 1:
        percentile = float(perc) / 100
    # percentile is now a decimal < 100

    sorted_list = sorted(ds)

    # take percentile of (n - 1).
    index = ((len(ds) - 1) * float(percentile))

    # Is it an integer?
    if abs(index - int(index)) < .0001:  # "close enough"
        # Yes, it is an integer.
        # Return the corresponding value.
        return sorted_list[int(index)]

    # Otherwise, is between two integers: upper and lower.
    upper = int(round(index + .5))
    lower = int(round(index - .5))

    # Final calculation calls for weighted average
    # based on how close index is to the other value.
    upshare = 1 - float(upper - index)
    lowshare = 1 - float(index - lower)

    # Return the weighted average of upper's and lower's corresponding values.
    return (sorted_list[upper] * upshare) + (sorted_list[lower] * lowshare)

def five_point_summary(ds):
    return (max(ds), percentile(ds, 25), percentile(ds, 50), percentile(ds, 75), min(ds))