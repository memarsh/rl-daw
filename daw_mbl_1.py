import random
import modelbasedlearner as mbl

class Agent():
	def __init__(self):
		state_dict = {1:[0], 2:[1, 2], 3:[3, 4]}
		self.ai = mbl.ModelBasedLearner(actions=["left", "right"], states = state_dict)
		self.lastAction = None
		self.lastState = None
		self.lastLevel = None
		self.currState = 0
		self.currLevel = 1
		self.currAction = None
		self.currReward = 0
		# stuff to set up the random walk of reward
		self.SD = 0.025
		self.lowerBoundary = 0.25
		self.upperBoundary = 0.75
		if randomReward:
			self.case1RewardProb = self.initializeReward()
			self.case2RewardProb = self.initializeReward()
			self.case3RewardProb = self.initializeReward()
			self.case4RewardProb = self.initializeReward()
		else:
			self.case1RewardProb = case1
			self.case2RewardProb = case2
			self.case3RewardProb = case3
			self.case4RewardProb = case4

	def initializeReward(self):
		rewardProb = 0
		while rewardProb < self.lowerBoundary or rewardProb > self.upperBoundary:
			rewardProb = random.random()
		return rewardProb 

	def getLastBoardState(self):
		return self.lastBoardState

	def getCurrBoardState(self):
		return self.currBoardState

	def getLastAction(self):
		return self.lastAction

	def getCurrReward(self):
		return self.currReward

	# random walk function
	def randomWalk(self, oldValue):
		newValue = 0
		noise = random.gauss(0, self.SD)
		addNoise = oldValue + noise
		if addNoise > self.upperBoundary:
			diff = self.upperBoundary - oldValue # how much distance between old value and upper boundary
			extra = noise - diff # how much the noise makes the value go over the upper boundary
			pointDiff = diff - extra # reflecting back, should be pos if 
			newValue = oldValue + pointDiff # old value plus whatever reflecting value we've calculated
		elif addNoise < self.lowerBoundary:
			diff = oldValue - self.lowerBoundary
			extra = -noise - diff
			pointDiff = diff - extra
			newValue = oldValue - pointDiff
		else:
			newValue = addNoise
		return newValue

	# 