# analysis.py
# by James Fulford


from datetime import datetime as dt
from matplotlib import pyplot as plt
from tools import *
from matplotlib.font_manager import FontProperties
import numpy as np
from analytics import pearson_r
import analytics
import math
import time

start_date = dt(2016, 11, 8)
round_digits = 3

def rnd(num):
    return round(num, round_digits)

# load headers
headers, n = load_csv("2.csv")

# # GROWTH BY WEEK
# # graphical exploration
# columns_to_analyze_by_week = [2, 4, 7]
# for var in columns_to_analyze_by_week:

#     # go through all accounts and plot weekly data
#     for account in map(str, range(1, 9)):
#         plt.plot(get_data_by_week(account + ".csv", start_date, var))

#     # make and save chart
#     plt.title("Dataset: " + headers[0][var].replace("Daily ", "") + " by weeks since " + start_date.strftime("%m/%d/%Y"))
#     plt.savefig(headers[0][var].replace("Daily ", "") + ".png")

#
# Total likes
#



from scipy.optimize import curve_fit

fig, ax = plt.subplots()
colors = ['m', 'g', 'r', 'c', 'b', 'y', 'k', "0.55"]

accounts = []
# Gathering and plotting data
for account in map(str, range(1, 9)):
    likes = get_data_by_day(account + ".csv", 1)
    ax.plot(range(len(likes)), likes, "--o", color=colors[int(account) - 1], label=account)
    accounts.append(likes)


# Fitting models to data, and plotting models


def line(x, m, b):
    return (m * x) + b

def metalog(mini, xoffset):
    """
    Returns a logistic formula lowerbounded by given minimum
    """
    def logistic(x, K, C, r):
        # expval = (-r * x) + (r * xoffset)
        expval = (-r * x) + (r * xoffset)
        return mini + (K / (1 + (C * np.exp(expval))))
    return logistic


def r_square(measures, predictions):
    """
    https://en.wikipedia.org/wiki/Coefficient_of_determination
    Seems legit.
    """
    mean = analytics.mean(measures)

    residuals = map(lambda i: measures[i] - predictions[i], range(len(predictions)))

    ss_tot = sum(map(lambda y: (y - mean) ** 2, measures))
    ss_res = sum(map(lambda e: e ** 2, residuals))

    return 1 - (float(ss_res) / float(ss_tot))


for i in range(len(accounts)):
    likes = accounts[i]
    xdata = np.linspace(0, len(likes) - 1, 100)

    rang, above_cutoff = range(len(likes)), likes
    for j in range(len(likes)):
        if likes[j] != 0:
            rang = range(j, len(likes))
            above_cutoff = likes[j:]
            break
    if len(rang) > 1:
        #
        # Choose model:
        #
        fitting = metalog(min(above_cutoff), min(rang)); isline = False
        # fitting = line; isline = True

        #
        #
        #
        params, vari = curve_fit(fitting, rang, above_cutoff)
        model = lambda x: fitting(x, *params)
        predictions = map(model, xdata)

        fmt = "{params}\nr^2: {r2}"

        print i + 1, "-" * 20
        # for x in range(len(rang)):
        #     print (above_cutoff[x] - model(rang[x])) ** 1
        if not isline:
            print "K  :", rnd(params[0] + min(above_cutoff))
            print "r  :", rnd(params[2])
            print "lnC/r:", rnd(math.log(params[1]) / params[2])
        else:
            print "m  :", rnd(params[0])
            print "r  :", rnd(pearson_r(rang, above_cutoff)), rnd(pearson_r(rang, above_cutoff) ** 2)

        print "R^2:", rnd(r_square(above_cutoff, map(model, rang)))
        print
        if i + 1 == 6:
            print rang, above_cutoff

        ax.plot(xdata, predictions, "-", color=colors[i])


# Chart details and saving chart
fontP = FontProperties()
fontP.set_size('small')
plt.title(headers[0][1] + " by week since " + start_date.strftime("%m/%d/%Y"))
legend = ax.legend(loc='upper right', shadow=True, prop=fontP)
frame = legend.get_frame()
frame.set_facecolor('0.90')
for label in legend.get_texts():
    label.set_fontsize('large')
for label in legend.get_lines():
    label.set_linewidth(1.5)
plt.savefig(headers[0][1] + ".png")
