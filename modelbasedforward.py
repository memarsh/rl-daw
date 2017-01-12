import random
import numpy as np

# This one is given the transition probabilities up front, 
# it doesn't learn them

class ModelBased:
    def __init__(self, actions, states, transitions, epsilon=0.1, alpha=0.3, gamma=0.5):
        self.q={} # this is a dictionary of the form: 
                # key: (state, action)
                # value: q_value 
        self.model_P = transitions # this is a dictionary of the form:
                    # key: (state, action)
                    # value: [state0_count, state1_count, state2_count]
        # may not need this, if we just use the actual reward that was received 
        self.model_R = {} # this is a dictionary of the form:
            # key: (state, action)
            # value: reward
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions
        self.states = states
        self.prev = None

    def getQ(self, state, action):
        return self.q.get((state,action),0.0)

    # value = R + gamma*Q(S', A')
    # oldv = Q(S, A)
    def learnQ(self, state, action, value):
        oldv = self.q.get((state, action), None)
        if oldv == None:
            self.q[(state,action)]=value
        else:
            self.q[(state,action)]=oldv+self.alpha*(value-oldv)
            #print (state, action), ':', oldv, '->', value
    

    # calculates R + gamma*max_a(Q(S', a))
    # qnext = max_a(Q(S', a))
    def learn(self, state1, action, reward, state2, state2_level):

        if state1 == 0:
            assert reward==0

        if state2 not in self.states[state2_level]:
            print "State " + str(state2) + " is not in level " + str(state2_level)
            return None
        qnext = self.calc_value(state1, action, state2_level)
        self.learnQ(state1, action, reward+self.gamma*qnext)
        if state2_level == 2:
            self.prev = state1, action, reward, state2, state2_level
        elif state2_level == 1:
            if self.prev != None:
                #print '----->',
                self.learn(*self.prev)    
                pass

                #state1, action, reward, state2, state2_level = self.prev 
                #action2 = 'right' if action == 'left' else 'left'
                #self.learn(state1, action2, reward, state2, state2_level)    
        return 1

    # this will be replaced by the neural part eventually
    # state2_level could be replaced by just all the states
    def calc_value(self, state1, action, state2_level):
        value = 0
        for state2 in self.states[state2_level]:
            next_action = self.max_action(state2)
            temp_value = self.model_P[(state1, action, state2)] * self.getQ(state2, next_action)
            value += temp_value
        return value

    # Choose A from S using policy derived from Q 
    def chooseAction(self,state):
        #if random.random()<self.epsilon:
        #    return random.choice(self.actions)
        #else:
        #    return self.max_action(state)

            noise = 0.05
            q=[self.getQ(state,a)+random.normalvariate(0, noise) for a in self.actions]
            i=q.index(max(q))
            action=self.actions[i]
            return action

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

    










    # update the model?
    # this is not the best way to do this, but it's a place to start
    #def updateModelProbabilities(self, state1, action, state2):
    # default 1.0 because if we've only seen it once, we think 
    # this transition is 100% likely
    #    oldp = self.model_P.get((state1, action), [0, 0, 0])
    #    oldp[state2] += 1
    #    self.model_P[(state1, action)]=oldp

    # basically, I'm treating the state transition probability
    # as the proportion of transitions to state2 (given the action)
    # to the total number of transitions from state1 (given the action)
    #def getStateProbability(self, state1, action, state2):
    #    counts = self.model_P.get((state1, action), [0, 0, 0])
    #    total = sum(counts)
    #    prob = 0
    #    if total > 0:
    #        prob = counts[state2]/total
    #    return prob
