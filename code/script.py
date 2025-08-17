import argparse
import time
import random
import os
from hill import hill_climbing
from SA import simulated_annealing
from approx import greedy_set_cover
from BnB import branch_and_bound, greedy_set_cover_bnb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-inst',required = True, help='Input filename')
    parser.add_argument('-alg',required=True,choices=['BnB','Approx','hill','annealing'],help='Algorithm')
    parser.add_argument('-time',type = float, required=True,help='Cutoff in seconds')
    parser.add_argument('-seed',type = int, help='Random seed')

    return parser.parse_args()

def read_file(file_path):
    with open(file_path,"r") as f:
        lines = f.readlines()
        n,m = map(int,lines[0].split())
        u = set(range(1,n+1))
        s = [set(map(int,line.strip().split()[1:])) for line in lines[1:m+1]]
    return u,s

def read_optimal(file_path):
    with open(file_path,'r') as f:
        return int(f.readline().strip())

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



 
def main():
    args = parse_args()
    filename = args.inst
    algo = args.alg
    # cut = float(args.time)
    cut = args.time
    if args.seed is not None:
        seed = int(args.seed)
    

    if algo == "hill":
        u,s = read_file(filename)
        start_time = time.time()
        best_cover,trace_time,trace_sol,_= hill_climbing(u, s,cutoff = cut,seed = seed)
        best_cover = [x+1 for x in best_cover]
        end_time = time.time()
        runtime = end_time - start_time
    elif algo == "annealing":
        u,s = read_file(filename)
        start_time = time.time()
        best_cover,trace_time,trace_sol,_= simulated_annealing(u, s,cutoff = cut,seed = seed)
        best_cover = [x+1 for x in best_cover]
        end_time = time.time()
        runtime = end_time - start_time
    elif algo == "Approx":
        u,s = read_file(filename)
        start_time = time.time()
        best_cover = greedy_set_cover(u,s)
        end_time = time.time()
        runtime = end_time - start_time
    else:
        n, m, subsets = read_input_bnb(filename)
        try:
            initial_solution = greedy_set_cover_bnb(n, subsets)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return
        initial_size = len(initial_solution)
        start_time = time.time()
        trace = [(0.0, initial_size)]
        best_cover = branch_and_bound(n, subsets, cut, initial_size, start_time, trace, initial_solution)
        end_time = time.time()
        runtime = round(end_time - start_time, 4)

    # generate solution file
    file_baseName = f'../output/{algo}/'+os.path.splitext(os.path.basename(filename))[0]
    if args.seed is not None: 
        sol_filename = f'{file_baseName}_{algo}_{cut}_{seed}.sol'
    else:
        sol_filename = f'{file_baseName}_{algo}_{cut}.sol'
    with open(sol_filename,'w') as f:
        f.write(str(len(best_cover))+'\n')
        for i in best_cover:
            f.write(str(i)+ ' ')
        
    # generate trace file
    if algo != "Approx":
        if algo == "hill" or algo == "annealing":
            trace_filename = f'{file_baseName}_{algo}_{cut}_{seed}.trace'
            with open(trace_filename,'w') as f:
                for i in range(len(trace_sol)):
                    f.write(str(trace_time[i])+ ' ' + str(trace_sol[i]) + '\n')

        else:
            trace_filename = f'{file_baseName}_{algo}_{cut}.trace'
            with open(trace_filename, 'w') as f_trace:
                for t, q in trace:
                    f_trace.write(f"{t:.2f} {q}\n")



if __name__ == "__main__":

    main()


