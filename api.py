# api.py
# parsons/15-nov-2017
#
# Version 5
#
# With acknowledgements to Jiaming Ke, who was the first to report the
# bug in corners and to spot the bug in the motion model.
#
# An API for use with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# This provides a simple way of controlling the way that Pacman moves
# and senses its world, to permit exercises with limited sensing
# ability and nondeterminism in sensing and action.
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

# The code here was written by Simon Parsons, based on examples from
# the PacMan AI projects.

from random import random
from pacman import Directions
import util

#
# Parameters
#

# Control visibility.
#
# If partialVisibility is True, Pacman will only see part of the
# environment.
partialVisibility = False

# The limits of visibility when visibility is partial
sideLimit = 1
hearingLimit = 2
visibilityLimit = 5

# Control determinism
#
# If nonDeterministic is True, Pacman's action model will be
# nonDeterministic.
nonDeterministic = True

# Probability that Pacman carries out the intended action:
directionProb = 0.8

# 
# Sensing
#
def whereAmI(state):
    # Returns an (x, y) pair of Pacman's position.
    #
    # This version says exactly where Pacman is.
    # In later version this may be obfusticated.

    return state.getPacmanPosition()

def legalActions(state):
    # Returns the legal set of actions
    #
    # Just pulls this data out of the state. Function included so that
    # all interactions are through this API.
    
    return state.getLegalPacmanActions()

def ghosts(state):
    # Returns a list of (x, y) pairs of ghost positions.
    #
    # This version just returns the ghost positions from the state data
    # In later versions this will be more restricted, and include some
    # uncertainty.
            
    return union(visible(state.getGhostPositions(),state), audible(state.getGhostPositions(),state))

def ghostStates(state):
    # Returns the position of the ghsosts, plus an indication of
    # whether or not they are scared/edible.
    #
    # The information is returned as a list of elements of the form:
    #
    # ((x, y), state)
    #
    # where "state" is 1 if the relevant ghost is scared/edible, and 0
    # otherwise.
    
    ghostStateInfo = state.getGhostStates()
    ghostStates = []
    for s in ghostStateInfo:
        if s.scaredTimer > 0:
            ghostStates.append((s.getPosition(), 1))
        else:
            ghostStates.append((s.getPosition(), 0))
    return ghostStates

def ghostStatesWithTimes(state):
    # Just as ghostStates(), but when the ghost is in scared/edible
    # mode, "state" is a time value (how much longer the ghost will
    # remain scared/edible) rather than 1.
    
    ghostStateInfo = state.getGhostStates()
    ghostStates = []
    for s in ghostStateInfo:
        ghostStates.append((s.getPosition(), s.scaredTimer))
    return ghostStates

def capsules(state):
    # Returns a list of (x, y) pairs of capsule positions.
    #
    # This version returns the capsule positions if they are within
    # the distance limit.
    #
    # Capsules are visible if:
    #
    # 1) Pacman is moving and the capsule is in front of Pacman and
    # within the visibilityLimit, or to the side of Pacman and within
    # the sideLimit.
    #
    # 2) Pacman is not moving, and the capsule is within the visibilityLimit.
    #
    # In both cases, walls block the view.
    
    return visible(state.getCapsules(), state)

def food(state):
    # Returns a list of (x, y) pairs of food positions
    #
    # This version returns all the current food locations that are
    # visible.
    #
    # Food is visible if:
    #
    # 1) Pacman is moving and the food is in front of Pacman and
    # within the visibilityLimit, or to the side of Pacman and within
    # the sideLimit.
    #
    # 2) Pacman is not moving, and the food is within the visibilityLimit.
    #
    # In both cases, walls block the view.
    
    foodList= []
    foodGrid = state.getFood()
    width = foodGrid.width
    height = foodGrid.height
    for i in range(width):
        for j in range(height):
            if foodGrid[i][j] == True:
                foodList.append((i, j))
            
    # Return list of food that is visible
    return visible(foodList, state)

def walls(state):
    # Returns a list of (x, y) pairs of wall positions
    #
    # This version just returns all the current wall locations
    # extracted from the state data.  In later versions, this will be
    # restricted by distance, and include some uncertainty.
    
    wallList= []
    wallGrid = state.getWalls()
    width = wallGrid.width
    height = wallGrid.height
    for i in range(width):
        for j in range(height):
            if wallGrid[i][j] == True:
                wallList.append((i, j))            
    return wallList

def corners(state):
    # Returns the coordinates of the four corners of the state space.
    #
    # For harder exploration we could obfusticate this information.

    corners=[]
    wallGrid = state.getWalls()
    width = wallGrid.width
    height = wallGrid.height
    corners.append((0, 0))
    corners.append((width-1, 0))
    corners.append((0, height-1))
    corners.append((width-1, height-1))
    return corners
                
#
# Acting
#
def makeMove(direction, legal):
    # This version implements non-deterministic movement.
    #
    # Paacman has a probability of directionProb of moving in the
    # specified direction, and 0.5*(1 - directionProb) of moving
    # perpendicular to the specified direction. Any attempt to move in
    # an direction that is not legal means Pacman stays in the same
    # place.
    #
    # With the default setting of directionProb = 0.8, this is exactly
    # the motion model we studied in the MDP lecture.

    # If Pacman hasn't yet moved, then non-determinism plays no role in
    # deciding what Pacman does:
    if direction == Directions.STOP:
        return direction
    
    if nonDeterministic:
        # Sample in the usual way to make Pacman move in the specified
        # direction with probability directionProb.
        #
        # Otherwise make a different move.
        sample = random()
        if sample <= directionProb:
            # Here the non-deterministic action selection says to
            # return the original move, but we need to check it is
            # legal in case we were passed an illegal action (because,
            # for example, that was the MEU action).
            #
            # If the specified action is not legal, in this case we
            # will not move.
            if direction in legal:
                return direction
            else:
                return Directions.STOP
        else:
            return selectNewMove(direction, legal)
    else:
        # When actions are deterministic, Pacman moves in the
        # specified direction
        return direction

#
# Details that you don't need to look at if you don't want to.
#

def distanceLimited(objects, state, limit):
    # When passed a list of object locations, tests how far they are
    # from Pacman, and only returns the ones that are within "limit".

    pacman = state.getPacmanPosition()
    nearObjects = []
    
    for i in range(len(objects)):
        if util.manhattanDistance(pacman,objects[i]) <= limit:
            nearObjects.append(objects[i])

    return nearObjects

def inFront(object, facing, state):
    # Returns true if the object is along the corridor in the
    # direction of the parameter "facing" before a wall gets in the
    # way.
    
    pacman = state.getPacmanPosition()
    pacman_x = pacman[0]
    pacman_y = pacman[1]
    wallList = walls(state)

    # If Pacman is facing North
    if facing == Directions.NORTH:
        # Check if the object is anywhere due North of Pacman before a
        # wall intervenes.
        next = (pacman_x, pacman_y + 1)
        while not next in wallList:
            if next == object:
                return True
            else:
                next = (pacman_x, next[1] + 1)
        return False

    # If Pacman is facing South
    if facing == Directions.SOUTH:
        # Check if the object is anywhere due North of Pacman before a
        # wall intervenes.
        next = (pacman_x, pacman_y - 1)
        while not next in wallList:
            if next == object:
                return True
            else:
                next = (pacman_x, next[1] - 1)
        return False

    # If Pacman is facing East
    if facing == Directions.EAST:
        # Check if the object is anywhere due East of Pacman before a
        # wall intervenes.
        next = (pacman_x + 1, pacman_y)
        while not next in wallList:
            if next == object:
                return True
            else:
                next = (next[0] + 1, pacman_y)
        return False
    
    # If Pacman is facing West
    if facing == Directions.WEST:
        # Check if the object is anywhere due West of Pacman before a
        # wall intervenes.
        next = (pacman_x - 1, pacman_y)
        while not next in wallList:
            if next == object:
                return True
            else:
                next = (next[0] - 1, pacman_y)
        return False

def atSide(object, facing, state):
    # Returns true if the object is in a side corridor perpendicular
    # to the direction that Pacman is travelling.
    
    pacman = state.getPacmanPosition()

    # If Pacman is facing North or Sout, then objects to the side are to the
    # East and West.
    #
    # These are objects that Pacman would see if it were facing East
    # or West.
    
    if facing == Directions.NORTH or facing == Directions.SOUTH:
        # Check if the object is anywhere due North of Pacman before a
        # wall intervenes.
       if inFront(object, Directions.WEST, state) or inFront(object, Directions.EAST, state):
                return True
       else:
                return False
            
    # Similarly for other directions
    if facing == Directions.WEST or facing == Directions.EAST:
        # Check if the object is anywhere due North of Pacman before a
        # wall intervenes.
       if inFront(object, Directions.NORTH, state) or inFront(object, Directions.SOUTH, state):
                return True
       else:
                return False

    else:
        return False
    
def visible(objects, state):
    # When passed a list of objects, returns those that are visible to
    # Pacman.

    # This code creates partial observability by only returning some
    # of the members of objects.
    facing = state.getPacmanState().configuration.direction
    visibleObjects = []
    sideObjects = []
    
    if facing != Directions.STOP:
    
        # If Pacman is moving, visible objects are those in front of,
        # and to the side (if there are any side corridors).

        # Objects in front. Visible up to "visibilityLimit"
        for i in range(len(objects)):
            if inFront(objects[i], facing, state):
                visibleObjects.append(objects[i])
        visibleObjects = distanceLimited(visibleObjects, state, visibilityLimit)
        
        # Objects to the side. Visible up to "sideLimit"
        for i in range(len(objects)):
            if atSide(objects[i], facing, state):
                sideObjects.append(objects[i])
        sideObjects = distanceLimited(sideObjects, state, sideLimit)

        # Combine lists.
        visibleObjects = visibleObjects + sideObjects
        
    else:

        # If Pacman is not moving, they can see in all directions.
        #
        # Unfortunately facing will never have value Directions.STOP
        # after the first move is made, so this code will not run
        # after the first move :-(

        for i in range(len(objects)):
            if inFront(objects[i], Directions.NORTH, state):
                visibleObjects.append(objects[i])
            if inFront(objects[i], Directions.SOUTH, state):
                visibleObjects.append(objects[i])
            if inFront(objects[i], Directions.EAST, state):
                visibleObjects.append(objects[i])
            if inFront(objects[i], Directions.WEST, state):
                visibleObjects.append(objects[i])
        visibleObjects = distanceLimited(visibleObjects, state, visibilityLimit)

    # If we return visibleObjects, we have partial observability. If
    # we return objects, then we have full observability.
    if partialVisibility:
        return visibleObjects
    else:
        return objects

def audible(ghosts, state):
    # A ghost is audible if it is any direction and less than
    # "hearingLimit" away.

    return distanceLimited(ghosts, state, hearingLimit)  
    
def union(a, b):
    # return the union of two lists 
    #
    # From https://www.saltycrane.com/blog/2008/01/how-to-find-intersection-and-union-of/
    #
    return list(set(a) | set(b))

def selectNewMove(direction, legal):
    # This function is called if Pacman isn't moving in the specified
    # direction. Need to pick another legal action.

    # Pick with 50% probability between the two perpendicular
    # possibilities.
    sample = random()
    if sample <= 0.5:
        left = True
    else:
        left = False

    # If chosen direction is North, then pick between West (left) and
    # East. If these moves are legal, make them, otherwise don't move.
    if direction == Directions.NORTH:
        if left:
            if Directions.WEST in legal:
                return Directions.WEST
            else:
                return Directions.STOP
        else:
              if Directions.EAST in legal:
                return Directions.EAST
              else:
                return Directions.STOP

    # If chosen direction is EAST
    if direction == Directions.EAST:
        if left:
            if Directions.NORTH in legal:
                return Directions.NORTH
            else:
                return Directions.STOP
        else:
              if Directions.SOUTH in legal:
                return Directions.SOUTH
              else:
                return Directions.STOP

    # If chosen direction is SOUTH
    if direction == Directions.SOUTH:
        if left:
            if Directions.EAST in legal:
                return Directions.EAST
            else:
                return Directions.STOP
        else:
              if Directions.WEST in legal:
                return Directions.WEST
              else:
                return Directions.STOP
  
    # If chosen direction is WEST
    if direction == Directions.WEST:
        if left:
            if Directions.SOUTH in legal:
                return Directions.SOUTH
            else:
                return Directions.STOP
        else:
              if Directions.NORTH in legal:
                return Directions.NORTH
              else:
                return Directions.STOP

    print "Why am I here?"
