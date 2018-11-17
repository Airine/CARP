# -*- coding: utf-8 -*-
import argparse
import time
import numpy as np
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

	# log(solver, cd, 14, 7)
	#
	# pre_end = time.time()
	# print('Time:', pre_end-start)
	# return

	end_1 = time.time()

	random_size = 50
	# TODO: 多进程用不同的method求route返回一个route列表
	mgr = Manager()
	route_list = mgr.list()
	pool = Pool(processes=13)
	for i in range(3):
		pool.apply_async(add_route, args=(route_list, solver, i))
	for j in range(2, 14):
		for i in range(3, 7):
			pool.apply_async(add_route, args=(route_list, solver, i, j))
		for k in range(random_size):
			pool.apply_async(add_route, args=(route_list, solver, 0, j, True))
	pool.close()
	pool.join()

	end_2 = time.time()

	# # TODO: Other operation
	route_set = set(route_list)

	end_3 = time.time()

	# normal_proc = 0

	end = time.time()
	multi_proc = end_2-end_1
	graph_proc = end_1-start
	normal_proc = end_3-end_2
	run = end-start
	print('Time cost: {} s\nGraph processing: {} s\nMultiprocessing: {} s\nList->set: {} s'.format(run, graph_proc, multi_proc, normal_proc))
	results = list(route_list)
	min_cost = np.Inf
	result = None
	for route in results:
		cost = route.get_cost(solver)
		if cost < min_cost:
			result = route
			min_cost = cost
	print('Results size:', len(results))
	print('Set size:', len(route_set))
	print('Random size:', random_size)
	print('---------------------------------------------------------------------------------------------------------')
	print(result)
	print('q', min_cost)
	print('---------------------------------------------------------------------------------------------------------')
	evo = Evolution(solver, route_set)
	times = 0
	new = result
	while True:
		# time.sleep(3)
		# new = evo.flip_rand(new)
		new = evo.flip_all(new)
		if new in route_set:
			break
		route_set.add(new)
		times += 1
	print(times)
	# print(len(route_list))
	# for route in route_list:
	# 	print('{} costs {}'.format(route, route.get_cost(solver)))

	# time_1 = time.time()
	# # flag = result in results
	# results.append(result)
	# time_2 = time.time()
	# print('list:', time_2 - time_1)
	# # flag2 = result in route_set
	# route_set.add(result)
	# time_3 = time.time()
	# print('set:', time_3-time_2)
	# tempt = list(route_set)
	# time_4 = time.time()
	# print('set->list:', time_4-time_3)


def graph(cd):
	print(cd)
	g = Graph(cd)
	print(g)
	g.floyd()
	print("---After Floyd---")
	print(g)


def log(solver, cd, end_fraction=10, methods=11):
	"""
	Generate csv files to compare the quality with different methods
	:param methods:
	:param solver: CARP_solver
	:param cd: CARP_data
	:param end_fraction: the end fraction
	:return: None
	"""
	log_content = list()
	min_cost = np.Inf
	min_route = None
	for frac in range(2, end_fraction):
		log_line = list()
		log_line.append('1/{}'.format(frac))
		for i in range(methods):  # method 2 被淘汰
			route = solver.path_scanning(i, give_up=frac)
			cost = route.get_cost(solver)
			if cost < min_cost:
				min_cost = cost
				min_route = route
			log_line.append(cost)
		for j in range(10):
			route = solver.path_scanning(rand=True, give_up=frac)
			cost = route.get_cost(solver)
			if cost < min_cost:
				min_cost = cost
				min_route = route
			log_line.append(cost)
		log_content.append(log_line)
	filename = 'csv/' + cd.specification.get('NAME') + '.csv'
	with open(filename, 'w') as f:
		writer = csv.writer(f)
		header = ['give_up_fraction', 'cost', 'cost+dis_depot', 'cost/demand', 'cost and dis_depot',
		          'cost/demand and dis_depot', 'cost and give_up', 'cost/demand and give_up', 'random']
		writer.writerow(header)
		writer.writerows(log_content)
	print(min_route)
	print('q', min_cost)


if __name__ == '__main__':
	main()
