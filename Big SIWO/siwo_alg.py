from FastGraph import fast_graph
import time
import sys

def siwo(inp,query,mode,debug,current_community_array,nodes_visited,comm_str):
	"""
	Implements the SIWO (Strong and Weak link Optimization) community search algorithm.

	Parameters:
	- inp (str): Path to the input file containing the graph data.
	- query (int): The query node around which the community will be detected.
	- mode (int): Mode of operation. Affects the minimum improvement value. 
					1 indicates one type of operation, other values indicate another.
	- debug (int): Debug level for print statements. 
					Higher values result in more detailed debugging information.
	- current_community_array (list): An array to store the nodes of the detected community.
	- nodes_visited (multiprocessing.Value): A shared variable to store the number of nodes visited.
	- comm_str (multiprocessing.Value): A shared variable to store the strength of the community.

	Raises:
	- ValueError: If the query node is a peripheral node.

	Note:
	This function modifies the `current_community_array`, `nodes_visited`, and `comm_str` in place and doesn't return a value explicitly.
	"""
	print('Starting SIWO')
	current_community=[query]
	current_community_array[0]=query
	time_list=[]
	min_improvement=0 if mode==1 else 1 #????????
	start_time=time.time()
	shell_info={}
	current_comm_str=0
	G=fast_graph(inp,mode)
	if len(G.get_neighbors(query))==1:
		raise ValueError('Query node is Peripheral')

	#start of algorithm
	for x in G.get_neighbors(query):
		shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[1],'relative_str_list':[],'current_str_contribution':G.strg(x,query)}
	

	while True:
		candidate_strg=[]
		candidate_nodes=list(shell_info.keys())
		for i in candidate_nodes:
			candidate_strg.append(shell_info[i]['current_str_contribution'])
		best_candidate_index=candidate_strg.index(max(candidate_strg))

		time_list.append(time.time()-start_time)
		if debug>=2:
			print("Current community: {}".format(current_community))
			print("Candidate nodes and strengths: {}".format([(candidate_nodes[i],candidate_strg[i]) for i in range(len(candidate_nodes))]))
			print('-----------')
			pass
		if (len(current_community)>=4 and candidate_strg[best_candidate_index]<min_improvement) or len(current_community)+1==len(current_community_array):
			break
		else:
			current_community.append(candidate_nodes[best_candidate_index])
			new_node=current_community[-1]
			current_community_array[len(current_community)-1]=new_node
			current_comm_str+=candidate_strg[best_candidate_index]
			comm_str.value=current_comm_str
			if debug>=1:
				print('New node: {}, Improvement: {:.4f}, Time spent: {:.4f}, Current community size: {}, Current community strength:{:.4f}'.format(candidate_nodes[best_candidate_index],candidate_strg[best_candidate_index],time_list[-1],len(current_community),current_comm_str))
				print('Support dict mem size:{:.4f} MBs, Strength dict mem size:{:.4f} MBs, Neighborhood dict mem size:{:.4f} MBs'.format(sys.getsizeof(G.support_dict)/(2**20),sys.getsizeof(G.strength_dict)/(2**20),sys.getsizeof(G.neighb_dict)/(2**20)))
				print('-----------')

			for x in set(shell_info.keys()).intersection(G.get_neighbors(new_node)):
				shell_info[x]['current_str_contribution']+=G.strg(new_node,x)
				# shell_info[x]['outward_str']-=G.strg(new_node,x)
			#neighbors of the new node are addded to shell
			for x in G.get_neighbors(new_node):
				if x not in shell_info and x not in current_community:
					# shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[len(current_community)],'relative_str_list':[],'current_str_contribution':sum([G.strg(x,y) for y in current_community]),'outward_str':sum([G.strg(x,y) for y in set(G.get_neighbors(x))-set(current_community)])}
					
					shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[len(current_community)],'relative_str_list':[],'current_str_contribution':sum([G.strg(x,y) for y in current_community])}
			
			del shell_info[new_node]
			if debug>=1:
				print()
			if debug>=2:
				print('Support dict size:{}, Strength dict size:{}, Neighborhood dict size:{}'.format(len(G.support_dict),len(G.strength_dict),len(G.neighb_dict)))
			if debug==-1 and len(current_community)%100==2:
				print('Current Community: {}({})'.format(sorted(current_community),len(current_community)))
			nodes_visited.value=len(G.neighb_dict)

		nodes_should_be_added=[]

	#adding peripheral nodes that were missed
	last_neighbor_list=[]
	for x in current_community:
		last_neighbor_list+=G.get_neighbors(x)
	for x in last_neighbor_list:
		if x not in current_community and len(G.get_neighbors(x))==1:
			nodes_should_be_added.append(x)
	if nodes_should_be_added:
		print('Peripheral nodes that should be added: {}'.format(nodes_should_be_added))
	for x in nodes_should_be_added:
		current_community.append(x)
		current_community_array[len(current_community)-1]=x

