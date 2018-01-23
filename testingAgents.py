# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class Grid:

	# Adapted from Lab Solutions 5 (Parsons, 2017)
	# Draws a grid - where an array has one position for each element on the grid
	# Not used for any function in the map other than printing a pretty grid

	def __init__(self, width, height):
		self.width = width
		self.height = height
		subgrid = []
		for i in range(self.height):
			row = []
			for j in range(self.width):
				row.append(0)
			subgrid.append(row)

		self.grid = subgrid

	def setValue(self, x, y, value):
		self.grid[y][x] = value

	def getValue(self, x, y):
		return self.grid[y][x]

	def getHeight(self):
		return self.height

	def getWidth(self):
		return self.width

	#Print grid
	def display(self):
		for i in range(self.height):
			for j in range(self.width):
				# print grid elements with no newline
				print self.grid[i][j],
			print
		print

	def prettyDisplay(self):
		for i in range(self.height):
			for j in range(self.width):
				# print grid elements with no newline
				print self.grid[self.height - (i + 1)][j],
			print
		print

class TestingAgent(Agent):
	"""
	The MDP Agent is one that calculates utilities for the map and for pacman's location
	In order to gain the best movement policy for every state of the map

	It updates every time a move is made (i.e. when a food is eaten, or a ghost moves)
	(i.e. recalculates using valueIteration)
	Number of loops in valueIteration depends on map size for efficiency. The smaller the map is,
	the lower the number of loops required.
	"""
	# Constructor: this gets run when we first invoke pacman.py
	def __init__(self):
		print "Starting up MDPAgent!"
		name = "Pacman"

		# Store permanent values
		# These lists store values that remain more or less static throughout
		# the entire game (with the exception of coordinates moving from capsules/foodMap to visited)
		self.visited = []
		self.foodMap = []
		self.wallMap = []
		self.capsuleMap = []


	# Gets run after an MDPAgent object is created and once there is
	# game state to access.
	def registerInitialState(self, state):
		print "Running registerInitialState for MDPAgent!"
		print "I'm at:"
		print api.whereAmI(state)

		# Make map. taken from lab 5 solutions (Parsons, 2017)
		self.makeMap(state)
		self.addWallsToMap(state)
		self.map.display()

	# This is what gets run in between multiple games
	def final(self, state):
		print "Looks like the game just ended!"

		self.visited = []
		self.foodMap = []
		self.wallMap = []
		self.capsuleMap = []


	# Make a map of a grid
	def makeMap(self, state):
		corners = api.corners(state)
		height = self.getLayoutHeight(corners)
		width = self.getLayoutWidth(corners)

		self.map = Grid(width, height)

	# Functions that get height and width of grid (+1 to account for 0-indexing)
	def getLayoutHeight(self, corners):
		yVals = []
		for i in range(len(corners)):
			yVals.append(corners[i][1])
		return max(yVals) + 1

	def getLayoutWidth(self, corners):
		xVals = []
		for i in range(len(corners)):
			xVals.append(corners[i][0])
		return max(xVals) + 1

	# Place walls into map grids
	def addWallsToMap(self, state):
		walls = api.walls(state)
		for i in range(len(walls)):
			self.map.setValue(walls[i][0], walls[i][1], "#")

	def makeValueMap(self, state):
		# This function returns a dictionary of all possible coordinates on a grid
		# As well as all the values that are assigned to each coordinate-category
		# Food is given a value of 5
		# Empty spaces are given a value of 0
		# Capsules are given a value of 5


		food = api.food(state)
		walls = api.walls(state)
		capsules = api.capsules(state)
		pacman = api.whereAmI(state)
		corners = api.corners(state)

		# If pacman's location has not been recorded in a list of visited locations
		# Record it
		if pacman not in self.visited:
			self.visited.append(pacman)

		# Up
		for i in food:
			if i not in self.foodMap:
				self.foodMap.append(i)

		for i in walls:
			if i not in self.wallMap:
				self.wallMap.append(i)

		for i in capsules:
			if i not in self.capsuleMap:
				self.capsuleMap.append(i)


		# Create a dictionary storing all
		# Food, wall and capsule locations, while assigning values to them
		self.foodDict = dict.fromkeys(self.foodMap, 5)
		self.wallDict = dict.fromkeys(self.wallMap, '#')
		self.capsuleDict = dict.fromkeys(self.capsuleMap, 5)

		# Initiate valueMap to store all coordinates
		valueMap = {}
		valueMap.update(self.foodDict)
		valueMap.update(self.wallDict)
		valueMap.update(self.capsuleDict)

		# Using the APIs to get coordinates tends to leave out pacman
		# Initial position
		# This will sweep through all available coordinates
		# And add the square to the list with 0

		for i in range(self.getLayoutWidth(corners) - 1):
			for j in range(self.getLayoutHeight(corners) - 1):
				if (i, j) not in valueMap.keys():
					valueMap[(i, j)] = 0

		# Update function. If pacman has been seen to visit a square
		# It means he has eaten the food or capsules there
		# Thus, set their values to 0
		for i in self.foodMap:
			if i in self.visited:
				valueMap[i] = 0

		for i in self.capsuleMap:
			if i in self.visited:
				valueMap[i] = 0

		# Another update function
		# Updates the location of the ghost
		ghosts = api.ghosts(state)
		ghostStates = api.ghostStatesWithTimes(state)

		for i in valueMap.keys():
			for j in range(len(ghosts)):
				ghostTime = ghostStates[j][1]
				#Convert coordinates to int (keys are stored as int, but coordinates from API are stored as float)
				if ((int(ghosts[j][0])), (int(ghosts[j][1]))) == i:
					valueMap[i] = -10
				#elif ((int(ghosts[j][0])), (int(ghosts[j][1]))) == i and ghostTime >= 5:
				#	valueMap[i] = 5

		return valueMap


	def getTransition(self, x, y, valueMap):
		# This function calculates the maximum expected utility of a coordinate on the initiated valueMap
		# An sets the value of the coordinate to the MEU
		# Which will then later be used as the transition value during value iteration

		# initialise a dictionary to store utility values
		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}
		# valueMap should be a dictionary containing a list of values assigned to every grid
		self.valueMap = valueMap

		self.x = x
		self.y = y

		north = (self.x, self.y + 1)
		south = (self.x, self.y - 1)
		east = (self.x + 1, self.y)
		west = (self.x - 1, self.y)
		stay = (self.x, self.y)


		# If North is not a wall, then multiply expected utility;
		# else multiply expected utility of staying in place
		# If the perpendicular directions are not walls, then multiply expected utility of those
		# else multiply expected utility of just staying in place

		if self.valueMap[north] != "#":
			n_util = (0.8 * self.valueMap[north])
		else:
			n_util = (0.8 * self.valueMap[stay])

		if self.valueMap[east] != "#":
			n_util += (0.1 * self.valueMap[east])
		else:
			n_util += (0.1 * self.valueMap[stay])

		if self.valueMap[west] != "#":
			n_util += (0.1 * self.valueMap[west])
		else:
			n_util += (0.1 * self.valueMap[stay])

		self.util_dict["n_util"] = n_util


		# Repeat for the rest of the directions
		if self.valueMap[south] != "#":
			s_util = (0.8 * self.valueMap[south])
		else:
			s_util = (0.8 * self.valueMap[stay])

		if self.valueMap[east] != "#":
			s_util += (0.1 * self.valueMap[east])
		else:
			s_util += (0.1 * self.valueMap[stay])

		if self.valueMap[west] != "#":
			s_util += (0.1 * self.valueMap[west])
		else:
			s_util += (0.1 * self.valueMap[stay])

		self.util_dict["s_util"] = s_util


		if self.valueMap[east] != "#":
			e_util = (0.8 * self.valueMap[east])
		else:
			e_util = (0.8 * self.valueMap[stay])

		if self.valueMap[north] != "#":
			e_util += (0.1 * self.valueMap[north])
		else:
			e_util += (0.1 * self.valueMap[stay])

		if self.valueMap[south] != "#":
			e_util += (0.1 * self.valueMap[south])
		else:
			e_util += (0.1 * self.valueMap[stay])

		self.util_dict["e_util"] = e_util

		if self.valueMap[west] != "#":
			w_util = (0.8 * self.valueMap[west])
		else:
			w_util = (0.8 * self.valueMap[stay])

		if self.valueMap[north] != "#":
			w_util += (0.1 * self.valueMap[north])
		else:
			w_util += (0.1 * self.valueMap[stay])

		if self.valueMap[south] != "#":
			w_util += (0.1 * self.valueMap[south])
		else:
			w_util += (0.1 * self.valueMap[stay])

		self.util_dict["w_util"] = w_util

		# Take the max value in the dictionary of stored utilities
		# Assign current grid MEU
		# Return updated valueMap that has transition values
		self.valueMap[stay] = max(self.util_dict.values())

		return self.valueMap[stay]


	def valueIteration(self, state, reward, gamma, V1):
		# This function does valueIteration for larger maps
		# Reward = assigned reward for every state
		# Gamma = discount function
		# V1 = valueMap initialised with values for every element in the map
		# Where food = 5, ghost = -10, capsules = 5

		corners = api.corners(state)
		walls = api.walls(state)
		food = api.food(state)
		ghosts = api.ghosts(state)
		capsules = api.capsules(state)

		#Get max width and height
		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		# Create a list of buffer coordinates within 3 squares NSEW of ghosts to calculate
		# value iteration around the ghosts (otherwise, food taken to be terminal value)
		# will not have negative utilities - meaning pacman will still go for those food
		# if a ghost is near by
		# This does not work in small maps due to the virtue of those maps being far too small
		# making this function redundant for them
		foodToCalculate = []
		for i in range(5):
			for x in range(len(ghosts)):
				# Append coordinates 5 squares east to ghost
				if (int(ghosts[x][0] + i), int(ghosts[x][1])) not in foodToCalculate:
					foodToCalculate.append((int(ghosts[x][0] + i), int(ghosts[x][1])))
				# Append coordinates 5 squares west to ghost
				if (int(ghosts[x][0] - i), int(ghosts[x][1])) not in foodToCalculate:
					foodToCalculate.append((int(ghosts[x][0] - i), int(ghosts[x][1])))
				# Append coordinates 5 squares north to ghost
				if (int(ghosts[x][0]), int(ghosts[x][1] + 1)) not in foodToCalculate:
					foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] + i)))
				# Append coordinates 5 squares south to ghost
				if (int(ghosts[x][0]), int(ghosts[x][1] - 1)) not in foodToCalculate:
					foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] - i)))


		# A list of coordinates that should not be calculated
		# Although it might be simple to just use foodToCalculate
		# it does not take into account when the food is eaten or not
		# So this list checks against available food that intersect with being outside of
		# 5 squares of each ghost
		doNotCalculate = []
		for i in food:
			if i not in foodToCalculate:
				doNotCalculate.append(i)

		# raise value error if gamma is not between 0 and 1
		if not (0 < gamma <= 1):
			raise ValueError("MDP must have a gamma between 0 and 1.")

		# Implement Bellman equation with _-loop iteration
		loops = 200
		while loops > 0:
			V = V1.copy() # This will store the old values
			for i in range(maxWidth):
				for j in range(maxHeight):
					# Exclude any food because in this case it is the terminal state
					# Except for food that are within 5 squares north/south/east/west of the ghost
					if (i, j) not in walls and (i, j) not in doNotCalculate and (i, j) not in ghosts and (i, j) not in capsules:
						V1[(i, j)] = reward + gamma * self.getTransition(i, j, V)
			loops -= 1

	def valueIterationSmall(self, state, reward, gamma, V1):
		# Similar to valueIteration function
		# does not calculate buffers around ghosts (cause it would be too small)
		# meant for maps smaller than 10 x 10

		corners = api.corners(state)
		walls = api.walls(state)
		food = api.food(state)
		ghosts = api.ghosts(state)
		capsules = api.capsules(state)

		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		if not (0 < gamma <= 1):
			raise ValueError("MDP must have a gamma between 0 and 1.")

		# Implement Bellman equation with 10-loop iteration
		# Since smaller maps do not require as big of a value iteration loop
		loops = 100
		while loops > 0:
			V = V1.copy() # This will store the old values
			for i in range(maxWidth):
				for j in range(maxHeight):
					# Exclude any food because in this case it is the terminal state
					if (i, j) not in walls and (i, j) not in food and (i, j) not in ghosts and (i, j) not in capsules:
						V1[(i, j)] = reward + gamma * self.getTransition(i, j, V)
			loops -= 1


	def getPolicy(self, state, iteratedMap):
		# gets movement policy for pacman's location at a given state
		# using valueiteration map that is updated at every step

		pacman = api.whereAmI(state)

		# put in a valueMap that has been run across valueIteration (otherwise)
		# a proper policy would not be able to be retrieved
		self.valueMap = iteratedMap

		# get pacman locations
		x = pacman[0]
		y = pacman[1]

		# initialise dictionaries to hold expected utilities
		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}

		corners = api.corners(state)
		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		# get directions relative to pacman's location
		north = (x, y + 1)
		south = (x, y - 1)
		east = (x + 1, y)
		west = (x - 1, y)
		stay = (x, y)

		# If North is not a wall, then multiply expected utility;
		# else multiply expected utility of staying in place
		# If the perpendicular directions are not walls, then multiply expected utility of those
		# else multiply expected utility of just staying in place

		if self.valueMap[north] != "#":
			n_util = (0.8 * self.valueMap[north])
		else:
			n_util = (0.8 * self.valueMap[stay])

		if self.valueMap[east] != "#":
			n_util += (0.1 * self.valueMap[east])
		else:
			n_util += (0.1 * self.valueMap[stay])

		if self.valueMap[west] != "#":
			n_util += (0.1 * self.valueMap[west])
		else:
			n_util += (0.1 * self.valueMap[stay])

		self.util_dict["n_util"] = n_util


		# Repeat for the rest of the directions
		if self.valueMap[south] != "#":
			s_util = (0.8 * self.valueMap[south])
		else:
			s_util = (0.8 * self.valueMap[stay])

		if self.valueMap[east] != "#":
			s_util += (0.1 * self.valueMap[east])
		else:
			s_util += (0.1 * self.valueMap[stay])

		if self.valueMap[west] != "#":
			s_util += (0.1 * self.valueMap[west])
		else:
			s_util += (0.1 * self.valueMap[stay])

		self.util_dict["s_util"] = s_util


		if self.valueMap[east] != "#":
			e_util = (0.8 * self.valueMap[east])
		else:
			e_util = (0.8 * self.valueMap[stay])

		if self.valueMap[north] != "#":
			e_util += (0.1 * self.valueMap[north])
		else:
			e_util += (0.1 * self.valueMap[stay])

		if self.valueMap[south] != "#":
			e_util += (0.1 * self.valueMap[south])
		else:
			e_util += (0.1 * self.valueMap[stay])

		self.util_dict["e_util"] = e_util

		if self.valueMap[west] != "#":
			w_util = (0.8 * self.valueMap[west])
		else:
			w_util = (0.8 * self.valueMap[stay])

		if self.valueMap[north] != "#":
			w_util += (0.1 * self.valueMap[north])
		else:
			w_util += (0.1 * self.valueMap[stay])

		if self.valueMap[south] != "#":
			w_util += (0.1 * self.valueMap[south])
		else:
			w_util += (0.1 * self.valueMap[stay])

		self.util_dict["w_util"] = w_util

		# get max expected utility
		maxMEU = max(self.util_dict.values())
		# return the move with the highest MEU
		return self.util_dict.keys()[self.util_dict.values().index(maxMEU)]

	def getAction(self, state):

		print "-" * 30
		legal = api.legalActions(state)
		corners = api.corners(state)

		maxWidth = self.getLayoutWidth(corners) - 1
		maxHeight = self.getLayoutHeight(corners) - 1

		# This function updates all locations at every state
		# for every action retrieved by getAction, thi3s map is recalibrated
		valueMap = self.makeValueMap(state)

		# If the map is large enough, calculate buffers around ghosts
		# also use higher number of iteration loops to get a more reasonable policy

		if maxWidth >= 10 and maxHeight >= 10:
			self.valueIteration(state, -0.5, 0.7, valueMap)
		else:
			self.valueIterationSmall(state, 0.2, 0.7, valueMap)

		print "best move: "
		print self.getPolicy(state, valueMap)

		# Update values in map with iterations
		for i in range(self.map.getWidth()):
			for j in range(self.map.getHeight()):
				if self.map.getValue(i, j) != "#":
					self.map.setValue(i, j, valueMap[(i, j)])

		self.map.prettyDisplay()


		# If the key of the move with MEU = n_util, return North as the best decision
		# And so on...

		if self.getPolicy(state, valueMap) == "n_util":
			return api.makeMove('North', legal)

		if self.getPolicy(state, valueMap) == "s_util":
			return api.makeMove('South', legal)

		if self.getPolicy(state, valueMap) == "e_util":
			return api.makeMove('East', legal)

		if self.getPolicy(state, valueMap) == "w_util":
			return api.makeMove('West', legal)
