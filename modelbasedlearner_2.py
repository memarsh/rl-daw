import random

# This one does not deal with "reward states" as separate terminal states

# states is a dictionary of the form:
# key: level (integers starting from 1)
# value: list_of_states
# since level numbering will start at 1, len(states) = terminal_level
class ModelBasedLearner:
    def __init__(self, actions, states, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q={} # this is a dictionary of the form: 
                    # key: (state, action)
                    # value: q_value 
        self.model_P = {} # this is a dictionary of the form:
                        # key: (state, action, next_state)
                        # value: probability
        # may not need this, if we just use the actual reward that was received 
        self.model_R = {} # this is a dictionary of the form:
                # key: (state, action)
                # value: reward
        self.epsilon = epsilon # this is the same as 'tau' in Glascher et al. 2010 (I think?)
        self.alpha = alpha # this is the same as 'eta' in Glascher et al. 2010
        self.gamma = gamma 
        self.actions = actions
        #self.default_action = "whatever"
        self.states = states
        self.terminal_level = len(self.states)
        self.initializeTransitionProbabilities()

    #
    def initializeTransitionProbabilities(self):
        for level in self.states.keys():
            next_level = level+1
            if level == self.terminal_level:
                next_level = 1
                # I'm assuming I can safely assume that there will always be only one state in the first level!!!!!!!
                # This could be easily changed if this assumption ever turned out to be wrong...
                for state in self.states[level]:
                    for action in self.actions:
                        for next_state in self.states[next_level]:
                            self.model_P[(state, action, next_state)] = 1.0
            else:
                for state in self.states[level]:
                    num_next_states = len(self.states[next_level])
                    for action in self.actions:
                        for next_state in self.states[next_level]:
                            self.model_P[(state, action, next_state)]=1.0/num_next_states

    # Okay, I'm going to decide that the code for a particular task is going to
    # keep track of which level it's on
    def updateTransitionProbabilites(self, state1, action, state2, state2_level):
        error = 1 - self.model_P[(state1, action, state2)]
        self.model_P[(state1, action, state2)] += self.alpha*error
        # now we have to reduce the probabilities of all states not arrived in
        for level_state in self.states[state2_level]:
            if level_state != state2:
                self.model_P[(state1, action, level_state)] *= (1-self.alpha)


    def getQ(self, state, action):
        return self.q.get((state,action),0.0)

    # I think we're recomputing Q each time, not updating it 
    def learnQ(self, state, action, reward, value):
        oldv = self.q.get((state, action), None)
        if oldv==None:
            self.q[(state, action)]=value
        else:
            self.q[(state, action)]=oldv+self.alpha*(value-oldv)

    # this will be replaced by the neural part eventually
    # state2_level could be replaced by just all the states
    def calc_value(self, state1, action, state2_level):
        value = 0
        for state2 in self.states[state2_level]:
            next_action = self.max_action(state2)
            temp_value = self.model_P[(state1, action, state2)] * self.getQ(state2, next_action)
            value += temp_value
        return value

    # This function updates both the Q-values and the P_probabilities
    # uses a Sarsa-like update, in that the action in s' is what action was actually taken
    # (not the argmax of the policy)
    def learn(self, state1, action, reward, state2, state2_level):
        if state2 not in self.states[state2_level]:
            print "State " + str(state2) + " is not in level " + str(state2_level)
            return None
        self.updateTransitionProbabilites(state1, action, state2, state2_level)
        qnext = self.calc_value(state1, action, state2_level)
        self.learnQ(state1, action, state2_level, reward+self.gamma*qnext)
        return 1

    # Choose A from S using policy derived from Q 
    def chooseAction(self,state):
        if random.random()<self.epsilon:
            return random.choice(self.actions)
            #print "           random"
            #print "          ", type(action)
        else:
            #print "           max"
            return self.max_action(state)
            #print "          ", type(action)
   	    #return action

    def max_action(self, state):
        q=[self.getQ(state,a) for a in self.actions]
        maxQ=max(q)
        count=q.count(maxQ)
        if count>1:
            best=[i for i in range(len(self.actions)) if q[i]==maxQ]
            i=random.choice(best)
        else:
            i=q.index(maxQ)
        action=self.actions[i]
        return action
