import nengo
import numpy as np
import nengo.spa as spa
from nengolib.signal import z

import pytry
D=5
T_interval=0.3
choice_noise=0.05
alpha=0.3
N_state_action=700
n_intervals=10
direct=False
env_seed=2
rate=True
syn=0.005
N_product=1000
N_error=500
pes_rate = 1e-4
"""
class RLLearnProbTrial(pytry.NengoTrial):
    def params(self):
        self.param('dimensions', D=5)
        self.param('time interval', T_interval=0.5)
        self.param('softmax noise', choice_noise=0.05)
        self.param('learning rate', alpha = 0.3)
        self.param('neurons for state and action', N_state_action=500)
        self.param('intervals to run', n_intervals=10)
        self.param('run in direct mode', direct=False)
        self.param('random seed for environment', env_seed=2)
        self.param('run with rate neurons', rate=False)
        self.param('value to environment synapse length (isn\'t used in direct or rate mode)', syn=0.005)
        self.param('neurons for product network', N_product=200)
        self.param('neurons in error population', N_error=500)
"""
#def model(self, p):

vocab = spa.Vocabulary(D, randomize=False)
vocab.parse('S0+SA+SB+L+R')

class Environment(object):
    def __init__(self, vocab, seed):
        self.vocab = vocab
        self.state = 'S0'
        self.consider_action = 'L'
        self.q = np.zeros((3,2)) + np.inf  # we don't actually need Q(S0)!!
                                           # so maybe it could be removed?
        self.most_recent_action = 'L'
        self.values = np.zeros(2)
        self.value_wait_times = [T_interval/2, T_interval]
        self.intervals_count = 0
        self.rng = np.random.RandomState(seed=seed) # random number generator
        self.upper_boundary = 0.75
        self.lower_boundary = 0.25
        self.reward_prob = self.rng.uniform(self.lower_boundary, self.upper_boundary, size=(2,2)) 
        self.history = [] # history of actions chosen in state 0 and state seen as a result
        self.rewards = [] # history of rewards received in terminal states
        self.chosen_action = 'S0'

    # environment node function
    # passes appropriate information around at correct time intervals
    def node_function(self, t, value):
        if t >= self.value_wait_times[0]:
            self.values[0] = value
            self.value_wait_times[0] = (self.intervals_count+1.5)*T_interval
            self.consider_action = 'R'
        if t >= self.value_wait_times[1]:
            self.values[1] = value
            self.value_wait_times[1] = (self.intervals_count+2)*T_interval

            self.chosen_action = self.choose_action()
            self.intervals_count += 1
            self.consider_action = 'L'

        s = self.vocab.parse(self.state).v

        # replace infinities with 0
        q = np.max(np.where(self.q==np.inf, 0, self.q), axis=1)

        a = self.vocab.parse(self.consider_action).v
        chosen_a = self.vocab.parse(self.chosen_action).v
        return np.hstack([s, a, q, chosen_a]) 


    def choose_action(self):
        action='S0'
        if self.state == 'S0':
            chosen = self.softmax(self.values)
            if chosen == 0:
                action = 'L'
                if self.rng.rand()<0.7:
                    self.state = 'SA'
                else:
                    self.state = 'SB'
            else:
                action = 'R'
                if self.rng.rand()<0.7:
                    self.state = 'SB'
                else:
                    self.state = 'SA'

            self.history.append((chosen, self.state))
        else:
            q_index = 1 if self.state=='SA' else 2
            chosen = self.softmax(self.q[q_index])
            action = 'L' if chosen == 0 else 'R'
            pp = self.reward_prob[0 if self.state=='SA' else 1,
                                 chosen]
            reward = self.rng.rand() < pp 
            self.random_walk()
            
            q = self.q[q_index,chosen]
            if q == np.inf:  # check for first setting of value
                q = reward
            else:
                q = q + alpha * (reward-q)
            self.q[q_index, chosen] = q
            self.state = 'S0'
            self.rewards.append(reward)
        return action

    # for action selection
    def softmax(self, values):
        return np.argmax(values + self.rng.normal(size=values.shape)*choice_noise)
        #return np.argmax(values + np.random.normal(size=values.shape)*p.choice_noise)

    # change reward_prob using random walk
    # all reward probabilities should change at each step
    def random_walk(self):
        new_noise = self.rng.normal(size=self.reward_prob.shape)*0.025 # magic number SD defined in Daw et al. 2011
        for index, pp in np.ndenumerate(self.reward_prob):
            new_prob = pp+new_noise[index]
            if new_prob > self.upper_boundary or new_prob < self.lower_boundary:
                self.reward_prob[index] = pp-new_noise[index]
            else:
                self.reward_prob[index] = new_prob


env = Environment(vocab, seed=env_seed)

model = nengo.Network()
with model:
    cfg = nengo.Config(nengo.Ensemble, nengo.Connection)
    if direct:
        cfg[nengo.Ensemble].neuron_type = nengo.Direct()
        cfg[nengo.Connection].synapse = None
    elif rate:
        cfg[nengo.Ensemble].neuron_type = nengo.LIFRate()
        cfg[nengo.Connection].synapse = None#nengo.synapses.Lowpass(tau=0.0)
    with cfg:
        env_node = nengo.Node(env.node_function, size_in=1)

        # for plotting
        state_plot = nengo.Node(size_in=3)
        nengo.Connection(env_node[:D-2], state_plot)
        #action_plot = nengo.Node(size_in=2)
        #nengo.Connection(env_node[p.D+3:p.D*2], action_plot)
        
        # actually doing stuff
        state_and_action = nengo.Ensemble(n_neurons=N_state_action, dimensions=D*2)
        nengo.Connection(env_node[:D*2], state_and_action)

        prod = nengo.networks.Product(n_neurons=N_product, dimensions=D)
        transform = np.array([vocab.parse('S0').v,
                              vocab.parse('SA').v,
                              vocab.parse('SB').v,])
        nengo.Connection(env_node[-(D+3):-D], prod.A, transform=transform.T) #send Q-values to product network
        # yeah the above will only work for D=5
        
        def ideal_transition(x):
            sim_s = np.dot(x[:D], vocab.vectors)
            index_s = np.argmax(sim_s)
            s = vocab.keys[index_s]

            sim_a = np.dot(x[D:D*2], vocab.vectors)
            index_a = np.argmax(sim_a)
            a = vocab.keys[index_a]

            threshold = 0.1

            if sim_s[index_s]<threshold:
                return np.zeros(D)
            if sim_a[index_a]<threshold:
                return np.zeros(D)
            if s == 'S0':
                if a == 'L':
                    pp = [0,0.7,0.3]
                elif a == 'R':
                    pp = [0,0.3,0.7]
                else:
                    pp = [0,0,0]
            elif s == 'SA' or s=='SB':
                pp = [1,0,0]
            else:
                pp = [0,0,0]

            return np.dot(transform.T, pp)
            
        #nengo.Connection(state_and_action, prod.B, function=ideal_transition)
        
        def inhibit(t, x):
            error = x[:D]
            
            sim_a_considered = np.dot(x[D:D*2], vocab.vectors)
            index_a_considered = np.argmax(sim_a_considered)
            a_considered = vocab.keys[index_a_considered]
            
            sim_a_chosen = np.dot(x[-D:], vocab.vectors)
            index_a_chosen = np.argmax(sim_a_chosen)
            a_chosen = vocab.keys[index_a_chosen]
            
            if a_chosen == a_considered:
                return error
            else:
                return np.zeros(D)
                
        conn_error = nengo.Connection(state_and_action, prod.B, function=lambda x: [0]*D,
                        learning_rule_type=nengo.PES(learning_rate=pes_rate, pre_synapse=z**(-int(T_interval*1000))),)
                        
        inhib = nengo.Node(inhibit, size_in=D*3, size_out=D)
                        
        error = nengo.Ensemble(n_neurons=N_error, dimensions=D)
        #nengo.Connection(error, conn_error.learning_rule)
        nengo.Connection(error, inhib[:D])
        nengo.Connection(env_node[D:D*2], inhib[D:D*2]) # considered action to inhib
        nengo.Connection(env_node[-D:], inhib[-D:]) # chosen action to inhib
        nengo.Connection(inhib, conn_error.learning_rule)
        nengo.Connection(env_node[:D], error, transform=-1)
        nengo.Connection(prod.B, error, transform=1,
                        synapse=z**(-int(T_interval*1000)))

        if rate or direct:
            nengo.Connection(prod.output, env_node, transform=np.ones((1, D)), synapse=0)
        else:
            nengo.Connection(prod.output, env_node, transform=np.ones((1, D)), synapse=syn)
        # for plotting
        learned_value_plot = nengo.Node(size_in=1)
        nengo.Connection(prod.output, learned_value_plot, transform=np.ones((1, D)))
        actual_value_plot = nengo.Node(size_in=1)
        prod2 = nengo.networks.Product(n_neurons=N_product, dimensions=D)
        nengo.Connection(env_node[-(D+3):-D], prod2.A, transform=transform.T) # yeah this will only work for D=5
        nengo.Connection(state_and_action, prod2.B, function=ideal_transition)
        nengo.Connection(prod2.output, actual_value_plot, transform=np.ones((1, D)))
        state_to_error = nengo.Node(size_in=D)
        nengo.Connection(env_node[:D], state_to_error, transform=-1)
        predicted_state = nengo.Node(size_in=D)
        nengo.Connection(prod.B, predicted_state)#, synapse=z**(-int(T_interval*1000)))
        correct_pred_state = nengo.Node(size_in=D)
        nengo.Connection(prod2.B, correct_pred_state)
        # check if Q-values are same to both product networks
        q_prod = nengo.Node(size_in = D)
        nengo.Connection(prod.A, q_prod)
        q_prod2 = nengo.Node(size_in=D)
        nengo.Connection(prod2.A, q_prod2)
    
#self.env = env
#self.locals = locals()
#eturn model
"""
    def evaluate(self, p, sim, plt):
        sim.run(p.n_intervals * p.T_interval)
        history = self.env.history
        rewards = self.env.rewards
        rare = []
        for choice, state in history:
            r = (choice==0 and state=='SB') or (choice==1 and state=='SA')
            rare.append(r)

        stays = np.zeros((2,2), dtype=float)
        counts = np.zeros((2,2), dtype=float)
        for i in range(len(history)-1):
            stay = history[i][0] == history[i+1][0]
            stays[rare[i], rewards[i]] += stay
            counts[rare[i], rewards[i]] +=1
        stay_prob = stays/counts

        if plt:
            data = []
            d = {}
            for r in [0,1]:
                d['rare'] = r
                for rewarded in [0,1]:
                    d['rewarded'] = rewarded
                    for i in range(int(stays[r, rewarded])):
                        d['stay'] = 1
                        data.append(dict(d))
                    for i in range(int(counts[r, rewarded] - stays[r, rewarded])):
                        d['stay'] = 0
                        data.append(dict(d))
            import pandas
            df = pandas.DataFrame(data)
            import seaborn
            seaborn.barplot('rewarded', 'stay', hue='rare', order=[1, 0], data=df)


        return dict(
                history=history,
                rewards=rewards,
                stay_prob=stay_prob,
                )

"""
#if __name__ == '__builtin__':
#    rl = RLLearnProbTrial()
#    model = rl.make_model(T_interval=0.3, rate=True)
#    for k, v in rl.locals.items():
#        locals()[k] = v
