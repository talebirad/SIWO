# SIWO
Implementation of "Fast Local Community Discovery: Relying on the Strength of Links".

### Abstract
Community detection methods aim to find nodes connected to each other more than other nodes in a graph. As they explore the entire network, global methods suffer from severe limitations when handling large networks due to their time and space complexity. Local community detection methods are based on an egocentric function aiming to find only the community containing a query node (or set of query nodes). However, existing local methods are often sensitive to which query node(s) is used to discover a particular community. Our proposed approach, called SIWO “Strong In, Weak Out,” is a novel community detection method, which can locally discover densely-connected communities precisely, deterministically, and quickly. Moreover, our experimental evaluation shows that the detected community is not dependent on the initial query node within a community. This method works in a one-node-expansion way based on the notions of strong and weak links in a graph. In short, SIWO starts with a community consisting only of the query node(s). Then it checks the set of nodes in the community’s neighborhood in each step to add the “best” node and finally returns the desired community around the given query node. It can also be used iteratively to detect the entire partitioning of a network with or without considering overlapping communities, and concurrently identify outliers that may not belong in any community. Moreover, as it does not store the entire graph into main memory, it can also be used to find the core of a community on very large networks, while there is limited time and memory available. Finally, SIWO is also able to handle weighted graphs, making SIWO a general framework for community discovery and detection in various type of social networks.


This repository provides implementation for SIWO and SIWO+ described in
> Fast Local Community Discovery: Relying on the Strength of Links.

In some of the files, the algorithm is referred to as "LSWL", which is the alternate name for the SIWO algorithm. The original codes are lswl_offline.py, which finds the communities of nodes in a given network (*the fast implementation*), big_siwo_online.py (in the folder Big SIWO), which does the same thing when the intended network is too large extensive memory consumption needs to be avoided (*the memory efficient implementation*). There is lswl_plus.py, which uses our novel local discovery framework to detect the entire community structure of a given network by iteratively applying the SIWO approach to the unexplored parts of the network. The SIWO+ is capable of finding a partition with overlapping communities or without them, based on user preferences. This method can also find outliers (peripheral nodes of the graph that are marginally connected to communities) and hubs (nodes that bridge the communities). We also have SIWO_plus_weighted.py which is the extension of SIWO+ to handle weighted networks (called SIWOw in the paper). Modularity R and Modularity M are two methods initially presented in the following references, which we implemented for evaluation purposes.


#### References
	@article{Clauset2005,
	 title = {Finding local community structure in networks},
	 volume = {72},
	 number = {2},
	 journal = {Physical Review E},
	 author = {Clauset, Aaron},
	 year = {2005},
	 pages = {026132},
	}

	@inproceedings{Luo2006,
	  year = {2006},
	  author = {Feng Luo and James Wang and Eric Promislow},
	  title = {Exploring Local Community Structures in Large Networks},
	  booktitle = {2006 {IEEE}/{WIC}/{ACM} International Conference on Web Intelligence ({WI}{\textquotesingle}06)},
	  pages = {233--239},
	}

### Requirements
The codebase is implemented in Python 3.8.5 package versions used for development are just below.
```
networkx          2.5
argparse          1.1
```

### Datasets

This repository also contains the synthetic networks we generated via the *LFR benchmark* for our paper's evaluation section. In this repository, lswl_offline.py and lswl_plus.py take the **edge list** of a graph, in which any line indicates an edge between two nodes separated by *\t*. In addition to the network file, a file containing all **query nodes** should exist. In this file, each line has a node used as the start node to discover its community. 

For big_siwo_online.py, the input file must be of the **adjacency list** form. In short, line i of the input file contains node i as the first entry of the line, and all its neighbors as subsequent entries separated by a delimeter. For nodes without neighbors, the line must be empty. Other datasets for larger networks that should be used by big_siwo_online.py are not included in this repository, refer to this link to get them in the desired format: https://drive.google.com/drive/folders/1bDn-pQ2ahxo5gXBZJp35oo7_wqd4DfQ2?usp=sharing

#### Input and output options
```
--strength_type   '1': strengths between [-1,+1] and '2': strengths between [0,1].   Default is '2'.
--network         The address of the network in form of edge list.                   No default value.
--output          The address of the file to store the results.                      Default is './community.dat'.
--timeout         The maximum time in which LSWL should retrieve the community. In some machines this is not reliable, you can try big_siwo_online.py if time is an issue.

for [lswl_offline.py] and [lswl_online.py]:
--query_nodes     The address of the list of query nodes.                            No default value.

for [lswl_plus.py]:
--outlier         If outliers need to merge into communities (y/n).                  Default is 'y'.
--overlap         If overlapping communities need to be detected (y/n).              Default is 'n'.

for [lswl_plus_weighted.py]
--outlier         If outliers need to merge into communities (y/n).                  Default is 'y'.
--overlap         If overlapping communities need to be detected (y/n).              Default is 'n'.
--mean_function	  'min', 'arithmetic', 'geometric', or 'harmonic' averaging.         Default is 'geometric'.
```

#### Examples

The following commands are examples demonstrating how each code in this repository can be executed:
```
$ python lswl_offline.py -n karate_edge_list.txt -q karate_query_nodes.txt -s 1
$ python lswl_plus.py -n karate_edge_list.txt -i y
$ python lswl_plus_weighted.py -n karate_weighted.txt -m arithmetic
$ python mod_r.py -n karate_edge_list.txt -q karate_query_nodes.txt
$ python mod_m.py -n karate_edge_list.txt -q karate_query_nodes.txt
```

Feel free to have a look at different parameters of each code via:
```
$ python [code_name.py] -h
```

#### Implementation for Big Networks
For files that are too big to fit into main memory, use 

This implementation does not use networkx, and has its own function for handling files and the graph. The implementation does not handle multiple query nodes and peripheral node as query node yet, so make sure you use the other codes if the query node is of that kind.

## Usage

To run the SIWO algorithm, use the following command:


`python big_siwo_online.py [options]`

Options:

- `-i, --input`: Path of input file as adjacency list. Default: `datasets/karate_adjlist.txt`
- `-q, --query`: Starting query node. Default: `1`
- `-m, --mode`: Mode for strength value types. Options:
    - `1`: Strength values in [-1,1]
    - `2`: Strength values in [0,1]
- `-d, --debug`: Debug level for verbose output. Default: `0`
- `-t, --timeout`: Timeout for algorithm in seconds. Default: `1200`
- `-o, --output`: Output file path for results. Default: `results.txt`

Example:

`python big_siwo_online.py -i datasets/example_adjlist.txt -q 5 -m 1`

## Examples

 **Basic Usage**:
    
    Command:

    `python big_siwo_online.py -i datasets/karate_adjlist.txt -q 2`
    
    Expected Output:
    
    
    `[List of nodes in the community]`
    
## Additional Notes

- Ensure your input graph is provided as an adjacency list.
- For larger networks, consider increasing the timeout to give the algorithm more time for computation.
- The SIWO algorithm is designed for efficiency but may require more time for extremely large networks.

