# -*- coding: utf-8 -*-
# from queue import PriorityQueue
import numpy as np
from utils.Graph import Graph
import random


class Solver(object):

	def __init__(self, CARP_data):
		self.graph = Graph(CARP_data)
		self.graph.floyd()
		self.tasks = self.get_tasks()
		self.depot = int(CARP_data.specification.get('DEPOT'))
		self.capacity = int(CARP_data.specification.get('CAPACITY'))
		self.task_number = int(CARP_data.specification.get('REQUIRED EDGES'))
		# print(len(self.tasks))
		# print(self.task_number)
		# assert len(self.tasks) == self.task_number

	# TODO: 这也是要重写的内容
	def evaluate_task(self, current_pos, task, method=0, current_capacity=0):
		"""
		第一次尝试每次使用evaluate_task对所有free_tasks排序，
		此函数只起到评估排序功能
		:param current_capacity:
		:param current_pos: 现在的位置
		:param task: 需要评估的task
		:param method: 使用的评估方法 { 0:cost,}
		:return: 评估结果
		"""
		start = task[0]
		end = task[1]
		cost = self.graph.distance_array[current_pos, start] \
		        + self.graph.get_edge_attr(start, end, 'weight')
		if method == 0:
			return cost
		demand = self.graph.get_edge_attr(start, end, 'demand')
		distance_depot = self.graph.distance_array[self.depot, end]

		cost_depot = self.graph.distance_array[self.depot, start] \
			+ self.graph.get_edge_attr(start, end, 'weight')

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

	def distance2task(self, current_post, task):
		return self.graph.distance_array[task[0], current_post]

	def get_tasks(self):
		edges = self.graph.connections
		tasks = list(filter(lambda x: self.graph.get_edge_attr(x[0], x[1], 'demand') > 0, edges))
		revert_tasks = list(map(lambda x: (x[1], x[0]), tasks))
		return tasks + revert_tasks

	# def get_nearest_tasks(self, current_pos, tasks):
	# 	tasks.sort(key=lambda t: self.distance2task(current_pos, t))
	# 	min_dis = self.distance2task(current_pos, tasks[0])
	#
	# 	nearest = list()
	# 	for task in tasks:

	def get_better_one(self, best_task, task, current_cap):
		cd_best = self.graph.get_edge_attr(best_task[0], best_task[1], 'weight') / self.graph.get_edge_attr(
			best_task[0], best_task[1], 'demand')
		cd_task = self.graph.get_edge_attr(task[0], task[1], 'weight') / self.graph.get_edge_attr(
			task[0], task[1], 'demand')
		re_best = self.graph.distance_array[best_task[1], self.depot]
		re_task = self.graph.distance_array[task[1], self.depot]
		# rule = random.randint(0, 4)
		rule = random.choice([0, 1, 2, 3, 4])
		if rule == 0:  # maximum cost/demand
			if cd_best > cd_task:
				return best_task
			elif cd_best < cd_task:
				return task
			else:
				return random.choice([best_task, task])
		if rule == 1:  # minimum cost/demand
			if cd_best < cd_task:
				return best_task
			elif cd_best > cd_task:
				return task
			else:
				return random.choice([best_task, task])
		if rule == 2:  # maximum return cost
			if re_best > re_task:
				return best_task
			elif re_best < re_task:
				return task
			else:
				return random.choice([best_task, task])
		if rule == 3:  # minimum return cost
			if re_best < re_task:
				return best_task
			elif re_best > re_task:
				return task
			else:
				return random.choice([best_task, task])
		if rule == 4:  # determine by the capacity
			if current_cap < self.capacity / 2:
				if re_best > re_task:
					return best_task
				elif re_best < re_task:
					return task
				else:
					return random.choice([best_task, task])
			else:
				if re_best < re_task:
					return best_task
				elif re_best > re_task:
					return task
				else:
					return random.choice([best_task, task])
		pass

	def path_scan(self):
		depot = self.depot
		free_tasks = list(self.tasks)
		capacity = self.capacity
		distance = self.graph.distance_array
		route = Route(list())
		cost = 0
		while len(free_tasks) > 0:
			tasks = list()
			current_pos = depot
			current_cap = capacity
			best_task = None
			while True:
				if not free_tasks:
					break
				dis_min = np.Inf
				for task in free_tasks:
					if self.graph.get_edge_attr(task[0], task[1], 'demand') > current_cap:
						dis_min = np.Inf
						break
					if best_task is None:
						best_task = task
						dis_min = distance[current_pos, best_task[0]]
					dis_tempt = distance[current_pos, task[0]]
					if dis_tempt < dis_min:
						dis_min = dis_tempt
						best_task = task
					elif dis_tempt == dis_tempt:
						dis_min = dis_tempt
						best_task = self.get_better_one(best_task, task, current_cap)
				if dis_min == np.Inf:
					break

				if distance[current_pos, best_task[0]] >= distance[current_pos, depot] + distance[best_task[0], depot] \
							and current_pos != depot:
					break

				give_up = random.randint(10, 14)
				if current_cap < capacity/give_up:
					break
				tasks.append(best_task)
				Solver.remove_task(free_tasks, best_task)
				cost += self.graph.get_edge_attr(best_task[0], best_task[1], 'weight') + dis_min
				current_cap += self.graph.get_edge_attr(best_task[0], best_task[1], 'demand')
				current_pos = best_task[1]
			cost += self.graph.distance_array[current_pos, depot]
			route.add_path(Path(tasks))
		# print(cost, route.get_cost(self))
		return route

	# TODO: 重写path_scanning 要能够在path-scanning的同时计算出route的 cost
	def path_scanning(self, method=0, rand=False, give_up=8, reload=True):
		# global free_tasks
		depot = self.depot
		free_tasks = list(self.tasks)
		capacity = self.capacity
		route = Route(list())
		while len(free_tasks) > 0:
			new_path = Path(list())
			current_pos = depot  # 每次从基地出发（结束后回到基地）
			current_cap = capacity  # 回到基地重新装满
			# distance = self.graph.distance_array[current_pos, depot]
			distance = self.graph.distance_array
			m = method
			if rand:
				m = random.randint(0, 7)
				# give_up = random.randint(2, 14)
			while current_cap > 0:
				if current_cap < capacity/give_up and method == 3:
					m = 1
				if current_cap < capacity/give_up and method == 4:
					m = 1
				if current_cap < capacity/give_up and method >= 5:
					break
				available_tasks = list(filter(lambda t: self.graph.get_edge_attr(t[0], t[1], 'demand') < current_cap, free_tasks))
				# 过滤出能装下的task
				if len(available_tasks) == 0:  # 如果装不下了就停止
					break
				available_tasks.sort(key=lambda t: self.evaluate_task(current_pos, t, m))
				# 根据评估函数对task排序
				task = available_tasks[0]

				# 取估值最小的task
				demand = self.graph.get_edge_attr(task[0], task[1], 'demand')

				# 如果经过原点就立马重新出发,证实有用！
				if distance[current_pos, task[0]] >= distance[current_pos, depot] + distance[task[0], depot]\
							and current_pos != depot\
							and reload:
					break

				new_path.add_task(task)
				# free_tasks = Solver.remove_task(free_tasks, task)
				Solver.remove_task(free_tasks, task)
				current_pos = task[1]
				current_cap -= demand
			route.add_path(new_path)
		# [print(path.get_cost(self)) for path in route.paths]
		# print('Number of paths: ', len(route.paths))
		return route

	@staticmethod
	def remove_task(tasks, task):
		rev_task = (task[1], task[0])
		tasks.remove(task)
		tasks.remove(rev_task)
		# print('Tasks: {}\n Task:{}\nAfter remove:'.format(tasks, task))
		# print(list(filter(lambda x: x not in (task, rev_task), tasks)))
		# return list(filter(lambda x: x not in (task, rev_task), tasks))


class Route(object):

	def __init__(self, paths=list()):
		self.paths = paths
		self.cost = None

	def add_path(self, path):
		self.paths.append(path)

	def get_cost(self, solver):
		if self.cost is not None:  # 如果曾经计算过cost，就不不要再次计算
			return self.cost
		cost = 0
		for path in self.paths:
			cost += path.get_cost(solver)
		self.cost = cost
		return cost

	def __eq__(self, other):
		if not isinstance(other, Route):
			return False
		return set(self.paths) == set(other.paths)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(frozenset(self.paths))

	def __str__(self):
		route = 's '
		for path in self.paths:
			route += str(path) + ','
		return route[:-1]


class Path(object):

	def __init__(self, tasks=list()):
		self.tasks = tasks
		self.cap = None
		self.cost = None
		self.str = None

	def add_task(self, task):
		self.tasks.append(task)

	def remove_task(self, task):
		self.tasks.remove(task)
		self.cap = None
		self.cost = None

	def get_cap(self, solver):
		if self.cap is not None:
			return self.cap
		return sum([solver.graph.get_edge_attr(task[0], task[1], 'demand') for task in self.tasks])

	def get_cost(self, solver):
		if self.cost is not None:
			return self.cost
		current_pos = solver.depot
		cost = 0
		for task in self.tasks:
			current_cost = solver.evaluate_task(current_pos, task)
			cost += current_cost
			current_pos = task[1]
		return_cost = solver.graph.distance_array[current_pos, solver.depot]
		cost += return_cost
		self.cost = cost
		return cost

	def __eq__(self, other):
		if not isinstance(other, Path):
			return False
		return self.__str__() == other.__str__()

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.__str__())

	def __str__(self):
		if self.str is not None:
			return self.str
		path = '0,'
		for task in self.tasks:
			path += '({},{}),'.format(task[0], task[1])
		path += '0'
		self.str = path
		return path
