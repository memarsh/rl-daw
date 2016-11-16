import random

class DynaQ:
	def __init__(self, actions, states, epsilon=0.1, alpha=0.2, gamma=0.9):
		self.q={} # this is a dictionary of the form: 
              	# key: (state, action)
              	# value: q_value 
		self.model = {} # this is a dictionary of the form:
						# key: (state, action) 		   ????????????????????
						# value: (reward, next_state)  ????????????????????
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
  # Model(S, A) <- R, S' (but this task doesn't actually have deterministic states)

	

