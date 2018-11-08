# from queue import PriorityQueue
from utils.Graph import Graph


class Solver(object):

	def __init__(self, CARP_data):
		self.graph = Graph(CARP_data)
		self.graph.floyd()
		# self.tasks =
		# self.free_
		self.depot = 1
		self.capacity = 0

	@staticmethod
	def get_tasks(connections):
		pass
	

class Route(object):

	def __init__(self, paths=list()):
		self.paths = paths

	def add_path(self, path):
		self.paths.append(path)

	def __str__(self):
		route = 's '
		for path in self.paths:
			route += str(path) + ','
		return route[:-1]


class Path(object):

	def __init__(self, tasks=list()):
		self.tasks = tasks

	def add_task(self, task):
		self.tasks.append(task)

	def __str__(self):
		path = '0,'
		for task in self.tasks:
			path += '({},{}),'.format(task[0], task[1])
		path += '0'
		return path


if __name__ == '__main__':
	p = Path([(1, 2), (2, 4), (5, 6)])
	r = Route([p, p, p])
	print(r)
