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
	solver.path_scanning()

	end = time.time()
	run = end-start
	print('Time cost: {} s'.format(run))
	# Graph.draw(cd)


if __name__ == '__main__':
	main()
