#encoding:utf-8
import random 
import sys
import time
from heapq import heapify, heappush, heappop

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
	def __init__(self, x, y, direction, alpha):		
		super(Passenger, self).__init__()
		self.x = self.lx = x
		self.y = self.ly = y
		self.alpha = alpha
		self.direction = direction
	
	def move(self, thisMap):
		mapWidth = len(thisMap)
		mapHeight = len(thisMap[0])

		D = [0] * 9 #Direction-parameter
		D[0] = D[2] = 0.7 * self.direction
		D[1] = 1 * self.direction
		D[3:6] = [0, 0, 0]
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
			
			if nx < 0 or nx >= mapWidth: #next cell is out of boundary
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
		for i in xrange(9):
			dx = i % 3 - 1
			dy = -1 * (i / 3 - 1)
			nx = self.x + dx
			ny = self.correctY(self.y + dy, mapHeight)

			if nx < 0 or nx >= mapWidth: #next cell is out of boundary
				C[i] = float('-inf')
				continue

			viewMap = self.setViewMap(nx, ny, thisMap)
			S1 = S2 = 0
			for c in viewMap:
				if c == 0:
					S1 += 1
				elif c.direction == self.direction:
					S1 += 1
				else:
					S2 += 1
			sizeOfViewMap = len(viewMap)
			C[i] = (S1 - S2) / sizeOfViewMap
		
		P = [self.alpha * (D[i] + E[i]) + (1 - self.alpha) * (F[i] + C[i]) for i in xrange(9)] #profile-value
		
		nextCell = random.sample([i for i in xrange(9) if P[i] == max(P)], 1)[0] #randomly pick a cell with the maximal P 
			
		dx = nextCell % 3 - 1
		dy = -1 * (nextCell / 3 - 1)
		self.x = self.x + dx
		self.y = self.correctY(self.y + dy, mapHeight)

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
				ny = self.correctY(y + dy, mapHeight)
				if nx >= mapWidth or nx < 0: #next cell is out of boundary
					continue
				r.append(thisMap[nx][ny])
		return r

	def undoMove(self):
		self.x = self.lx
		self.y = self.ly

	def confirmMove(self):
		self.lx = self.x
		self.ly = self.y

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
		self.map = [[0] * self.mapHeight for x in xrange(self.mapWidth)]
		for i in xrange(self.totalPassenger):
			c = passengerCoordinates[i]
			x = c % self.mapWidth
			y = c / self.mapWidth
			if i < self.numOfDownPassenger:
				d = -1
			else:
				d = 1
			a = 0.5 #configuration
			p = Passenger(x, y, d, a)
			self.passengers.append(p)
			self.map[x][y] = p

	def __cmp__(self, p1, p2):
		vp1 = p1.x + p1.y * self.mapWidth
		vp2 = p2.x + p2.y * self.mapWidth
		if vp1 < vp2:
			return -1
		elif vp1 > vp2:
			return 1
		else:
			return 0 

	def next(self):
		for p in self.passengers:
			p.move(self.map)
		
		#collision detect
		h = self.passengers[:]
		while True:
			if len(h) <= 1: #only one passenger
				break
			h.sort(cmp = self.__cmp__)
			for i in xrange(len(h)):
				for j in xrange(i + 1, len(h)):
					if self.__cmp__(h[i], h[j]) == 0:
						continue
					else:
						break
				#i start index, j index of first different element
				#j may not exists
				if 'j' not in dir(): # i is at the end of array
					continue 
				if j - i <= 1: #no collision
					continue
				else:
					#if there is an element not moved, undo other elements
					for k in xrange(i, j):
						if h[k].lx == h[k].x and h[k].ly == h[k].ly:
							for l in xrange(i, j):
								if l is not k:
									h[l].undoMove()
							break
					else:#pick an element randomly to take the cell, undo all other elements, break 
						try:
							k = random.sample(range(i, j), 1)
						except ValueError:
							print 'i = %s, j = %s' %(i, j)
							sys.exit()
						for l in xrange(i, j):
							if l is not k:
								h[l].undoMove()
					break
			else: #no collision
				break
		#location exchange detect
		pass
		
		#confirm move
		del h
		for p in self.passengers:
			p.confirmMove()
			
		#update map
		for c in self.map:
			for i in xrange(len(c)):
				c[i] = 0
		for p in self.passengers:
			self.map[p.x][p.y] = p

	def show(self):
		for i in xrange(self.mapHeight - 1, -1, -1):
			for j in xrange(self.mapWidth):
				if self.map[j][i] == 0:
					sys.stdout.write('0 ')
				else:
					sys.stdout.write('%s ' % self.map[j][i].direction)
			print ''

def main():
	m = Map(5, 5, 5, 5)
	
	for i in range(5):
		m.show()
		print ''
		time.sleep(1)
		m.next()

if __name__ == '__main__':
	main()