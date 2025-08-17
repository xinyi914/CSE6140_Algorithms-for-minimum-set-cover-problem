# This file implements the approximation algorithm
# greedy_set_cover() will be called in script.py
# return best solution

import time
def greedy_set_cover(U, subsets):
    """
    Parameters:
    - n: number of elements in the universe
    - subsets: list of sets (each is a set of integers representing items)

    Returns:
    - chosen_subsets: indices of subsets chosen (1-indexed)
    """
    # U = set(range(1, n + 1))  # universe to cover
    covered = set()
    chosen_subsets = []

    while covered != U:
        best_subset = None
        best_index = -1
        max_newly_covered = 0

        for idx, subset in enumerate(subsets):
            newly_covered = len(subset - covered)
            if newly_covered > max_newly_covered:
                max_newly_covered = newly_covered
                best_subset = subset
                best_index = idx

        if best_subset is None:
            raise ValueError("Cannot cover all elements in the universe.")

        covered |= best_subset
        chosen_subsets.append(best_index + 1)  # convert to 1-indexed

    return chosen_subsets

