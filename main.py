import argparse
import time
from pprint import pprint
from utils.CARPData import CARPData
from utils.Graph import Graph
from utils.Solver import Solver


def main():
	start = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('instance', type=argparse.FileType('r'),
	                    help='filename for CARP instance')
	args = parser.parse_args()
	cd = CARPData()
	cd.read_file(args.instance)
	# print(cd)
	# g = Graph(cd)
	# print(g)
	# g.floyd()
	# print("---After Floyd---")
	# print(g)
	solver = Solver(cd)
	for i in [0, 1, 3, 4, 5, 6, 7]:  # method 2 被淘汰
		print('---- method {} ----'.format(i))
		st = time.time()
		route = solver.path_scanning(i)
		en = time.time()
		ru = en - st
		route.get_cost(solver)
		print('Method {} cost: {} s'.format(i, ru))

	end = time.time()
	run = end-start
	print('Time cost: {} s'.format(run))
	# Graph.draw(cd)


if __name__ == '__main__':
	main()
