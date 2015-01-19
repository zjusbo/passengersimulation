#encoding:utf-8
import random 
import sys
import time
import Tkinter
import FileDialog
import os
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
		if self.x != self.lx or self.ly != self.y:
			print 'move not confirmed'
			pdb.set_trace()

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
				#E[i]  = float('-inf')
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
		#nextCell = random.sample([i for i in xrange(9) if P[i] == max(P)], 1)[0] #randomly pick a cell with the maximal P 
		
		# only can move forward, left, right and don't move.
		if self.direction == 1: # move up
			nextCell = random.sample([i for i in [1, 3, 4, 5] if P[i] == max([P[1], P[3], P[4], P[5]])], 1)[0] #randomly pick a cell with the maximal P 
		elif self.direction == -1: #move down
			nextCell = random.sample([i for i in [7, 3, 4, 5] if P[i] == max([P[7], P[3], P[4], P[5]])], 1)[0] #randomly pick a cell with the maximal P 

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
	def __init__(self, numOfUpPassenger, numOfDownPassenger, mapWidth, mapHeight, markerSize, frameInterval = 50, stepInterval = 1000, cangoback = True):
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
		self.cangoback = cangoback
		if self.totalPassenger > self.mapSize:
			raise ValueError, 'too many passengers!' 
		self.passengers = []

		self.fig, self.ax = plt.subplots(1, 1)
		self.ax.grid(b = True, which = 'major')
		self.ax.grid(b = True, which = 'minor')
		self.ax.set_yticks(range(-1, self.mapHeight), minor = True)
		self.ax.set_xticks(range(-1, self.mapWidth), minor = True)
		plt.axis([-1, self.mapWidth, -1, self.mapHeight])
		self.udots, self.ddots= plt.plot([], [], '^r', [], [], '*b', markersize = markerSize)
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

	def canGoBack(self, bool):
		self.cangoback = bool

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
		while True:
			collideCells = self.isCollide()
			if collideCells == []:
				break
			else:
				# find unmoved Passenger in collide cells
				unmovedP = []
				for p in collideCells:
					if p.lx == p.x and p.ly == p.y:
						unmovedP = p
						break
				if unmovedP != []:
					for p in collideCells:
						if p != unmovedP:
							p.undoMove()
				else: # no unmoved passengers
					r = random.sample(range(len(collideCells)), 1)[0]
					for idx, p in enumerate(collideCells):
						if r != idx:
							p.undoMove()

		#location exchange detect
		for p in self.passengers:
			for q in self.passengers:
				if p != q and p.x == q.lx and p.y == q.ly:
					p.undoMove()
					q.undoMove()
					continue
		
		#testing area
		for p in self.passengers:
			for q in self.passengers:
				if p != q and p.x == q.x and p.y == q.y:
					for r in self.passengers:
						sys.stdout.write('(%s, %s) ' % (r.x, r.y))
					print ''
					pdb.set_trace()
					print 'Collision at (%s, %s)' %(p.x, p.y)

		#update map
		for c in self.map:
			for i in xrange(len(c)):
				c[i] = 0
		for p in self.passengers:
			self.map[p.x][p.y] = p

		#calculate passenger average speed

	def statistics(self):
		count = 0
		for p in self.passengers:
			if p.lx == p.x and p.ly == p.y:
				count += 1
		return float(count) / self.totalPassenger

	def isCollide(self):
		r = []
		for p in self.passengers:
			for q in self.passengers:
				if p != q and p.x == q.x and p.y == q.y:
					r.append(q)
			if r != []:
				r.append(p)
				return r
		return []

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
			if p.y == 0 and p.ly == self.mapHeight - 1: # touch the ceiling
				thisy = p.ly + float(i % f) / f * 1
				if thisy > self.mapHeight - 0.5:
					thisy = thisy - self.mapHeight
			elif p.y == self.mapHeight - 1 and p.ly == 0: # touch the bottom
				thisy = p.ly + float(i % f) / f * -1
				if thisy < -0.5:
					thisy = thisy + self.mapHeight
			else: # normal scenario 
				thisy = p.ly + float(i % f) / f * (p.y - p.ly)
			if p.direction == 1:
				uy.append(thisy)
			else:
				dy.append(thisy)

		self.udots.set_data(ux, uy)
		self.ddots.set_data(dx, dy)
		return self.udots, self.ddots

	def ani_init(self):
		self.udots.set_data([], [])
		self.ddots.set_data([], [])
		return self.udots, self.ddots

def main():
	try:
		mapWidth = int(raw_input('Map width: '))
		if mapWidth <= 0:
			raise ValueError
		mapHeight = int(raw_input('Map height: '))
		if mapHeight <= 0:
			raise ValueError
		numUpPassenger = int(raw_input('Num of up people: '))
		if numUpPassenger < 0:
			raise ValueError
		numDownPassenger = int(raw_input('Num of down people: '))
		if numDownPassenger < 0:
			raise ValueError
		markerSize = int(raw_input('Size of marker (10 - 30 is recommended): '))
		if markerSize < 0:
			raise ValueError
		iterationTime = int(raw_input('iteration times (100 - 500 is recommended): '))
		if iterationTime < 0:
			raise ValueError
	except ValueError:
		print 'Please enter a number bigger than 0.'
		sys.exit(-1)
	else:
		m = Map(numUpPassenger, numDownPassenger, mapWidth, mapHeight, markerSize)
		#m = Map(5,5,5,5)
		for x in xrange(0,iterationTime):
			if float(x) / iterationTime * 100 in range(0, 101):
				os.system('cls')
				print 'iterating... %s%%' % (float(x) / iterationTime * 100)
			m.next()
		os.system('cls')
		print 'iteration finished.'
		m.setFrameInterval(50)
		m.setStepInterval(100)
		percentage = m.statistics()
		print 'Percentage of unmoved passengers after %sth iteration: %s%%' % (iterationTime, percentage * 100)
		anim = animation.FuncAnimation(m.fig, m.animate, init_func = m.ani_init, frames = None, interval = m.frameInterval, blit = True)
		plt.show()

if __name__ == '__main__':
	main()