# tools.py
# by James Fulford


from datetime import datetime as dt


def load_csv(path):
    # Loads data in csv at given path.
    # (path includes extension, i.e. ".csv")
    with open(path) as phile:
        content = phile.read()
        lines = content.split("\n")
        headers = lines[0:1]
        headers = map(lambda x: x.split(","), headers)

        data = lines[2:]
        data = map(lambda x: x.split(","), data)
    return headers, data

def get_data_by_week(path, start_date, col):
    headers, data = load_csv(path)

    #
    # Go through the data:
    #

    # index represents weeks after start_date,
    # value holds sum of values of days in that week
    by_date = [0 for i in range((len(data) / 7))]

    # add in the data
    for i in range(len(data)):
        try:
            # find the date (first column)
            date = dt.strptime(data[i][0], "%Y-%m-%d")
        except:
            # if have trouble parsing date,
            # line is likely empty.
            # skip the line, move onto the next one.
            continue

        # Which week does this day belong to?
        week = (date - start_date).days / 7  # does integer division

        # What is this day's value?
        value = data[i][col]

        # Complete data is not available for week 13,
        # so we exclude it from this analysis
        if week > 12:
            continue

        # Add value to the running sum for this week
        if len(value) > 0:
            by_date[week] += int(value)
    return by_date


def get_data_by_day(path, col):
    headers, data = load_csv(path)
    dat = [0 for i in range((len(data) / 7))]
    for i in range(len(data)):
        if i / 7 > 12:
            continue
        try:
            dat[i / 7] = max(dat[i / 7], int(data[i][col]))
        except:
            # value was blank - would be 0
            # dat's value would be >= 0, so no need to update anything
            continue
    return dat


