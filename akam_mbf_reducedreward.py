import random
import modelbasedforward as mb

# Uses the Q-update strategy found in Daw et al. 2011 supplemental materials
# Implements part of the reduced task in Akam et al. 2015
# i.e., simplified reward probabilities
# actions in the same stage 2 state have the same reward probability

class Agent():
    # rewardSwitch tells how many trials to go before switching the reward probabilities
    def __init__(self, rewardSwitch=50):
        state_dict = {1:[0], 2:[1, 2]}
        transition_dict = {(0, "left", 1):0.7,
                            (0, "left", 2):0.3,
                            (0, "right", 1):0.3,
                            (0, "right", 2):0.7,
                            (1, "left", 0):1.0,
                            (1, "right", 0):1.0,
                            (2, "left", 0):1.0,
                            (2, "right", 0):1.0}
        self.ai = mb.ModelBasedForward(actions=["left", "right"], states = state_dict, transitions=transition_dict)
        self.lastAction = None
        self.lastState = None
        self.numLevels = len(state_dict)
        self.firstLevel = 1
        self.currBoardState = 0
        self.lastBoardState = None
        self.currLevel = 1
        self.currAction = None
        self.pastReward = 0
        self.currReward = 0
        self.lowProb = 0.2
        self.highProb = 0.8
        self.rewardProb = [self.lowProb, self.lowProb, self.highProb, self.highProb]
        self.numSteps = 0
        self.rewardSwitch = rewardSwitch

    def getLastBoardState(self):
        return self.lastBoardState

    def getCurrBoardState(self):
        return self.currBoardState

    def getLastAction(self):
        return self.lastAction

    def getCurrReward(self):
        return self.currReward

    def switchReward(self):
        if self.rewardProb[0] == self.lowProb:
            self.rewardProb = [self.highProb, self.highProb, self.lowProb, self.lowProb]
        elif self.rewardProb[0] == self.highProb:
            self.rewardProb = [self.lowProb, self.lowProb, self.highProb, self.highProb]

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
                if currProb > self.rewardProb[0]:
                    reward = 1
                return reward
            elif currAction == "right": # choose right (CASE 2)
                reward = 0 
                #print currProb, self.case2RewardProb
                if currProb > self.rewardProb[1]:
                    reward = 1
                return reward
            else:
                print "Something went very wrong with choosing the action: should be either left or right"
                return None
        if currState == 2:
            if currAction == "left": # choose left (CASE 3)
                reward = 0 
                #print currProb, self.case3RewardProb
                if currProb > self.rewardProb[2]:
                    reward = 1
                return reward
            elif currAction == "right": # choose right (CASE 4) 
                reward = 0 
                #print currProb, self.case4RewardProb
                if currProb > self.rewardProb[3]:
                    reward = 1
                return reward
            else:
                print "Something went very wrong with choosing the action: should be either left or right"
                return None


    # calculates the next state probabilistically
    # (may want to include some way to change these probabilities externally)
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

    def calcNextLevel(self):
        if self.currLevel == self.numLevels:
            return self.firstLevel
        else:
            return self.currLevel + 1

    def oneStep(self):
        #print ""
        #print "debug:"
        #print "    ", self.lastBoardState, self.lastAction, self.currBoardState, self.currLevel
        currAction = self.ai.chooseAction(self.currBoardState)
        #print "  and the current action is", currAction
        nextBoardState = self.calcNextState(self.currBoardState, currAction)
        self.currReward = self.calcReward(self.currBoardState, currAction)
        if self.numSteps%self.rewardSwitch == 0:
            self.switchReward()
        self.numSteps += 1
        
        if self.lastAction != None:
            #print "  learning is happening"
            #print self.ai.getQ(self.lastBoardState, self.lastAction)
            if self.ai.learn(self.lastBoardState, self.lastAction, self.pastReward, self.currBoardState, self.currLevel) == None:
                return None
        # more bookkeeping
        self.lastBoardState = self.currBoardState
        self.currBoardState = nextBoardState
        self.currLevel = self.calcNextLevel()
        self.pastReward = self.currReward
        self.lastAction = currAction
        return 1    

if __name__ == '__main__':
    agent = Agent()

    #print "firstStageChoice secondStage secondStageChoice finalReward"
    firstStageChoice = None
    secondStage = None
    secondStageChoice = None
    finalReward = None
    for step in range(20000): # Repeat (for each step of episode):
        if agent.oneStep() == None:
            print "oneStep broke"
            break
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

    