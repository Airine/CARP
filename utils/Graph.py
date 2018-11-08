from collections import defaultdict


class Graph(object):
	""" Graph data structure, undirected by default. """

	def __init__(self, CARP_data, directed=False):
		self.graph = defaultdict(set)
		self._directed = directed
		# self.add_connections(connections)
		self.weight_dict = dict()
		self.demand_dict = dict()
		self.generator(CARP_data)

	def generator(self, CARP_data):
		""" Generate a graph with a CARP_data object """

		connections = []
		for i in CARP_data.data:
			tempt = tuple(i[0:2])
			connections.append(tempt)
			self.weight_dict[tempt] = i[2]
			self.demand_dict[tempt] = i[3]
		self.add_connections(connections)

	def add_connections(self, connections):
		""" Add connections (list of tuple pairs) to graph """

		for node1, node2 in connections:
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
		return self.weight_dict[tempt]

	def find_path(self, node1, node2, path=[], cost=0):
		""" Find any path between node1 and node2 (may not be shortest) """

		path = path + [node1]
		# print(path)
		if node1 == node2:
			return path, cost
		if node1 not in self.graph:
			return None, cost
		for node in self.graph[node1]:
			tempt_cost = cost
			tempt_cost += self.get_weight(node, node1)
			if node not in path:
				new_path = self.find_path(node, node2, path, tempt_cost)
				if new_path[0] is not None:
					# print(new_path)
					return new_path, cost
		return None, cost
	#
	# def find_path(self, node1, node2, path=[]):
	# 	""" Find any path between node1 and node2 (may not be shortest) """
	#
	# 	path = path + [node1]
	# 	if node1 == node2:
	# 		return path
	# 	if node1 not in self.graph:
	# 		return None
	# 	for node in self.graph[node1]:
	# 		if node not in path:
	# 			new_path = self.find_path(node, node2, path)
	# 			if new_path:
	# 				return new_path
	# 	return None

	def find_all_path(self, node1, node2, path=list()):
		""" Find all the paths between node1 and node2 """

		path_list = list()
		cost_list = list()
		path = path + [node1]
		if node1 == node2:
			return path
		if node1 not in self.graph:
			return None
		for node in self.graph[node1]:
			if node not in path:
				new_path = self.find_path(node, node2, path)
				if new_path:
					path_list.append(new_path)
		return path_list

	def __str__(self):
		return '{}({})'.format(self.__class__.__name__, dict(self.graph))\
		       + '\n{}({})'.format('Weight', dict(self.weight_dict)) \
		       + '\n{}({})'.format('Demand', dict(self.demand_dict))
