# -*- coding: utf-8 -*-

import numpy as np


class CARPData(object):

	def __init__(self):
		self.specification = dict()
		self.data = None

	def read_file(self, file_stream):
		content = file_stream.readlines()
		content = [line.strip() for line in content]
		data = list()
		for line in content[:8]:
			line = line.split(':')
			self.specification[line[0].strip()] = line[1].strip()
		for line in content[9:-1]:
			data.append([int(x) for x in line.split()])
		self.data = np.array(data)
		file_stream.close()

	def __str__(self):
		return 'Specifications:\n' + self.specification.__str__()\
		       + '\nData:\n' + self.data.__str__()
