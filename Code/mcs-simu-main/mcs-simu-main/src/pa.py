# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

from datatypes import Criticality, PriorityAssignmentPolicy, SchedulingPolicies


def priority_assignment(taskset, priority_assignment_policy = PriorityAssignmentPolicy.RM):
    """ output will be written in the ".prio" property; 0 is the highest
        taskset is an array of Task class

    Args:
        taskset: list
            the taskset to be sorted

    Returns:
        ordered taskset, with .priority set
    """
    # sort tasks by their execution times
    taskset_ordered_by_c = []
    for task_i in taskset:
        if not taskset_ordered_by_c:
            taskset_ordered_by_c.append(task_i)
        else:
            b_found = False
            for idx, task_j in enumerate(taskset_ordered_by_c):
                if task_i.C <= task_j.C:
                    taskset_ordered_by_c.insert(idx, task_i)
                    b_found = True
                    break
            if not b_found:  # append at the end if no place found
                taskset_ordered_by_c.append(task_i)

    # sort priority assignment
    taskset_ordered = []
    if priority_assignment_policy == PriorityAssignmentPolicy.RM:  # Rate Monotonic
        for task_i in taskset_ordered_by_c:
            if not taskset_ordered:
                taskset_ordered.append(task_i)
            else:
                b_found = False
                for idx, task_j in enumerate(taskset_ordered):
                    if task_i.T < task_j.T:
                        taskset_ordered.insert(idx, task_i)
                        b_found = True
                        break
                if not b_found:  # append at the end if no place found
                    taskset_ordered.append(task_i)
    elif priority_assignment_policy == PriorityAssignmentPolicy.DM:  # Deadline Monotonic
        for task_i in taskset_ordered_by_c:
            if not taskset_ordered:
                taskset_ordered.append(task_i)
            else:
                b_found = False
                for idx, task_j in enumerate(taskset_ordered):
                    if task_i.D < task_j.D:
                        taskset_ordered.insert(idx, task_i)
                        b_found = True
                        break
                if not b_found:  # append at the end if no place found
                    taskset_ordered.append(task_i)
    else:
        raise Exception("Priority assignment policy is invalid.")

    # assign priorities (larger is higher)
    for idx, task_i in enumerate(taskset_ordered):
        task_i.prio = len(taskset_ordered) - idx
        task_i.id = idx

    return taskset_ordered
