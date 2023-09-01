from FastFile import fast_file
import os

class fast_graph():
	"""
    A class representing the graph structure optimized for the SIWO algorithm.

    Attributes:
    - neighb_dict: Dictionary storing neighbors for each node.
    - support_dict: Dictionary storing the support values for pairs of nodes.
    - strength_dict: Dictionary storing the strength values for pairs of nodes.
    - file: An instance of fast_file to efficiently access the graph file.
    - line_offset: An offset to correctly access lines in the file.
    - mode: Mode of operation determining how strengths are calculated.

    Methods:
    - __init__: Initializes the fast_graph object, sets up the initial dictionaries, and reads the graph from the file.
    - get_neighbors: Returns the neighbors of a given node.
    - sup_u_v: Computes the support value between two nodes.
    - strg: Computes the strength of the connection between two nodes.
    """
	def __init__(self,file_name,mode):
		self.neighb_dict={}
		self.support_dict={}
		self.strength_dict={}
		self.neighb_dict={}
		self.file=fast_file(file_name)
		self.line_offset=1
		self.mode=mode
		if not os.path.isfile(file_name):
			raise ValueError('Input file does not exist')
		self.line_offset=1-int(self.file.getline(1).strip().split()[0])
	def get_neighbors(self,i):
		if self.neighb_dict.get(i):
			return self.neighb_dict[i]
		line_list=[int(x) for x in self.file.getline(i+self.line_offset).split()]
		if line_list:
			result= line_list[1:]
			result = sorted(list(set(result)))
			if i in result:
				result.remove(i)
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
			result=0 #??
		else:
			default_result=-1 if self.mode==1 else 0 #??
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