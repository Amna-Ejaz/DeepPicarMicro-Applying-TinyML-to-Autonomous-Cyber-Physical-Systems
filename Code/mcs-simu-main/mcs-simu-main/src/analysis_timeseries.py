# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import json
import numpy as np
import pandas as pd
import seaborn
import scipy
import csv
import cpd
import matplotlib.pyplot as plt
import ruptures as rpt
import matplotlib.cm as cm

from events import EventID

numer_of_trials = 1
number_of_inputs = 3
number_of_tasks = 10

length_of_data = 200000+1
switching_point = int(length_of_data / 2)

sampling_window = 2000   # [todo] adaptive window size [cautious of words: trying to find classic reference; not to re-invert wheel badly]
overlap_size = int(sampling_window * 0.50)

# [todo] earth moving distance
# [todo] differential KS test?
# [todo] sparsity of the data


# iterative the data with a sliding window
# x_in and y_in are discrete values!
# output: data after applying the sliding window
# output_before: data before the switching point
# output_after: data after the switching point
def sampling_data_with_sliding_window(x_in, y_in, sampling_window_size=1000):
    # expanding data
    x = np.arange(length_of_data)
    y = np.zeros(length_of_data)

    for x_i, x_idx in enumerate(x_in):
        try:
            y[x_idx] += y_in[x_i]
        except Exception as exc:
            print(exc)
            print(x_idx)

    # iterate x and y
    x_output = np.array([])
    y_output = np.array([])
    idx = sampling_window_size
    while length_of_data-1 >= idx+sampling_window_size:
        x_this = x[idx]
        y_this = sum(y[idx:idx+sampling_window_size])
        #print(x_this, y_this)
        x_output = np.append(x_output, x_this)
        y_output = np.append(y_output, y_this)
        idx += overlap_size

    return x_output, y_output


color_palette = ['red', 'orange', 'blue', 'yellow', 'green', 'purple', 'pink', 'deepskyblue', 'cyan', 'navy']


def plot_metrics_and_stat_test(log_filename):
    with open(log_filename, newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=",")

        fig, axs = plt.subplots(6, 3)  # sharex=True, sharey=True

        for i in range(numer_of_trials):
            csvfile.seek(0)  # reset file handler
            x = []
            y = []
            for k in range(number_of_inputs):
                x.append([])
                y.append([])

            # iterate the csv line by line
            for row in csvdata:
                #print(row)
                if int(row[0]) == i:
                    event_str = row[2].strip()
                    if event_str == "EventID.Overrun":
                        j = 0
                    elif event_str == "EventID.TaskDrop":
                        j = 1
                    else:
                        j = 2
                    x[j].append(int(row[1]))
                    y[j].append(int(row[3]))

            # plot diagram per input
            for j in range(number_of_inputs):
                if len(x[j]) != 0:
                    # plot the subplot
                    #axs[i, j].stem(x[j], y[j])

                    # analyze data
                    x_output, y_output = sampling_data_with_sliding_window(x[j], y[j])

                    mask = x_output <= switching_point

                    y_output_before = y_output[mask]
                    y_output_after = y_output[np.invert(mask)]

                    mask_1 = x_output >= switching_point - sampling_window
                    mask_2 = x_output <= switching_point + sampling_window

                    y_output_right_before = y_output[mask & mask_1]
                    y_output_right_after = y_output[mask & mask_2]

                    axs[j*2, 0].plot(x_output, y_output, '-x', color=color_palette[j])
                    axs[j*2, 1].hist(y_output_before, color=color_palette[j])
                    axs[j*2, 2].hist(y_output_after, color=color_palette[j])
                    axs[j*2+1, 1].hist(y_output_right_before, color=color_palette[j])
                    axs[j*2+1, 2].hist(y_output_right_after, color=color_palette[j])

                    # if not y_output_before and not y_output_after and not y_output_right_after and not y_output_right_before:

                    # earth mover's distance
                    EMD1 = scipy.stats.wasserstein_distance(y_output_before, y_output_after)
                    EMD2 = scipy.stats.wasserstein_distance(y_output_right_before, y_output_right_after)
                    print("----------------------------------------")
                    print(f"The earth mover's distance is: {EMD1}")
                    print(f"The earth mover's distance (small window) is: {EMD2}")

                    # ks test
                    KS1 = scipy.stats.ks_2samp(y_output_before, y_output_after)
                    KS2 = scipy.stats.ks_2samp(y_output_right_before, y_output_right_after)

                    if KS1.pvalue < 0.05:
                        KS1_bool = "Rejected"
                        axs[j * 2, 1].set_facecolor('xkcd:salmon')
                        axs[j * 2, 2].set_facecolor('xkcd:salmon')
                    else:
                        KS1_bool = "Not Rejected"

                    if KS2.pvalue < 0.05:
                        KS2_bool = "Rejected"
                        axs[j * 2 + 1, 1].set_facecolor('xkcd:salmon')
                        axs[j * 2 + 1, 2].set_facecolor('xkcd:salmon')
                    else:
                        KS2_bool = "Not Rejected"

                    print(f"The KS test gives {KS1_bool}, {KS1}")
                    print(f"The KS test (small window) gives {KS2_bool}, {KS2}")

        # set titles
        plt.figure(fig.number)

        axs[0, 0].set_title("# of Overrun")
        axs[2, 0].set_title("# of JNE")
        axs[4, 0].set_title("# of DM")

        fig.suptitle(f"Window size={sampling_window}, Overlap size={overlap_size} --- {log_filename}")

        # show (and save) figure
        plt.savefig(f"../figures/fig_{sampling_window}.png", dpi=300, format="png")
        #plt.show()
        plt.close()


def plot_response_times(log_filename):
    # load data from the csv
    with open(log_filename, newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=",")
        csvfile.seek(0)  # reset file handler

        x = []  # 2D array to store time (per task)
        y = []  # 2D array to store data (per task)
        for k in range(number_of_tasks):
            x.append([])
            y.append([])

        # iterate the csv line by line, and load data into its relevant arrays (x[i], y[i])
        trial_number = 0
        for row in csvdata:
            #print(row)
            if int(row[0]) == trial_number:
                j = int(row[2])           # taskid
                x[j].append(int(row[1]))  # timestamp
                y[j].append(int(row[3]))  # response time

        distance1 = []
        distance2 = []
        distance3 = []
        distance4 = []

        CTBL1 = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}
        CTBL2 = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}
        CTBL3 = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}
        CTBL4 = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

        # cpd analysis and plot the results
        for task_id in range(number_of_tasks):
            # convert dataset into numpy
            signal = np.array(y[task_id])

            # CUSUM cpd
            #cpd.cusum(signal)

            # bayesian cpd
            R = cpd.bayesian_cpd(signal)

            fig, ax = plt.subplots(3, figsize=[18, 16], sharex=True)
            sparsity = 5  # only plot every fifth data for faster display
            ax[0].plot(signal)
            ax[1].pcolor(np.array(range(0, len(R[:, 0]), sparsity)),
                         np.array(range(0, len(R[:, 0]), sparsity)),
                         -np.log(R[0:-1:sparsity, 0:-1:sparsity]),
                         cmap=cm.Greys, vmin=0, vmax=30)
            Nw = 10
            ax[2].plot(R[Nw, Nw:-1])
            plt.savefig('../figures/'+str(task_id) + '_bayesian' + '.png')
            plt.close()

            # rpt
            fig, axs = plt.subplots(4)  # sharex=True, sharey=True

            ground_truth = int(len(signal) / 2)

            bkps = cpd.rpt_pelt(signal)
            cpd.plot_change_points(signal, bkps, axs[0], 'CPD: Pelt Search Method')
            CTBL, distance = cpd_stat(bkps, ground_truth)
            if distance != -1:
                distance1.append(distance)
            ctbl_add(CTBL1, CTBL)

            bkps = cpd.rpt_binseg(signal)
            cpd.plot_change_points(signal, bkps, axs[1], 'CPD: Binary Segmentation Search Method')
            CTBL, distance = cpd_stat(bkps, ground_truth)
            if distance != -1:
                distance2.append(distance)
            ctbl_add(CTBL2, CTBL)

            bkps = cpd.rpt_window(signal)
            cpd.plot_change_points(signal, bkps, axs[2], 'CPD: Window-Based Search Method')
            CTBL, distance = cpd_stat(bkps, ground_truth)
            if distance != -1:
                distance3.append(distance)
            ctbl_add(CTBL3, CTBL)

            bkps = cpd.rpt_dynamic(signal)
            cpd.plot_change_points(signal, bkps, axs[3], 'CPD: Dynamic Programming Search Method')
            CTBL, distance = cpd_stat(bkps, ground_truth)
            if distance != -1:
                distance4.append(distance)
            ctbl_add(CTBL4, CTBL)

            #rpt.display(signal, bkps)
            fig.tight_layout()

            # save file
            util = log_filename[12:-8]  # [todo] make this proper
            plt.savefig('../figures/' + str(util) + '_t' + str(task_id) + '_rupture' + '.png')

        print(util)

        print("\n Distances:")
        print(distance1)
        print(distance2)
        print(distance3)
        print(distance4)

        print("\n Confuse Table:")
        print([CTBL1['TP'], CTBL1['TN'], CTBL1['FP'], CTBL1['FN']])
        print([CTBL2['TP'], CTBL2['TN'], CTBL2['FP'], CTBL2['FN']])
        print([CTBL3['TP'], CTBL3['TN'], CTBL3['FP'], CTBL3['FN']])
        print([CTBL4['TP'], CTBL4['TN'], CTBL4['FP'], CTBL4['FN']])

        print(" ")

        # Detect change points using the segneigh model [todo] not fully working
        #change_points = segneigh(y)
        #print(change_points)

        return


def cpd_stat(bkps, ground_truth):
    CTBL = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}  # confusion table

    detected = 0
    distance = -1

    if len(bkps) <= 1:
        CTBL["FN"] += 1

    if bkps:
        for bkps_i in bkps[:-1]:
            if bkps_i < ground_truth:
                CTBL["FP"] += 1
            else:
                if not detected:
                    CTBL["TP"] += 1
                    detected = 1
                    distance = bkps_i - ground_truth
                else:
                    CTBL["FP"] += 1
    else:
        CTBL["FN"] += 1

    return CTBL, distance


def ctbl_add(table1, table2):
    table1["TP"] += table2["TP"]
    table1["TN"] += table2["TN"]
    table1["FP"] += table2["FP"]
    table1["FN"] += table2["FN"]


if __name__ == "__main__":
    # for util_idx in range(1, 20):
    #     util_factor = ((util_idx + 1) * 0.1)
    #     utilization = 1 * util_factor
    #     plot_diagram(f"../logs/log_{round(utilization,2)}.csv")

    # for sampling_window in range(100, 50000, 1000):
    #     overlap_size = int(sampling_window * 0.50)
    #     plot_metrics_and_stat_test(f"../logs/log_1.2.csv")

    plot_metrics_and_stat_test(f"../logs/log_0.5.csv")
    plot_response_times(f"../logs/log_0.5_raw.csv")

    # or loop through parameters:
    # for arg in range(1, 21):
    #     utilization = arg / 10.0
    #     plot_response_times(f"../logs/log_{round(utilization, 2)}_raw.csv")
