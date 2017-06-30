# This is not a real python file! I just wanted to take advantage of syntax highlighting

# looking at influence of time intervals
pytry-many sqsub -o pytry1.log -r22h pytry rl_trial.py --env_seed [1:6] --n_intervals 20000 --direct [False~True] --T_interval [0.1~0.2~0.3] --verbose False
pytry-many sqsub -o pytry3.log -r22h pytry rl_trial.py --env_seed [6:11] --n_intervals 20000 --direct [False~True] --T_interval [0.1~0.2~0.3] --verbose False
# what we learned from this:
# time intervals of 0.2 and 0.3 look pretty much like pure model-based behaviour
# 0.1 seems to have the opposite effect to that of the original paper: 
# the middle two bars are different in the opposite way (left shorter than right)

pytry-many sqsub -o pytry2.log -r22h pytry rl_trial.py --env_seed [1:11] --n_intervals 20000 --direct [False~True] --T_interval [0.4~0.5] --verbose False
# what we learned from this:
# these time intervals also have the opposite effect

# more exploration of time interval effect
pytry-many sqsub -o pytry4.log -r22h pytry rl_trial.py --env_seed [1:11] --n_intervals 20000 --direct [False~True] --T_interval [0.05~0.45~0.6] --verbose False
# what we learned from this:
# T_interval==0.05 reproduces the effect from the original paper
# and apparently T_interval==0.45 does too
# and apparently T_interval==0.6 does too
# so why doesn't T_interval==0.5 work????

# test if nengo seed has an influence (keeping environment seed constant)
pytry-many sqsub -o pytry5.log -r22h pytry rl_trial.py --seed [1:11] --n_intervals 20000 --direct [False~True] --T_interval [0.1~0.3~0.5] --verbose False
# what we learned from this: 
# in direct mode, the seed makes no difference
# with regular neurons, the seed makes a HUGE difference 
# (looking at plots individually, some have the 'right' effect, others have the opposite, some look like pure model-based; 
# combined, it looks like pure model-based but with huge confidence intervals)

# looking at different seeds on the time intervals that 'worked'
pytry-many sqsub -o pytry6.log -r22h pytry rl_trial.py --seed [2:11] --n_intervals 20000 --T_interval [0.05~0.45~0.6] --verbose False
# what we learned from this:
# averaging over nengo seeds produces more-or-less model-based behaviour (large-ish confidence intervals)

# trying to find different 'working time intervals'
pytry-many sqsub -o pytry7.log -r22h pytry rl_trial.py --env_seed [1:11] --n_intervals 20000 --T_interval [0.04~0.09~0.41~0.49~0.51] --verbose False
# what we learned from this:

# Changing the neuron seed seems to have the largest effect, producing the most variability
# So why would changing the time interval have such an effect when the neuron seed is held constant? 
# In other words, why would certain neuron distributions be so sensitive to particular time intervals?

# varying env_seed and seed while keeping time interval constant (logs 8 and 9 used the wrong number of intervals - oops)
pytry-many sqsub -o pytry10.log -r22h pytry rl_trial.py --env_seed [3:11] --seed [2:11] --T_interval 0.05 --n_intervals 20000 --verbose False
pytry-many sqsub -o pytry11.log -r22h pytry rl_trial.py --env_seed 1 --seed [2:11] --T_interval 0.05 --n_intervals 20000 --verbose False

# looking at different numbers of neurons for state-action representation with rate neurons
pytry-many sqsub -o fast0.log -r22h pytry rl_fast_trial.py --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action [50~100~200~300~400~500] --rate True --n_intervals 20000 --verbose False
# 100 neurons is the fewest that worked in this set

# I guess I'll look at learning rate 
pytry-many sqsub -o fast1.log -r3h pytry rl_fast_trial.py --alpha [0.05~0.1~0.2~0.4] --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action 100 --rate True --n_intervals 20000 --verbose False
# As learning rate increases, the separation between outside and inside bars increases (outside get higher, inside lower)
# However, they aren't significantly different until alpha=0.2 or higher

# Let's see if this trend continues
pytry-many sqsub -o fast2.log -r3h pytry rl_fast_trial.py --alpha [0.5~0.6~0.7~0.8~0.9~1.0] --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action 100 --rate True --n_intervals 20000 --verbose False
# yep, it does, and with remarkably small confidence intervals, too
# So when alpha=1, there is basically no memory in learning the values of the terminal states,
# the value is just set to the immediate reward.
# What?

# does this break anything?
pytry-many sqsub -o fast3.log -r3h pytry rl_fast_trial.py --alpha [1.1~1.2~1.3] --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action 100 --rate True --n_intervals 20000 --verbose False
# huh, rewarded bars start going down as alpha increases, unrewarded don't seem to change
# this is very odd: if rewarded, the Q-value should just stay at 1, thus the rewarded common stay probability should increase, but instead it's decreasing?
# oh wait, if what was normally rewarded (previously q=1) is *not*, the new q would be -0.3 (if alpha is 1.3)
# and if it's rewarded again after, the new q=1.39, and the q-values are just going to keep getting more positive and more negative from there
# but then how does this influence the stay probability? 

# test if this trend happens in direct mode (oops, didn't have to test across nengo seeds)
pytry-many sqsub -o fast4.log -r1h pytry rl_fast_trial.py --alpha [0.05~0.1~0.2~0.3~0.4~0.5~0.6~0.7~0.8~0.9~1.0] --direct True --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action 100 --n_intervals 20000 --verbose False
# okay, same trend

# when I test with the original python code, all bars decrease as alpha increases

# check other numbers of neurons
pytry-many sqsub -o fast5.log -r1h pytry rl_fast_trial.py --alpha [0.05~0.1~0.2~0.3~0.4~0.5~0.6~0.7~0.8~0.9~1.0] --rate True --env_seed 1 --seed [1:11] --T_interval 0.002 --N_state_action [50~200~300~400~500] --n_intervals 20000 --verbose False
# when alpha is 0.5 or greater, even 50 neurons is enough to produce 'significantly' model-based behaviour
# there's something about 300 neurons that seems to produce very small confidence intervals...cd

# maybe I should try higher numbers of neurons, since the original model had 750?


# different time intervals with rate neurons
pytry-many sqsub -o fast6.log -r1h pytry rl_fast_trial.py --alpha [0.05~0.1~0.3~0.5~0.7~0.9~1.0] --rate True --env_seed 1 --seed [1:21] --T_interval [0.004~0.05~0.1] --N_state_action [50~100~300~500] --n_intervals 20000 --verbose False
# pretty sure all of these completed successfully
# Ah, I did this wrong. To see the difference of time intervals, I need to keep the nengo seed constant and vary environment seed and time interval, like this:
pytry-many sqsub -o fast7.log -r1h pytry rl_fast_trial.py --rate True --env_seed [1:21] --T_interval [0.004~0.05~0.1~0.2~0.4] --N_state_action 100 --n_intervals 20000 --verbose False
# oops, I think some of these will time out, try again:
pytry-many sqsub -o fast8.log -r4h pytry rl_fast_trial.py --rate True --env_seed [1:21] --T_interval [0.2~0.4] --N_state_action 100 --n_intervals 20000 --verbose False


# more runs with refactored model (spiking) and fewer neurons
pytry-many sqsub -o pytry12.log -r22h pytry rl_trial.py --seed [11:21]  --n_intervals 20000 --T_interval [0.05~0.1~0.5] --N_state_action [20~50~70~100~200~500] --verbose False
pytry-many sqsub -o pytry13.log -r22h pytry rl_trial.py --seed [1:11] --n_intervals 20000 --T_interval [0.05~0.1~0.5] --N_state_action [20~50~70~100~200] --verbose False
# oh right, I forgot that there was something about 300 neurons that made the confidence intervals really small...
# in general, though, decreasing the number of neurons seems to have a similar effect to decreasing alpha: outside bars shrink and inside bars grow 

# sanity check for alpha effect
pytry-many sqsub -o pytry14.log -r22h pytry rl_trial.py --seed [1:21] --n_intervals 20000 --T_interval 0.05 --alpha [0.05~0.1~0.3~0.5~0.7~1.0] --verbose False
# okay, it still does the same thing as the rate neurons, thank goodness

# more environment seed runs for different seeds giving different results
pytry-many sqsub -o pytry14.log -r22h pytry rl_trial.py --env_seed [11:21] --seed [1:21] --T_interval [0.05~0.1] --n_intervals 20000 --verbose False


pytry-many sqsub -o pytry15.log -r22h pytry rl_trial.py --env_seed [11:21] --n_intervals 20000 --T_interval [0.2~0.5~0.51] --verbose False


# synapse length and increasing num neuron tests:
pytry-many sqsub -o syn0.log -r3d pytry rl_synapse_trial.py  --env_seed [1:21] --seed [1:21] --T_interval 0.05 --N_state_action [100~500~750~1000] --N_product [100~200~300~500~750~1000] --syn [0.005~0.01~0.017~0.025] --n_intervals 20000 --verbose False
# okay yeah so this was way too many jobs

pytry-many sqsub -o syn01.log -r3d pytry rl_synapse_trial.py  --env_seed 21 --seed [1:10] --T_interval 0.05 --N_state_action [100~500~750~1000] --N_product [100~200~300~500~750~1000] --syn [0.005~0.01~0.017~0.025] --n_intervals 20000 --verbose False

pytry-many sqsub -o syn21.log -r3d pytry rl_synapse_trial.py  --env_seed 21 --seed [10:22] --T_interval 0.05 --N_state_action [100~500~750~1000] --N_product [100~200~300~500~750~1000] --syn [0.005~0.01~0.017~0.025] --n_intervals 20000 --verbose False
# syn=0.01 seems to produce more human-like data

pytry-many sqsub -o syn41.log -r3d pytry rl_synapse_trial.py  --env_seed 22 --seed [1:21] --T_interval [0.05~0.1~0.2] --N_product [200~300~500~1000] --syn [0.001~0.005~0.01~0.017~0.025~0.049] --n_intervals 20000 --verbose False
# in a rather counterintuitive turn of events, syn=0.001 and T_interval=0.2 produces almost human-like data, but only when N_product is high enough

pytry-many sqsub -o syn42.log -r3d pytry rl_synapse_trial.py  --env_seed 22 --seed [1:21] --T_interval [0.3~0.5] --N_product [200~1000] --syn [0~0.001~0.003~0.005~0.025] --n_intervals 20000 --verbose False
# not particularly interesting

pytry-many sqsub -o syn43.log -r3d pytry rl_synapse_trial.py  --env_seed 23 --seed [1:21] --T_interval [0.05~0.1~0.2] --N_product [200~1000] --syn [0~0.003] --n_intervals 20000 --verbose False


pytry-many sqsub -o syn44.log -r3d pytry rl_synapse_trial.py  --env_seed 23 --seed [1:21] --T_interval [0.01~0.007~0.02] --n_intervals 20000 --verbose False

pytry-many sqsub -o syn45.log -r1d pytry rl_synapse_trial.py  --env_seed 23 --seed [1:21] --T_interval 0.03 --n_intervals 20000 --verbose False

pytry-many sqsub -o syn47.log -r3d pytry rl_synapse_trial.py --env_seed 23 --seed [1:21] --T_interval [0.3~0.5] --n_intervals 20000 --verbose False --syn [0.01~0.017~0.049]

pytry-many sqsub -o syn48.log -r3d pytry rl_synapse_trial.py --env_seed 23 --seed [1:21] --T_interval 0.51 --n_intervals 20000 --verbose False --syn [0~0.001~0.003~0.01~0.017~0.025~0.049~0.1]
pytry-many sqsub -o syn49.log -r3d pytry rl_synapse_trial.py --env_seed 23 --seed [1:21] --T_interval 0.5 --n_intervals 20000 --verbose False --syn 0.1



####
# Learning model testing commands
####

# learning rate
# (environment seed default is now 1 because that makes so much more sense, really)
pytry-many sqsub -o learn0.log -r3d pytry rl_learnprob_trial.py --alpha [0.05~0.1~0.2~0.3~0.4~0.5~0.6~0.7~0.8~0.9~1.0] --seed [1:21] --T_interval [0.05~0.3~0.5] --n_intervals 20000 --verbose False
# since some of these didn't run:
pytry-many sqsub -o learn1.log -r5d pytry rl_learnprob_trial.py --alpha [0.05~0.1~0.2~0.3~0.4~0.5~0.6~0.7] --seed [1:21] --T_interval [0.05~0.3~0.5] --n_intervals 20000 --verbose False
pytry-many sqsub -o learn2.log -r3d pytry rl_learnprob_trial.py --alpha 0.8 --seed [1:18] --T_interval 0.05 --n_intervals 20000 --verbose False
pytry-many sqsub -o learn3.log -r5d pytry rl_learnprob_trial.py --alpha [0.8~0.9~1.0] --seed [1:21] --T_interval [0.3~0.5] --n_intervals 20000 --verbose False
pytry-many sqsub -o learn4.log -r3d pytry rl_learnprob_trial.py --alpha 1.0 --seed 5 --T_interval 0.05 --n_intervals 20000 --verbose False


####
# Learning model takes way too long to simulate long intervals, so learnset can be told how long to learn for
# Hopefully this takes less time
####

pytry-many sqsub -o set0.log -r3d pytry rl_learnset_trial.py --seed [1:21] --T_interval [0.05~0.3~0.5] --learn_intervals [100~500~1000~2000~5000] --n_intervals 20000 --verbose False
# sqsub seems to be having problems, so some of these jobs may not have been submitted, grrrr
# it kinda seems like none of these ran

# From now on, time interval should be the first parameter set on sharcnet, to make killing jobs easier
# also I only have to run seeds [1:20] - scratch that - [1:10] and then see what I need to run more of

# on own computer
pytry rl_learnpast_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval 0.1 --seed 1
# this looks a lot more like human data than the learn_future (original) version, but perhaps the number of intervals and time interval should match better
# even with this smaller amount of trials, the original model still looks purely model-based with tiny error bars

pytry rl_learnpast_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.05 --seed 1
# this is a non significant mess (though closest to a model-based trend) (around 0.8 probability)

# perhaps a longer time interval would help
pytry rl_learnpast_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.3 --seed 1
# this is an even worse non significant mess (though still closest to model-based trend) (around 0.55 probability)

# checking if it's a magical time interval, but I think it has more to do with the number of trials, but just in case:
pytry rl_learnpast_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --seed 1
# maybe this time interval is magical, because this looks like significantly model-based behaviour, though the error bars are a bit bigger than the original model

# then I should quickly check the number of trials (hopefully this runs quickly)
pytry rl_learnpast_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval 0.05 --seed 1
# this is kinda messy, not quite significantly model-based, humanish if you squint

# maybe I should try a time interval of 0.2
pytry rl_learnpast_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval 0.2 --seed 1
# looks human like with 10 seeds! and 20 seeds!

pytry rl_learnpast_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval 0.15 --seed 1
# this is probably the most convincingly human yet! (with 10 seeds) (a little worse with 20 seeds)

pytry rl_learnpast_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.15 --seed 1
# Not quite as good as the previous one

pytry rl_learnpast_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval 0.25 --seed 1
# ugh. non-significant mess

pytry rl_learnset_trial.py --learn_intervals 10000 --n_intervals 10000 --T_interval [0.1~0.15~0.2~0.4~0.6] --seed 1
# These all look pretty much the same: model-based
# there does seems to be a very slight downward trend of the outside bars as the time interval increases


pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval [0.01~0.03~0.05~0.1~0.2~0.4] --seed 1

pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.05 --N_state_action 20 --seed 1

pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 1

pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 11
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 12
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 13
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 14
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 15
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 16
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 18
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 19
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.05 --seed 20



pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 1
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 2
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 3
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 4
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 5
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 6
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 7
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 8
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 9
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 1
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 2
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 3
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 4
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 5
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 6
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 7
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 8
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 9
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 10

# only run second half of this block for 500 neurons!!!!!!!!!!!!! DONE I think
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 1
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 2
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 3
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 4
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 5
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 6
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 7
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 8
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 9
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 11
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 12
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 13
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 14
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 15
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 16
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 18
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 19
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 20 --seed 20

# DONE
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 100 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 300 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 100 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 200 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 500 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 10 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 10 --seed 10

# DONE
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 1000 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 1000 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 100 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 300 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 750 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 500 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 750 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 500 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 70 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 50 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 20 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 50 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 20 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 10 --seed 10


# DONE
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 10 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 11 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 12 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 13 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 14 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 15 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 16 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 17 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 18 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 19 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 20 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 2 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 3 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 4 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 5 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 6 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 7 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 8 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 9 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 70 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 50 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 20 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 100 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 200 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 300 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 400 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 70 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 5 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.1 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.2 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.4 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.5 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.6 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.7 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.8 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 0.9 --seed 17
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --alpha 1.0 --seed 17

#DONE
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 10 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_product 10 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 10 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 20 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 70 --N_error 50 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.01 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.02 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.03 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.04 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.05 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.05 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.2 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.4 --seed 20


#running
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 10 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 11 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 12 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 13 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 14 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 15 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 16 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 17 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 18 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 19 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 20 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 2 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 3 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 4 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 5 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 6 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 7 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 8 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --N_state_action 50 --N_product 70 --N_error 50 --env_seed 9 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 10 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 11 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 12 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 13 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 14 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 15 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 16 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 17 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 18 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 19 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 20 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 2 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 3 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 4 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 5 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 6 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 7 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 8 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 9 --seed 20
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 10 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 11 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 12 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 13 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 14 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 15 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 16 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 17 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 18 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 19 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 20 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 2 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 3 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 4 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 5 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 6 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 7 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 8 --seed 10
pytry rl_learnset_trial.py --learn_intervals 20000 --n_intervals 20000 --T_interval 0.1 --env_seed 9 --seed 10

# Other things to look at:
# softmax choice noise (seems like it should have predictable effect) - but maybe I should check it anyway
# number of time intervals? 

#######
# old model testing commands
#######

sqsub -o old00.log -r5d python gather_nengo_data.py --seed 13 --t_interval 0.5 --valtoenv
sqsub -o old01.log -r5d python gather_nengo_data.py --seed 13 --t_interval 0.5 --synapse 0.005
sqsub -o old02.log -r5d python gather_nengo_data.py --seed 13 --t_interval 0.5 --valtoenv --synapse 0.005
sqsub -o old03.log -r5d python gather_nengo_data.py --seed 13 --t_interval 0.5 --synapse 0.025
# I'm anticipating these will run out of time too, so running these as well:
sqsub -o old050.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '0'
sqsub -o old051.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '1'
sqsub -o old052.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '2'
sqsub -o old053.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '3'
sqsub -o old054.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '4'
sqsub -o old055.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '5'
sqsub -o old056.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '6'
sqsub -o old057.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '7'
sqsub -o old058.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '8'
sqsub -o old059.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '9'
sqsub -o old060.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '0' --valtoenv
sqsub -o old061.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '1' --valtoenv
sqsub -o old062.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '2' --valtoenv
sqsub -o old063.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '3' --valtoenv
sqsub -o old064.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '4' --valtoenv
sqsub -o old065.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '5' --valtoenv
sqsub -o old066.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '6' --valtoenv
sqsub -o old067.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '7' --valtoenv
sqsub -o old068.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '8' --valtoenv
sqsub -o old069.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '9' --valtoenv
sqsub -o old070.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '0' --synapse 0.005
sqsub -o old071.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '1' --synapse 0.005
sqsub -o old072.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '2' --synapse 0.005
sqsub -o old073.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '3' --synapse 0.005
sqsub -o old074.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '4' --synapse 0.005
sqsub -o old075.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '5' --synapse 0.005
sqsub -o old076.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '6' --synapse 0.005
sqsub -o old077.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '7' --synapse 0.005
sqsub -o old078.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '8' --synapse 0.005
sqsub -o old079.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '9' --synapse 0.005
sqsub -o old080.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '0' --valtoenv --synapse 0.005
sqsub -o old081.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '1' --valtoenv --synapse 0.005
sqsub -o old082.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '2' --valtoenv --synapse 0.005
sqsub -o old083.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '3' --valtoenv --synapse 0.005
sqsub -o old084.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '4' --valtoenv --synapse 0.005
sqsub -o old085.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '5' --valtoenv --synapse 0.005
sqsub -o old086.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '6' --valtoenv --synapse 0.005
sqsub -o old087.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '7' --valtoenv --synapse 0.005
sqsub -o old088.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '8' --valtoenv --synapse 0.005
sqsub -o old089.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '9' --valtoenv --synapse 0.005
sqsub -o old090.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '0' --synapse 0.025
sqsub -o old091.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '1' --synapse 0.025
sqsub -o old092.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '2' --synapse 0.025
sqsub -o old093.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '3' --synapse 0.025
sqsub -o old094.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '4' --synapse 0.025
sqsub -o old095.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '5' --synapse 0.025
sqsub -o old096.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '6' --synapse 0.025
sqsub -o old097.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '7' --synapse 0.025
sqsub -o old098.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '8' --synapse 0.025
sqsub -o old099.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.5 --runs 1 --label '9' --synapse 0.025


sqsub -o old04.log -r4d python gather_nengo_data.py --seed 13 --t_interval 0.3 
sqsub -o old05.log -r4d python gather_nengo_data.py --seed 13 --t_interval 0.3 --valtoenv
sqsub -o old06.log -r4d python gather_nengo_data.py --seed 13 --t_interval 0.3 --synapse 0.005
sqsub -o old07.log -r4d python gather_nengo_data.py --seed 13 --t_interval 0.3 --valtoenv --synapse 0.005
sqsub -o old08.log -r4d python gather_nengo_data.py --seed 13 --t_interval 0.3 --synapse 0.025
# These all timed out, so instead will try running:
sqsub -o old000.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '0'
sqsub -o old001.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '1'
sqsub -o old002.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '2'
sqsub -o old003.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '3'
sqsub -o old004.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '4'
sqsub -o old005.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '5'
sqsub -o old006.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '6'
sqsub -o old007.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '7'
sqsub -o old008.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '8'
sqsub -o old009.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '9'
sqsub -o old010.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '0' --valtoenv
sqsub -o old011.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '1' --valtoenv
sqsub -o old012.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '2' --valtoenv
sqsub -o old013.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '3' --valtoenv
sqsub -o old014.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '4' --valtoenv
sqsub -o old015.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '5' --valtoenv
sqsub -o old016.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '6' --valtoenv
sqsub -o old017.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '7' --valtoenv
sqsub -o old018.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '8' --valtoenv
sqsub -o old019.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '9' --valtoenv
sqsub -o old020.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '0' --synapse 0.005
sqsub -o old021.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '1' --synapse 0.005
sqsub -o old022.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '2' --synapse 0.005
sqsub -o old023.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '3' --synapse 0.005
sqsub -o old024.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '4' --synapse 0.005
sqsub -o old025.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '5' --synapse 0.005
sqsub -o old026.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '6' --synapse 0.005
sqsub -o old027.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '7' --synapse 0.005
sqsub -o old028.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '8' --synapse 0.005
sqsub -o old029.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '9' --synapse 0.005
sqsub -o old030.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '0' --valtoenv --synapse 0.005
sqsub -o old031.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '1' --valtoenv --synapse 0.005
sqsub -o old032.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '2' --valtoenv --synapse 0.005
sqsub -o old033.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '3' --valtoenv --synapse 0.005
sqsub -o old034.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '4' --valtoenv --synapse 0.005
sqsub -o old035.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '5' --valtoenv --synapse 0.005
sqsub -o old036.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '6' --valtoenv --synapse 0.005
sqsub -o old037.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '7' --valtoenv --synapse 0.005
sqsub -o old038.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '8' --valtoenv --synapse 0.005
sqsub -o old039.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '9' --valtoenv --synapse 0.005
sqsub -o old040.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '0' --synapse 0.025
sqsub -o old041.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '1' --synapse 0.025
sqsub -o old042.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '2' --synapse 0.025
sqsub -o old043.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '3' --synapse 0.025
sqsub -o old044.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '4' --synapse 0.025
sqsub -o old045.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '5' --synapse 0.025
sqsub -o old046.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '6' --synapse 0.025
sqsub -o old047.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '7' --synapse 0.025
sqsub -o old048.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '8' --synapse 0.025
sqsub -o old049.log -r4d python gather_nengo_data_2.py --seed 13 --t_interval 0.3 --runs 1 --label '9' --synapse 0.025 



# This all ran as expected
sqsub -o old09.log -r3d python gather_nengo_data.py --seed 13 --t_interval 0.1 
sqsub -o old14.log -r3d python gather_nengo_data.py --seed 13 --t_interval 0.1 --valtoenv
sqsub -o old11.log -r3d python gather_nengo_data.py --seed 13 --t_interval 0.1 --synapse 0.005
sqsub -o old15.log -r3d python gather_nengo_data.py --seed 13 --t_interval 0.1 --valtoenv --synapse 0.005
sqsub -o old13.log -r3d python gather_nengo_data.py --seed 13 --t_interval 0.1 --synapse 0.025
