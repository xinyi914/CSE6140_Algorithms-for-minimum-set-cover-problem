# The file is the implementation for Branch and Bound
# branch_and_bound() will be called in script.py
# and return the best solution

import sys
import os
import time
import argparse
from collections import deque

def read_input_bnb(filename):
    with open(filename, 'r') as f:
        first_line = f.readline().split() #reads a single line from the file, splits the string by space
        n = int(first_line[0]) #number of elements in U
        m = int(first_line[1]) #number of subsets
        subsets = [] #initializes an empty list to store information about each subset
        for idx in range(m): #subset 1 to m
            parts = list(map(int, f.readline().split())) # reads each line/subset
            size = parts[0] #size of each subset
            elements = parts[1:] #elements of each subset
            bitmask = 0 #we use bitmasking(a binary number to store a set) to make the best solution finding process more efficient. We use a decimal number to represent a binary number, and that binary number’s bit positions tell us whether each element is in or out of a subset. the process is : use binary to represent a subset, and the conver the binary to a decimal, which is bitmask value
            for e in elements:
                bitmask |= 1 << (e - 1) #Shift 1 left by e-1 positions, then OR it with the current mask. Bitwise OR rule: A bit becomes 1 if either side is 1
            subsets.append((bitmask, size, idx)) # a list of tuples, subset 1 to m
    return n, m, subsets

# We use a greedy algorithm to find a bounding solution, providing an upper bound for pruning to make bnb more efficient
def greedy_set_cover_bnb(n, subsets):
    universe = (1 << n) - 1 # Make bits 0 to n-1 are 1, by shifting 1 left n times, 1 at position n, and 0s everywhere else(starting from position 0). And subtracting 1 flips all the bits below position n to 1
    covered = 0 #also a bitmask, tracks which elements in the universe have already been covered by the subsets we've selected so far
    selected = [] #store the indices of selected subsets that we pick for our solution
    remaining_subsets = subsets.copy()
    remaining_subsets.sort(key=lambda x: (-x[1], x[2])) #Sorts the subsets in descending order of size (greedily prefer large ones first), and then by ascending original index
    while covered != universe:
        best_gain = 0 # tracks the maximum number of new elements(elements that aren't already covered) a subset can add to the current solution at each iteration of the loop
        best_subset = None
        best_idx = -1 #the position of the subset in the current remaining_subsets list
        best_original_idx = -1 #original input index of that subset
        for i, (bitmask, size, original_idx) in enumerate(remaining_subsets): #returns the index and the item in the sorted remaining_subset
            gain = bin(bitmask & (~covered)).count('1') #~covered gives bits for elements not yet covered, so & means keep the elements in both bitmask and uncovered sets
            if gain > best_gain or (gain == best_gain and original_idx < best_original_idx): # We update our best choice if this subset adds more new elements or it adds the same amount, but has a smaller original index
                best_gain = gain
                best_subset = bitmask
                best_idx = i
                best_original_idx = original_idx
        if best_gain == 0:
            raise ValueError("No feasible solution exists.")
        covered |= best_subset # Update the covered set — OR in the new subset’s bitmask
        selected.append(best_original_idx) #Record this subset’s index as part of the solution
        remaining_subsets.pop(best_idx) #Remove it from the list so it won’t be picked again
    return selected

# We use Breadth-First Search to implement BnB
def branch_and_bound(n, subsets, cutoff_time, initial_size, start_time, trace, initial_solution):
    #step1: Initialization
    sorted_subsets = sorted(subsets, key=lambda x: (-x[1], x[2]))
    m = len(sorted_subsets)
    max_remaining = [0] * m # initialize a list with m zeros, and max_remaining[i] will store the largest size of any subset from index i to the end
    if m > 0:
        max_remaining[-1] = sorted_subsets[-1][1]
        for i in range(m-2, -1, -1):
            max_remaining[i] = max(sorted_subsets[i][1], max_remaining[i+1])
    all_covered = (1 << n) - 1
    best_solution = initial_solution.copy() #the greedy solution is used as the initial solution
    best_size = initial_size

    #step2: BFS
    queue = deque([(0, 0, 0, [])])
    while queue and (time.time() - start_time) < cutoff_time:
        i, covered, count, selected = queue.popleft()  #BFS is FIFO. Take the next node from the front of the queue

        if covered == all_covered:
            if count < best_size: #If all elements are covered, update the best solution if this one is smaller
                best_size = count
                best_solution = selected.copy()
                trace.append((time.time() - start_time, best_size))
            continue

        if i >= m:
            continue

        remaining_elements = all_covered & (~covered) 
        num_uncovered = bin(remaining_elements).count('1') #Count how many elements are left to cover
        if num_uncovered == 0:
            if count < best_size:
                best_size = count
                best_solution = selected.copy()
                trace.append((time.time() - start_time, best_size))
            continue

        #3.Lower Bound Calculation
        if i + 1 < m:
            remaining_max = max_remaining[i + 1]
        else:
            remaining_max = 0

        if remaining_max == 0:
            lower_bound = float('inf') if num_uncovered > 0 else count
        else:
            lower_bound = count + (num_uncovered + remaining_max - 1) // remaining_max #The best-case estimate of how many subsets we still need, starting from a partial solution

        current_bitmask, _, original_idx = sorted_subsets[i]
        new_covered = covered | current_bitmask #What we would cover if we include this subset
        
        if lower_bound >= best_size:#if lower bound > upper bound, then cut the subtree
            if new_covered != covered and (count + 1) < best_size: #Compute coverage if we include subset i
                new_selected = selected.copy()
                new_selected.append(original_idx)
                queue.append((i + 1, new_covered, count + 1, new_selected))

        else: # If lower bound is promising, add two branches
            queue.append((i + 1, covered, count, selected.copy()))  # 1.exclude current subset
            if new_covered != covered and (count + 1) < best_size: # 2.include current subset
                new_selected = selected.copy()
                new_selected.append(original_idx)
                queue.append((i + 1, new_covered, count + 1, new_selected))

    return best_solution

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-inst', type=str, required=True)
    parser.add_argument('-alg', type=str, required=True)
    parser.add_argument('-time', type=float, required=True)
    args = parser.parse_args()

    n, m, subsets = read_input(args.inst)
    try:
        initial_solution = greedy_set_cover_bnb(n, subsets)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return
    initial_size = len(initial_solution)

    start_time = time.time()
    trace = [(0.0, initial_size)]
    best_solution = branch_and_bound(n, subsets, args.time, initial_size, start_time, trace, initial_solution)
    end_time = time.time()
    runtime = round(end_time - start_time, 4)
    print(f"BnB runtime: {runtime} seconds") #this is only for bnb running, not including the greedy algorithm

    instance_name = os.path.splitext(os.path.basename(args.inst))[0]
    sol_filename = f"{instance_name}_{args.alg}_{int(args.time)}.sol"
    trace_filename = f"{instance_name}_{args.alg}_{int(args.time)}.trace"

    with open(sol_filename, 'w') as f_sol:
        f_sol.write(f"{len(best_solution)}\n")
        f_sol.write(' '.join(map(str, best_solution)))

    with open(trace_filename, 'w') as f_trace:
        for t, q in trace:
            f_trace.write(f"{t:.2f} {q}\n")

if __name__ == '__main__':
    main()