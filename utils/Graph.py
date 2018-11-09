from collections import defaultdict, namedtuple
from utils.GraphDrawer import draw_graph
import numpy as np
Edge = namedtuple('Edge', 'weight, demand')

Inf = np.Inf


class Graph(object):
	""" Graph data structure, undirected by default. """

	def __init__(self, CARP_data, directed=False):
		self.graph = defaultdict(set)
		self._directed = directed
		self.node_number = int(CARP_data.specification.get('VERTICES'))
		self.edge_dict = dict()
		self.distance_array = np.full((self.node_number+1, self.node_number+1), Inf)
		self.connections = list()
		self.generator(CARP_data)

	def generator(self, CARP_data):
		""" Generate a graph with a CARP_data object """

		for i in CARP_data.data:
			tempt = tuple(i[0:2])
			self.connections.append(tempt)
			self.edge_dict[tempt] = Edge(i[2], i[3])
			self.distance_array[tempt] = i[2]
			self.distance_array[tempt[1], tempt[0]] = i[2]
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

	def get_edge_attr(self, node1, node2, attr_name):
		""" Get the weight between two connected nodes """

		assert self.is_connected(node1, node2)
		tempt = (node1, node2) if node1 < node2 else (node2, node1)
		return getattr(self.edge_dict[tempt], attr_name)

	def get_distances(self, node):
		"""
		Used for debug.
		:param node:
		:return:
		"""
		distances_list = list()
		for dest in self.graph:
			distances_list.append('{} -> {}\t: {}'.format(node, dest, self.distance_array[node, dest]))
		return distances_list

	def floyd(self):
		for i in self.graph:
			self.distance_array[i, i] = 0
		for k in self.graph:
			for i in self.graph:
				for j in self.graph:
					# tempt = self.get_distance(i, k) + self.get_distance(k, j)
					self.distance_array[i, j] = min(self.distance_array[i, k] + self.distance_array[k, j], self.distance_array[i, j])

	@staticmethod
	def draw(CARP_data):
		edges = list()
		[edges.append(x[:3]) for x in CARP_data.data]
		draw_graph(edges)
		pass

	def __str__(self):
		return '{}({})'.format(self.__class__.__name__, dict(self.graph))\
		       + '\n{}({})'.format('Total', dict(self.edge_dict))\
		       + '\n' + str(self.distance_array)
