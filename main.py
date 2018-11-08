import argparse
from pprint import pprint
from utils.CARPData import CARPData
from utils.Graph import Graph


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('instance', type=argparse.FileType('r'),
	                    help='filename for CARP instance')
	args = parser.parse_args()
	cd = CARPData()
	cd.read_file(args.instance)
	print(cd)
	g = Graph(cd)
	print(g)
	# print(g.find_path(1, 9))
	print(g.find_all_path(1, 9))
	# print(cd)
	# connections = [('A', 'B'), ('B', 'C'), ('B', 'D'),
	#                ('C', 'D'), ('E', 'F'), ('F', 'C')]
	# g = Graph(connections)
	# pprint(g.graph)
	# g.generator(cd)


if __name__ == '__main__':
	main()
