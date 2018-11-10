# -*- coding: utf-8 -*-
# from queue import PriorityQueue
from utils.Graph import Graph


class Solver(object):

	def __init__(self, CARP_data):
		self.graph = Graph(CARP_data)
		self.graph.floyd()
		self.tasks = self.get_tasks()
		self.depot = int(CARP_data.specification.get('DEPOT'))
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
		distance_depot = self.graph.distance_array[self.depot, end]
		cost = self.graph.distance_array[current_pos, start] \
			+ self.graph.get_edge_attr(start, end, 'weight')
		if method == 0:
			return cost
		if method == 1:
			return cost+distance_depot
		if method == 2:
			return cost/demand
		if method == 3:  # special method 0
			return cost
		if method == 4:  # special method 3
			return cost/demand
		if method == 5:  # special method 0
			return cost
		if method == 6:  # special method 3
			return cost/demand
		return 0

	@staticmethod
	def if_continue(c):
		pass

	def get_tasks(self):
		edges = self.graph.connections
		tasks = list(filter(lambda x: self.graph.get_edge_attr(x[0], x[1], 'demand') > 0, edges))
		revert_tasks = list(map(lambda x: (x[1], x[0]), tasks))
		return tasks + revert_tasks

	def path_scanning(self, method=0, random=False, give_up=8, reload=True):
		global free_tasks
		depot = self.depot
		free_tasks = self.tasks
		capacity = self.capacity
		route = Route(list())
		while len(free_tasks) > 0:
			new_path = Path(list())
			current_pos = depot  # 每次从基地出发（结束后回到基地）
			current_cap = capacity  # 回到基地重新装满
			# distance = self.graph.distance_array[current_pos, depot]
			distance = self.graph.distance_array
			m = method
			while current_cap > 0:
				available_tasks = list(filter(lambda t: self.graph.get_edge_attr(t[0], t[1], 'demand') < current_cap, free_tasks))
				# 过滤出能装下的task
				if len(available_tasks) == 0:  # 如果装不下了就停止
					break
				if current_cap < capacity/give_up and method == 3:
					m = 1
				if current_cap < capacity/give_up and method == 4:
					m = 1
				if current_cap < capacity/give_up and method == 5:
					break
				if current_cap < capacity/give_up and method == 6:
					break
				available_tasks.sort(key=lambda t: self.evaluate_task(current_pos, t, m))
				# 根据评估函数对task排序
				task = available_tasks[0]
				# 取估值最小的task
				demand = self.graph.get_edge_attr(task[0], task[1], 'demand')

				# 如果经过原点就立马重新出发,证实有用！
				if distance[current_pos, task[0]] == distance[current_pos, depot] + distance[task[0], depot]\
							and current_pos != depot\
							and reload:
					break

				new_path.add_task(task)
				free_tasks = Solver.remove_task(free_tasks, task)
				current_pos = task[1]
				current_cap -= demand
			route.add_path(new_path)
		# [print(path.get_cost(self)) for path in route.paths]
		# print('Number of paths: ', len(route.paths))
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

	def get_cost(self, solver):
		cost = 0
		for path in self.paths:
			cost += path.get_cost(solver)
		# print('Route cost:', cost)
		return cost

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
			# print('{}->{}-{}:{}'.format(current_pos, task[0], task[1], current_cost))
			cost += current_cost
			current_pos = task[1]
		return_cost = solver.graph.distance_array[current_pos, solver.depot]
		cost += return_cost
		# print('Return cost:', return_cost)
		# print('Total:', cost)
		return cost

	def __str__(self):
		path = '0,'
		for task in self.tasks:
			path += '({},{}),'.format(task[0], task[1])
		path += '0'
		return path


if __name__ == '__main__':
	# p = Path([(1, 2), (2, 4), (5, 6)])
	# r = Route([p, p, p])
	rout = [[(1, 5), (5, 2), (2, 4), (4, 7), (7, 5), (5, 6)], [(1, 11), (11, 6), (6, 4), (4, 3), (3, 8)], [(1, 9), (9, 8), (8, 12), (12, 10), (10, 9), (9, 3), (3, 2)], [(1, 4), (4, 11), (11, 12), (10, 1), (1, 2), (2, 7), (1, 8)]]
	r = Route()
	print(r)
