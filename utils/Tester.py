import random
import numpy as np


class Tester(object):

	def __init__(self, array=list([1, 2, 3]), age=5):
		self.arr = array
		self.age = age

	def __eq__(self, other):
		print('equaling...')
		return isinstance(other, Tester) and self.age == other.age and set(self.arr) == set(other.arr)

	def __hash__(self):
		print('hashing...')
		return hash(self.arr.__str__()+str(self.age))

	@staticmethod
	def weighted_choice(weights):
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
		# print(a, b)
		# return tuple([a, b])
		return a, b


def test1():
	test_list = list()
	test = Tester(array=[1, 2, 2, 3])
	hash_set = set()
	hash_set.add(test)
	for i in range(6):
		tempt = Tester(age=i)
		test_list.append(tempt)
		hash_set.add(tempt)
	test_2 = Tester(array=[1, 3, 2], age=5)


def test2():
	result1 = np.zeros(6, dtype=int)
	result2 = np.zeros(6, dtype=int)
	for i in range(10000):
		ran = Tester.weighted_choice([1/5, 1/3, 1/3, 1/10, 1/4, 1/5])
		# ran = Tester.weighted_choice([1000 / 5, 1000 / 3, 1000 / 3, 1000 / 10, 1000 / 4, 1000 / 5])
		result1[ran[0]] += 1
		result2[ran[1]] += 1
	print(result1)
	print(result2)


if __name__ == '__main__':
	test2()
