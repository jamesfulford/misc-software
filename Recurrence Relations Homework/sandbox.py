# sandbox.py
# by James Fulford

from matplotlib import pyplot as plt
import numpy as np


def page(list1, list2):
    assert len(list1) is len(list2)
    temp = []
    for i in range(len(list1)):
        temp.append(list1[i])
        temp.append(list2[i])
    return temp

def fall(func, initial, delta=.0001, depth=100):
    init = initial
    close_enough = False
    dep = depth
    while not close_enough and dep != 0:
        res = func(init)
        close_enough = abs(res - init) < delta
        init = func(init)
        dep += -1
    if dep is 0:
        print "After", depth, "fall steps; stopping."
    return init

def putt(func, initial, delta=.0001, depth=100):
    xdata = [initial]
    ydata = [0]
    dep = depth
    init = initial
    close_enough = False
    while (not close_enough and dep != 0) and abs(init - initial) < 10:
        res = func(init)
        xdata.append(init)
        ydata.append(res)
        xdata.append(res)
        ydata.append(res)
        close_enough = abs(res - init) < delta
        init = func(init)
        dep += -1
    return xdata, ydata

def plot(func, initial):
    fig, ax = plt.subplots()
    xsct, ysct = putt(f, initial, depth=20)
    # mini, maxi = min(xsct), max(xsct)
    # diff = (maxi - mini) * .5
    # print diff
    # mini, maxi = mini - diff, maxi - diff
    rng = np.linspace(-4, 6, num=100)
    data = map(func, rng)
    ax.plot(rng, rng, rng, data)
    ax.plot(xsct, ysct)
    ax.grid(True, which="both")
    return ax

####################################


def f(x):
    return (3 * x) - (x ** 2) + 3


def x(n):
    if n is 0:
        return 4242
    return f(x(n - 1))

initial_condition = 3.5
# print "x-bar ", round(fall(f, initial_condition, depth=5), 3)
ax = plot(f, initial_condition)
ax.grid()
plt.savefig("Cobweb 1.png")
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')
plt.show()

####################################


def f(x):
    return 1.4 * x - .2 * x ** 2 + 3

initial_condition = 2.93
# print "x-bar ", round(fall(f, initial_condition, depth=20), 3)
ax = plot(f, initial_condition)
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')
plt.savefig("Cobweb 2.png")
plt.show()
