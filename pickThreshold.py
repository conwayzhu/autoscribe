import numpy as np
import pickle 
from scipy.signal import argrelextrema
import math
from copy import deepcopy
sr = 11025
window_size = 0.050
songdir = "./maps/songs/"
duration = 30.0

def load_GT(abbrev): 
	f = open(songdir + 'MAPS_MUS-alb_' + abbrev + '_SptkBGCl.txt', 'rb')
	lines = f.readlines()[1:]
	GT = {}
	num_timesets = 0  
	for row in lines:
		row = row.decode().strip('\r\n')
		row = row.split('\t')
		note = row[2]
		start = row[0]
		end = row[1]
		if float(start) > duration:
			break
		else:        
			if note in GT:
				GT[note].append([start, end])
			else:
				GT[note] = [[start, end]]
			num_timesets += 1
	return GT, num_timesets
def load_activations(abbrev): 
    with open('maps_results_' + abbrev + '.pkl','rb') as Y:
        Y1 = pickle.load(Y)
    return Y1

def reset_threshold(Y, threshold):
    lmaxes = np.asarray([])
    for row in Y:
        relex = argrelextrema(row,np.greater)[0]
        lmaxes = np.concatenate((lmaxes,row[relex]))

    p75,p25 = np.percentile(lmaxes, [75,25])
    threshold1 = p75 + threshold*(p75-p25)

    # new array of only below threshold
    lowvals = Y < threshold1
    Y[lowvals] = 0
    return Y

def calculation(Y, GT, num_timesets):
    # vars intialization for parsing the 50ms windows
    window_size = 0.05
    start = 0
    l = int(sr*window_size)
    end = l
    window = 0

    # 2D array that represents onsets
    onsets = np.zeros((88,int(duration/0.05)))
    # highest and lowest note (for plotting purposes)
    highnote = 0
    lownote = 100
    total = 0
    correct = 0
    poped = 0
    GT_cpy = deepcopy(GT)
    
    for i in range(int(duration/window_size)):
        row = Y[start:end,:]
        #print(row.shape)
        sumrow = np.sum(row,axis=0)
        relex = argrelextrema(sumrow,np.greater)[0]
        if(len(relex) != 0):
            # time index that the note occurs
            high = np.amax(relex)
            low = np.amin(relex)
            if high > highnote:
                highnote = high
            if low < lownote:
                lownote = low
            tindex = window
            onsets[relex,tindex] = 1
            t = window_size * window

            for note in relex:
                note += 21
                total += 1
                if str(note) in GT:
                    time_ranges = GT[str(note)]
                    for time_range in time_ranges:
                        s = float(time_range[0])
                        e = float(time_range[1])
                        if t < s - window_size:
                            break
                        elif t >= s - window_size and t <= e + window_size:
                            correct += 1
                            break

                if str(note) in GT_cpy:
                    time_ranges = deepcopy(GT_cpy[str(note)]) 
                    for i in range(len(time_ranges)):
                        s = float(time_ranges[i][0])                   
                        e = float(time_ranges[i][1])
                        if t < s - window_size:
                            break
                        elif t >= s - window_size and t <= e + window_size:
                            time_ranges.pop(i)
                            GT_cpy[str(note)] = time_ranges
                            poped += 1
                            break
        start = end
        end += l
        window+=1


    precision = float(correct) / total
    print ("Correct percentage is: " + str(precision))

    recall = float(poped) / num_timesets
    print ("Detected percentage is: " + str(recall))

    f1 = 2 * ((precision * recall) / (precision + recall))
    print ("f1 is: " + str(f1))
    return f1

threshold_lst = [6,7,8,9, 10,11, 12,13, 14,15, 16]
abbrev_lst = ["esp2", "esp5", "esp6"]
best_multiplier = 0
best_mean = 0
fmeasure_lst = {'esp2': [], 'esp5': [], 'esp6': []}

for multiplier in threshold_lst:
    fmeasure = []
    for abbrev in abbrev_lst:
        GT, num_timesets = load_GT(abbrev)
        Y = load_activations(abbrev)
        Y = reset_threshold(Y, multiplier)
        f1 = calculation(Y, GT, num_timesets)
        fmeasure_lst[abbrev].append(f1)
        fmeasure.append(f1)
    mean = sum(fmeasure) / 3.0
    if mean > best_mean:
        best_mean = mean
        best_multiplier = multiplier
print ("The best threshold is achieve using the multiplier of: " + str(best_multiplier))
print ("with mean of f1 " + str(best_mean))
print (fmeasure_lst)

