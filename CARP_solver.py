# -*- coding: utf-8 -*-
import argparse
import time
import numpy as np
import copy
from utils.CARPData import CARPData
from utils.Graph import Graph
from utils.Solver import Solver
from utils.Evolution import Evolution
import csv
from multiprocessing import Process, Pool, Manager


def add_route(route_list, solver, i, give_up_frac=10, rand=False):
	route = solver.path_scanning(i, rand=rand, give_up=give_up_frac)
	route_list.append(route)
	# queue.append(solver.path_scanning(i, give_up=give_up_frac))


def new_add(route_list, solver):
	route = solver.path_scan()
	route_list.append(route)


def solve_problem(Evo_list, solver, population_set, pop_size, time_limit, rls, cross=True):
	ps = copy.copy(population_set)
	evo = Evolution(solver, ps, pop_size, time_limit)
	if cross:
		evo.evolute(rls)
	else:
		evo.self_evolute(rls)
		# print('self')
	Evo_list.append(evo)
	# print('pop_size:', pop_size, 'rls:', rls, 'min_cost:', evo.min_cost)


def main():
	start = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('instance', type=argparse.FileType('r'),
	                    help='filename for CARP instance')
	parser.add_argument('-t', metavar='termination', type=int,
	                    help='termination time limit', required=True)
	parser.add_argument('-s', metavar='random seed',
	                    help='random seed for stochastic algorithm')
	args = parser.parse_args()
	cd = CARPData()
	cd.read_file(args.instance)
	time_limit = args.t
	seed = args.s

	# graph(cd)

	solver = Solver(cd)

	end_1 = time.time()

	random_size = 50
	# TODO: 多进程用不同的method求route返回一个route列表
	mgr = Manager()
	route_list = mgr.list()
	pool = Pool(processes=8)
	for i in range(3):
		pool.apply_async(add_route, args=(route_list, solver, i))
	for j in range(2, 14):
		for i in range(3, 7):
			pool.apply_async(add_route, args=(route_list, solver, i, j))
		for k in range(random_size):
			pool.apply_async(add_route, args=(route_list, solver, 0, j, True))
	# for i in range(random_size):
	# 	pool.apply_async(new_add, args=(route_list, solver))
	pool.close()
	pool.join()

	end_2 = time.time()

	# # TODO: Other operation
	results = list(route_list)
	# results.sort(key=lambda r: r.get_cost(solver))
	route_set = set(results)

	end_3 = time.time()

	# normal_proc = 0

	end = time.time()
	multi_proc = end_2-end_1
	graph_proc = end_1-start
	normal_proc = end_3-end_2
	run = end-start
	# print('Time cost: {} s\nGraph processing: {} s\nMultiprocessing: {} s\nList->set: {} s'.format(
	# 	run, graph_proc, multi_proc, normal_proc))

	time_remain = time_limit - run
	evo_limit = time_remain - 15
	mgr = Manager()
	evo_list = mgr.list()
	pool = Pool(processes=8)
	# for pop_size in [20, 30, 50, 100]:
	# 	pool.apply_async(solve_problem, args=(evo_list, solver, route_set, pop_size, evo_limit, 0.5))
	# 	pool.apply_async(solve_problem, args=(evo_list, solver, route_set, pop_size, evo_limit, 0.6))
	for rls in [0.4, 0.5, 0.6, 0.7]:
		pool.apply_async(solve_problem, args=(evo_list, solver, route_set, 50, evo_limit, rls))
		if rls == 0.6:
			pool.apply_async(solve_problem, args=(evo_list, solver, route_set, 30, evo_limit, rls))
		else:
			pool.apply_async(solve_problem, args=(evo_list, solver, route_set, 100, evo_limit, rls))
	pool.close()
	pool.join()

	evos = list(evo_list)
	evo = evos[0]
	results = list()
	for e in evos:
		results.append(e.best)

	min_cost = np.Inf
	result = None
	for route in results:
		cost = route.get_cost(solver)
		if cost < min_cost:
			result = route
			min_cost = cost
	# print('Results size:', len(results))
	# print('Set size:', len(route_set))
	# print('Random size:', random_size)
	# print('---------------------------------------------------------------------------------------------------------')
	# print(result)
	# print('q', min_cost)
	brothers = evo.local_search_plus(result)
	brothers.sort(key=lambda b: b.get_cost(solver))
	result = brothers[0]
	print(result)
	print('q', min_cost)
	# print('---------------------------------------------------------------------------------------------------------')
	# evo = Evolution(solver, route_set, time_limit=time_limit - 10)
	# evo.evolute(0.6)
	# result = evo.get_best()
	# print(result)
	# print('q', result.get_cost(solver))
	# print('---------------------------------------------------------------------------------------------------------')
	# result = evo.local_search(result, 0.8)
	# print(result)
	# print('q', result.get_cost(solver))
	# evo.self_evolute(0.6)
	# result = evo.get_best()
	# print(result)
	# print('q', result.get_cost(solver))
	# print('---------------------------------------------------------------------------------------------------------')
	# print('time cost:', time.time()-start)


def graph(cd):
	print(cd)
	g = Graph(cd)
	print(g)
	g.floyd()
	print("---After Floyd---")
	print(g)


def test():
	start = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('instance', type=argparse.FileType('r'),
	                    help='filename for CARP instance')
	parser.add_argument('-t', metavar='termination', type=int,
	                    help='termination time limit', required=True)
	parser.add_argument('-s', metavar='random seed',
	                    help='random seed for stochastic algorithm')
	args = parser.parse_args()
	cd = CARPData()
	cd.read_file(args.instance)
	time_limit = args.t
	seed = args.s

	# graph(cd)

	solver = Solver(cd)
	result = solver.path_scan()
	print(result)


if __name__ == '__main__':
	main()
	# test()
