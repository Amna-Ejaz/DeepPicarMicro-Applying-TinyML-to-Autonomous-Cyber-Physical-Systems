# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

from enum import Enum, IntEnum


class DebugLevel(IntEnum):
    Off = -1
    Critical = 0
    Error = 1
    Warning = 2
    Info = 3
    Detail = 4
    All = 5


# processor-related
class ProcessorStatus(Enum):
    Null = 0
    Idle = -1
    Busy = 1


# task-related
class TaskStatus(IntEnum):
    Null = 0
    Running = 1     # currently running on a processor
    Pending = 2     # preempted or waiting for resource
    Ready = 3       # ready for execution (but is not running)


# scheduling-related
class Criticality(IntEnum):
    LOW = 0
    HIGH = 1


class PriorityAssignmentPolicy(IntEnum):
    RND = -1  # Random priority assignment
    RM = 0    # Rate Monotonic
    DM = 1    # Deadline Monotonic
    OPA = 2   # Audsley's Optimal Priority Assignment


class SchedulingPolicies(IntEnum):
    FPPS = 0        # Preemptive FPS (no mode switch)
    AMC_P = 1       # AMC+
    AMC_RH = 2      # AMC-RH
    AMC_DT = 3      # AMC-DT
    AMC_DT_P = 4    # AMC-DT+
