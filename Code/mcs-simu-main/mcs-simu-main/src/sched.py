# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

class Sched:
    sched_policy = 0                # 0: FIFO; 1: FPS; 2: EDF
    mcs_policy = 0                  # 0: standard; 1: AMC; 2: AMC-RA; 3: AMC-RH

    def __init__(self):
        pass

    def set_sched_policy(self, policy):
        self.sched_policy = policy

    def set_mcs_policy(self, policy):
        self.mcs_policy = policy

    def on_schedule_point(self):
        pass

    def on_criticality_mode_change(self):
        pass

    def on_task_start(self):
        pass

    def on_task_finish(self):
        pass

    def on_mode_change(self):
        pass
