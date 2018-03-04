import mido, pickle, time
import numpy as np
from midi_read import MidiReader
from midi_constants import *
import note_processing, notes_io

def chord_match(chord1, chord2):
	notes1 = [n.note for n in chord1]
	notes2 = [n.note for n in chord2]
	return set(notes1)==set(notes2)

def unique(chords):
	unique_set = []
	for chord in chords:
		if not any([chord_match(chord, c) for c in unique_set]):
			unique_set.append(chord)
	return unique_set

def main(port_string):
	with open('data/chord_bank.pickle', 'r') as f:
		chords = unique(pickle.load(f))
	np.random.shuffle(chords)
	try:
		port = mido.open_ioport(port_string)
	except:
		print "'{}' is not a valid port. Please change the midi port.".format(port_string)
		exit(1)
	test = [chord for chord in chords if len(chord)==3]
	for chord in test:
		notes_io.play_chord(chord, port)
		user_chord = notes_io.read_chord(port)
		if chord_match(user_chord, chord):
			print "You got it right!"
		else:
			print "You missed this one. You played:"
			print note_processing.print_chord(user_chord)
			print "Here's the right answer:"
			print note_processing.print_chord(chord)
		time.sleep(3)

if __name__=='__main__':
	main('Digital Piano')