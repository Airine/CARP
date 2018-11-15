# -*- coding: utf-8 -*-
import argparse
import time
from utils.CARPData import CARPData
from utils.Graph import Graph
from utils.Solver import Solver
import csv
from multiprocessing import Process, Pool, Manager


def add_route(route_list, solver, i, give_up_frac=10):
	route_list.append(solver.path_scanning(i, give_up=give_up_frac))
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

	log(solver, cd, 14, 7)

	return

	end_1 = time.time()

	# TODO: 多进程用不同的method求route返回一个route列表
	mgr = Manager()
	route_list = mgr.list()
	pool = Pool(processes=13)
	for i in range(3):
		pool.apply_async(add_route, args=(route_list, solver, i))
	for i in range(3, 7):
		for j in range(2, 14):
			pool.apply_async(add_route, args=(route_list, solver, i, j))
	pool.close()
	pool.join()

	end_2 = time.time()

	# # TODO: 不用多进程
	# tempt = list()
	# for i in range(3):
	# 	add_route(tempt, solver, i)
	# for i in range(3, 7):
	# 	for j in range(2, 14):
	# 		add_route(tempt, solver, i, j)
	# end_3 = time.time()

	normal_proc = 0

	end = time.time()
	multi_proc = end_2-end_1
	graph_proc = end_1-start
	# normal_proc = end_3-end_2
	run = end-start
	print('Time cost: {} s\nGraph processing: {} s\nMultiprocessing: {} s\nNormal processing: {} s'.format(run, graph_proc, multi_proc, normal_proc))
	# print(len(route_list))
	# for route in route_list:
	# 	print('{} costs {}'.format(route, route.get_cost(solver)))


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
	for frac in range(2, end_fraction):
		log_line = list()
		log_line.append('1/{}'.format(frac))
		for i in range(methods):  # method 2 被淘汰
			# print('---- method {} ----'.format(i))
			st = time.time()
			route = solver.path_scanning(i, give_up=frac)
			en = time.time()
			ru = en - st
			cost = route.get_cost(solver)
			log_line.append(cost)
			# print('Method {} cost: {} s'.format(i, ru))
		cost = solver.path_scanning(rand=True, give_up=frac).get_cost(solver)
		log_line.append(cost)
		log_content.append(log_line)
	# print(log_content)
	filename = 'csv/' + cd.specification.get('NAME') + '.csv'
	# with open(filename, 'w', newline='') as f:
	with open(filename, 'w') as f:
		writer = csv.writer(f)
		header = ['give_up_fraction', 'cost', 'cost+dis_depot', 'cost/demand', 'cost and dis_depot',
		          'cost/demand and dis_depot', 'cost and give_up', 'cost/demand and give_up', 'random']
		writer.writerow(header)
		writer.writerows(log_content)


if __name__ == '__main__':
	main()
