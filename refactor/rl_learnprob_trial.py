import nengo
import numpy as np
import nengo.spa as spa
from nengolib.signal import z

import pytry

class RLLearnProbTrial(pytry.NengoTrial):
    def params(self):
        self.param('dimensions', D=5)
        self.param('time interval', T_interval=0.5)
        self.param('softmax noise', choice_noise=0.05)
        self.param('learning rate', alpha = 0.3)
        self.param('neurons for state and action', N_state_action=500)
        self.param('intervals to run', n_intervals=10)
        self.param('run in direct mode', direct=False)
        self.param('random seed for environment', env_seed=1)
        self.param('run with rate neurons', rate=False)
        self.param('value to environment synapse length (isn\'t used in direct or rate mode)', syn=0.005)
        self.param('neurons for product network', N_product=200)
        self.param('neurons in error population', N_error=500)
        self.param('learning rate for PES learning rule', pes_rate=1e-4)

    def model(self, p):

        vocab = spa.Vocabulary(p.D, randomize=False)
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
                self.value_wait_times = [p.T_interval/2, p.T_interval]
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
                chosen = self.chosen_action
                if t >= self.value_wait_times[0]:
                    self.values[0] = value
                    self.value_wait_times[0] = (self.intervals_count+1.5)*p.T_interval
                    self.consider_action = 'R'
                if t >= self.value_wait_times[1]:
                    self.values[1] = value
                    self.value_wait_times[1] = (self.intervals_count+2)*p.T_interval

                    self.chosen_action = self.choose_action()
                    self.intervals_count += 1
                    self.consider_action = 'L'

                s = self.vocab.parse(self.state).v

                # replace infinities with 0
                q = np.max(np.where(self.q==np.inf, 0, self.q), axis=1)

                a = self.vocab.parse(self.consider_action).v
                #self.chosen_action = chosen
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
                        q = q + p.alpha * (reward-q)
                    self.q[q_index, chosen] = q
                    self.state = 'S0'
                    self.rewards.append(reward)
                return action

            # for action selection
            def softmax(self, values):
                return np.argmax(values + self.rng.normal(size=values.shape)*p.choice_noise)
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


        env = Environment(vocab, seed=p.env_seed)

        model = nengo.Network()
        with model:
            cfg = nengo.Config(nengo.Ensemble, nengo.Connection)
            if p.direct:
                cfg[nengo.Ensemble].neuron_type = nengo.Direct()
                cfg[nengo.Connection].synapse = None
            elif p.rate:
                cfg[nengo.Ensemble].neuron_type = nengo.LIFRate()
                cfg[nengo.Connection].synapse = None#nengo.synapses.Lowpass(tau=0.0)
            with cfg:
                env_node = nengo.Node(env.node_function, size_in=1)
    
                # for plotting
                state_plot = nengo.Node(size_in=3)
                nengo.Connection(env_node[:p.D-2], state_plot)
                #action_plot = nengo.Node(size_in=2)
                #nengo.Connection(env_node[p.D+3:p.D*2], action_plot)
                
                # actually doing stuff
                state_and_action = nengo.Ensemble(n_neurons=p.N_state_action, dimensions=p.D*2)
                nengo.Connection(env_node[:p.D*2], state_and_action)
    
                prod = nengo.networks.Product(n_neurons=p.N_product, dimensions=p.D)
                transform = np.array([vocab.parse('S0').v,
                                      vocab.parse('SA').v,
                                      vocab.parse('SB').v,])
                #nengo.Connection(env_node[-3:], prod.A, transform=transform.T) #send Q-values to product network
                nengo.Connection(env_node[-(p.D+3) :-p.D], prod.A, transform=transform.T) #send Q-values to product network
                # yeah the above will only work for D=5
    
                def ideal_transition(x):
                    sim_s = np.dot(x[:p.D], vocab.vectors)
                    index_s = np.argmax(sim_s)
                    s = vocab.keys[index_s]
    
                    #sim_a = np.dot(x[p.D:], vocab.vectors) # this is probably wrong in the original refactored code, but it doesn't seem to have any impact on performance?
                    sim_a = np.dot(x[p.D:p.D*2], vocab.vectors)
                    index_a = np.argmax(sim_a)
                    a = vocab.keys[index_a]
    
                    threshold = 0.1
    
                    if sim_s[index_s]<threshold:
                        return np.zeros(p.D)
                    if sim_a[index_a]<threshold:
                        return np.zeros(p.D)
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
                    error = x[:p.D]
                    
                    sim_a_considered = np.dot(x[p.D:p.D*2], vocab.vectors)
                    index_a_considered = np.argmax(sim_a_considered)
                    a_considered = vocab.keys[index_a_considered]
                    
                    sim_a_chosen = np.dot(x[-p.D:], vocab.vectors)
                    index_a_chosen = np.argmax(sim_a_chosen)
                    a_chosen = vocab.keys[index_a_chosen]
                    
                    if a_chosen == a_considered:
                        return error
                    else:
                        return np.zeros(p.D)
                    
    
                conn_error = nengo.Connection(state_and_action, prod.B, function=lambda x: [0]*p.D,
                                learning_rule_type=nengo.PES(learning_rate = p.pes_rate, pre_synapse=z**(-int(p.T_interval*1000))),)
                
                inhib = nengo.Node(inhibit, size_in=p.D*3, size_out=p.D)
                                
                error = nengo.Ensemble(n_neurons=p.N_error, dimensions=p.D)
                #nengo.Connection(error, conn_error.learning_rule)
                nengo.Connection(error, inhib[:p.D])
                nengo.Connection(env_node[p.D:p.D*2], inhib[p.D:p.D*2]) # considered action to inhib
                nengo.Connection(env_node[-5:], inhib[-5:]) # chosen action to inhib
                nengo.Connection(inhib, conn_error.learning_rule)
                nengo.Connection(env_node[:p.D], error, transform=-1)
                nengo.Connection(prod.B, error, transform=1,
                                synapse=z**(-int(p.T_interval*1000)))
    
                if p.rate or p.direct:
                    nengo.Connection(prod.output, env_node, transform=np.ones((1, p.D)), synapse=0)
                else:
                    nengo.Connection(prod.output, env_node, transform=np.ones((1, p.D)), synapse=p.syn)
                # for plotting
                learned_value_plot = nengo.Node(size_in=1)
                nengo.Connection(prod.output, learned_value_plot, transform=np.ones((1, p.D)))
                #actual_value_plot = nengo.Node(size_in=1)
                #prod2 = nengo.networks.Product(n_neurons=p.N_product, dimensions=p.D)
                #nengo.Connection(env_node[-(p.D+3):-p.D], prod2.A, transform=transform.T)# yeah this will only work for D=5
                #nengo.Connection(state_and_action, prod2.B, function=ideal_transition)
                #nengo.Connection(prod2.output, actual_value_plot, transform=np.ones((1, p.D)))
                state_to_error = nengo.Node(size_in=5)
                nengo.Connection(env_node[:p.D], state_to_error, transform=-1)
                predicted_state = nengo.Node(size_in=5)
                nengo.Connection(prod.B, predicted_state)#, synapse=z**(-int(p.T_interval*1000)))
                #correct_pred_state = nengo.Node(size_in=5)
                #nengo.Connection(prod2.B, correct_pred_state)
                considered_action = nengo.Node(size_in=5)
                nengo.Connection(env_node[p.D:p.D*2], considered_action)
                current_action = nengo.Node(size_in=5)
                nengo.Connection(env_node[-p.D:], current_action)
                q_prod = nengo.Node(size_in = p.D)
                nengo.Connection(prod.A, q_prod)
            
        self.env = env
        self.locals = locals()
        return model

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


if __name__ == '__builtin__':
    rl = RLLearnProbTrial()
    model = rl.make_model(T_interval=0.3, rate=False, N_state_action=500, N_product=200)
    for k, v in rl.locals.items():
        locals()[k] = v
