# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

from datatypes import TaskStatus, Criticality
import random


class Task:
    def __init__(self, id, C, T, D):
        self.id = id

        self.C = C
        self.T = T
        self.D = D

        self.util = self.C / self.T

        self.prio = -1
        self.BCET_factor = 0.5              # [todo] make this as a configurable parameter
        self.BCET = max(round(self.C * self.BCET_factor), 1)
        self.states = {"C_this": self.C, "T_this": self.T, "c": 0, "d": 0, "t": 0, "core_allocated": -1}
        self.flag = TaskStatus.Pending

    def __repr__(self):
        return f"(id: {self.id}, prio: {self.prio}, c: {self.states['c']}/{self.C}, t: {self.states['t']}/{self.T}, d: {self.states['d']}/{self.D})"

    def run(self, duration):
        self.states["c"] += duration

    def reset(self):
        self.states = {"C_this": self.C, "T_this": self.T, "c": 0, "d": 0, "t": 0, "core_allocated": -1}

    def is_ready(self):
        return self.states["t"] >= self.T

    def is_finished(self):
        return self.states["c"] >= self.states["C_this"]


class MCSTask(Task):
    def __init__(self, id, C, T, D):
        super(MCSTask, self).__init__(id, C, T, D)

        self.criticality = Criticality.LOW

        self.HIGH_failure_rate = 0
        self.C_HIGH_factor = 2
        self.execution_time_factor = 1

        self.C_LOW = C
        self.C_HIGH = self.C_LOW

        self.R_LOW = -1
        self.R_LOW_to_HIGH = -1
        self.R_HIGH = -1

        self.C_trace = []
        self.R_hist_trace = []
        self.R_LOW_updated_trace = []
        self.timestamps_trace_R = []

        self.slack_trace = []
        self.timestamps_trace_slack = []


    def __repr__(self):
        return f"(id: {self.id}, crit: {self.criticality}, prio: {self.prio}, c: {self.states['c']}/{self.states['C_this']}/({self.C_LOW},{self.C_HIGH}), t: {self.states['t']}/{self.T}, d: {self.states['d']}/{self.D})"

    def set_failure_rate(self, failure_rate):
        self.HIGH_failure_rate = failure_rate

    def set_execution_time_factor(self, factor):
        self.execution_time_factor = factor
        self.C_LOW = min(round(self.C_LOW * factor), self.C_HIGH)

    def set_criticality(self, criticality):
        self.criticality = criticality

        if criticality == Criticality.HIGH:
            self.C_HIGH = self.C_LOW * self.C_HIGH_factor
        else:
            self.C_HIGH = self.C_LOW

    def set_C_HIGH_factor(self, factor):
        self.C_HIGH_factor = factor
        self.C_HIGH = self.C_LOW * self.C_HIGH_factor

    def on_release(self):
        # task execution time is determined where it is released
        # the default distribution is uniform
        # [todo] add more distributions
        if self.criticality == Criticality.HIGH:
            # for HI tasks
            if random.random() >= self.HIGH_failure_rate:
                # if not failure
                c_this = random.randint(self.BCET, self.C_LOW)
            else:
                # if failure
                c_this = random.randint(self.C_LOW, self.C_HIGH)
        else:
            # for LO tasks
            c_this = random.randint(self.BCET, self.C_LOW)

        self.states["C_this"] = c_this

    def is_overrun_over_C(self):
        return self.states["c"] > self.C_LOW

    def is_overrun_over_R(self):
        if self.criticality == Criticality.HIGH:
            return self.states["d"] > self.R_LOW
        # LO criticality tasks would not trigger a mode change
        else:
            return False

    def is_deadline_miss(self):
        return self.states["d"] > self.D

    def update_R_estimation(self, R_LO_new):
        alpha = 0.9
        WCRT_new_estimate = R_LO_new * 3
        self.R_LOW = min(self.R_LOW * alpha + WCRT_new_estimate * (1 - alpha), self.R_HIGH)

    def record_R_LOW(self):
        self.R_LOW_updated_trace.append(self.R_LOW)

    def record_response_time(self, t, R_LO_new):
        self.R_hist_trace.append(R_LO_new)
        self.timestamps_trace_R.append(t)

    def record_slack(self, t, slack):
        self.slack_trace.append(slack)
        self.timestamps_trace_slack.append(t)


class DAGTask(Task):
    # [todo] need further implementation
    pass


# a job is an instance of task
class Job:
    # [todo] need further implementation
    pass
