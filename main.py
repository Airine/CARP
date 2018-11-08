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
	# print(cd)
	g = Graph(cd)
	print(g)
	g.floyd()
	print("---After Floyd---")
	print(g)

	# [print(x) for x in g.get_distances(1)]
	# [print(x) for x in g.get_distances(2)]
	Graph.draw(cd)


if __name__ == '__main__':
	main()
