import midi
from midi_parse import MidiEventParser

def write_midi_from_log(input_filename, output_filename):
	pattern = midi.Pattern()
	started = False
	for (tick, velocity, pitch) in MidiEventParser(input_filename):
		if not started:
			started = True
			first = tick
		new_tick = tick-first
		if not velocity:
			event = midi.NoteOffEvent(tick=new_tick, pitch=eval('midi.{}'.format(pitch)))
		else:
			pattern = midi.Pattern()
			event = midi.NoteOnEvent(tick=new_tick, velocity=velocity, pitch=eval('midi.{}'.format(pitch)))
		track.append(event)
		pattern.append(track)
	midi.write_midifile(output_filename, pattern)

if __name__=='__main__':
	import sys
	input_filename = sys.argv[1]
	output_filename = sys.argv[2]
	write_midi_from_log(input_filename, output_filename)