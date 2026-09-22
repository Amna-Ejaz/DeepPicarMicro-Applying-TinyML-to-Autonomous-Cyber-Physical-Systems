# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

# CPD: Algorithms for Change Point Detection (CPD)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from detecta import detect_cusum
import ruptures as rpt
import changefinder

import bayesian_changepoint_detection.online_changepoint_detection as oncd
from functools import partial


def bayesian_cpd(x):
    R, maxes = oncd.online_changepoint_detection(x, partial(oncd.constant_hazard, 100),
                                                 oncd.StudentT(0.1, .01, 1, 0))

    return R


def cusum(x):
    ta, tai, taf, amp = detect_cusum(x, threshold=100, drift=50, ending=True, show=True, ax=None)

    return ta, tai, taf, amp


# Changepoint detection with the Pelt search method
def rpt_pelt(x):
    # detection
    kernel = "rbf"
    algo = rpt.Pelt(model=kernel, min_size=3, jump=5).fit(x)
    bkps = algo.predict(pen=10)

    return bkps


# Changepoint detection with the Binary Segmentation search method
def rpt_binseg(x, n_bkps=1):
    model = "l2"
    algo = rpt.Binseg(model=model).fit(x)
    bkps = algo.predict(n_bkps)

    return bkps


# Changepoint detection with window-based search method
def rpt_window(x, n_bkps=1):
    model = "l2"  # "l1", "rbf", "linear", "normal", "ar"
    algo = rpt.Window(width=80, model=model).fit(x)
    bkps = algo.predict(n_bkps)

    return bkps


# Changepoint detection with dynamic programming search method
def rpt_dynamic(x, n_bkps=1):
    model = "l1"
    algo = rpt.Dynp(model=model, min_size=3, jump=5).fit(x)
    bkps = algo.predict(n_bkps)

    return bkps


def change_finder(x):
    cf = changefinder.ChangeFinder()
    scores = [cf.update(p) for p in x]

    return scores


def plot_change_points(signal, bkps, ax, title):
    ax.plot(signal)
    for x in bkps:
        ax.axvline(x, lw=2, color='red')
    ax.title.set_text(title)
