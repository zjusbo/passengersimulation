#encoding:utf-8
import random 
import sys
import time
class Passenger(object):
	"""Passenger
	AdjacentCell:
		0 1 2
		3 4 5
		6 7 8
	Direction:
		up 1
		down -1
	"""

	def __init__(self, x, y, direction):		
		super(Passenger, self).__init__()
		self.x = self.lx = x
		self.y = self.ly = y
		self.direction = direction
	
	def move(self, thisMap):
		mapWidth = len(thisMap)
		mapHeight = len(thisMap[0])

		D = [0] * 9 #Direction-parameter
		D[0] = D[2] = 0.7 * self.direction
		D[1] = 1 * self.direction
		D[3:6] = 0
		D[6] = D[8] = -0.7 * self.direction
		D[7] = -1 * self.direction

		E = [0] * 9 #Empty-parameter
		for i in xrange(9):
			dx = i % 3 - 1
			dy = -1 * (i / 3 - 1)
			nx = self.x + dx
			ny = self.correctY(self.y + dy, mapHeight)
			if dx == 0 and dy == 0: #current cell
				E[4] = 0
			elif nx < 0 or nx >=  mapWidth: #next cell is out of boundary
				E[i] = float('-inf')
			elif thisMap[nx][ny] == 0: #next cell is empty
				E[i] = 1
			else: #next cell is occupied
				E[i]  = -1

		F = [0] * 9 #Forward-parameter
		for i in xrange(9):
			dx = i % 3 - 1
			dy = -1 * (i / 3 - 1)
			nx = self.x + dx
			ny = self.correctY(self.y + dy, mapHeight)
			
			if nx < 0 or nx >= mapWidth:#next cell is out of boundary
				F[i] = float('-inf')
				continue

			viewMap = self.setViewMap(nx, ny, thisMap)
			S1 = 0
			S2 = 0
			for c in viewMap:
				if c == 0: #current cell is empty
					S1 += 1
				else: #current cell is occupied
					S2 += 1
			sizeOfViewMap = len(viewMap)
			F[i] = (S1 - S2) / sizeOfViewMap

		C = [0] * 9 #Category-parameter
		pass
	def correctY(self, y, mapHeight):
		if y >= 0 and y < mapHeight:
			return y
		elif y < 0:
			return mapHeight + y
		else:
			return y - mapHeight
	
	def setViewMap(self, x, y, thisMap):
		"""return a one-dimensional list contain the view map of the passenger at point (x, y)"""
		mapHeight = len(thisMap[0])
		mapWidth = len(thisMap)
		r = []

		for dx in xrange(-1, 2):
			for dy in xrange(0, 5):
				dy = self.direction * dy
				nx = x + dx
				ny = self.correctY(y + dy)
				if nx >= mapWidth or nx < 0: #next cell is out of boundary
					continue
				r.append(thisMap[nx][ny])
		return r
	def undo(self):
		pass
class Map(object):
	"""docstring for PassengerManager"""
	def __init__(self, numOfUpPassenger, numOfDownPassenger, mapWidth, mapHeight):
		super(Map, self).__init__()
		self.numOfUpPassenger = numOfUpPassenger
		self.numOfDownPassenger = numOfDownPassenger
		self.mapWidth = mapWidth
		self.mapHeight = mapHeight
		self.mapSize = self.mapWidth * self.mapHeight
		self.totalPassenger = numOfDownPassenger + numOfUpPassenger
		if self.totalPassenger > self.mapSize:
			raise ValueError, 'too many passengers!' 
		self.passengers = []

		passengerCoordinates = random.sample(range(self.mapSize), self.totalPassenger)
		self.map = [[0] * self.mapHeight for x in xrange(0, self.mapWidth)]
		for i in xrange(self.totalPassenger):
			c = passengerCoordinates[i]
			x = c % self.mapWidth
			y = c / self.mapWidth
			if i < self.numOfDownPassenger:
				d = -1
			else:
				d = 1
			p = Passenger(x, y, d)
			self.passengers.append(p)
			self.map[x][y] = p


	def show(self):
		for i in xrange(self.mapHeight - 1, -1, -1):
			for j in xrange(self.mapWidth):
				if self.map[i][j] == 0:
					sys.stdout.write('0 ')
				else:
					sys.stdout.write('%s ' %self.map[i][j].direction)
			print ''

def main():
	m = Map(5, 5, 5, 5)
	m.show()

if __name__ == '__main__':
	main()