from collections import deque


class fast_file():
    """
    A utility class designed for efficient reading and interaction with graph data.

    Attributes:
    - lines: Stores the lines of the input file for quick access.
    - nodes: Dictionary storing nodes and their properties.
    - edges: Dictionary storing edges and their properties.

    Methods:
    - __init__: Initializes the fast_file object, reads the input file, and sets up initial data structures.
    - get_neighbors: Returns the neighbors of a given node.
    - strg: Computes the strength of the connection between a node and a community.
    """
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