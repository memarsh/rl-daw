import random
import sarsa


class Agent():
	def __init__(self, randomReward = True, case1 = 0.25, case2 = 0.5, case3 = 0.5, case4 = 0.75):
		self.ai = sarsa.Sarsa(actions=["left", "right"], epsilon=0.1, alpha=0.1, gamma=0.9)
		self.lastAction = None
		self.lastBoardState = None
		self.currBoardState = 0 # there are three possible boards (states)
		self.currAction = None
		self.currReward = 0
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

	# so Gaussian random walk (I think) works like this:
	# get Gaussian noise
	# check if the addition of this noise to the current value 
	# 	will push it above or below the reflecting boundaries
	# if not, just add the noise and return the new value
	# otherwise,
	# if it will push it above, do stuff as below
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

	# this should return the current reward based on the 
	# action taken in the current state
	def calcReward(self, currState, currAction):
		if currState == 0:
			return 0
		currProb = random.random()	
		if currState == 1:
			if currAction == "left": # choose left (CASE 1)
				reward = 0 
				#print currProb, self.case1RewardProb
				if currProb > self.case1RewardProb:
					reward = 1
				return reward
			elif currAction == "right": # choose right (CASE 2)
				reward = 0 
				#print currProb, self.case2RewardProb
				if currProb > self.case2RewardProb:
					reward = 1
				return reward
			else:
				print "Something went very wrong with choosing the action: should be either left or right"
				return None
		if currState == 2:
			if currAction == "left": # choose left (CASE 3)
				reward = 0 
				#print currProb, self.case3RewardProb
				if currProb > self.case3RewardProb:
					reward = 1
				return reward
			elif currAction == "right": # choose right (CASE 4) 
				reward = 0 
				#print currProb, self.case4RewardProb
				if currProb > self.case4RewardProb:
					reward = 1
				return reward
			else:
				print "Something went very wrong with choosing the action: should be either left or right"
				return None

	def updateRewardProb(self):
		self.case1RewardProb = self.randomWalk(self.case1RewardProb)
		self.case2RewardProb = self.randomWalk(self.case2RewardProb)
		self.case3RewardProb = self.randomWalk(self.case3RewardProb)
		self.case4RewardProb = self.randomWalk(self.case4RewardProb)


	# calculates the next state probabilistically
	# may want to include some way to change these probabilities externally
	# the paper does say that this prob was fixed throughout the experiment
	def calcNextState(self, currState, currAction):
		nextState = 0
		if currState == 0:
			#print "here"
			if currAction == "left":
				state1Prob = random.random()
				if state1Prob > 0.3: # more likely to be state 1
					nextState = 1
				else:
					nextState = 2
			if currAction == "right":
				state1Prob = random.random()
				if state1Prob > 0.7: # more likely to be state 2
					nextState = 1
				else:
					nextState = 2
		return nextState

	def oneStep(self):
		currAction = self.ai.chooseAction(self.currBoardState)
		#print "action: ", currAction
		nextBoardState = self.calcNextState(self.currBoardState, currAction)
		#print nextBoardState
		self.currReward = self.calcReward(self.currBoardState, currAction)
		self.updateRewardProb()
		if self.lastAction != None:
			self.ai.learn(self.lastBoardState, self.lastAction, self.currReward, self.currBoardState, currAction)
		self.lastBoardState = self.currBoardState
		self.currBoardState = nextBoardState
		self.lastAction = currAction
		

if __name__ == '__main__':
	agent = Agent()

	#print "firstStageChoice secondStage secondStageChoice finalReward"
	firstStageChoice = None
	secondStage = None
	secondStageChoice = None
	finalReward = None
	for step in range(40000):
		agent.oneStep()
		#tempLastBoardState = agent.getLastBoardState()
		#tempLastAction = agent.getLastAction()
		#tempCurrReward = agent.getCurrReward()
		#tempCurrBoardState = agent.getCurrBoardState()
		if step%2 == 0: # in stage 1
			firstStageChoice = agent.getLastAction()
			secondStage = agent.getCurrBoardState()
			#print agent.getLastBoardState(), agent.getLastAction(), agent.getCurrReward(), agent.getCurrBoardState()
		else: # in stage 2
			secondStageChoice = agent.getLastAction()
			finalReward = agent.getCurrReward()
			print firstStageChoice, secondStage, secondStageChoice, finalReward
			#print "          ", agent.getLastBoardState(), agent.getLastAction(), agent.getCurrReward()



