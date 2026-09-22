# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import pprint
import pickle
from datatypes import Criticality, SchedulingPolicies, DebugLevel
from events import EventType, FailureEventType


class Stats:
    def __init__(self):
        self.metadata = {}

        self.cnt_idle = []  # idle tick (per core)
        self.cnt_job_released = 0
        self.cnt_job_finished = 0
        self.cnt_overruns = 0
        self.cnt_deadline_missed = 0
        self.cnt_deadline_missed_high = 0
        self.cnt_deadline_missed_low = 0
        self.cnt_job_not_executed = 0

        # counters for experiments [todo] need to improve
        self.cnt_jne1 = 0
        self.cnt_jne2 = 0
        self.cnt_jne3 = 0

        self.cnt_ldm1 = 0
        self.cnt_ldm2 = 0
        self.cnt_ldm3 = 0

        self.cnt_hdm1 = 0
        self.cnt_hdm2 = 0
        self.cnt_hdm3 = 0

        # trace for stats
        self.trace_period = 200  # counter for periodic tracing
        self.trace_jne = []  # job not executed
        self.trace_modes = [(0, 0)]  # traces of mode change (ts, mode)


class Simulator:
    def __init__(self, configs, trial_id=-1):
        self.pp = pprint.PrettyPrinter(width=200, compact=True)

        self.trial_id = trial_id

        # Debug level
        self.debugLevel = DebugLevel(configs.get("debug_level"))

        # simulation duration
        self.simu_duration = configs.get("simulation_duration")

        # trigger points
        self.trigger_point_changed = int(self.simu_duration / 3)  # this is where a change applies
        self.trigger_point_detected = int(self.simu_duration / 3 * 2)  # this is where an action is applied

        # change event type
        self.trigger_event_type = FailureEventType.task_ET_change

        # system time tick
        self.tick_cnt = 0

        # task set
        self.taskset = []  # all tasks

        # task queues [todo] currently these are task queues, change it to job queues to allow multiple jobs to co-exist
        self.ready_q = []  # tasks (jobs) that are ready to be executed
        self.sched_q = []  # scheduled tasks (jobs)
        self.pending_q = []  # tasks (jobs) that are pending for TT/ET events

        # variables for processors and cores
        self.m = configs.get("number_of_cores")  # number of processors  [todo] m > 1 should be fine but has not been extensively tested
        self.processors = []  # processor status: -1 (idle) otherwise the running taskID
        self.running_q = []  # queue of all the running tasks on each processor (one queue per core)

        # variables for scheduling
        self.sched_policy = configs.get("sched_policy")
        self.sched_preemptive = configs.get("sched_preemptive")  # True: preemptive / False: non-premptive

        # variables for MCS criticality mode
        self.criticality_mode = Criticality.LOW

        # variables for system mode changes and adaptation
        self.system_mode_change_on = False
        self.system_mode_changed = False
        self.system_mode_changed_detected = False

        if self.sched_policy in [SchedulingPolicies.AMC_DT, SchedulingPolicies.AMC_DT_P]:
            self.system_adaptation_enabled = True
        else:
            self.system_adaptation_enabled = False

        # folders for saving logs (will be changed to the correct paths later)
        self.log_on = configs.get("log_on")
        self.log_file_dir = "./"

        # counters for stats
        self.perf = Stats()

    def start(self):
        # init the task queues
        self.ready_q = []
        self.sched_q = []
        self.pending_q = []

        # all tasks are released at time = 0
        for tau in self.taskset:
            self.ready_q.append(tau)
            self.perf.cnt_job_released += 1

        # initialize all processor status
        for i in range(self.m):
            self.processors.append(-1)
            self.perf.cnt_idle.append(0)

        # print debug information
        if self.debugLevel >= DebugLevel.Info:
            self.pp.pprint("---------------")
            self.pp.pprint("mcs-simu initialization:")
            self.print_tasks()
            self.print_queues()
            self.print_total_util(self.ready_q)

    def set_policy(self, policy):
        self.sched_policy = policy

    def set_taskset(self, taskset):
        self.taskset = taskset

    def add_task(self, tau):
        self.taskset.append(tau)

    def remove_task(self, tau):
        # [todo] not yet implemented
        pass

    def tick(self, cnt):
        self.tick_cnt += cnt

    # [todo] work out the next event so the tick does not need to be only increased by 1 every time
    # event-driven simulation will significantly improve efficiency
    def tick_before_next_event(self):
        next_tick = 1000  # this is the maximal step size

        # work out the next release
        for tau_i in self.pending_q:
            pass

        # work out the next complete
        # work out the next deadline miss
        # work out criticality change (may not need)

        next_tick = 1
        return next_tick

    def run_one_tick(self):
        # trap point for debugging
        if self.tick_cnt == 1234:
            self.tick_cnt = self.tick_cnt

        # call the scheduler & allocate tasks to queues
        for core_id in range(self.m):
            if self.ready_q:
                current_running_task_id = self.processors[core_id]
                if current_running_task_id == -1:
                    highest_prio = -1
                else:
                    highest_prio = self.taskset[current_running_task_id].prio
                task_to_schedule_id = -1
                for task_idx, task_i in enumerate(self.ready_q):  # iterate all ready tasks
                    if task_i.prio > highest_prio:
                        task_to_schedule_id = task_idx
                        task_to_schedule = task_i
                        highest_prio = task_i.prio

                # check preemptive (true) or non-preemptive (false)
                if self.sched_preemptive:
                    # preemption
                    #   put the running task back to ready_q
                    #   and then put the task to the sched_q
                    if task_to_schedule_id != -1:
                        task_running_id = self.processors[core_id]
                        if task_running_id != -1:  # if any task is running
                            for idx, task_j in enumerate(self.sched_q):
                                if task_running_id == task_j.id:
                                    self.sched_q.pop(idx)
                            self.ready_q.append(self.taskset[task_running_id])

                        tau = self.ready_q.pop(task_to_schedule_id)
                        tau.states["core_allocated"] = core_id
                        self.sched_q.append(tau)
                        self.processors[core_id] = tau.id
                        if self.debugLevel >= DebugLevel.Detail:
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} is allocated to core {core_id} (preemption).")
                else:
                    # [todo] non-preemptive is not implemented
                    return -1

        # check idle state and check if it is okay to move back from HIGH to LOW criticality mode
        for core_id in range(self.m):
            flag_all_cores_idle = True
            if self.processors[core_id] == -1:
                self.perf.cnt_idle[core_id] += 1
            else:
                flag_all_cores_idle = False

            # AMC-P: mode switch back to normal mode on an idle tick
            # [todo] this mode switch may need more work
            # [todo] [solved] there was a bug in the criticality mode switch where tasks are not release or allocated on some cores
            # [todo] measuring the transition time during the high mode
            if self.criticality_mode == Criticality.HIGH and flag_all_cores_idle:
                if self.sched_policy in [SchedulingPolicies.AMC_P]:
                    # return to normal mode on idle tick
                    self.criticality_mode = Criticality.LOW
                    self.perf.trace_modes.append((self.tick_cnt, 0))
                    if self.debugLevel >= DebugLevel.Info:
                        self.pp.pprint(f"(t:{self.tick_cnt}) Event: Criticality mode changed to LOW")
                elif self.sched_policy in [SchedulingPolicies.AMC_RH, SchedulingPolicies.AMC_DT, SchedulingPolicies.AMC_DT_P]:
                    # return to normal mode if no high task is overrunning
                    flag_no_hi_task_overrun = True
                    for tau in self.sched_q:
                        if tau.criticality == Criticality.HIGH and tau.is_overrun_over_R():
                            flag_no_hi_task_overrun = False
                    if flag_no_hi_task_overrun:
                        self.criticality_mode = Criticality.LOW
                        self.perf.trace_modes.append((self.tick_cnt, 0))
                        if self.debugLevel >= DebugLevel.Info:
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Criticality mode changed to LOW")
                else:
                    pass

        # run the clock & post-processing
        tick_increment = self.tick_before_next_event()
        self.tick(tick_increment)

        for tau in self.taskset:
            if tau in self.ready_q:
                # [todo] task could miss its deadline in the ready_q
                tau.states["t"] += tick_increment
                tau.states["d"] += tick_increment
            elif tau in self.sched_q:
                tau.states["c"] += tick_increment

                # check task completion
                if tau.is_finished():
                    self.sched_q.remove(tau)
                    self.pending_q.append(tau)
                    self.processors[tau.states["core_allocated"]] = -1  # reset the processor

                    # update response time of tau
                    R_i = tau.states["d"] + 1
                    C_i = tau.states["c"]
                    slack_i = tau.D - R_i

                    tau.record_response_time(self.tick_cnt, R_i)

                    # make adaptations if mode change is detected (only when adaptation is on)
                    if self.system_mode_changed_detected and self.system_adaptation_enabled:
                        if tau.criticality == Criticality.HIGH:
                            tau.update_R_estimation(R_i)
                    tau.record_R_LOW()
                    tau.record_slack(self.tick_cnt, slack_i)

                    # write the response time to the log (d == R)
                    self.write_event_to_log_raw(self.tick_cnt, tau.id, R_i, C_i, slack_i)
                    tau.reset()  # reset the task
                    self.perf.cnt_job_finished += 1
                    if self.debugLevel >= DebugLevel.Info:
                        self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} finished.")

                # check task overrun and perform criticality mode change
                if self.sched_policy == SchedulingPolicies.FPPS:
                    # No mode switch check in FPPS
                    pass
                elif self.sched_policy == SchedulingPolicies.AMC_P and tau.is_overrun_over_C():
                    if self.criticality_mode == Criticality.LOW and tau.criticality == Criticality.HIGH:
                        # this will trigger a mode change
                        self.criticality_mode = Criticality.HIGH

                        # record event & stat
                        self.perf.cnt_overruns += 1
                        self.perf.trace_modes.append((self.tick_cnt, 1))
                        self.write_event_to_log(self.tick_cnt, EventType.Overrun, tau.id)

                        # for AMC, all LO tasks will be dropped
                        for tau_to_drop in self.sched_q + self.ready_q:
                            if tau_to_drop.criticality == Criticality.LOW:
                                # remove from the queue
                                if tau_to_drop in self.sched_q:
                                    self.sched_q.remove(tau_to_drop)
                                    # free the processor
                                    self.processors[tau.states["core_allocated"]] = -1
                                elif tau_to_drop in self.ready_q:
                                    self.ready_q.remove(tau_to_drop)

                                # reset and add to the pending queue
                                tau_to_drop.reset()
                                self.pending_q.append(tau_to_drop)
                                self.perf.cnt_job_not_executed += 1
                                self.write_event_to_log(self.tick_cnt, EventType.TaskDrop, tau.id)

                        # print debug messages
                        if self.debugLevel >= DebugLevel.Warning:
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} overruns.")
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Criticality mode changed to HIGH.")
                elif self.sched_policy in {SchedulingPolicies.AMC_RH, SchedulingPolicies.AMC_DT, SchedulingPolicies.AMC_DT_P} and tau.is_overrun_over_R():
                    if self.criticality_mode == Criticality.LOW and tau.criticality == Criticality.HIGH:
                        # this will trigger a mode change
                        self.criticality_mode = Criticality.HIGH

                        # record event & stat
                        self.perf.cnt_overruns += 1
                        self.perf.trace_modes.append((self.tick_cnt, 1))
                        self.write_event_to_log(self.tick_cnt, EventType.Overrun, tau.id)

                        # for AMC, all LO tasks will be dropped
                        for tau_to_drop in self.sched_q + self.ready_q:
                            if tau_to_drop.criticality == Criticality.LOW:
                                # remove from the queue
                                if tau_to_drop in self.sched_q:
                                    self.sched_q.remove(tau_to_drop)
                                    # free the processor
                                    self.processors[tau.states["core_allocated"]] = -1
                                elif tau_to_drop in self.ready_q:
                                    self.ready_q.remove(tau_to_drop)

                                # reset and add to the pending queue
                                tau_to_drop.reset()
                                self.pending_q.append(tau_to_drop)
                                self.perf.cnt_job_not_executed += 1
                                self.write_event_to_log(self.tick_cnt, EventType.TaskDrop, tau.id)

                        # print debug messages
                        if self.debugLevel >= DebugLevel.Warning:
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} overruns.")
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Criticality mode changed to HIGH.")
                else:
                    pass

                # check task deadline misses
                if tau.is_deadline_miss():
                    # terminate the task if it missed deadline and put it back into the pending queue
                    self.sched_q.remove(tau)
                    self.pending_q.append(tau)
                    self.processors[tau.states["core_allocated"]] = -1  # reset the processor
                    # deadline counters
                    self.perf.cnt_deadline_missed += 1
                    self.write_event_to_log(self.tick_cnt, EventType.DeadlineMiss, tau.id)
                    if tau.criticality == Criticality.HIGH:
                        self.perf.cnt_deadline_missed_high += 1
                    else:
                        self.perf.cnt_deadline_missed_low += 1
                    tau.reset()  # reset the task
                    # print debug messages
                    if self.debugLevel >= DebugLevel.Error:
                        self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} deadline missed.")
                else:
                    tau.states["t"] += tick_increment
                    tau.states["d"] += tick_increment
            elif tau in self.pending_q:
                tau.states["t"] += tick_increment

                # task release check
                if tau.states["t"] >= tau.T:
                    if self.criticality_mode == Criticality.HIGH and tau.criticality == Criticality.LOW:
                        # drop low tasks in high mode
                        # reset and add to the pending queue
                        tau.reset()
                        self.pending_q.append(tau)
                        self.perf.cnt_job_not_executed += 1
                        self.write_event_to_log(self.tick_cnt, EventType.TaskDrop, tau.id)
                    else:
                        self.perf.cnt_job_released += 1
                        tau.on_release()
                        self.pending_q.remove(tau)
                        self.ready_q.append(tau)

                        # print debug messages
                        if self.debugLevel >= DebugLevel.Info:
                            self.pp.pprint(f"(t:{self.tick_cnt}) Event: Task {tau.id} is released.")
            else:
                pass  # should not have any tasks not in any queue

        # --------------------------------------------------------------------------------------------------------------
        # trigger failures
        if self.system_mode_change_on:
            if self.tick_cnt == self.trigger_point_changed:
                # change the system mode
                self.system_mode_changed = True

                # iterate all the tasks in all queues
                # [todo] check if tasks are duplicated in self.taskset
                for tau in self.ready_q + self.pending_q + self.sched_q + self.taskset:
                    if tau.prio >= 0:
                        if tau.criticality == Criticality.HIGH:
                            #tau.set_failure_rate(min(tau.failure_rate * 5, 1.0))
                            tau.set_execution_time_factor(2)
                            # if failure_type == FailureEventID.system_ET_has_changed:
                            # system.set_execution_time(2)
                            # elif failure_type == FailureEventID.system_FR_has_changed:
                            # system.set_failure_rate(2)

            # failure is detected
            if self.tick_cnt == self.trigger_point_detected:
                # change the system mode
                self.system_mode_changed_detected = True

        # monitoring
        # 1. time-triggered perf
        if self.tick_cnt % self.perf.trace_period == 0:
            self.perf.trace_jne.append(self.perf.cnt_job_not_executed)

        # 2. event-triggered perf
        if self.tick_cnt == self.trigger_point_changed:
            self.perf.cnt_jne1 = self.perf.cnt_job_not_executed
            self.perf.cnt_ldm1 = self.perf.cnt_deadline_missed_low
            self.perf.cnt_hdm1 = self.perf.cnt_deadline_missed_high

        if self.tick_cnt == self.trigger_point_detected:
            self.perf.cnt_jne2 = self.perf.cnt_job_not_executed
            self.perf.cnt_ldm2 = self.perf.cnt_deadline_missed_low
            self.perf.cnt_hdm2 = self.perf.cnt_deadline_missed_high

        if self.tick_cnt == self.simu_duration - 1:
            self.perf.cnt_jne3 = self.perf.cnt_job_not_executed
            self.perf.cnt_ldm3 = self.perf.cnt_deadline_missed_low
            self.perf.cnt_hdm3 = self.perf.cnt_deadline_missed_high

        # print debug messages
        if self.debugLevel >= DebugLevel.Detail:
            self.pp.pprint("---------------")
            self.print_tick()
            self.print_queues()
            self.print_processor_states()

    def on_finish(self):
        if self.debugLevel >= DebugLevel.Info:
            # --------------------------------------------------------------------------------------------------------------
            # print R list (for MATLAB)
            print("R = {")
            for tau_i in self.taskset:
                print(tau_i.R_hist_trace)
            print("};")

            print("R_LOW_est = {")
            for tau_i in self.taskset:
                print(tau_i.R_LOW_updated_trace)
            print("};")

            print("R_ts = {")
            for tau_i in self.taskset:
                print(tau_i.timestamps_trace_R)
            print("};")

            print("jne_dat = {")
            print(self.perf.trace_jne)
            print("};")

            print("slack_dat = {")
            for tau_i in self.taskset:
                print(tau_i.slack_trace)
            print("};")

            print("slack_ts = {")
            for tau_i in self.taskset:
                print(tau_i.timestamps_trace_slack)
            print("};")

            # traces of mode changes
            trace_mode_list = list(zip(*self.perf.trace_modes))
            if trace_mode_list:
                print("mode_ts = ", list(trace_mode_list[0]), ";")
                print("mode_dat = ", list(trace_mode_list[1]), ";")
            else:
                print("mode_ts = []", ";")
                print("mode_dat = []", ";")

            # --------------------------------------------------------------------------------------------------------------
            print("\n CPU Utilization:")
            for core_id in range(self.m):
                self.pp.pprint(
                    "Core {0}: {1:.1f}%".format(core_id, (1 - self.perf.cnt_idle[core_id] / self.tick_cnt) * 100))

            print("\n Performance stats:")
            print(f"\n cnt_job_released:, {self.perf.cnt_job_released}, \
                  \n cnt_job_finished:, {self.perf.cnt_job_finished}, \
                  \n cnt_overruns / mode_changes:, {self.perf.cnt_overruns}, \
                  \n cnt_deadline_missed (#DM):, {self.perf.cnt_deadline_missed}, \
                  \n cnt_deadline_missed_high (#HDM):, {self.perf.cnt_deadline_missed_high}, \
                  \n cnt_deadline_missed_low (#LDM):, {self.perf.cnt_deadline_missed_low}, \
                  \n cnt_job_not_executed (#JNE): {self.perf.cnt_job_not_executed}")

        self.write_stats_to_log()
        self.write_metadata_to_log(self.perf.cnt_jne1, self.perf.cnt_jne2, self.perf.cnt_jne3,
                                   self.perf.cnt_ldm1, self.perf.cnt_ldm2, self.perf.cnt_ldm3,
                                   self.perf.cnt_hdm1, self.perf.cnt_hdm2, self.perf.cnt_hdm3)
        self.write_stat_to_pickle()

        if self.debugLevel >= DebugLevel.Info:
            self.pp.pprint("Finished")

    def run(self):
        # [todo] optimize tick-based simulation to event-based simulation
        while self.tick_cnt <= self.simu_duration:
            self.run_one_tick()

        self.on_finish()

    # ------------------------------------------------------------------------------------------------------------------
    # Logging-related Utility Functions
    # [todo] move this into the logger.py and avoid open the file multiple times
    # ------------------------------------------------------------------------------------------------------------------
    def set_log_path(self, log_path):
        """ set log path
        """
        self.log_file_dir = log_path

    # write everything into a log file:
    def write_stats_to_log(self):
        """ write_stats_to_log
        """
        if self.log_on:
            with open(self.log_file_dir + "log.csv", 'a') as f:
                f.write(f"{self.perf.cnt_job_released}, "
                        f"{self.perf.cnt_job_finished}, "
                        f"{self.perf.cnt_overruns}, "
                        f"{self.perf.cnt_deadline_missed}, "
                        f"{self.perf.cnt_deadline_missed_high}, "
                        f"{self.perf.cnt_deadline_missed_low}, "
                        f"{self.perf.cnt_job_not_executed} \n")

    def write_event_to_log(self, timestamp, event, event_para):
        """ write_event_to_log
        """
        if self.log_on:
            with open(self.log_file_dir + "event.csv", 'a') as f:
                f.write(f"{timestamp}, {event}, {event_para}\n")

    def write_event_to_log_raw(self, timestamp, task_id, task_r, task_c, slack_i):
        """" write_event_to_log_raw
        """
        if self.log_on:
            with open(self.log_file_dir + "raw.csv", 'a') as f:
                f.write(f"{timestamp}, {task_id}, {task_r}, {task_c}, {slack_i}\n")

    def write_metadata_to_log(self, jne1, jne2, jne3, ldm1, ldm2, ldm3, hdm1, hdm2, hdm3):
        """ write_metadata_to_log
        """
        if self.log_on:
            with open(self.log_file_dir + "meta.csv", 'a') as f:
                f.write(f"{jne1}, {jne2}, {jne3}, {ldm1}, {ldm2}, {ldm3}, {hdm1}, {hdm2}, {hdm3} \n")

    def write_stat_to_pickle(self):
        with open(self.log_file_dir + "data.pkl", "wb") as f:
            pickle.dump(self.perf, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_stat_from_pickle(self):
        with open(self.log_file_dir + "data.pkl", "rb") as f:
            perf = pickle.load(f)

        return perf

    # ------------------------------------------------------------------------------------------------------------------
    # Print-related Utility Functions
    # ------------------------------------------------------------------------------------------------------------------
    def print_queues(self):
        self.pp.pprint(f"Ready_q: {self.ready_q}")
        self.pp.pprint(f"Sched_q: {self.sched_q}")
        self.pp.pprint(f"Pending_q: {self.pending_q}")

    def print_tasks(self):
        for tau in self.taskset:
            self.pp.pprint(tau)

    def print_processor_states(self):
        self.pp.pprint(f"Processor states: {self.processors}")
        self.pp.pprint(f"Running queue: {self.running_q}")
        self.pp.pprint(f"Criticality mode: {self.criticality_mode}")

    def print_total_util(self, tasks):
        util_total = 0
        for tau in tasks:
            util_total += tau.C / tau.T

        self.pp.pprint(f"Total utilization: {round(util_total, 2)}")

    def print_tick(self):
        self.pp.pprint(f"tick: {self.tick_cnt}")
