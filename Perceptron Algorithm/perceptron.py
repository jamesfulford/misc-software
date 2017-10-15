# perceptron.py
# by James Fulford


"""
#
# Instructions on how to format CSV
#

For a SAMPLE CSV, run this script without
"perceptron_training_data.csv" in the same folder.

1. Put in all points (any number of dimensions/columns), one per row.
   - Must be same dimension for all points!
   - All coordinates must be numbers!
   - As many points as you wish!
2. Include on each row which class they belong to (True, False)
   + Case Insensitive
   + Can be in any column (first, last, middle)
3. Run the script!
   * Outputs final weight vector if data is linearly seperable
   * If data is 2-dimensonal, a graph will be shown!
   * If data is 2- or 3-dimensional, the equation will be shown

Not linearly seperable? Try again!
"""


import numpy as np
from numpy import array
import os
import csv


# Make sure we can still work if matplotlib not installed
try:
    from matplotlib import pyplot
    has_matplotlib = True
except Exception:
    has_matplotlib = False


#
# Define some useful functions
#


def dot(v1, v2):
    # returns dot product of two vectors
    return sum(v1 * v2)


def augment(v):
    # augments given vector
    w = list(v)
    w.append(1)
    return array(w)


def sign(i):
    # returns sign of number
    if int(i) < 0:
        return -1
    elif int(i) > 0:
        return 1
    elif i is False:
        return -1
    else:
        return 0


def isnumber(i):
    try:
        float(i)
        return True
    except ValueError:
        return False


def get_bool(b):
    b = b.title()
    if b == "True":
        return True
    else:
        return False


def perceptron(dataset, targets, w=None, max_recur=800, show_work=False):
    """
    Runs perceptron algorithm.
    + dataset is [] of np.array, each of same length
    + targets is [] of booleans (depending on corresponding np.array's class)
    - w is initial weight vector (np.array) - defaults to 0's
    - max_recur is number of iterations before declaring non-convergence - defaults to 800
    - show_work is boolean: True to print whenever w is modified - defaults to False

    ! If dataset is not linearly seperable, raises Exception on iteration==max_recur.
    """

    # Handle initial weight vector
    if w is not None:
        assert len(w) is len(dataset[0])
        w = augment(w)
    else:
        w = augment(np.zeros(len(dataset[0])))

    # augment our dataset vectors
    data = map(augment, dataset)

    # prepare to iterate
    count = 0  # number of successes in a row.
    i = 0  # position in array (wraps around)
    j = 0  # total iterations

    if show_work:
        # print initial weight vector
        print str(j) + ": w = " + str(w)

    #
    # Begin iterating
    #
    while True:
        res = sign(dot(data[i], w))
        res = sign(res)

        tar = sign(targets[i])

        # Do the signs match?
        if res == tar:
            # success - increase success count by 1
            count += 1
        else:
            # failure - adjust weight
            count = 0
            w = w + (data[i] * sign(targets[i]))

            if show_work:
                # print new weight vector
                print str(j) + ": w = " + str(w)

        # Should we stop?
        if count >= len(data):
            # Yes, we've succeeded on all data points.
            if show_work:
                print "Iterations to completion:", j
            return w
        else:
            # No, move onto next data point.
            i += 1
            j += 1
            i = i % len(data)

        # Are we converging?
        if j > max_recur:
            # No, not fast enough.
            raise Exception("Did not converge.")


def test(pt, w):
    """
    Use perceptron output to determine class of given point
    """
    return sign(dot(augment(pt), w))

#
# Get data and targets
#

datapath = "perceptron_training_data.csv"
if not os.path.exists(datapath):
    # Generate sample csv
    with open(datapath, "w") as phile:
        wr = csv.writer(phile)
        sample_data = [
            [-1, 0, True],
            [0, -2, True],
            [-5, 5, True],
            [-8, -8, True],

            [-3, 5, False],
            [0, 0, False],
            [1, 1, False],
            [4, -3, False]
        ]
        for d in sample_data:
            wr.writerow(map(unicode, d))

#
# Read data from csv
#
targ = []
data = []
with open(datapath) as phile:
    read = csv.reader(phile)
    for row in read:
        # Append bool to targ
        t = filter(lambda x: x.title() in ["True", "False"], row)[0]
        targ.append(get_bool(t))

        # Append np.array to data of just the numbers
        d = filter(isnumber, row)
        data.append(map(float, d))


try:
    result = perceptron(data, targ, show_work=True)
    print "Final Weight Vector:", result

    #
    # Print Equation (only with 2 or 3 variables)
    #
    if len(data[0]) in [2, 3]:
        if len(data[0]) == 2:
            variables = array(["x", "y", ""])
        elif len(data[0]) == 3:
            variables = array(["x", "y", "z", ""])
        s = []
        for i in range(len(result)):
            s.append(str(result[i]) + variables[i])
        print " + ".join(s) + " = 0"

    #
    # Plot equation (only 2 variables)
    #
    if len(data[0]) in [2] and has_matplotlib:
        def f(x):
            r = result
            return ((-r[0] * x) - r[2]) / r[1]
        domain = map(lambda p: p[0], data)
        mini, maxi = min(domain), max(domain)
        domain = np.linspace(mini, maxi, num=10 * (maxi - mini))
        pyplot.plot(domain, map(f, domain))
except Exception, e:
    print e

if len(data[0]) in [2]:
    if has_matplotlib:
        # Plot data that has True in target
        cls1 = map(lambda j: data[j], filter(lambda i: targ[i], range(len(data))))
        pyplot.scatter(map(lambda x: x[0], cls1), map(lambda x: x[1], cls1), c="r")

        # Plot data that has False in target
        cls2 = map(lambda j: data[j], filter(lambda i: not targ[i], range(len(data))))
        pyplot.scatter(map(lambda x: x[0], cls2), map(lambda x: x[1], cls2), c="g")

        pyplot.show()
    else:  # can't graph
        print "Install matplotlib in order to see a graph!"
        print "\t$ pip install matplotlib"
