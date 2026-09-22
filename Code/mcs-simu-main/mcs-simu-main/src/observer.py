# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import random

import numpy as np
import pandas as pd
import seaborn as sn

import scipy.stats
import matplotlib.pyplot as plt

from scipy.stats import truncnorm
from sklearn.metrics import confusion_matrix
from hmmlearn import hmm

from distfit import distfit


# ----------------------------------------------------------------------------------------------------------------------
# generate data from truncated normal distribution with mean, std, between [low, upp]
def get_truncated_normal(mean=0, std=1, low=0, upp=10):
    return truncnorm((low - mean) / std, (upp - mean) / std, loc=mean, scale=std)


# ----------------------------------------------------------------------------------------------------------------------
# generate a sequence with two-state Markov chain model
def state_generator(seq_len=1000):
    seq = []

    # transition probability
    transition_prob = [[0.998, 0.002],
                       [0.002, 0.998]]

    # initial state = 0
    state = 0
    seq.append(state)

    # generate sequence
    for i in range(seq_len - 1):
        if random.random() < transition_prob[state][1-state]:
            if state == 0:
                state = 1
            elif state == 1:
                state = 0
        seq.append(state)

    return seq


# ----------------------------------------------------------------------------------------------------------------------
# This generates execution times with either C(LO) or C(HI) based on the failure rate
# The failure rate will be doubled after the failure point
def et_generator(seq_len=1000, failure_point=0.5, failure_rate=0.05, failure_expansion_factor=10, BCET=10, C_LOW=20, C_HIGH=50, c_offset=[0, 10]):
    # https://stackoverflow.com/questions/36894191/how-to-get-a-normal-distribution-within-a-range-in-numpy
    rnd_data = np.array([])
    for seq_i in range(seq_len):
        # trigger point of a system state change (this is an one-off change)
        if seq_i >= round(seq_len * failure_point):
            failure_rate_this = failure_rate * failure_expansion_factor
            #C_LOW = C_LOW + 10
        else:
            failure_rate_this = failure_rate

        # generate two normal distributions, one from BCET to C_LOW; one from C_LOW to C_HIGH.
        X_lo = get_truncated_normal(mean=round((C_LOW - BCET)/2 + BCET), sd=(C_LOW - BCET)/5, low=BCET, upp=C_LOW)
        X_hi = get_truncated_normal(mean=round((C_HIGH - C_LOW)/2 + C_LOW), sd=(C_HIGH - C_LOW)/5, low=C_LOW, upp=C_HIGH)

        if random.random() >= failure_rate_this:
            # if not failure
            c_this = X_lo.rvs()
        else:
            # if failure
            c_this = X_hi.rvs()

        rnd_data = np.append(rnd_data, c_this)

    return rnd_data


# ----------------------------------------------------------------------------------------------------------------------
def et_generator_with_state(state, BCET=10, C_LOW=20, C_HIGH=50, c_offset=[0, 10]):
    # https://stackoverflow.com/questions/36894191/how-to-get-a-normal-distribution-within-a-range-in-numpy
    rnd_data = np.array([])

    seq_len = len(state)
    failure_rate = [0.000, 0.000]     # failure rate under different states

    for seq_i in range(seq_len):
        # generate two normal distributions, one from BCET to C_LOW; one from C_LOW to C_HIGH.
        X_lo = get_truncated_normal(mean=round((C_LOW - BCET)/2 + BCET), std=(C_LOW - BCET)/5, low=BCET, upp=C_LOW)
        X_hi = get_truncated_normal(mean=round((C_HIGH - C_LOW)/2 + C_LOW), std=(C_HIGH - C_LOW)/5, low=C_LOW, upp=C_HIGH)

        # deal with random failure
        if random.random() >= failure_rate[state[seq_i]]:
            # if not failure
            c_this = X_lo.rvs()
            c_this += c_offset[state[seq_i]]
        else:
            # if failure
            c_this = X_hi.rvs()
            c_this += c_offset[state[seq_i]]

        rnd_data = np.append(rnd_data, c_this)

    return rnd_data


# ----------------------------------------------------------------------------------------------------------------------
def count_identical(list1, list2):
    # Identical element summation in lists
    # using sum() + zip()
    res = sum(x == y for x, y in zip(list1, list2))

    return res


# ----------------------------------------------------------------------------------------------------------------------
def cal_confusion_table(list_actual, list_prediction):
    """ elementally compare two lists

    Args:
        list_actual : list
        list_prediction : list

    Returns:
        : list
        the output is the confusion matrix [[TP, FP], [FN, TN]]
    """

    FP, FN, TN, TP = 0, 0, 0, 0

    for x, y in zip(list_actual, list_prediction):
        if not x and y:
            FP += 1
        elif x and not y:
            FN += 1
        elif not x and not y:
            TN += 1
        elif x and y:
            TP += 1

    return [[TP, FP], [FN, TN]]


# ----------------------------------------------------------------------------------------------------------------------
t1 = [0]
v1 = [10]

t2 = [0]
v2 = [10]

def estimate_statistical(test_data):
    # generate data with ET generator
    #test_data = data_generator(seq_len=2000, failure_rate=0.05)

    # or read data from a dat file
    plt.figure()
    plt.plot(test_data)

    # I. Applying Statistical Learning
    # sliding window definition
    sliding_index = 0
    sliding_window = 50
    step_size = round(sliding_window / 2)

    while (sliding_index + sliding_window) < test_data.shape[0]:
        # sample data
        sampled_data = test_data[sliding_index:sliding_index + sliding_window]

        # Initialize distfit
        # ref: https://erdogant.github.io/distfit/pages/html/Percentile.html
        dfit = distfit(distr=['norm'])

        # Determine best-fitting probability distribution for data
        dfit.fit_transform(sampled_data)

        # Print summary of evaluated distributions
        print(dfit.summary)
        print(dfit.model)

        t1.append(sliding_index + sliding_window)
        v1.append(dfit.model['CII_max_alpha'])  # dfit.model['CII_min_alpha']

        # Plot results
        #dfit.plot()

        # Plot seperately
        #fig, ax = plt.subplots(2, 1, figsize=(20, 25))

        # fig, ax = dfit.plot(chart='pdf')
        # fig, ax = dfit.plot(chart='cdf')

        #Change or remove properties of the chart.
        # dfit.plot(chart='pdf', pdf_properties={'color': 'r'}, cii_properties={'color': 'g'}, emp_properties=None,
        #           bar_properties=None)
        # dfit.plot(chart='cdf', pdf_properties={'color': 'r'}, cii_properties={'color': 'g'}, emp_properties=None,
        #           bar_properties=None)


        # dfit.plot(chart='pdf', ax=ax[0])
        # dfit.plot(chart='cdf', ax=ax[1])
        # plt.show()


        # Change or remove properties of the chart.
        # fig, ax = dfit.plot(chart='pdf', pdf_properties={'color': 'r', 'linewidth': 3},
        #                     cii_properties={'color': 'r', 'linewidth': 3}, bar_properties={'color': '#1e3f5a'})
        # dfit.plot(chart='cdf', n_top=10, pdf_properties={'color': 'r'}, cii_properties=None, bar_properties=None, ax=ax)


        # ? Predict ?
        # y = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        # results = dfit.predict(y)
        # print(results)

        sliding_index += step_size

    # fig, ax = plt.subplots(2, 1, figsize=(20, 25))
    # ax[0].plot(test_data)
    # ax[1].plot(t1, v1)

    plt.plot(test_data)
    plt.plot(t1, v1)

    plt.show()

    return


# ----------------------------------------------------------------------------------------------------------------------
# Bayesian estimation
def compute_posterior(prior=0.074, sensitivity=0.90, specificity=0.99):
    likelihood = sensitivity  # p(test|disease present)
    marginal_likelihood = sensitivity * prior + (1 - specificity) * (1 - prior)
    posterior = (likelihood * prior) / marginal_likelihood

    return posterior


# ----------------------------------------------------------------------------------------------------------------------
def estimate_bayes(test_data):
    # II. Applying Bayesian Estimation
    # init as uniform distribution (with (C_HIGH - C_LOW)/2)

    # make prediction

    # ---------------------------------------------------------------------------
    # https://towardsdatascience.com/how-to-use-bayesian-inference-for-predictions-in-python-4de5d0bc84f3
    prior_values = np.arange(0.001, 0.5, 0.001)
    posterior_values = compute_posterior(prior_values, sensitivity, specificity)

    plt.plot(prior_values)
    plt.plot(posterior_values)
    plt.xlabel('prior')
    _ = plt.ylabel('posterior')
    plt.show()

    # +
    num_responders = 64
    num_tested = 100

    bayes_df = pd.DataFrame({'proportion': np.arange(0.0, 1.01, 0.01)})

    # compute the binomial likelihood of the observed data for each
    # possible value of proportion
    bayes_df['likelihood'] = scipy.stats.binom.pmf(num_responders,
                                                   num_tested,
                                                   bayes_df['proportion'])
    # The prior is equal for all possible values
    bayes_df['prior'] = 1 / bayes_df.shape[0]

    # compute the marginal likelihood by adding up the likelihood of each possible proportion times its prior probability.
    marginal_likelihood = (bayes_df['likelihood'] * bayes_df['prior']).sum()
    bayes_df['posterior'] = (bayes_df['likelihood'] * bayes_df['prior']) / marginal_likelihood

    # plot the likelihood, prior, and posterior
    plt.plot(bayes_df['proportion'], bayes_df['likelihood'], label='likelihood')
    plt.plot(bayes_df['proportion'], bayes_df['prior'], label='prior')
    plt.plot(bayes_df['proportion'], bayes_df['posterior'],
             'k--', label='posterior')

    plt.legend()
    plt.show()

    # +
    num_responders = 312
    num_tested = 1000

    # copy the posterior from the previous analysis and rename it as the prior
    study2_df = bayes_df[['proportion', 'posterior']].rename(columns={'posterior': 'prior'})

    # compute the binomial likelihood of the observed data for each
    # possible value of proportion
    study2_df['likelihood'] = scipy.stats.binom.pmf(num_responders,
                                                    num_tested,
                                                    study2_df['proportion'])

    # compute the marginal likelihood by adding up the likelihood of each possible proportion times its prior probability.
    marginal_likelihood = (study2_df['likelihood'] * study2_df['prior']).sum()
    study2_df['posterior'] = (study2_df['likelihood'] * study2_df['prior']) / marginal_likelihood

    # plot the likelihood, prior, and posterior
    plt.plot(study2_df['proportion'], study2_df['likelihood'], label='likelihood')
    plt.plot(study2_df['proportion'], study2_df['prior'], label='prior')
    plt.plot(study2_df['proportion'], study2_df['posterior'],
             'k--', label='posterior')

    plt.title("Task Execution Time Estimation (% of C(HI))")
    plt.legend()
    plt.show()


# ----------------------------------------------------------------------------------------------------------------------
# State-based estimation
# work out the convergency and the measure of that (variance)
# priorities, periods, weighting?
def estimation_hmm_state_prediction(data):
    # load and reshape data
    observed_data = np.reshape(data, (-1, 1))
    #observed_data = np.array([[1], [2], [3], [2], [1]])
    #observed_data = np.array([[1.2], [2.1], [0.8], [1.9], [2.5]])

    # Define the model: GMMHMM or GaussianHMM
    num_of_states = 2
    model = hmm.GMMHMM(n_components=num_of_states)  # System with n hidden states
    # Initialize model parameters (transition matrix, means, covariances, initial state distribution)
    # model.startprob_ = np.array([0.7, 0.3])                     # initial probabilities for the two hidden states
    # model.transmat_ = np.array([[0.95, 0.05], [0.8, 0.2]])      # transition probabilities
    # model.means_ = np.array([[10.0], [20.0]])                   # initial guess of means
    # model.covars_ = np.tile(np.diag([1.0]), (num_of_states, 1)) # initial guess of diagonal covariances
    # model.n_iter = 100      # maximum number of iterations for EM algorithm

    # Train the model
    model.fit(observed_data)

    # Predict hidden states for new data
    hidden_states = model.predict(observed_data)

    # [quickfix]: the initial state has to be 0
    #   reversely all states if predicted incorrectly
    if hidden_states[0] == 1:
        hidden_states = 1 - hidden_states

    return hidden_states


# ----------------------------------------------------------------------------------------------------------------------
def plot_confusion_matrix(cm):
    # normalize confusion table before print
    cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(10,7))
    sn.set(font_scale=1.4)      # for label size
    ax = sn.heatmap(cmn, annot=True, annot_kws={"size": 16})  # font size
    ax.set_xlabel("Actual States", fontsize=14, labelpad=20)
    ax.xaxis.set_ticklabels(['Positive', 'Negative'])
    ax.set_ylabel("Predicted States", fontsize=14, labelpad=20)
    ax.yaxis.set_ticklabels(['Positive', 'Negative'])
    plt.show()


# ----------------------------------------------------------------------------------------------------------------------
def voting(candidates, threshold):
    """ Voting mechanism for a given candidates and a threshold

    Args:
        candidates (list):
        threshold (int):

    Returns:
        result (bool): True if # of true in candidates >= threshold; False elsewise
    """
    count = 0
    for candidate in candidates:
        count += candidate

    return count >= threshold


# ----------------------------------------------------------------------------------------------------------------------
def hmm_run_test(trial_number=10):
    confusion_tbl_accum1 = np.array([[0, 0], [0, 0]])
    confusion_tbl_accum2 = np.array([[0, 0], [0, 0]])
    confusion_tbl_accum3 = np.array([[0, 0], [0, 0]])
    confusion_tbl_accum_cb = np.array([[0, 0], [0, 0]])

    accuracy_array1 = np.zeros(trial_number)
    accuracy_array2 = np.zeros(trial_number)
    accuracy_array3 = np.zeros(trial_number)
    accuracy_array_cb = np.zeros(trial_number)

    for trial_id in range(trial_number):
        print(f"\n Trial: {trial_id} / {trial_number}:")

        # generate system states
        sys_state = state_generator()

        # generate data with ET generator
        et1 = et_generator_with_state(state=sys_state, BCET=10, C_LOW=20, C_HIGH=40, c_offset=[0, 10])
        et2 = et_generator_with_state(state=sys_state, BCET=30, C_LOW=60, C_HIGH=120, c_offset=[0, -20])
        et3 = et_generator_with_state(state=sys_state, BCET=50, C_LOW=100, C_HIGH=200, c_offset=[0, 50])

        # estimate_statistical(data_et)
        # estimate_bayes(data_et)

        hidden_states1 = estimation_hmm_state_prediction(et1)
        hidden_states2 = estimation_hmm_state_prediction(et2)
        hidden_states3 = estimation_hmm_state_prediction(et3)

        # voting
        pred = np.zeros(len(sys_state))
        for i in range(len(sys_state)):
            pred[i] = voting([hidden_states1[i], hidden_states2[i], hidden_states3[i]], 2)

        # get prediction accuracy
        accuracy1 = count_identical(hidden_states1, sys_state) / len(sys_state)
        accuracy2 = count_identical(hidden_states2, sys_state) / len(sys_state)
        accuracy3 = count_identical(hidden_states3, sys_state) / len(sys_state)
        accuracy_cb = count_identical(pred, sys_state) / len(sys_state)

        confusion_tbl1 = cal_confusion_table(sys_state, hidden_states1)
        confusion_tbl2 = cal_confusion_table(sys_state, hidden_states2)
        confusion_tbl3 = cal_confusion_table(sys_state, hidden_states3)

        confusion_tbl_cb = cal_confusion_table(sys_state, pred)

        print(f"Prediction Accuracy: {accuracy_cb:.3f}")
        print(confusion_tbl3)

        accuracy_array1[trial_id] = accuracy1
        accuracy_array2[trial_id] = accuracy2
        accuracy_array3[trial_id] = accuracy3
        accuracy_array_cb[trial_id] = accuracy_cb

        # confusion table count
        confusion_tbl_accum1[0][0] += confusion_tbl1[0][0]
        confusion_tbl_accum1[0][1] += confusion_tbl1[0][1]
        confusion_tbl_accum1[1][0] += confusion_tbl1[1][0]
        confusion_tbl_accum1[1][1] += confusion_tbl1[1][1]

        confusion_tbl_accum2[0][0] += confusion_tbl2[0][0]
        confusion_tbl_accum2[0][1] += confusion_tbl2[0][1]
        confusion_tbl_accum2[1][0] += confusion_tbl2[1][0]
        confusion_tbl_accum2[1][1] += confusion_tbl2[1][1]

        confusion_tbl_accum3[0][0] += confusion_tbl3[0][0]
        confusion_tbl_accum3[0][1] += confusion_tbl3[0][1]
        confusion_tbl_accum3[1][0] += confusion_tbl3[1][0]
        confusion_tbl_accum3[1][1] += confusion_tbl3[1][1]

        confusion_tbl_accum_cb[0][0] += confusion_tbl_cb[0][0]
        confusion_tbl_accum_cb[0][1] += confusion_tbl_cb[0][1]
        confusion_tbl_accum_cb[1][0] += confusion_tbl_cb[1][0]
        confusion_tbl_accum_cb[1][1] += confusion_tbl_cb[1][1]

    # print result
    print(accuracy_array3)
    print(confusion_tbl_accum3)

    # save result
    np.savetxt("result.csv", accuracy_array3, delimiter=",")

    # load and plot
    dat = np.loadtxt("result.csv", delimiter=",", dtype=float)

    plt.figure()
    _ = plt.hist(dat, bins='auto')  # arguments are passed to np.histogram
    plt.title("Histogram of Prediction Accuracy")

    plt.figure()
    labels = ["Tau 1", "Tau 2", "Tau 3", "Combined"]
    plt.boxplot([accuracy_array1, accuracy_array2, accuracy_array3, accuracy_array_cb], labels=labels)
    plt.title("Boxplot of Prediction Accuracy")
    plt.show()

    # plot confusion matrix
    plot_confusion_matrix(confusion_tbl_accum1)
    plot_confusion_matrix(confusion_tbl_accum2)
    plot_confusion_matrix(confusion_tbl_accum3)
    plot_confusion_matrix(confusion_tbl_accum_cb)


# ----------------------------------------------------------------------------------------------------------------------
def hmm_run_single_test():
    # generate system states
    sys_state = state_generator(seq_len=1000)
    print("Generated system states:", sys_state)

    # generate data with ET generator
    et1 = et_generator_with_state(state=sys_state, BCET=10, C_LOW=20, C_HIGH=40, c_offset=[0, 10])
    et2 = et_generator_with_state(state=sys_state, BCET=30, C_LOW=60, C_HIGH=120, c_offset=[0, -20])
    et3 = et_generator_with_state(state=sys_state, BCET=50, C_LOW=100, C_HIGH=200, c_offset=[0, 50])

    #estimate_statistical(data_et)
    #estimate_bayes(data_et)

    hidden_states1 = estimation_hmm_state_prediction(et1)
    hidden_states2 = estimation_hmm_state_prediction(et2)
    hidden_states3 = estimation_hmm_state_prediction(et3)

    # voting
    pred = np.zeros(len(sys_state))
    for i in range(len(sys_state)):
        pred[i] = voting([hidden_states1[i], hidden_states2[i], hidden_states3[i]], 2)

    print("Predicted hidden states:", hidden_states1)

    # get prediction Accuracy
    print(f"Prediction Accuracy: {count_identical(hidden_states1, sys_state) / len(sys_state):.3f}")

    # plot
    fig, axs = plt.subplots(8)

    axs[0].plot(sys_state)
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Sys ST')

    axs[1].plot(et1)
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('ET 1')

    axs[2].plot(et2)
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('ET 2')

    axs[3].plot(et3)
    axs[3].set_xlabel('Time')
    axs[3].set_ylabel('ET 3')

    axs[4].plot(hidden_states1)
    axs[4].set_xlabel('Time')
    axs[4].set_ylabel('ST 1')

    axs[5].plot(hidden_states2)
    axs[5].set_xlabel('Time')
    axs[5].set_ylabel('ST 2')

    axs[6].plot(hidden_states3)
    axs[6].set_xlabel('Time')
    axs[6].set_ylabel('ST 3')

    axs[7].plot(pred)
    axs[7].set_xlabel('Time')
    axs[7].set_ylabel('Pred.')

    fig.suptitle("State Estimation")
    plt.show()


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    hmm_run_single_test()
    #hmm_run_test(trial_number=100)
