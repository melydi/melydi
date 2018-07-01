import pickle
import numpy as np

def get_deltas(messages, times):
    note_on_events = [times[i] for i in range(len(times)) if messages[i].velocity>0]
    note_on_events = np.array(note_on_events)
    return note_on_events[1:]-note_on_events[:-1]

with open('data/single_line.pickle', 'r') as f:
    mr = pickle.load(f)
single_line_deltas = get_deltas(mr.messages, mr.times)
with open('data/double_line.pickle', 'r') as f:
    mr = pickle.load(f)
double_line_deltas = get_deltas(mr.messages, mr.times)

import matplotlib.pyplot as plt
import IPython as ipy
ipy.embed()
plt.hist(single_line_deltas, bins=80, label='single line')
plt.hist(double_line_deltas, bins=80, label='two lines')
plt.xlim([0, 0.3])
plt.legend()
plt.show()