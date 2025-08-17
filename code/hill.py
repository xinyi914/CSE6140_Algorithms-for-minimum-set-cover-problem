# The file is the implementation for Random Restart Hill Climbing
# hill_climbing() will be called in script.py
# and return the best solution, trace time, trace solution, and the time searching for the best solution

import random
import time
import math

# check if the solution is a valid cover
def is_valid_cover(universe,solution_indices,subsets):
    covered = set().union(*(subsets[i] for i in solution_indices))
    return covered == universe

# check if the cost of a solution
def cost(solution):
    return len(solution)

# get the best next state based on current solution which is one less than or the same as current solution
# return the best neighbor
def get_best_neighbor(current_solution, subsets, universe):

    neighbor = current_solution[:]
    choices = neighbor # have a list of choices which for now is current solution

    to_remove = random.choice(choices) #  randomly choose an index for remove
    test = list(set(neighbor)-set([to_remove])) # remove the choice from the neighbor
    choices = test # update the choice list
    valid = is_valid_cover(universe,test,subsets)  # test if test is a valid cover

    # loop the same process as before until finding a valid cover or there's no choice for index to remove
    while not valid and len(choices) > 0:
        to_remove = random.choice(choices) 
        test = list(set(neighbor)-set([to_remove]))
        choices = list(set(choices)-set([to_remove]))
        valid = is_valid_cover(universe,test,subsets)

    if valid:
        neighbor = test

    return neighbor

# get the random initial solutio
# return the solution indices 
def get_random_initial(subsets, universe):

    uncovered = set(universe) # the set of uncovered set for universe
    left_subsets = subsets # subset for randomly choose
    solution_indices = []
    random_choice = random.randint(0, len(subsets)-1) # randomly choose an index of a subset
    solution_indices.append(random_choice) # add the chosen index to the solution
    uncovered -= subsets[random_choice] # remove the chosen subset from the universe
    temp = subsets[random_choice] # store the chosen subset for now

    left_subsets.remove(temp) # remove the chosen subset from the list of choices so that it will not be chosen again

    # loop until all element in universe covered
    while uncovered:
        # choose the subset that covers most uncovered part of universe
        best_index = max(range(len(left_subsets)), key=lambda i: len(left_subsets[i] & uncovered))
        # add the chosen subset into the solution 
        solution_indices.append(best_index)
        # removed the chosen subset from the uncovered part because now it is covered
        uncovered -= subsets[best_index]

    # add what removed from subset back to keep the subset the same
    left_subsets.append(temp)

    return solution_indices

    
# random restart hill climbing
def hill_climbing(universe, subsets, max_iterations=10000,seed = 42,cutoff = 1000):
    random.seed(seed)
    start = time.time()
    trace_time = []
    trace_sol = []

    current_solution = get_random_initial(subsets,universe) # get initial solution
    best_solution = current_solution[:] # set this initial solution as the initial best solution 
    trace_time.append(round(time.time() - start,4))
    trace_sol.append(len(best_solution))
    
    track_converge = 0 # track for convergence of the algorithm

    for _ in range(max_iterations):
        if (time.time()-start) > cutoff:
            break
        if track_converge > 100: # if the best solution is not updated after 100 iterations, then it stops
            break

        track_converge += 1

        current_solution = get_random_initial(subsets,universe) # get another initial solution: random restart
        neighbor = get_best_neighbor(current_solution, subsets, universe) # find the best next state

        # loop until there's no better neighbor
        while cost(neighbor) < cost(current_solution):
            current_solution = neighbor 
            neighbor = get_best_neighbor(current_solution, subsets, universe) #find the best next state based on current solution

        # when there's no better solution, check if this random initial gives a better local optimum
        if cost(neighbor) < cost(best_solution):
            track_converge = 0
            best_solution = neighbor # assign the current solution to the neighbor
            trace_time.append(round(time.time() - start,4))
            trace_sol.append(len(best_solution))


    end = time.time()
    time_stamp = end - start
    final_time = trace_time[-1]
    return best_solution,trace_time,trace_sol,final_time
