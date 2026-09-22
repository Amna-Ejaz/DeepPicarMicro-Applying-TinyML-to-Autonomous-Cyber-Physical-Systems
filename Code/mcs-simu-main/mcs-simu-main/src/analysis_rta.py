# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import math
from datatypes import Criticality


def rta_low(i, taskset):
    """
    Check low response time (preemptive). Task is ordered by their priorities (highest-first).

    Args:
        i: index of task i to be analysed
        taskset: the taskset

    Returns:

    """
    Ci = taskset[i].C_LOW
    Ti = taskset[i].T
    Di = Ti

    Ri = -100000
    Ri_new = Ci

    while abs(Ri_new - Ri) > 0:
        Ri = Ri_new
        Ij = 0
        for j in range(len(taskset)):
            if j < i:
                Cj = taskset[j].C_LOW
                Tj = taskset[j].T
                Ij += math.ceil(Ri / Tj) * Cj
        Ri_new = Ci + Ij

        if Ri_new > Di:
            Ri = Ri_new
            break

    return Ri


def rta_high(i, taskset):
    """
    check high response time (preemptive). Task is ordered by their priorities.

    Args:
        i: index of task i to be analysed
        taskset: the taskset

    Returns:

    """
    # Ri = -1 if criticality is low
    if taskset[i].criticality == Criticality.LOW:
        return -1

    Ci_high = taskset[i].C_HIGH
    Ti = taskset[i].T
    Di = Ti
    Ri = -100000
    Ri_new = Ci_high

    while abs(Ri_new - Ri) > 0:
        Ri = Ri_new
        Ij = 0
        for j in range(len(taskset)):
            typej = taskset[j].criticality
            if j < i and typej == Criticality.HIGH:  # j = hpH(i)
                Cj_high = taskset[j].C_HIGH
                Tj = taskset[j].T
                Ij += math.ceil(Ri / Tj) * Cj_high
        Ri_new = Ci_high + Ij

        if Ri_new > Di:
            Ri = Ri_new
            break

    return Ri


def rta_low_to_high(i, taskset):
    """
    Check low -> high (for dual-criticality only; preemptive). Task is ordered by their priorities.
    (*) Normally we only need to check this switch condition.

    Args:
        i: index of task i to be analysed
        taskset: the taskset

    Returns:

    """
    Ri_LO = rta_low(i, taskset)

    Ri = -100000
    Ri_new = taskset[i].C_HIGH

    Ti = taskset[i].T
    Di = Ti

    while abs(Ri_new - Ri) > 0:
        Ri = Ri_new
        Ij = 0
        for j in range(len(taskset)):
            if j < i:
                typej = taskset[j].criticality
                if typej == Criticality.LOW:  # j = hpL(i)
                    Cj_low = taskset[j].C_LOW
                    Tj = taskset[j].T
                    Ij += math.ceil(Ri_LO / Tj) * Cj_low
                elif typej == Criticality.HIGH:  # j = hpH(i)
                    Cj_high = taskset[j].C_HIGH
                    Tj = taskset[j].T
                    Ij += math.ceil(Ri / Tj) * Cj_high
        Ri_new = Ci_high + Ij

        if Ri_new > Di:
            Ri = Ri_new
            break

    return Ri
