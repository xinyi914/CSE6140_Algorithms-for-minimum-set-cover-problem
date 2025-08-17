# The file is the implementation for Simulated Annealing
# simulated_annealing() will be called in script.py
# and return the best solution, trace time, trace solution, and the time searching for the best solution

import random
import time
import math

# check whether the solution is a valid cover: return true or false
def is_valid_cover(universe,solution_indices,subsets):
    """Check if selected sets cover the entire universe."""
    covered = set().union(*(subsets[i] for i in solution_indices))
    return covered == universe

# check the cost of solution: return the length of the solution
def cost(solution):
    return len(solution)

# get the initial solution: return a list of indices in the solution
def get_initial_solution(universe, subsets):
    uncovered = set(universe) # the uncovered part to universe
    solution_indices = []

    while uncovered:
        # find the subset that has the most covered of universe
        best_index = max(range(len(subsets)), key=lambda i: len(subsets[i] & uncovered))
        solution_indices.append(best_index)
        uncovered -= subsets[best_index] # remove the covered part from uncovered set

    return solution_indices

# get the neighbor based on current solution
def get_neighbor(current_solution, subsets, universe):

    neighbor = current_solution[:]

    action = random.choice(["add", "remove", "swap"]) # randomly choose three actions

    # remove a random subset from the list 
    if action == "remove" and len(neighbor) > 1:
        choices = neighbor # have a list of choices which for now is current solution

        to_remove = random.choice(choices) #  randomly choose an index for remove
        test = list(set(neighbor)-set([to_remove])) # remove the choice from the neighbor
        choices = test # update the choice list

        # loop the same process as before until finding a valid cover or there's no choice for index to remove
        while not is_valid_cover(universe, test,subsets) and len(choices) > 0:
            to_remove = random.choice(choices) 
            test = list(set(neighbor)-set([to_remove]))
            choices = list(set(choices)-set([to_remove]))

        if is_valid_cover(universe, test,subsets):
            neighbor = test
      
            
    # add a random subset from the list
    elif action == "add":
        candidate = random.choice(range(len(subsets))) # choose a random candidate for adding
        if candidate not in neighbor:
            neighbor.append(candidate)
    
    # swap a subset with a new one
    elif action == "swap" and len(neighbor) > 0 and len(neighbor) < len(subsets):

        to_remove = random.choice(neighbor)# randomly choose an index from the current solution to remove
    
        not_neighbor = list(set(range(len(subsets))) - set(neighbor))# the list of the index that not in the current solution
        
        to_add = random.choice([s for s in not_neighbor])# randomly choose an index not from the current solution to add
        ori_list = list(set(neighbor)-set([to_remove]))
        test = ori_list + [to_add] # merge the rest of original current solution and newly added index
        not_neighbor = list(set(not_neighbor)-set([to_add])) # update the list of index that are not in new solution

        # loop same process as before until it find one valid solution or there's no choice for adding 
        while not is_valid_cover(universe, test,subsets) and len(not_neighbor) > 0: 
            to_add = random.choice([s for s in not_neighbor]) 
            ori_list = list(set(neighbor)-set([to_remove]))
            test = ori_list + [to_add]
            not_neighbor = list(set(not_neighbor)-set([to_add]))

        # if a valid neiighbor is found
        if is_valid_cover(universe, test,subsets): 
            neighbor = test      

    return neighbor

# the algorithm for simulated annealing
def simulated_annealing(universe, subsets, initial_temp=1, cooling_rate=0.95, max_iterations=10000,seed=42,cutoff = 1000):
    start = time.time()
    trace_time = []
    trace_sol = []
    random.seed(seed)
    current_solution = get_initial_solution(universe, subsets) # get initial solution 
    best_solution = current_solution[:] # current best solution
    print(len(best_solution))
    trace_time.append(round(time.time() - start,4))
    trace_sol.append(len(best_solution))
    temperature = initial_temp # 
    track_convergence = 0 # track if it convergence
    for _ in range(max_iterations):
        
        # conditions for breaking the loop
        if (time.time()-start) > cutoff:
            break
        if temperature == 0:
            break
        if track_convergence > 1000: # if the best solution not being updated over 1000 times, cut it
            break

        track_convergence += 1

        neighbor = get_neighbor(current_solution, subsets, universe) # get neighbor
        delta = cost(current_solution) - cost(neighbor) # calculate delta

        if delta > 0:
            current_solution = neighbor
        
        elif random.random() < math.exp(delta / temperature): # bad move with some probability
            current_solution = neighbor

        if cost(current_solution) < cost(best_solution): # record and track the best solution
            track_convergence = 0
            best_solution = current_solution
            trace_time.append(round(time.time() - start,4))
            trace_sol.append(len(best_solution))

        temperature *= cooling_rate # update the temperature

    final_time = trace_time[-1] # record the final time of the best overall solution 
    return best_solution,trace_time,trace_sol,final_time