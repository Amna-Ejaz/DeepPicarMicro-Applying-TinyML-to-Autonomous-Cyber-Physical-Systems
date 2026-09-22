import pickle
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pprint


def load_stat_from_pickle(log_file_dir):
    with open(log_file_dir + "data.pkl", "rb") as f:
        perf = pickle.load(f)

    return perf


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(width=200, compact=True)

    trial_num = 20
    policy_num = 5
    policies = ['FPPS', 'AMC_P', 'AMC_RH', 'AMC_DT', 'AMC_DT_P']

    # collect data from log dumps
    jne_all = [[], [], [], [], []]
    util_all = [[], [], [], [], []]

    for util in [0.5, 0.6, 0.7, 0.8, 0.9]:  # group
        for policy in range(policy_num):
            for idx in range(trial_num):
                log_file_folder = f"../logs/{util}/{idx}/{policy}/"
                dat = load_stat_from_pickle(log_file_folder)

                jne_all[policy].append(dat.cnt_overruns)    # data
                util_all[policy].append(util)   # group

    # group into Pandas dataframe and plot with Seaborn
    df = pd.DataFrame({'Group': util_all[0],
                       'FPPS': jne_all[0],
                       'AMC_P': jne_all[1],
                       'AMC_RH': jne_all[2],
                       'AMC_DT': jne_all[3],
                       'AMC_DT_P': jne_all[4]})
    df2 = df[['Group', 'FPPS', 'AMC_P', 'AMC_RH', 'AMC_DT', 'AMC_DT_P']]

    dd = pd.melt(df2, id_vars=['Group'], value_vars=['FPPS', 'AMC_P', 'AMC_RH', 'AMC_DT', 'AMC_DT_P'], var_name='policies')
    sns.boxplot(x='Group', y='value', data=dd, hue='policies')
    plt.show()
