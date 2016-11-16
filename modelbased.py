import random



class ModelBased:
	def __init__(self, actions, states, epsilon=0.1, alpha=0.2, gamma=0.9):
		self.q={} # this is a dictionary of the form: 
              	# key: (state, action)
              	# value: q_value 
		self.model_P = {} # this is a dictionary of the form:
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
    maxqnew=max([self.getQ(state2,a) for a in self.actions])
    self.learnQ(state1,action1,reward+self.gamma*maxqnew)

  # update the model?
  def updateModelProbabilities(self, state1, action, state2):
    # default 1.0 because if we've only seen it once, we think 
    # this transition is 100% likely
    oldp = self.model_P.get((state1, action, state2), 1.0)
    self.model_P[(state1, action, state2)]=oldp

	

