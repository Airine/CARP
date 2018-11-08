from collections import defaultdict, namedtuple
from utils.GraphDrawer import draw_graph
import numpy as np
Edge = namedtuple('Edge', 'weight, demand, distance')

Inf = np.Inf


class Graph(object):
	""" Graph data structure, undirected by default. """

	def __init__(self, CARP_data, directed=False):
		self.graph = defaultdict(set)
		self._directed = directed
		self.node_number = int(CARP_data.specification.get('VERTICES'))
		self.edge_dict = dict()
		self.connections = list()
		self.generator(CARP_data)

	def generator(self, CARP_data):
		""" Generate a graph with a CARP_data object """

		for i in CARP_data.data:
			tempt = tuple(i[0:2])
			self.connections.append(tempt)
			self.edge_dict[tempt] = Edge(i[2], i[3], i[2])
		self.add_connections()

	def add_connections(self):
		""" Add connections (list of tuple pairs) to graph """

		for node1, node2 in self.connections:
			self.add(node1, node2)

	def add(self, node1, node2):
		""" Add connection between node1 and node2 """

		self.graph[node1].add(node2)
		if not self._directed:
			self.graph[node2].add(node1)

	def remove(self, node):
		""" Remove all references to node """

		for n, cxns in self.graph.iteritems():
			try:
				cxns.remove(node)
			except KeyError:
				pass
		try:
			del self.graph[node]
		except KeyError:
			pass

	def is_connected(self, node1, node2):
		""" Is node1 directly connected to node2 """

		return node1 in self.graph and node2 in self.graph[node1]

	def get_weight(self, node1, node2):
		""" Get the weight between two connected nodes """

		assert self.is_connected(node1, node2)
		tempt = (node1, node2) if node1 < node2 else (node2, node1)
		return getattr(self.edge_dict[tempt], 'weight')

	def set_distance(self, node1, node2, dis):
		""" Set the distance between two nodes """

		tempt = (node1, node2) if node1 < node2 else (node2, node1)
		is_edge = self.edge_dict.keys().__contains__(tempt)
		temp_demand = 0
		temp_weight = 0
		if is_edge:
			temp_weight = getattr(self.edge_dict[tempt], 'weight')
			temp_demand = getattr(self.edge_dict[tempt], 'demand')
		self.edge_dict[tempt] = Edge(temp_weight, temp_demand, dis)

	def get_distance(self, node1, node2):
		""" Get the distance between two nodes """

		if node1 == node2:
			return 0
		tempt = (node1, node2) if node1 < node2 else (node2, node1)
		if not self.edge_dict.keys().__contains__(tempt):
			return Inf
		return getattr(self.edge_dict[tempt], 'distance')

	def get_distances(self, node):
		distances_list = list()
		for dest in self.graph:
			distances_list.append('{} -> {}\t: {}'.format(node, dest, self.get_distance(node, dest)))
		return distances_list

	def floyd(self):
		for i in self.graph:
			for j in self.graph:
				for k in self.graph:
					tempt = self.get_distance(i, k) + self.get_distance(k, j)
					if self.get_distance(i, j) > tempt:
						self.set_distance(i, j, tempt)

	@staticmethod
	def draw(CARP_data):
		edges = list()
		[edges.append(x[:3]) for x in CARP_data.data]
		draw_graph(edges)
		pass

	def __str__(self):
		return '{}({})'.format(self.__class__.__name__, dict(self.graph))\
		       + '\n{}({})'.format('Total', dict(self.edge_dict))
