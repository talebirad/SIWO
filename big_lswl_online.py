import linecache
import time
import pandas as pd
import matplotlib.pyplot as plt
import sys
import multiprocessing
import argparse 
import scipy.stats
import os.path
from itertools import islice
from collections import deque
from collections import Counter
import gc
import networkx as nx
def convert_colored_list(L):
	return '['+', '.join(str(item) for item in L)+']'


class fast_file():
    def __init__(self, inp):
        self.file=open(inp,'rb',8192)
        self.line_offset = deque()
        self.line_offset.append(0)
    def getline(self, i):
        diff=i-len(self.line_offset)
        if diff>0:
            j=0
            offset = self.line_offset[-1]
            self.file.seek(offset)
            for line in self.file:
                j+=1
                offset += len(line)
                self.line_offset.append(offset)
                if j>=diff:
                    break
        self.file.seek(self.line_offset[i-1])
        result=self.file.readline()
        if diff==0:
            self.line_offset.append(self.line_offset[-1]+len(result))
        return result 
    def close(self):
        self.file.close()

def score(input_file,query,result,timeout,ground_path,output_path,time_spent,nodes_visited,comm_str,color):
	if not os.path.isfile(ground_path):
		raise ValueError('Ground truth file does not exist')
	ground_file=fast_file(ground_path)
	line_offset=1-int(str(ground_file.getline(1))[2])

	queries=[query] #list of query nodes [q1,q2,...]
	ground=[] #list of ground truch communities for each query node: [comm(q1),comm(q2),...]
	output=[sorted(result)] #list of outputs for each query node: [lswl(q1),lswl(q2),...]
	results={'Datetime':[],'Timeout':[],'Time_spent':[], 'Network':[],'Node':[],'Output_size':[],'Ground_size':[],'Nodes_visited':[],'Community_str':[],'Recall':[],'Precision':[],'F1':[]}

	for x in queries:
		txt=str(ground_file.getline(x+line_offset))
		idx2=txt.index('(')
		idx1=txt.index('[')
		ground.append(eval(txt[idx1:idx2-1])) 



	for x in range(len(queries)):
		recall=len(set(ground[x]).intersection(set(output[x])))/len(set(ground[x]))
		precision=len(set(ground[x]).intersection(set(output[x])))/len(set(output[x]))
		f1=(2*precision*recall)/(precision+recall)
		temp_output=['\033[92m'+str(y)+'\033[0m' if y in ground[x] else '\033[94m'+str(y)+'\033[0m' for y in output[x] ]
		temp_ground=['\033[92m'+str(y)+'\033[0m' if y in output[x] else '\033[91m'+str(y)+'\033[0m' for y in ground[x] ]
		temp_output=convert_colored_list(temp_output)
		temp_ground=convert_colored_list(temp_ground)
		if recall>0.5:
			print('\033[93mNode {} results:\033\n'.format(queries[x]))
			print('[0mOutput: {} (Size {})\n'.format(temp_output,len(output[x])))
			print('Ground Truth: {} (Size {})\n'.format(temp_ground,len(ground[x])))
			print('Scores for node {}: \033[91mRecall\033[0m {}, \033[94mPrecision\033[0m: {}, F1: {}'.format(queries[x],recall,precision,f1))
		else:

			print('\033[91mNode {} results:\033\n'.format(queries[x]))
			print('[0mOutput: {} (Size {})\n'.format(temp_output,len(output[x])))
			print('Ground Truth: {} (Size {})\n'.format(temp_ground,len(ground[x])))
			print('Scores for node {}: \033[91mRecall: {}\033[0m, \033[94mPrecision\033[0m: \033[91m{}\033[0m, \033[91mF1: {}\033[0m'.format(queries[x],recall,precision,f1))
		results['Datetime'].append(pd.to_datetime('now',utc=True))
		results['Timeout'].append(timeout)
		results['Time_spent'].append(time_spent)
		results['Network'].append(input_file)
		results['Node'].append(queries[x])
		results['Output_size'].append(len(output[x]))
		results['Ground_size'].append(len(ground[x]))
		results['Nodes_visited'].append(nodes_visited)
		results['Community_str'].append(comm_str)
		results['Recall'].append(recall)
		results['Precision'].append(precision)

		results['F1'].append(f1)

		print('―' * 172)
	if output_path:
		df=pd.DataFrame(data=results)
		df.to_csv(output_path, index=False, mode='a', header=not os.path.exists(output_path))
		print('Scores saved in {}'.format(output_path))

class fast_graph():
	def __init__(self,file_name,mode):
		self.neighb_dict={}
		self.support_dict={}
		self.strength_dict={}
		self.neighb_dict={}
		self.file=fast_file(file_name)
		self.line_offset=0
		self.mode=mode
		if not os.path.isfile(file_name):
			raise ValueError('Input file does not exist')
		temp_line_number=1
		for x in open(file_name, 'rb'):
			if x.strip():
				first_line=[int(y) for y in x.split()]
				self.line_offset=temp_line_number-first_line[0]
				self.neighb_dict[first_line[0]]=first_line[1:]
				break
			temp_line_number+=1
	def get_neighbors(self,i):
		if self.neighb_dict.get(i):
			return self.neighb_dict[i]
		line_list=[int(x) for x in self.file.getline(i+self.line_offset).split()]
		if line_list:
			result= line_list[1:]
			self.neighb_dict[i]=result
			return result
		raise ValueError('Node is isolated')
	def sup_u_v(self,u,v):
		if self.support_dict.get((u,v)):
			return self.support_dict[(u,v)]
		if self.support_dict.get((v,u)):
			return self.support_dict[(v,u)]
		N_u=set(self.get_neighbors(u))
		if v not in N_u:
			self.support_dict[(u,v)]=0
			return 0
		N_v=set(self.get_neighbors(v))
		result= len(N_u.intersection(N_v))
		self.support_dict[(u,v)]=result
		return result
	def strg(self,node1,node2):
		if self.strength_dict.get((node1,node2)):
			return self.strength_dict[(node1,node2)]
		if self.strength_dict.get((node2,node1)):
			return self.strength_dict[(node2,node1)]
		if node2 not in set(self.get_neighbors(node1)):
			result=0 #???????????????????????
		else:
			default_result=-1 if self.mode==1 else 0 #?????????
			sup_uv=self.sup_u_v(node1,node2)
			sup_u_max=max([self.sup_u_v(node1,y) for y in self.get_neighbors(node1)])
			sup_v_max=max([self.sup_u_v(y,node2) for y in self.get_neighbors(node2)])
			if sup_u_max and sup_v_max:
				if self.mode==1:
					result=(sup_uv*((1/sup_u_max)+(1/sup_v_max)))-1
				if self.mode==2:
					result=(sup_uv*((1/sup_u_max)+(1/sup_v_max)))/2
				if self.mode==3:
					result=sup_uv/len(set(self.get_neighbors(node1)).union(set(self.get_neighbors(node2))))
			else:
				result=default_result
		self.strength_dict[(node1,node2)]=result
		return result
	def visualize_ego(self,node,radius,vis_out_path):
		H = nx.Graph(self.neighb_dict)
		E = nx.ego_graph(H, node, radius=radius)
		for u,v,d in E.edges(data=True):
			d['weight']=int(self.strg(u,v)*100)/100
		pos=nx.spring_layout(E)
		nx.draw_networkx(E,pos,font_size=5,node_size=17)
		labels = nx.get_edge_attributes(E,'weight')
		nx.draw_networkx_edge_labels(E, pos, edge_labels=labels, font_size=4)
		plt.savefig(vis_out_path)
		print("EGO network visualization saved in {}.".format(vis_out_path))
def lswl(inp,query,mode,debug,current_community_array,nodes_visited,comm_str,vis_out_path):
	print('Starting lswl')
	current_community=[query]
	current_community_array[0]=query
	time_list=[]
	min_improvement=0 if mode==1 else 1 #????????
	start_time=time.time()
	shell_info={} #'degree':degree in graph,'ranking_list':list of rankings (between 0 and 1) in str list over time,'steps_added':step numbers for any step this node is added,'relative_str':list of str(n,C)/str(c) over time
	current_comm_str=0
	G=fast_graph(inp,mode)
	if len(G.get_neighbors(query))==1:
		raise ValueError('Query node is Peripheral')

	#start of algorithm
	for x in G.get_neighbors(query):
		#additional shell analysis:
		# shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[1],'relative_str_list':[],'current_str_contribution':G.strg(x,query),'outward_str':sum([G.strg(x,y) for y in set(G.get_neighbors(x))-set([query])])}
	
		shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[1],'relative_str_list':[],'current_str_contribution':G.strg(x,query)}
	
	# print(shell_info)
	while True:
		candidate_strg=[]
		candidate_nodes=list(shell_info.keys())
		for i in candidate_nodes:
			candidate_strg.append(shell_info[i]['current_str_contribution'])
		best_candidate_index=candidate_strg.index(max(candidate_strg))
		##for Tie analysis:
		# max_list=[candidate_nodes[i] for i in range(len(candidate_strg)) if candidate_strg[i]==max(candidate_strg)]
		# if len(max_list)>1:
			# print("Warning! Ties: {}".format(max_list))
			# pass
		time_list.append(time.time()-start_time)
		# min_improvement=0 if mode==1 else (len(set(get_neighbors(inp,neighb_dict,candidate_nodes[best_candidate_index])).intersection(set(current_community))))/2 #?????
		if debug>=2:
			print("Current community: {}".format(current_community))
			print("Candidate nodes and strengths: {}".format([(candidate_nodes[i],candidate_strg[i]) for i in range(len(candidate_nodes))]))
			print('-----------')
			pass
		if (len(current_community)>=2 and candidate_strg[best_candidate_index]<min_improvement) or len(current_community)+1==len(current_community_array):
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
			#shell info is updated for all

			##additional shell analysis:
			#candidate_rankings=[sorted(candidate_strg)[::-1].index(x) for x in candidate_strg]
			# print("Candidate nodes, strengths, rankings: {}".format([(candidate_nodes[i],candidate_strg[i],candidate_rankings[i]) for i in range(len(candidate_nodes))]))
			# print("rankings: {}".format(candidate_rankings))
			# for x in shell_info:
				# x_index=candidate_nodes.index(x)
			# 	shell_info[x]['relative_ranking_list'].append(1-candidate_rankings[x_index]/len(candidate_rankings))
			# 	shell_info[x]['relative_str_list'].append(candidate_strg[x_index]/current_comm_str)
			for x in set(shell_info.keys()).intersection(G.get_neighbors(new_node)):
				shell_info[x]['current_str_contribution']+=G.strg(new_node,x)
				# shell_info[x]['outward_str']-=G.strg(new_node,x)
			#neighbors of the new node are addded to shell
			for x in G.get_neighbors(new_node):
				if x not in shell_info and x not in current_community:
					# shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[len(current_community)],'relative_str_list':[],'current_str_contribution':sum([G.strg(x,y) for y in current_community]),'outward_str':sum([G.strg(x,y) for y in set(G.get_neighbors(x))-set(current_community)])}
					
					shell_info[x]={'degree':len(G.get_neighbors(x)),'relative_ranking_list':[],'steps_added':[len(current_community)],'relative_str_list':[],'current_str_contribution':sum([G.strg(x,y) for y in current_community])}
					# print('New shell node {} current contribution is {}.'.format(x,shell_info[x]['current_str_contribution']))
			# print('Shell node {} is \033[91mdeleted\033[0m after staying for {} steps. Last info: {}'.format(new_node,len(current_community)-shell_info[new_node]['steps_added'][0],shell_info[new_node]))
			del shell_info[new_node]
			if debug>=1:
				print()
			if debug>=2:
				print('Support dict size:{}, Strength dict size:{}, Neighborhood dict size:{}'.format(len(G.support_dict),len(G.strength_dict),len(G.neighb_dict)))
			if debug==-1 and len(current_community)%100==2:
				print('Current Community: {}({})'.format(sorted(current_community),len(current_community)))
			nodes_visited.value=len(G.neighb_dict)
	#additional shell analysis:
	# for x in shell_info:
	# 	print('Shell info for {}: {}'.format(x,shell_info[x]))
	# 	N=set(G.get_neighbors(x))
	# 	print("Inward degree: {}, Outward degree: {}".format(len(N.intersection(set(current_community))),len(N-(set(current_community)))))
	# 	for y in N.intersection(set(current_community)):
	# 		print("Node {} with strength {}.".format(y,G.strg(y,x)))
	if vis_out_path:
		G.visualize_ego(query,2,vis_out_path)
if __name__=='__main__':
	start_time=time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--timeout",  const=10,default=1200, type=float, nargs='?',help = "Timeout for algorithm in seconds (float), default: 1200 ")
	parser.add_argument("-i", "--input",  const="datasets/karate_adjlist.txt",default="datasets/karate_adjlist.txt", type=str, nargs='?',help = "Path of input file as adjacency list, default: datasets/karate_adjlist.txt")
	parser.add_argument("-q", "--query",  const=1,default=1, type=int, nargs='?',help = "Starting query node, default: 1")
	parser.add_argument("-m", "--mode",  const=1,default=1, type=int, nargs='?',help = "Mode for strength value types, 1 for values in [-1,1], 2 for values in [0,1], 3 for Jaccard Index as strengths, default: 1")
	parser.add_argument("-d", "--debug",  const=0,default=0, type=int, nargs='?',help = "Debug, default: 0")
	parser.add_argument("-g", "--ground",  const=None,default=None, type=str, nargs='?',help = "Path of ground truth file for scoring")
	parser.add_argument("-so", "--score_output",  const=None,default=None, type=str, nargs='?',help = "Output file path (CSV) for scoring")
	parser.add_argument("-vo", "--vis_output",  const=None,default=None, type=str, nargs='?',help = "Output file path (PNG) for local visualization of the ego graph")
	
	parsed_args = vars(parser.parse_args())
	inp=parsed_args['input']
	query=parsed_args['query']
	mode=parsed_args['mode']
	debug=parsed_args['debug']
	timeout=parsed_args['timeout']
	ground_path=parsed_args['ground']
	score_out_path=parsed_args['score_output']
	vis_out_path=parsed_args['vis_output']
	max_size=100000
	results={}
	current_community = multiprocessing.Array('i',[-1 for i in range(max_size)])
	nodes_visited=multiprocessing.Value('i', 0)
	comm_str=multiprocessing.Value('d', 0)
	
	p = multiprocessing.Process(target=lswl,args=(inp,query,mode,debug,current_community,nodes_visited,comm_str,vis_out_path))
	p.start()
	p.join(max(0,timeout-(time.time()-start_time)))
	is_timeout=False
	if p.is_alive():
	    print ("Timeout! Results could improve given more time.")
	    is_timeout=True
	    p.terminate()

	    p.join()
	
	if current_community:
		result=[x for x in current_community if x!=-1]
		if len(result)>1:
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
		print('LSWL was terminated too soon.')
	time_spent=time.time()-start_time
	print("Exact time spent: {} seconds".format(time_spent))
	if ground_path and current_community and len(result)>1:
		print('Scoring the output with ground truth {}:'.format(ground_path))
		score(inp,query,result,timeout,ground_path,score_out_path,time_spent,nodes_visited.value,comm_str.value,True)