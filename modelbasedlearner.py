import random
import numpy as np

# This more or less reimplements the FORWARD learner described in
# Glascher et al. 2010

# transition_list should be a list of tuples where each tuple is of the form
# (first_state, possible_action, possible_second_state, number_of_states_on_second_level)

# states should be all non-terminal states (I guess?)
# terminal_states are states where action doesn't need to be selected, just for giving reward
class ModelBasedLearner:
	def __init__(self, actions, states, terminal_states, transition_list, epsilon=0.1, alpha=0.2, gamma=0.9):
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
		self.epsilon = epsilon
		self.alpha = alpha # this is the same as 'eta' in Glascher et al. 2010
		self.gamma = gamma 
		self.actions = actions
    self.default_action = "whatever"
		self.states = states
    self.terminal_states = terminal_states
    self.transitions = transition_list
    self.initializeTransitionProbabilities()

  def initializeTransitionProbabilities(self):
    for transition in self.transitions:
      state1, action, state2, num_states = transition
      self.model_P[(state1, action, state2)] = 1.0/num_states

  def updateTransitionProbabilites(self, state1, action, state2):
    


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

	# Choose A from S using policy derived from Q 
  def chooseAction(self,state):

   	if random.random()<self.epsilon:
     	action=random.choice(self.actions)
   	else:
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

  # calculates R + gamma*max_a(Q(S', a))
  # qnext = max_a(Q(S', a))
	def learn(self,state1,action1,reward,state2):
    qnext=self.getQ(state2,action2)
    self.learnQ(state1,action1,reward+self.gamma*qnext)

  # update the model?
  # this is not the best way to do this, but it's a place to start
  def updateModelProbabilities(self, state1, action, state2):
    oldp = self.model_P.get((state1, action), [0, 0, 0])
    oldp[state2] += 1
    self.model_P[(state1, action)]=oldp

  # basically, I'm treating the state transition probability
  # as the proportion of transitions to state2 (given the action)
  # to the total number of transitions from state1 (given the action)
  def getStateProbability(self, state1, action, state2):
    counts = self.model_P.get((state1, action), [0, 0, 0])
    total = sum(counts)
    prob = 0
    if total > 0:
      prob = counts[state2]/total
    return prob

  def planWithModel(self, n):
    for i in range(n):
      state, action = random.choice(list(self.model_P.keys()))



	

