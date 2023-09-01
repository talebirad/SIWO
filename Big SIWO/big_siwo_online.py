'''
SIWO Algorithm Entry Point:
This script provides a command-line interface to run the SIWO community search algorithm. It allows users to specify various parameters including input file, query node, mode of operation, debug level, and more.

Usage:
python main.py [options]

For a list of options, use:
python main.py -h
'''

import time
import multiprocessing
import argparse 
from siwo_alg import siwo

if __name__=='__main__':
    start_time = time.time()

    # Initialize argument parser
    parser = argparse.ArgumentParser()

    # Input file containing the graph data
    parser.add_argument("-i", "--input",  const="datasets/karate_adjlist.txt", default="datasets/karate_adjlist.txt", type=str, nargs='?', help = "Path of input file as adjacency list, default: datasets/karate_adjlist.txt")

    # Starting query node for community detection
    parser.add_argument("-q", "--query",  const=1, default=1, type=int, nargs='?', help = "Starting query node, default: 1")

    # Mode determines the strength value types used in the algorithm
    parser.add_argument("-m", "--mode",  const=1, default=1, type=int, nargs='?', help = "Mode for strength value types, 1 for values in [-1,1], 2 for values in [0,1], 3 for Jaccard Index as strengths, default: 1")

    # Debug level for verbose output
    parser.add_argument("-d", "--debug",  const=0, default=0, type=int, nargs='?', help = "Debug, default: 0")

    # Maximum execution time for the algorithm
    parser.add_argument("-t", "--timeout",  const=10, default=1200, type=float, nargs='?', help = "Timeout for algorithm in seconds (float), default: 1200 ")

    # Path for the output file where results will be saved
    parser.add_argument("-o", "--output",  const="results.txt", default="results.txt", type=str, nargs='?', help = "Output file path for results (community and time spent), default: results.txt)")

    # Parse the given arguments
    parsed_args = vars(parser.parse_args())

    # Extract the parsed arguments
    inp = parsed_args['input']
    query = parsed_args['query']
    mode = parsed_args['mode']
    debug = parsed_args['debug']
    timeout = parsed_args['timeout']
    out_path = parsed_args['output']

    # Initialize shared variables for multiprocessing
    max_size = 100000
    current_community = multiprocessing.Array('i',[-1 for i in range(max_size)])
    nodes_visited = multiprocessing.Value('i', 0)
    comm_str = multiprocessing.Value('d', 0)
    
    # Start the SIWO algorithm in a separate process
    p = multiprocessing.Process(target=siwo, args=(inp, query, mode, debug, current_community, nodes_visited, comm_str))
    p.start()
    p.join(max(0, timeout - (time.time() - start_time)))

    # Check for timeout
    is_timeout = False
    if p.is_alive():
        print("Timeout! Results could improve given more time.")
        is_timeout = True
        p.terminate()
        p.join()
    
    # Display the results
    if current_community:
        result = [x for x in current_community if x != -1]
        if len(result) > 1:
            if is_timeout:
                print("Current results:")
            else:
                print("Run Finished! Complete results:")

            print(sorted(result))
            print("Size of community: {}".format(len(result)))
            print("Number of nodes visited: {}".format(nodes_visited.value))
        else:
            print("No community found for this query node.")
    else:
        print('SIWO was terminated too soon.')
    
    # Display execution time
    time_spent = time.time() - start_time
    print("Exact time spent: {} seconds".format(time_spent))

    # Save results to the output file
    with open(out_path, 'w') as f:
        if len(result) > 1:
            f.write(str(sorted(result)) + "\n")
            f.write(str(time_spent) + "\n")
        else:
            f.write("")