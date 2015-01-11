#encoding:utf-8
import random 
import sys
import time
from heapq import heapify, heappush, heappop
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import pdb

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
				E[i] = 0
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
			F[i] = float((S1 - S2)) / sizeOfViewMap

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
			S1 = 0 
			S2 = 0
			for c in viewMap:
				if c == 0: #cell is empty
					S1 += 1
				elif c.direction == self.direction:
					S1 += 1
				else:
					S2 += 1
			sizeOfViewMap = len(viewMap)
			C[i] = float((S1 - S2)) / sizeOfViewMap
		
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
	def __init__(self, numOfUpPassenger, numOfDownPassenger, mapWidth, mapHeight, frameInterval = 50, stepInterval = 1000):
		super(Map, self).__init__()
		self.numOfUpPassenger = numOfUpPassenger
		self.numOfDownPassenger = numOfDownPassenger
		self.mapWidth = mapWidth
		self.mapHeight = mapHeight
		self.mapSize = self.mapWidth * self.mapHeight
		self.totalPassenger = numOfDownPassenger + numOfUpPassenger
		self.frameInterval = frameInterval
		self.stepInterval = stepInterval
		self.framesPerStep = self.stepInterval / self.frameInterval
		if self.totalPassenger > self.mapSize:
			raise ValueError, 'too many passengers!' 
		self.passengers = []

		self.fig = plt.figure()
		plt.axis([-1, self.mapWidth, -1, self.mapHeight])
		self.udots, self.ddots= plt.plot([], [], '^r', [], [], '*b')
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

	def setFrameInterval(self, v):
		if v <= 0:
			raise ValueError, 'Frame Interval Illegal'
		self.frameInterval = v
		self.framesPerStep = self.stepInterval / self.frameInterval

	def setStepInterval(self, v):
		if v <= 0:
			raise ValueError, 'Step Interval Illegal'
		self.stepInterval = v
		self.framesPerStep = self.stepInterval / self.frameInterval

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
		#confirm last move
		for p in self.passengers:
			p.confirmMove()
		
		#move
		for p in self.passengers:
			p.move(self.map)
		
		#collision detect
		self.collisionDetect()

		#location exchange detect
		pass
				
		#update map
		for c in self.map:
			for i in xrange(len(c)):
				c[i] = 0
		for p in self.passengers:
			self.map[p.x][p.y] = p

	def collisionDetect(self):
		#pdb.set_trace()
		h = self.passengers[:]
		while True:
			isCollision = False
			if len(h) <= 1: #only one passenger
				break
			h.sort(cmp = self.__cmp__)
			for i in xrange(len(h) - 1):
				for j in xrange(i + 1, len(h)):
					if self.__cmp__(h[i], h[j]) != 0:
						break
				#i start index, j index of first different element
				if j == len(h) - 1 and self.__cmp__(h[i], h[j]) == 0:
					j += 1
				if j - i == 1:
					continue
				else:
					isCollision = True
					#if there is an element not moved, undo other elements
					for k in xrange(i, j):
						#pdb.set_trace()
						if h[k].lx == h[k].x and h[k].ly == h[k].y:
							for l in xrange(i, j):
								if l != k:
									h[l].undoMove()
							break
					else:#pick an element randomly to take the cell, undo all other elements, break 
						k = random.sample(range(i, j), 1)[0]
						for l in xrange(i, j):
							if l != k:
								h[l].undoMove()
					break
			if isCollision == False: #no collision
				break

		for i in range(len(self.passengers)):
			for j in xrange(i + 1, len(self.passengers)):
				if self.passengers[i].x == self.passengers[j].x and self.passengers[i].y == self.passengers[j].y:
					for p in h:
						sys.stdout.write('(%s, %s) ' % (p.x, p.y))
					print ''
					pdb.set_trace()
					print 'Collision at (%s, %s)' %(self.passengers[i].x, self.passengers[i].y)

		#free memory
		del h
	def _show(self):
		'''deprecated'''
		for i in xrange(self.mapHeight - 1, -1, -1):
			for j in xrange(self.mapWidth):
				if self.map[j][i] == 0:
					sys.stdout.write('0 ')
				else:
					sys.stdout.write('%s ' % self.map[j][i].direction)
			print ''

	def show(self):
		ux = [p.x for p in self.passengers if p.direction == 1]
		uy = [p.y for p in self.passengers if p.direction == 1]
		dx = [p.x for p in self.passengers if p.direction == -1]
		dy = [p.y for p in self.passengers if p.direction == -1]
		plt.style.use('bmh')
		plt.plot(ux, uy, 'r^', dx, dy, 'g*')
		plt.axis([-1, self.mapWidth, -1, self.mapHeight])
		plt.show()

	def animate(self, i):
		f = self.framesPerStep
		if i % f == 0:
			self.next()
		ux = [p.lx + (p.x - p.lx) * (float(i % f) / f) for p in self.passengers if p.direction == 1]
		dx = [p.lx + (p.x - p.lx) * (float(i % f) / f) for p in self.passengers if p.direction == -1]
		uy = []
		dy = []
		for p in self.passengers: 
			if p.direction == 1: # up passengers
				if p.y - p.ly < 0: # leave boundary and enter boundary
					offset = 1 * (float(i % f) / f)
					if offset > 0.5: # entering boundary
						thisy = -0.5 + offset - 0.5
					else: # leaving boundary
						thisy = p.ly + offset
				else: # within boundary
					thisy = p.ly + (p.y - p.ly) * (float(i % f) / f)
				uy.append(thisy)
			elif p.direction == -1: # down passengers
				if p.y - p.ly > 0: # leave boundary and enter boundary
					offset = 1 * (float(i % f) / f)
					if offset > 0.5: # entering boundary
						thisy = self.mapHeight - offset 
					else: # leaving boundary
						thisy = p.ly - offset
				else: # within boundary
					thisy = p.ly + (p.y - p.ly) * (float(i % f) / f)
				dy.append(thisy)
		self.udots.set_data(ux, uy)
		self.ddots.set_data(dx, dy)
		return self.udots, self.ddots

	def ani_init(self):
		self.udots.set_data([], [])
		self.ddots.set_data([], [])
		return self.udots, self.ddots

def main():
	m = Map(5, 5, 5, 5)
	m.setFrameInterval(50)
	m.setStepInterval(500)
	anim = animation.FuncAnimation(m.fig, m.animate, init_func = m.ani_init, frames = 2000, interval = m.frameInterval, blit = True)
	# for i in range(1):
	# 	m.show()
	# 	print ''
	# 	time.sleep(1)
	# 	m.next()
	plt.show()
if __name__ == '__main__':
	main()