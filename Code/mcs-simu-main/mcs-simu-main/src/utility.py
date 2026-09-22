# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import math


def aggregate_window(x, y, sampling_window_size):
    """Aggregate data inside a sampling window. The data is provided in a (x,y) pair.

    Parameters
    ----------
    x : list
    y : list
    sampling_window_size : int
        The size of the window to use

    Returns
    -------
    list
        the output is a sequence of sum(y[idx], y[idx+window_size-1])
    """
    z = []

    # iterate x and y
    idx = 0

    max_x = max(x)

    while max_x >= idx + sampling_window_size - 1:
        idx_low = 0
        idx_high = 0

        data = y[idx:idx + sampling_window_size]
        print(x[idx], sum(data))
        z.append(sum(data))
        idx += sampling_window_size


if __name__ == "__main__":
    xs = [0, 10, 15, 20, 25]
    ys = [1, 1, 1, 1, 1]
    aggregate_window(xs, ys, 5)
