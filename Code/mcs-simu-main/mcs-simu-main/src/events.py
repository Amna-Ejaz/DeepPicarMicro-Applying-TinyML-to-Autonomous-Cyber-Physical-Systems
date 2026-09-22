# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

from enum import Enum


class EventType(Enum):
    Overrun = 0
    TaskDrop = 1
    DeadlineMiss = 2
    Overrun_over_R_LO = 3


#   Type 0: task_ET_has_changed
#   Type 1: task_FR_has_changed
#   Type 2: Type 0 + 1
class FailureEventType(Enum):
    task_ET_change = 0
    task_FR_change = 1
    task_ET_FR_change = 2


class Event:
    timestamp: int
    eventID: int
    eventType: EventType

    def __str__(self):
        return f"{self.timestamp}:Event"
