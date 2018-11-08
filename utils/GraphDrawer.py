import time
import threading
import networkx as nx
import matplotlib.pyplot as plt


def draw_graph(e):
	one_thr = threading.Thread(target=_draw_graph(e), args=['test'])
	one_thr.start()
	return one_thr


def _draw_graph(e):
	g = nx.Graph()
	g.add_weighted_edges_from(e)
	pos = nx.spring_layout(g)
	nx.draw(g, pos, node_size=15, with_labels=True)
	edge_labels = nx.get_edge_attributes(g, 'weight')
	nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=6)
	# nx.draw_networkx_labels(g, pos)
	plt.show()


if __name__ == '__main__':
	edges = []
	with open('CARP_samples/gdb1.dat', 'r') as file:
		for i in range(9):
			file.readline()
		line = file.readline()
		while line != 'END':
			edges.append(list(map(int, line.split()[:-1])))
			print(list(map(int, line.split()[:-1])))
			line = file.readline()
	_draw_graph(edges)
