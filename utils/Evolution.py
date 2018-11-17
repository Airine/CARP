import math

import numpy as np
import time
from utils.Solver import *


class Evolution(object):

	def __init__(self, solver, population_set, pop_size=1000, time_limit=50):
		self.solver = solver
		self.population = population_set
		self.population_size = pop_size
		self.time_limit = time_limit
		self.start_time = time.time()
		self.best = None

	def get_best(self):
		if self.best is not None:
			return self.best
		else:
			self.refresh_best()
			return self.best

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

	def select_parents(self):
		pop = list(self.population[self.population_size:])
		best = self.get_best()
		weights = list(map(lambda route: math.pow(best, 2)/route.get_cost(self.solver), pop))
		a, b = Evolution.weighted_choice2(weights)
		return pop[a], pop[b]

	# TODO: 写完crossover
	def crossover(self, pa, pb):
		free_tasks = list(self.solver.tasks)
		child = Route(list())
		pa_path_number = len(pa.paths)
		rand = random.randint(0, pa_path_number-1)
		pa_gene_path = pa.paths[rand]
		capa = self.solver.capacity
		task_set = set()
		for task in pa_gene_path:
			Solver.remove_task(free_tasks, task)
		child.add_path(pa_gene_path)

		for path in pb.paths:
			tasks = list()
			tempt_capa = capa
			for task in path.tasks:
				if not free_tasks:
					break
				if task not in free_tasks:
					continue
				demand = self.solver.graph.get_edge_attr(task[0], task[1], 'demand')
				if tempt_capa - demand >= 0:
					tasks.append(task)
				else:
					print('我不信')
					break
				tempt_capa -= demand
				Solver.remove_task(free_tasks, task)
			child.add_path(Path(tasks))
		print('我真不信', free_tasks)
		print('parents cost:', pa.get_cost(self.solver), ',', pb.get_cost(self.solver))
		print('child cost:', child.get_cost(self.solver))
		return child

	def local_search(self, route, rls):
		# TODO: 没看懂后面的操作
		cost = route.get_cost(self.solver)
		brothers = list()
		brothers.append(self.single_insertion(route))
		brothers.append(self.double_insertion(route))
		brothers.append(self.swap(route))
		best = max(brothers, key=lambda solution: solution.get_cost(self.solver))
		if best.get_cost(self.solver) == cost:
			return route
		elif random.random() < rls:
			return self.local_search(best, rls)
		else:
			return best

	def evolute(self, rls):
		while time.time() - self.start_time < self.time_limit:
			p_1, p_2 = self.select_parents()
			child = self.crossover(p_1, p_2)
			# if random.random < rls:
			# 	brother = self.local_search(child, rls)
			# 	if brother not in self.population:
			# 		self.population.add(brother)
			if child not in self.population:
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
		print('old cost:', route.get_cost(self.solver))
		print('new cost:', new_route.get_cost(self.solver))
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
		print('old cost:', route.get_cost(self.solver))
		print('new cost:', new_route.get_cost(self.solver))
		return new_route

	# TODO: single insertion
	def single_insertion(self, route):
		# rand = random.random() * self.solver.task_number
		task_number = self.solver.task_number
		rand = int(random.random() * task_number)
		target = None
		capacity = self.solver.capacity
		new_route = Route(list())
		cost_reduce = 0
		for path in route.paths:
			rand -= len(path)
			if rand <= 0:
				pre_cost = path.get_cost()
				target = path.tasks[rand]
				path.remove_task()
				aft_cost = path.get_cost()
				cost_reduce = pre_cost - aft_cost
				break
		assert target is not None
		flip_target = tuple([target[1], target[0]])
		demand = self.solver.graph.get_edge_attr(target[0], target[1], 'demand')
		for path in route.paths:
			new_path = path
			pre_cost = path.get_cost(self.solver)
			# aft_cost =
			if path.get_cap(self.solver) + demand < capacity:
				tasks = path.tasks
				for i in range(len(tasks)):
					pass

		# for
		pass

	# TODO: double insertion
	def double_insertion(self, route):
		pass

	# TODO: swap
	def swap(self, route):
		pass





