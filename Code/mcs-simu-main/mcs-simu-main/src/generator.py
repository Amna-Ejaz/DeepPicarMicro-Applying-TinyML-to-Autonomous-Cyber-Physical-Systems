# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import random


# UUniFast
def uunifast(n, u):
    """ Function: UUniFast
    Args:
        n (int): number of tasks
        u (float): total utilization
    Returns:
        sets (list)
    """
    sumU = u
    vectU = []

    for i in range(1, n):
        nextSumU = sumU * random.uniform(0, 1) ** (1.0 / (n - i))
        vectU.append(sumU - nextSumU)
        sumU = nextSumU

    vectU.append(sumU)

    return vectU


def uunifast_discard(n, u, nsets, ulimit=1):
    """ Function: uunifast_discard
    Args:
        n (int): number of tasks
        u (float): total utilization
        nsets (int): number of sets
        ulimit (float): upper limit of the utlization of a single DAG

    Returns:
        sets (list)
    """

    if n <= u:
        # no feasible solution
        return []

    sets = []
    while len(sets) < nsets:
        # Classic UUniFast algorithm:
        utilizations = []
        sumU = u
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        # If no task utilization exceeds ulimit:
        if all(ut <= ulimit for ut in utilizations):
            sets.append(utilizations)

    return sets


def gen_period(n, population):
    """ random generate periods from a population set

    Args:
        n (int):
        population (list):

    Returns:

    """
    periods = []

    for _ in range(n):
        if len(population) == 2:
            # in this case, the period set actually defines a range
            period = random.randint(population[0], population[1])
        else:
            period = random.choice(population)
        periods.append(period)

    return periods
