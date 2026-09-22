# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import os
import glob
import math
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from simulator import Simulator
from task import MCSTask
from datatypes import Criticality, PriorityAssignmentPolicy, SchedulingPolicies
from configurations import ParameterServer
import generator
import analysis_rta
from pa import priority_assignment


def taskset_generation(util):
    number_of_tasks = configs.get("taskset_number_of_task")
    b_check_schedulability = configs.get("check_schedulability_at_start")
    retry_counter_max = configs.get("taskset_generate_retry_max_times")

    # generating tasksets (with discard and retry)
    retry_counter = 0
    while True:
        # generate a task set
        taskset = []

        u = generator.uunifast(number_of_tasks, util)
        T = generator.gen_period(number_of_tasks, configs.get("taskset_periods"))
        idx = 0
        u_sum = 0

        HI_task_portion = configs.get("HI_task_portion")
        number_of_high_tasks = math.ceil(number_of_tasks * HI_task_portion)

        for i in range(number_of_tasks):
            # define tasks
            ci = max(math.floor(T[i] * u[i]), 1)
            ui = ci / T[i]
            u_sum += ui
            task = MCSTask(id=idx, C=ci, T=T[i], D=T[i])  # id, C, T, D

            # set task criticality (high-crit for the first x% of the unordered taskset)
            if i < number_of_high_tasks:
                task.set_criticality(Criticality.HIGH)
                task.set_failure_rate(configs.get("HI_task_failure_rate"))
                task.set_C_HIGH_factor(configs.get("HI_task_C_factor"))

            # add tasks into simulator
            taskset.append(task)
            idx += 1

        # Priority assignment: re-order tasks by priority (the highest first)
        taskset = priority_assignment(taskset, priority_assignment_policy=PriorityAssignmentPolicy.RM)

        # work out the response times and schedulability
        # [note] this is preemptive analysis and cannot be used for testing non-preemptive schedulability
        for i in range(number_of_tasks):
            taskset[i].R_LOW = analysis_rta.rta_low(i, taskset)
            taskset[i].R_LOW_to_HIGH = analysis_rta.rta_low_to_high(i, taskset)
            taskset[i].R_HIGH = analysis_rta.rta_high(i, taskset)

            # print(i, D, R_LO, R, R_HI, criticality)

        # print("---------------------------------------------------------")
        # (optional) check the schedulability
        if b_check_schedulability:
            b_taskset_schedulable = True
            for i in range(number_of_tasks):
                D = taskset[i].D
                R = analysis_rta.rta_low_to_high(i, taskset)
                if R > D:
                    # print(f"Task {i} NOT scheduable.")
                    b_taskset_schedulable = False
            if b_taskset_schedulable:
                # print(f"Schedulability test passed ({retry_counter}/{retry_counter_max}).")
                break
            else:
                # print(f"[Error] Schedulability test is NOT passed ({retry_counter}/{retry_counter_max}).")
                retry_counter += 1
                if retry_counter > retry_counter_max:
                    # print("[Error] Error generating a feasible taskset.")
                    exit(-1)
        else:
            # print("[Warning] Schedulability is NOT checked.")
            break
        # print("---------------------------------------------------------")

    return taskset


def worker_thread(util, trial_id, taskset, policy):
    # print("---------------------------------------------------------")
    # print(f"Util: {util}, Trial: {trial_id+1} / {num_of_trials} ({(trial_id+1) / num_of_trials * 100}%)")

    # initialize the simulator
    # each thread has its own copy of a simulator instance to avoid race condition
    sim = Simulator(configs, trial_id)

    # set log path
    log_basefolder_main = configs.get("log_base_folder")
    log_basefolder = f"{log_basefolder_main}/{round(util, 2)}/{trial_id}/{policy}/"
    os.makedirs(os.path.dirname(log_basefolder), exist_ok=True)  # create folder if it does not exist
    sim.set_log_path(log_basefolder)

    # set taskset
    sim.set_taskset(taskset=taskset)
    sim.set_policy(policy=policy)

    # start the simulator
    sim.start()
    sim.run()

    del sim


if __name__ == "__main__":
    # load configurations from the global configuration file
    # the config file is in json format
    configs = ParameterServer()
    configs.load_from_file("../configs.json")

    # config logging base folder
    # each trial will have its independent folder
    log_folder = configs.get("log_base_folder")

    # make the log directory if it does not exist
    # this cannot be done in the thread as it could create race condition
    for root, dirs, files in os.walk(log_folder, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))

        # Add this block to remove folders
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

    # Add this line to remove the root folder at the end
    #os.rmdir(log_folder)

    # [todo] running the simulator with thread-level parallelism;
    # the parallel function commented as it is making some mess
    # with Pool() as pool:
    #     # call the same function with different data in parallel
    #     for result in pool.map(task, range(1, 21)):
    #         # report the value to show progress
    #         print(result)

    # utilizations
    utilization_set = configs.get("taskset_util")

    # scheduling policies
    # policies = [SchedulingPolicies.FPPS,
    #             SchedulingPolicies.AMC_P,
    #             SchedulingPolicies.AMC_RH,
    #             SchedulingPolicies.AMC_DT,
    #             SchedulingPolicies.AMC_DT_P]
    policies = [SchedulingPolicies.AMC_P]

    # create threads to execute trials
    with ThreadPoolExecutor(max_workers=configs.get("number_of_multithread_workers")) as executor:
        threads = []    # contain all tasks

        for utilization in utilization_set:
            # scale trials within the same utilization
            num_of_trials = configs.get("number_of_trials")

            # iterate through trial_id
            for trial_id in range(num_of_trials):
                # fix the random seed for reproducibility
                rnd_seed = configs.get("rnd_seed")
                random.seed(rnd_seed + trial_id)

                # generate task set
                taskset = taskset_generation(util=utilization)

                # scale policies (with the same task set)
                for policy in policies:
                    if configs.get("with_multithread_on"):
                        # -- with multithreading
                        print(f"Submit Trial: Util={utilization}, Trial ID={trial_id}, Policy={policy}")
                        job = executor.submit(worker_thread, util=utilization, trial_id=trial_id, taskset=taskset, policy=policy)
                        threads.append(job)
                    else:
                        # -- with single thread
                        print(f"Running Trial: Util={utilization}, Trial ID={trial_id}, Policy={policy}")
                        worker_thread(trial=trial_id, util=utilization, taskset=taskset)

        # Create a progress bar to track progress
        total_trials = len(utilization_set) * num_of_trials * len(policies)
        with tqdm(total=total_trials) as pbar:
            # Track progress as tasks complete
            for thread in as_completed(threads):
                result = thread.result()  # Get the result of the completed task
                pbar.update(1)  # Update the progress bar

    print("Evaluation Finished.")
