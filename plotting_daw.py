import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


datafile = open("all_data.txt", "r").readlines()
all_data = np.zeros((4, len(datafile)))

for i, line in enumerate(datafile):
	total = line.split(" ")
	all_data[:,i] = total

df = pd.DataFrame(data=all_data)
sns.plot(data=df)
