# from queue import PriorityQueue
from utils.Graph import Graph


class Solver(object):

	def __init__(self, CARP_data):
		self.graph = Graph(CARP_data)
		self.graph.floyd()
		self.tasks = self.get_tasks()
		self.depot = int(CARP_data.specification.get('DEPOT'))
		print('Depot:', self.depot)
		self.capacity = int(CARP_data.specification.get('CAPACITY'))

	def evaluate_task(self, current_pos, task, method=0):
		"""
		第一次尝试每次使用evaluate_task对所有free_tasks排序，
		此函数只起到评估排序功能
		:param current_pos: 现在的位置
		:param task: 需要评估的task
		:param method: 使用的评估方法 { 0:cost,}
		:return: 评估结果
		"""
		start = task[0]
		end = task[1]
		demand = self.graph.get_edge_attr(start, end, 'demand')
		cost = self.graph.distance_array[current_pos, start] \
			+ self.graph.get_edge_attr(start, end, 'weight')
		if method == 0:
			return cost
		if method == 1:
			return demand/cost
		if method == 2:
			return cost/demand
		return 0

	@staticmethod
	def if_continue(c):
		pass

	def get_tasks(self):
		edges = self.graph.connections
		tasks = list(filter(lambda x: self.graph.get_edge_attr(x[0], x[1], 'demand') > 0, edges))
		revert_tasks = list(map(lambda x: (x[1], x[0]), tasks))
		print(tasks + revert_tasks)
		return tasks + revert_tasks

	def path_scanning(self):
		global free_tasks
		depot = self.depot
		free_tasks = self.tasks
		capacity = self.capacity
		route = Route()
		while len(free_tasks) > 0:
			new_path = Path(list())
			current_pos = depot  # 每次从基地出发（结束后回到基地）
			current_cap = capacity  # 回到基地重新装满
			distance = self.graph.distance_array[current_pos, depot]
			while current_cap > 0:
				available_tasks = list(filter(lambda t: self.graph.get_edge_attr(t[0], t[1], 'demand') < current_cap, free_tasks))
				if len(available_tasks) == 0:
					break
				available_tasks.sort(key=lambda t: self.evaluate_task(current_pos, t))
				task = available_tasks[0]
				demand = self.graph.get_edge_attr(task[0], task[1], 'demand')
				new_path.add_task(task)
				free_tasks = Solver.remove_task(free_tasks, task)
				current_pos = task[1]
				current_cap -= demand
			route.add_path(new_path)
		print(route)
		# [print(path) for path in route.paths]
		return route

	@staticmethod
	def remove_task(tasks, task):
		rev_task = (task[1], task[0])
		# print('Tasks: {}\n Task:{}\nAfter remove:'.format(tasks, task))
		# print(list(filter(lambda x: x not in (task, rev_task), tasks)))
		return list(filter(lambda x: x not in (task, rev_task), tasks))


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

	def get_cost(self, solver):
		current_pos = solver.depot
		cost = 0
		for task in self.tasks:
			current_cost = solver.evaluate_task(current_pos, task)
			print('{}->{}-{}:{}'.format(current_pos, task[0], task[1], current_cost))
			cost += current_cost
		print('Total:', cost)
		return cost

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
