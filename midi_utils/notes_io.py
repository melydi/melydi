import mido, pickle, time, os
import numpy as np
from midi_read import MidiReader
from midi_constants import *
import note_processing

def play_chord(chord, ioport):
	ioport.reset()
	off_events = [mido.Message('note_off', note=note.note) for note in chord]
	for note in chord:
		ioport.send(note)
	time.sleep(3)
	for note_off in off_events:
		ioport.send(note_off)

def read_chord(ioport):
	# flush the port
	while ioport.poll():
		pass
	chord = []
	for msg in ioport:
		if not chord:
			chord_start = time.time()
		delta_t = time.time()-chord_start
		if delta_t>DELTA_T_MAX:
			break
		else:
			chord.append(msg)
	return chord

def debug_io(port_string):
	try:
		port = mido.open_ioport(port_string)
	except:
		print("'{}' is not a valid port. Please change the midi port.".format(port_string))
		exit(1)
	while True:
		print("Please play a chord.")
		chord = read_chord(port)
		print("Your chord:")
		note_processing.print_chord(chord)
		print("Num notes:")
		print(len(chord))


def save_chords_interactively(port_string, save_file):
	try:
		port = mido.open_ioport(port_string)
	except:
		print("'{}' is not a valid port. Please change the midi port.".format(port_string))
		exit(1)
	try:
		chords = []
		while True:
			print("Please play a chord.")
			chord = read_chord(port)
			print("Your chord:")
			note_processing.print_chord(chord)
			print("Num notes:")
			print(len(chord))
			answer = raw_input("Save? ([Y]/n)")
			if not answer or answer.lower=='y':
				chords.append(chord)
	except KeyboardInterrupt:
		try:
			if os.path.isfile(save_file):
				with open(save_file, 'r') as f:
					previous_data = pickle.load(f)
			else:
				previous_data = []
			with open(save_file, 'w') as f:
				pickle.dump(previous_data+chords, f)
		except Exception as e: # debugging
			import IPython as ipy
			ipy.embed()

def print_chords_file(save_file):
	with open(save_file, 'r') as f:
		chords = pickle.load(f)
	for chord in chords:
		note_processing.print_chord(chord)

if __name__=='__main__':
	import sys
	debug_io(' '.join(sys.argv[1:]))
	# save_chords_interactively('Digital Piano', 'data/chord_bank.pickle')
	# print "Printing chords file:"
	# print_chords_file('data/chord_bank.pickle')
