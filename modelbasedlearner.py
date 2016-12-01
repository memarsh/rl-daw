import random
import numpy as np

# This more or less reimplements the FORWARD learner described in
# Glascher et al. 2010

# states is a dictionary of the form:
# key: level
# value: list_of_states
# since level numbering will start at 1, len(states) = terminal_level
# and states[terminal_level] = all states that use the default action
# so actions doesn't include whatever brings us back to the root state
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
		self.epsilon = epsilon
		self.alpha = alpha # this is the same as 'eta' in Glascher et al. 2010
		self.gamma = gamma 
		self.actions = actions
    self.default_action = "whatever"
		self.states = states
    self.initializeTransitionProbabilities()

  #
  def initializeTransitionProbabilities(self):
    terminal_level = len(self.states)
    for level in self.states.keys():
      next_level = level+1
      if level == terminal_level:
        next_level = 1
        # I'm assuming I can safely assume that there will always be only one state in the first level!!!!!!!
        # This could be easily changed if this assumption ever turned out to be wrong...
        for state in self.states[level]:
          self.model_P[(state, self.default_action, self.states[next_level])] = 1.0
      else:
        for state in self.states[level]:
          num_next_states = len(self.states[next_level])
          for action in self.actions:
            for next_state in self.states[next_level]:
              self.model_P[(state, action, next_state)]=1.0/num_next_states

  # Okay, I'm going to decide that the code for a particular task is going to
  # keep track of which level it's on
  def updateTransitionProbabilites(self, state1, action, state2, state2_level):
    error = 1 - self.model_P(state1, action, state2)
    self.model_P(state1, action, state2) += self.alpha*error
    # now we have to reduce the probabilities of all states not arrived in
    for level_state in self.states[state2_level]:
      if level_state != state2:
        self.model_P(state1, action, level_state) *= (1-self.alpha)


	def getQ(self, state, action):
		return self.q.get((state,action),0.0)

  # calculates R + gamma*max_a(Q(S', a))
  # qnext = max_a(Q(S', a))
  def learn(self,state1,action1,reward,state2):
    qnext=self.getQ(state2,action2)
    self.learnQ(state1,action1,reward+self.gamma*qnext)

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

