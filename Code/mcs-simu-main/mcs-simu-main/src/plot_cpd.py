# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import dataclasses
import matplotlib.pyplot as plt
import numpy as np
import csv
import ast


def plot_cpd_stat():
    fig1, axs1 = plt.subplots(1, 11)
    fig2, axs2 = plt.subplots(4, 11)

    idx = 0
    i = 0

    x = range(10)
    labels = ["TP ", "FP", "FN"]

    with open("../performance.txt") as my_file:
        data = my_file.read().splitlines()

        while idx < 88:
            a = ast.literal_eval(data[idx + 0])
            b = ast.literal_eval(data[idx + 1])
            c = ast.literal_eval(data[idx + 2])
            d = ast.literal_eval(data[idx + 3])

            e = ast.literal_eval(data[idx + 4])
            tp1 = e[0]
            fp1 = e[2]
            fn1 = e[3]
            y1 = np.vstack([tp1, fp1, fn1])

            f = ast.literal_eval(data[idx + 5])
            tp2 = f[0]
            fp2 = f[2]
            fn2 = f[3]
            y2 = np.vstack([tp2, fp2, fn2])

            g = ast.literal_eval(data[idx + 6])
            tp3 = g[0]
            fp3 = g[2]
            fn3 = g[3]
            y3 = np.vstack([tp3, fp3, fn3])

            h = ast.literal_eval(data[idx + 7])
            tp4 = h[0]
            fp4 = h[2]
            fn4 = h[3]
            y4 = np.vstack([tp4, fp4, fn4])

            # plot 1
            axs1[i].boxplot([a, b, c, d])
            axs1[i].set_xticklabels(['Pelt', 'BinSeg', 'Window-based', 'Dynamic'], rotation=90)
            axs1[i].set_title("Util=" + str((i+10) / 10.0))
            axs1[i].set_ylim(bottom=0, top=500)

            # plot 2
            axs2[0, i].stackplot(x, y1, labels=labels)
            axs2[0, 0].legend(loc='upper left')
            axs2[0, 0].set_ylabel('Pelt')

            axs2[1, i].stackplot(x, y2)
            axs2[1, 0].set_ylabel('Binary Segmentation')

            axs2[2, i].stackplot(x, y3)
            axs2[2, 0].set_ylabel('Window-based')

            axs2[3, i].stackplot(x, y4)
            axs2[3, 0].set_ylabel('Dynamic')

            i += 1
            idx += 8

    plt.show()


if __name__ == "__main__":
    plot_cpd_stat()
