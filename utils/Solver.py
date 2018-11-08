

class Solver(object):

	def __init__(self):
		pass


class Route(object):

	def __init__(self, paths=list()):
		self.paths = paths

	def add_path(self, path):
		self.paths.append(path)

	def __str__(self):
		route = 's '
		for path in self.paths:
			route += str(path)
		return route


class Path(object):

	def __init__(self, tasks=list()):
		self.tasks = tasks

	def add_task(self, task):
		self.tasks.append(task)

	def __str__(self):
		path = '0,'
		for task in self.tasks:
			path += '({},{}),'.format(task[0], task[1])
		path += '0'
		return path
