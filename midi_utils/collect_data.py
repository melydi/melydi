import pickle
from midi_read import MidiReader

raw_input("Play a single-voice melody at a range of speeds.")
mr = MidiReader()
mr.read()
with open('data/single_line.pickle','w') as f:
	pickle.dump(mr, f)

raw_input("Play a double-voice melody at a range of speeds.")
mr = MidiReader()
mr.read()
with open('data/double_line.pickle','w') as f:
	pickle.dump(mr, f)