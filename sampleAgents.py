# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):


	def getAction(self, state):
		# Get the actions we can try, and remove "STOP" if that is one of them.
		legal = api.legalActions(state)
		if Directions.STOP in legal:
			legal.remove(Directions.STOP)
		# Random choice between the legal options.
		return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

	# Constructor
	#
	# Create a variable to hold the last action
	def __init__(self):
		 self.last = Directions.STOP

	def getAction(self, state):
		# Get the actions we can try, and remove "STOP" if that is one of them.
		legal = api.legalActions(state)
		if Directions.STOP in legal:
			legal.remove(Directions.STOP)
		# If we can repeat the last action, do it. Otherwise make a
		# random choice.
		if self.last in legal:
			return api.makeMove(self.last, legal)
		else:
			pick = random.choice(legal)
			# Since we changed action, record what we did
			self.last = pick
			return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

	def getAction(self, state):

		# Demonstrates the information that Pacman can access about the state
		# of the game.
		print "-" * 30 #divider
		# What are the current moves available

		legal = api.legalActions(state)

		print "Legal moves: ", legal

		# Where is Pacman?
		pacman = api.whereAmI(state)
		print "Pacman position: ", pacman

		# Where are the ghosts?
		print "Ghost positions:"
		theGhosts = api.ghosts(state)
		for i in range(len(theGhosts)):
			print theGhosts[i]

		# How far away are the ghosts?
		print "Distance to ghosts:"
		for i in range(len(theGhosts)):
			print util.manhattanDistance(pacman,theGhosts[i])

		# Where are the capsules?
		print "Capsule locations:"
		print api.capsules(state)

		# Where is the food?
		print "Food locations: "
		print api.food(state)
		print len(api.food(state))

		# Where are the walls?
		print "Wall locations: "
		print api.walls(state)

		print "Corners: "
		print api.corners(state)
		# getAction has to return a move. Here we pass "STOP" to the
		# API to ask Pacman to stay where they are.
		return api.makeMove(random.choice(legal), legal)

class GoWestAgent(Agent):

	def getAction(self,state):
		legal = state.getLegalPacmanActions() #get a list of pacman's legal actions
		if Directions.STOP in legal:
			legal.remove(Directions.STOP) #make it so that pacman won't stop even though it is legal to

		#if going west is in the list of legal moves, then go west
		#else pick a random direction to move
		if Directions.WEST in legal:
			return api.makeMove('West', legal)
		else:
			pick = random.choice(legal)
			return api.makeMove(pick, legal)


class HungryAgent(Agent):
	#Pacman moves towards the closest food he senses
	#though he is unable to get himself past walls...
	#if he doesn't smell any food close to him that he can legally access, he moves in a random direction then
	#continues from there

	def getAction(self, state):

		legal = state.getLegalPacmanActions() #Again, get a list of pacman's legal actions
		if Directions.STOP in legal:
			legal.remove(Directions.STOP)
		pacman = api.whereAmI(state) #retrieve location of pacman
		food = api.food(state) #retrieve location of food

		#Distance of food
		dist = [] # initiate list of distances
		for i in range(len(food)):
			dist.append(util.manhattanDistance(pacman, food[i]))

		minIndex = dist.index(min(dist)) #get index of min dist value (assuming the array remains ordered)
		closestFood = food[minIndex]

		#current position coordinates
		x1, y1 = pacman[0], pacman[1]
		x2, y2 = closestFood

		print "closest food is: "
		print closestFood
		print "pacman's location is: "
		print pacman

		print "list of distances: "
		print dist

		#if pacman is to the West of closest food, then goEast = True and so on...
		goEast = x1 < x2 and y1 == y2
		goWest = x1 > x2 and y1 == y2
		goNorth = x1 == x2 and y1 < y2
		goSouth = x1 == x2 and y1 > y2

		last = state.getPacmanState().configuration.direction

		if x1 == 9 and y1 == 1:
			return api.makeMove(random.choice(legal), legal)
		else:
			pass

		if Directions.EAST in legal and (goEast):
			return api.makeMove('East', legal)

		elif Directions.WEST in legal and (goWest):
			return api.makeMove('West', legal)

		elif Directions.NORTH in legal and (goNorth):
			return api.makeMove('North', legal)

		elif Directions.SOUTH in legal and (goSouth):
			return api.makeMove('South', legal)

		elif last in legal:                   #if pacman doesnt find a move he can do, he just repeats the last move.
			return api.makeMove(last, legal)  #this makes it so that the closest food isn't across the wall from him next

		else:
			return api.makeMove(random.choice(legal), legal) #just return a random move when he's out of moves

class SurvivalAgent(Agent):
	#This agent runs away from ghosts
	#when he senses that ghosts are within range (distance <= 5)
	#Otherwise, like hungry agent, he forages for food

	def getAction(self, state):
		ghosts = api.ghosts(state) #get state of ghosts
		legal = state.getLegalPacmanActions() #Again, get a list of pacman's legal actions
		pacman = api.whereAmI(state) #retrieve location of pacman
		food = api.food(state) #retrieve location of food
		last = state.getPacmanState().configuration.direction #store last move

		#remove stop
		if Directions.STOP in legal:
			legal.remove(Directions.STOP)

		gDist = [] #get distance from ghosts
		for i in range(len(ghosts)):
			gDist.append(util.manhattanDistance(pacman, ghosts[i]))

		minIndex = gDist.index(min(gDist)) #get index of min dist to ghost value
		closestGhost = ghosts[minIndex] #returns x,y of closest ghost

		####Hungry agent####
		#Distance of food
		dist = [] # initiate list of distances
		for i in range(len(food)):
			dist.append(util.manhattanDistance(pacman, food[i]))

		minIndex = dist.index(min(dist)) #get index of min dist value (assuming the array remains ordered)
		closestFood = food[minIndex]

		#current position coordinates
		x1, y1 = pacman[0], pacman[1]
		x2, y2 = closestFood
		x3, y3 = closestGhost

		print "-" * 15
		print "closest food is: "
		print closestFood
		print "list of distances: "
		print dist
		print "Location of pacman: "
		print pacman
		print "Location of ghosts: "
		print ghosts
		print "Distance to ghosts: "
		print gDist
		print "Closest ghost: "
		print closestGhost
		print "Food Map: "
		print food

		if min(gDist) > 5:
		#if pacman is to the West of closest food, then goEast = True and so on...
			goEast = x1 < x2 and y1 == y2
			goWest = x1 > x2 and y1 == y2
			goNorth = x1 == x2 and y1 < y2
			goSouth = x1 == x2 and y1 > y2

			if x1 == 9 and y1 == 1:
				return api.makeMove(random.choice(legal), legal)
			else:
				pass

			if Directions.EAST in legal and (goEast):
				return api.makeMove('East', legal)

			elif Directions.WEST in legal and (goWest):
				return api.makeMove('West', legal)

			elif Directions.NORTH in legal and (goNorth):
				return api.makeMove('North', legal)

			elif Directions.SOUTH in legal and (goSouth):
				return api.makeMove('South', legal)

			elif last in legal:                   #if pacman doesnt find a move he can do, he just repeats the last move.
				return api.makeMove(last, legal)  #this makes it so that the closest food isn't across the wall from him next

			else:
				return api.makeMove(random.choice(legal), legal) #just return a random move when he's out of moves

		#these directions would be opposite of HungryAgent
		#mainly because you are trying to run away
		else:
			warnEast = x1 > x3 and y1 == y3
			warnWest = x1 < x3 and y1 == y3
			warnNorth = x1 == x3 and y1 > y3
			warnSouth = x1 == x3 and y1 < y3

			if Directions.EAST in legal and (warnEast):
				return api.makeMove('East', legal)

			elif Directions.WEST in legal and (warnWest):
				return api.makeMove('West', legal)

			elif Directions.NORTH in legal and (warnNorth):
				return api.makeMove('North', legal)

			elif Directions.SOUTH in legal and (warnSouth):
				return api.makeMove('South', legal)

			elif last in legal:                   #if pacman doesnt find a move he can do, he just repeats the last move.
				return api.makeMove(last, legal)  #this makes it so that the closest food isn't across the wall from him next

			else:
				return api.makeMove(random.choice(legal), legal) #just return a random move when he's out of moves


class MyGreedyAgent(Agent):
	#Refer to : http://aima.cs.berkeley.edu/python/mdp.html
	#http://pythonfiddle.com/markov-decision-process/
	#For implementing MDP

	def __init__(self):
		print "Initialising"

		self.visited = [] #A list to store visited locations
		self.foodMap = [] #Store a permanent list of food

	def getValueMap(self, state, reward):
		"""
		This method helps to map rewards to the state of each grid that contains food
		It gives each coordinate of food an R(s) value
		It also updates each coordinate of food to no reward when it finds
		that Pacman has already eaten it

		This is the initial state that will have to be value-iterated for each change in state
		of ghost and pacman

		returns a dictionary of coordinates and their assigned utility values
		"""
		pacman = api.whereAmI(state)
		food = api.food(state)
		capsules = api.capsules(state)

		self.reward = reward

		if pacman not in self.visited:
			self.visited.append(pacman)

		for i in food:
			if i not in self.foodMap:
				self.foodMap.append(i)

		foodsMap = dict.fromkeys(self.foodMap, self.reward)
		# make a dictionary of capsules and give a reward value of 0 since it's neutral
		capsuleMap = dict.fromkeys(capsules, 0)

		#join these two together to get a complete map of legal squares
		valueMap = {}
		valueMap.update(foodsMap)
		valueMap.update(capsuleMap)

		#Check: If key in food-list is in visited list,
		#Set value of food in valueMap dictionary to 0
		#update value of the dictionary key
		for key in self.foodMap:
			if key in self.visited:
				valueMap[key] = 0

		return valueMap

	def getMEU(self, pos, valueMap, walls):
		"""
		This function takes pacman's coordinates and returns the maximum expected utility of a square

		pos = tuple that contains coordinates of the grid that is to be calculated
		valueMap = dictionary of each grid of food and the values mapped to them
		walls = list of walls [(x,y), (x1,y1) ...]
		"""
		self.x = pos[0]
		self.y = pos[1]
		self.walls = walls
		self.valueMap = valueMap

		#Flag the walls to each direction of a food grid
		north = self.x, self.y + 1
		south = self.x, self.y - 1
		east = self.x + 1, self.y
		west = self.x - 1, self.y

		#initialise a dictionary to store utility values
		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}
		#These if-else statements check that, given a direction X to the grid being checked,
		#if direction X is not a wall, and direction X is a grid that contains/contained foodVal
		#then calculate the total utility of moving in that direction
		if (north not in self.walls) and (north in self.valueMap):
			n_util = (0.8 * self.valueMap[north])
			if (east not in self.walls) and (east in self.valueMap):
				n_util += (0.1 * self.valueMap[east])
			if (west not in self.walls) and (west in self.valueMap):
				n_util += (0.1 * self.valueMap[west])

			self.util_dict["n_util"] = n_util

		if (south not in self.walls) and (south in self.valueMap):
			s_util = (0.8 * self.valueMap[south])
			if (east not in self.walls) and (east in self.valueMap):
				s_util += (0.1 * self.valueMap[east])
			if (west not in self.walls) and (west in self.valueMap):
				s_util += (0.1 * self.valueMap[west])

			self.util_dict["s_util"] = s_util

		if (east not in self.walls) and (east in self.valueMap):
			e_util = (0.8 * self.valueMap[east])
			if (north not in self.walls) and (north in self.valueMap):
				e_util += (0.1 * self.valueMap[north])
			if (south not in self.walls) and (south in self.valueMap):
				e_util += (0.1 * self.valueMap[south])

			self.util_dict["e_util"] = e_util

		if (west not in self.walls) and (west in self.valueMap):
			w_util = (0.8 * self.valueMap[west])
			if (north not in self.walls) and (north in self.valueMap):
				w_util += (0.1 * self.valueMap[north])
			if (south not in self.walls) and (south in self.valueMap):
				w_util += (0.1 * self.valueMap[south])

			self.util_dict["w_util"] = w_util

		return max(self.util_dict.values())


	def valueIteration(self, state, reward, valueMap, gamma, epsilon=0.01):
		#Currently breaks pacman if called
		"""
		This method should calculate the utility of a map of squares
		And get a terminal value. Granted unlike the world of AIMA, there is not terminal grid
		(Unless the game is about to end - the last food pellets could be considered a terminal state)
		(or a grid that a ghost is on)
		In the case of this world, reward states are binary - a square either has food or it doesn't

		Returns U, which is a copy of a valueMap with updated utility values

		reward = reward function
		valueMap = dictionary from self.getValueMap that initiates the reward grid (state 0)
		gamma = discount function
		epsilon = difference threshold for termination

		TODO: using PacMEU to calculate utilities based on legal moves is also possible
		Just replace pac_x and pac_y with the locations of the grids in order to get the legal
		actions, then calculate utilities from there...
		"""
		self.gamma = gamma
		self.reward = reward
		self.valueMap = valueMap

		walls = api.walls(state)

		#value error raised by MDP code in AIMA python file http://aima.cs.berkeley.edu/python/mdp.html
		if not (0 < self.gamma <= 1):
			raise ValueError("MDP must have a gamma between 0 and 1")

		while True:
			loops = 10
			U = self.valueMap.copy()
			delta = 0 #to update difference to calculate termination condition

			for s in valueMap.keys():
				U[s] = self.reward + self.gamma * self.getMEU(s, self.valueMap, walls)
				loops -= 1
				#Calculate difference between new and old value
				#This method of calculating the termination condition is taken from AIMA at Berkeley CS
				#delta = max(delta, abs(U[s] - self.valueMap[s]))
			if loops == 0:
				break
				return U
			#if delta < epsilon * (1 - self.gamma) / self.gamma:
				#return U


	def getPacMEU(self, pac_x, pac_y, foodVal, legalActions):
		"""
		This function takes pacman's coordinates and returns the immediate MEU
		for grids around him

		pac_x, pac_y = pacman locations
		foodVal = dictionary of mapped foods with values
		legalActions = list of legal actions
		"""
		self.pac_x = pac_x
		self.pac_y = pac_y
		self.legalActions = legalActions
		self.foodVal = foodVal

		#Flag the grids to each direction of pacman
		north = self.pac_x, self.pac_y + 1
		south = self.pac_x, self.pac_y - 1
		east = self.pac_x + 1, self.pac_y
		west = self.pac_x - 1, self.pac_y

		self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}
		#MEU is calculated by 0.8 * (foodVal of Grid to pacman's intended direction) + 0.1 * (perpendicular) + 0.1 * (perpendicular)
		#These statements help calculate MEU for each move pacman can make
		#And appends them to a utility dictionary
		if Directions.NORTH in self.legalActions and north in foodVal:
			n_util = (0.8 * foodVal[north])
			if Directions.EAST in self.legalActions and east in foodVal:
				n_util += (0.1 * foodVal[east])
			if Directions.WEST in self.legalActions and west in foodVal:
				n_util += (0.1 * foodVal[west])
			self.util_dict["n_util"] = n_util

		if Directions.SOUTH in self.legalActions and south in foodVal:
			s_util = (0.8 * foodVal[south])
			if Directions.EAST in self.legalActions and east in foodVal:
				s_util += (0.1 * foodVal[east])
			if Directions.WEST in self.legalActions and west in foodVal:
				s_util += (0.1 * foodVal[west])
			self.util_dict["s_util"] = s_util

		if Directions.EAST in self.legalActions and east in foodVal:
			e_util = (0.8 * foodVal[east])
			if Directions.NORTH in self.legalActions and north in foodVal:
				e_util += (0.1 * foodVal[north])
			if Directions.SOUTH in self.legalActions and south in foodVal:
				e_util += (0.1 * foodVal[south])
			self.util_dict["e_util"] = e_util

		if Directions.WEST in self.legalActions and west in foodVal:
			w_util = (0.8 * foodVal[west])
			if Directions.NORTH in self.legalActions and north in foodVal:
				w_util += (0.1 * foodVal[north])
			if Directions.SOUTH in self.legalActions and south in foodVal:
				w_util += (0.1 * foodVal[south])
			self.util_dict["w_util"] = w_util

		return self.util_dict


	def getAction(self, state):
		print "-" * 30 #divider
		ghosts = api.ghosts(state) #get state of ghosts
		legal = state.getLegalPacmanActions() #Again, get a list of pacman's legal actions
		last = state.getPacmanState().configuration.direction #store last move
		pacman = api.whereAmI(state) #retrieve location of pacman
		food = api.food(state) #retrieve location of food
		walls = api.walls(state)

		#how to call getfoodvalmap method.
		#In reality, the reward should be the final value-iteration of the grid.
		foodVal = self.getValueMap(state, 10)

		print foodVal

		#example on how to use getPacMEU function
		currentUtil = self.getPacMEU(pacman[0], pacman[1], foodVal, legal)
		print "Utility values: "
		print currentUtil
		print max(currentUtil.values())
		#example on how to use getMEU function
		foodUtil = self.getMEU((18, 3), foodVal, walls)
		print "max utility for (18, 3) is: "
		print foodUtil


		if Directions.STOP in legal:
			legal.remove(Directions.STOP)
		# Random choice between the legal options.
		return api.makeMove(random.choice(legal), legal)

		"""	
# If none of the grids to the east/west/north/south are out of bounds,
		# calculate utilities like so
		# These if-statements are required so that Grid[y][x] does not return an out of bounds error
		if self.x - 1 > -1 and self.x + 1 < maxWidth and self.y - 1 > -1 and self.y + 1 < maxHeight:
			self.util_dict["n_util"] = (0.8 * self.valueMap[north]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["s_util"] = (0.8 * self.valueMap[south]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["e_util"] = (0.8 * self.valueMap[east]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])
			self.util_dict["w_util"] = (0.8 * self.valueMap[west]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])

		# If the east grid is out of bounds, set east utility to multiply by itself (since argument passed is stop)
		if self.x + 1 > maxWidth:
			self.util_dict["n_util"] = (0.8 * self.valueMap[north]) + (0.1 * self.valueMap[stay]) + (0.1 * self.valueMap[west])
			self.util_dict["s_util"] = (0.8 * self.valueMap[south]) + (0.1 * self.valueMap[stay]) + (0.1 * self.valueMap[west])
			self.util_dict["e_util"] = (0.8 * self.valueMap[stay]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])
			self.util_dict["w_util"] = (0.8 * self.valueMap[west]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])

		# If west grid is out of bounds, set case of moving west to multiply by itself (since argument passed is stop)
		if self.x - 1 < -1:
			self.util_dict["n_util"] = (0.8 * self.valueMap[north]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[stay])
			self.util_dict["s_util"] = (0.8 * self.valueMap[south]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[stay])
			self.util_dict["e_util"] = (0.8 * self.valueMap[east]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])
			self.util_dict["w_util"] = (0.8 * self.valueMap[stay]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[south])

		# If north grid is out of bounds, set north utility to multiply by its own square (since argument passed is stop)
		if self.y + 1 > maxHeight:
			self.util_dict["n_util"] = (0.8 * self.valueMap[stay]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["s_util"] = (0.8 * self.valueMap[south]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["e_util"] = (0.8 * self.valueMap[east]) + (0.1 * self.valueMap[stay]) + (0.1 * self.valueMap[south])
			self.util_dict["w_util"] = (0.8 * self.valueMap[west]) + (0.1 * self.valueMap[stay]) + (0.1 * self.valueMap[south])

		# If south grid is out of bounds, set south utility to multiply by its own square (since argument passed is stop)
		if self.y - 1 < -1:
			self.util_dict["n_util"] = (0.8 * self.valueMap[north]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["s_util"] = (0.8 * self.valueMap[stay]) + (0.1 * self.valueMap[east]) + (0.1 * self.valueMap[west])
			self.util_dict["e_util"] = (0.8 * self.valueMap[east]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[stay])
			self.util_dict["w_util"] = (0.8 * self.valueMap[west]) + (0.1 * self.valueMap[north]) + (0.1 * self.valueMap[stay])

		self.valueMap[(self.x, self.y)] = max(self.util_dict.values())
		return self.valueMap
		"""