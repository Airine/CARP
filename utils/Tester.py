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


if __name__ == '__main__':
	test_list = list()
	test = Tester(array=[1, 2, 2, 3])
	hash_set = set()
	hash_set.add(test)
	for i in range(6):
		tempt = Tester(age=i)
		test_list.append(tempt)
		hash_set.add(tempt)
	test2 = Tester(array=[1, 3, 2], age=5)
