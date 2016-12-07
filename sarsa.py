import random

# taken directly from Terry's RL tutorial
# comments try to connect this to Sarsa algorithm in Sutton & Barto, 2013

class Sarsa:
    def __init__(self,actions,epsilon=0.1,alpha=0.2,gamma=0.9):
        self.q={} # this is a dictionary of the form: 
                # key: (state, action)
                # value: q_value 

        self.epsilon=epsilon # this is the same as 'tau' in Glascher et al. 2010 (I think?)
        self.alpha=alpha # learning rate
        self.gamma=gamma # future discounting
        self.actions=actions

    def getQ(self,state,action):
        # returns the value with a default of 0.0 rather than None
        return self.q.get((state,action),0.0)

    # value = R + gamma*Q(S', A')
    # oldv = Q(S, A)
    def learnQ(self,state,action,value):
        oldv=self.q.get((state,action),None)
        if oldv==None:
            self.q[(state,action)]=value
        else:
            # Q(S, A) <- Q(S, A) + alpha*(value-oldv) 
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

    # not sure why this has been broken into two functions
    # calculates R + gamma*Q(S', A')
    # qnext = Q(S', A')
    def learn(self,state1,action1,reward,state2,action2):
        qnext=self.getQ(state2,action2)
        self.learnQ(state1,action1,reward+self.gamma*qnext)




