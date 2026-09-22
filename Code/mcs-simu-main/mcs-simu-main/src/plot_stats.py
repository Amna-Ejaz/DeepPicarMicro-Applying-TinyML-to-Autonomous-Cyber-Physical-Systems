# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import dataclasses
import matplotlib.pyplot as plt
import json
import pandas
import seaborn
from pathlib import Path

import numpy as np
import csv
from ast import literal_eval


def plot_diagram(log_filename):
    x1 = [0, 1, 2, 3, 4, 5, 6]
    y1 = []

    with open(log_filename, newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=",")

        row_idx = 1
        for row in csvdata:
            print(row)
            r = row
            y1.append([])

            for it in r:
                y1[row_idx-1].append(int(it))

            row_idx += 1

        print(y1)

        y_pos = np.arange(len(y1))

        a = np.array(y1)
        a.transpose()
        print(a)

        # plot the result
        fig = plt.figure()
        seaborn.boxplot(a)
        plt.xticks(x1, ["#jobs", "#jobs_exe", "#overruns", "#DM", "H-DM", "L-DM", "JNE"])

        #plt.legend()
        plt.title(log_filename)
        plt.show()


if __name__ == "__main__":
    for utilization in [0.5, 0.6, 0.7, 0.8, 0.9]:
        plot_diagram(f"../logs/{utilization}/0/raw.csv")
