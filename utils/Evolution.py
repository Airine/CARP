import math

import numpy as np
import time
import copy
from utils.Solver import *


class Evolution(object):

	def __init__(self, solver, population_set, pop_size=30, time_limit=10):
		self.solver = solver
		self.population = population_set
		self.population_size = pop_size
		self.time_limit = time_limit
		self.start_time = time.time()
		self.best = None
		self.min_cost = None

	def get_best(self):
		if self.best is not None:
			return self.best
		else:
			self.refresh_best()
			return self.best

	def get_min_cost(self):
		if self.min_cost is not None:
			return self.min_cost
		else:
			self.refresh_best()
			return self.min_cost

	def refresh_best(self):
		solutions = list(self.population)
		min_cost = np.Inf
		best_solution = None
		for route in solutions:
			cost = route.get_cost(self.solver)
			if cost < min_cost:
				min_cost = cost
				best_solution = route
		self.best = best_solution
		self.min_cost = min_cost

	def select_parents(self):
		pop = list(self.population)
		pop.sort(key=lambda route: route.get_cost(self.solver))
		pop = pop[:self.population_size]
		min_cost = self.get_min_cost()
		weights = list(map(lambda route: math.pow(2*min_cost, 2)/route.get_cost(self.solver), pop))
		a, b = Evolution.weighted_choice2(weights)
		return pop[a], pop[b]

	# TODO: 写完crossover
	def crossover(self, pa, pb):
		free_tasks = list(self.solver.tasks)
		child = list()
		pa_paths = copy.deepcopy(pa.paths)
		pb_paths = copy.deepcopy(pb.paths)
		capa = self.solver.capacity

		pa_path_number = len(pa_paths)
		rand = random.randint(0, pa_path_number-1)
		pa_gene_path = pa_paths[rand]
		# print(pa_gene_path)
		[Solver.remove_task(free_tasks, task) for task in pa_gene_path.tasks]
		child.append(pa_gene_path.tasks)
		child.append([])

		tempt_cap = capa

		for path in pb_paths:
			for task in path.tasks:
				if len(free_tasks) == 0:
					break
				if task not in free_tasks:
					continue
				demand = self.solver.graph.get_edge_attr(task[0], task[1], 'demand')
				if tempt_cap - demand >= 0:
					child[-1].append(task)
				else:
					child.append([])
					child[-1].append(task)
					tempt_cap = capa
				Solver.remove_task(free_tasks, task)
				tempt_cap -= demand
		route = Route(list())
		# print(child)
		# exit(0)
		for tasks in child:
			route.add_path(Path(tasks))
		return route

	def self_evolute(self, rls):
		while time.time() - self.start_time < self.time_limit:
			p_1, p_2 = self.select_parents()
			# child_a = self.local_search(p_1, rls)
			# child_b = self.local_search(p_2, rls)
			# child = child_a if child_a.get_cost(self.solver) < child_b.get_cost(self.solver) else child_b
			# if child.get_cost(self.solver) > min(p_1.get_cost(self.solver), p_2.get_cost(self.solver)):
			# 	continue
			if random.random() < rls:
				brothers = self.local_search_plus(p_1)
				for brother in brothers:
					if brother not in self.population:
						self.population.add(brother)
			else:
				brothers = self.local_search_plus(p_2)
				for brother in brothers:
					if brother not in self.population:
						self.population.add(brother)
			# if  not in self.population:
			# 	print('self evolution')
			# 	self.population.add(child)
			self.refresh_best()

	def local_search_plus(self, route):
		# TODO: 没看懂后面的操作
		# print('local searching')
		# cost = route.get_cost(self.solver)
		brothers = list()
		brothers.append(self.single_insertion(route))
		brothers.append(self.flip_rand(route))
		brothers.append(self.flip_rand(brothers[0]))
		brothers.append(self.flip_all(route))
		return brothers

	def local_search(self, route, rls):
		# TODO: 没看懂后面的操作
		# print('local searching')
		cost = route.get_cost(self.solver)
		brother = route
		operator = random.choice([1, 1, 2, 2, 3])
		if operator == 1:
			brother = self.single_insertion(route)
		if operator == 2:
			brother = self.flip_rand(route)
		if operator == 3:
			brother = self.flip_all(route)

		# best = max(brothers, key=lambda solution: solution.get_cost(self.solver))
		if brother.get_cost(self.solver) == cost:
			# print('收敛了')
			return route
		elif random.random() < rls:
			return self.local_search(brother, rls)
		else:
			return brother

	def evolute(self, rls):
		while time.time() - self.start_time < self.time_limit:
			p_1, p_2 = self.select_parents()
			childa = self.crossover(p_1, p_2)
			childb = self.crossover(p_2, p_1)
			child = childa if childa.get_cost(self.solver) < childb.get_cost(self.solver) else childb
			if child.get_cost(self.solver) > min(p_1.get_cost(self.solver), p_2.get_cost(self.solver)):
				continue
			if random.random() < rls:
				brother = self.local_search(child, rls)
				if brother not in self.population:
					self.population.add(brother)
			elif child not in self.population:
				self.population.add(child)
			self.refresh_best()

	@staticmethod
	def weighted_choice(weights):
		rnd = random.random() * sum(weights)
		for i, w in enumerate(weights):
			rnd -= w
			if rnd < 0:
				return i

	@staticmethod
	def weighted_choice2(weights):
		"""
		This static method return two different random indexes according to the weights.
		:param weights: weight list
		:return: 2 different indexes
		"""
		rnd1 = random.random() * sum(weights)
		rnd2 = random.random() * sum(weights)
		a = 0
		b = 0
		flag_1 = True
		flag_2 = True
		for i, w in enumerate(weights):
			if not flag_1 and not flag_2:
				break
			rnd1 -= w
			rnd2 -= w
			if rnd1 < 0 and flag_1:
				a = i
				flag_1 = False
				continue
			if rnd2 < 0 and flag_2:
				b = i
				flag_2 = False
				continue
		return a, b

	def flip_rand(self, route):
		new_route = Route(list())
		task_number = self.solver.task_number
		rand = int(random.random() * task_number)
		flag = True
		# print(rand)
		for path in route.paths:
			current_pos = self.solver.depot
			depot = self.solver.depot
			tasks = path.tasks
			rand -= len(path.tasks)
			# print(rand)
			if rand <= 0 and flag:
				for i in range(len(tasks)):
					task = tasks[i]
					flip_task = tuple([task[1], task[0]])
					if i < len(tasks) - 1:
						tempt_cost = self.solver.evaluate_task(current_pos, task) + self.solver.evaluate_task(task[-1],
						                                                                                      tasks[i + 1])
						flip_cost = self.solver.evaluate_task(current_pos, flip_task) + self.solver.evaluate_task(
							flip_task[-1], tasks[i + 1])
					else:
						tempt_cost = self.solver.evaluate_task(current_pos, task) + self.solver.graph.distance_array[
							task[-1], depot]
						flip_cost = self.solver.evaluate_task(current_pos, flip_task) + self.solver.graph.distance_array[
							task[-1], depot]
					if flip_cost < tempt_cost:
						tasks[i] = flip_task
						# task = flip_task
						flag = False
						break
					current_pos = task[-1]
			new_route.add_path(Path(tasks))
		# print('old cost:', route.get_cost(self.solver))
		# print('new cost:', new_route.get_cost(self.solver))
		return new_route

	def flip_all(self, route):
		new_route = Route(list())
		for path in route.paths:
			current_pos = self.solver.depot
			depot = self.solver.depot
			tasks = path.tasks
			for i in range(len(tasks)):
				task = tasks[i]
				flip_task = tuple([task[1], task[0]])
				if i < len(tasks)-1:
					tempt_cost = self.solver.evaluate_task(current_pos, task) + self.solver.evaluate_task(task[-1],
					                                                                                      tasks[i + 1])
					flip_cost = self.solver.evaluate_task(current_pos, flip_task) + self.solver.evaluate_task(
						flip_task[-1], tasks[i + 1])
				else:
					tempt_cost = self.solver.evaluate_task(current_pos, task) + self.solver.graph.distance_array[
						task[-1], depot]
					flip_cost = self.solver.evaluate_task(current_pos, flip_task) + self.solver.graph.distance_array[
						task[-1], depot]
				if flip_cost < tempt_cost:
					tasks[i] = flip_task
					task = flip_task
				current_pos = task[-1]
			new_route.add_path(Path(tasks))
		# print('old cost:', route.get_cost(self.solver))
		# print('new cost:', new_route.get_cost(self.solver))
		return new_route

	# TODO: single insertion
	def single_insertion(self, route_origin):
		route = copy.deepcopy(route_origin)
		task_number = self.solver.task_number
		rand = int(random.random() * (task_number-1))
		target = None
		capacity = self.solver.capacity
		depot = self.solver.depot
		new_route = Route(list())
		cost_reduce = 0
		for path in route.paths:
			rand -= len(path.tasks)
			# print(len(path.tasks))
			# print(rand)
			if rand < 0:
				pre_cost = path.get_cost(self.solver)
				target = path.tasks[rand]
				path.remove_task(target)
				aft_cost = path.get_cost(self.solver)
				cost_reduce = pre_cost - aft_cost
				break

		assert target is not None
		flip_target = tuple([target[1], target[0]])
		demand = self.solver.graph.get_edge_attr(target[0], target[1], 'demand')
		weight = self.solver.graph.get_edge_attr(target[0], target[1], 'weight')

		flag = True  # 只插一次并用来判断是否有插入操作
		for path in route.paths:
			new_path = copy.deepcopy(path)
			current_pos = depot
			if path.get_cap(self.solver) + demand < capacity and flag:
				tasks = path.tasks
				for i in range(len(tasks)):
					task = tasks[i]
					orig_cost = self.solver.graph.distance_array[current_pos, task[0]]
					aft_cost_t = self.solver.graph.distance_array[current_pos, target[0]] + weight +\
						self.solver.graph.distance_array[target[1], task[0]]
					aft_cost_f = self.solver.graph.distance_array[current_pos, target[1]] + weight +\
						self.solver.graph.distance_array[target[0], task[0]]
					aft_cost = min(aft_cost_t, aft_cost_f)
					if aft_cost - orig_cost >= cost_reduce:
						continue
					else:
						if aft_cost_t < aft_cost_f:
							tasks.insert(i, target)
						else:
							tasks.insert(i, flip_target)
						# print('insertion success')
						flag = False
						break
				new_path = Path(tasks)
			new_route.add_path(new_path)
		if not flag:
			return new_route
		else:
			return route_origin

	# TODO: double insertion
	def double_insertion(self, route):
		pass

	# TODO: swap
	def swap(self, route):
		pass





