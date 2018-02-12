import pygame, pygame.midi, sys

def convert_pitch(midi_pitch):
	offset = 21
	letter_names = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
	octave = (midi_pitch-offset)//12
	letter_name = letter_names[(midi_pitch-offset)-octave*12]
	return octave, letter_name

class MidiEvent():
	type_dict = {144:'note', 176:'pedal'}

	def __init__(self, input_data):
		self.type = self.type_dict[input_data[0][0]]
		self.data = input_data[0]
		self.time = input_data[1]

class Note:
	letter_names = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

	def __init__(self, octave, letter_name):
		self.octave = octave
		self.letter_name = letter_name

	def __eq__(self, other):
		return self.octave==other.octave and self.letter_name==other.letter_name

	def __lt__(self, other):
		if self.octave<other.octave:
			return True
		elif self.octave>other.octave:
			return False
		else:
			return self.letter_names.index(self.letter_name)<self.letter_names.index(other.letter_name)

	def __le__(self, other):
		return self<other or self==other

	def __gt__(self, other):
		return not self<=other

	def __ge__(self, other):
		return self>other or self==other

class NoteEvent(MidiEvent):
	def __init__(self, input_data):
		MidiEvent.__init__(self, input_data)
		self.velocity = self.data[2]
		self.note = Note(*convert_pitch(self.data[1]))

class PedalEvent(MidiEvent):
	def __init__(self, input_data):
		self.depth = self.data[2]

class Chord:
	def __init__(self, note_events):
		self.time = sum([note_event.time for note_event in note_events])/float(len(note_events))
		self.notes = [note_event.note for note_event in note_events]

	def order(self):
		self.notes = sorted(self.notes)

class MidiEventParser():
	def __init__(self, filename):
		with open(filename, 'r') as f:
			lines = f.readlines()
		self.events = []
		for line in lines:
			event_data = eval(line)
			event = MidiEvent(event_data)
			if event.type == 'note':
				self.events.append(event)
		self.index = 0

	def __iter__(self):
		return self

	def next(self):
		if self.index==len(self.events):
			raise StopIteration
		else:
			event = self.events[self.index]
			tick = event.time
			velocity = event.data[2]
			octave, letter_name = convert_pitch(event.data[1])
			pitch = letter_name+'_'+str(octave)
			self.index += 1
			return tick, velocity, pitch

class MidiChordsParser():
	def __init__(self, filename):
		with open(filename, 'r') as f:
			lines = f.readlines()
		self.note_events = []
		for line in lines:
			event_data = eval(line)
			t = MidiEvent(event_data).type
			if t=='note':
				self.note_events.append(NoteEvent(event_data))
		self.index = 0
		self.num_notes = len(self.note_events)

	def __iter__(self):
		return self

	def next(self):
		chord = self.find_next_chord()
		chord.order()
		if not chord:
			raise StopIteration
		else:
			return chord

	def find_next_chord(self):
		curr_time = self.note_events[self.index].time
		new_i = self.index+1
		# chord mush be a combination of notes within 600 ms of each other
		while new_i<self.num_notes and self.note_events[new_i].time<curr_time+600:
			new_i += 1
		notes = [self.note_events[i] for i in range(self.index, new_i)]
		self.index = new_i
		return Chord(notes)

def write_midi_events(in_file, out_file):
		with open(in_file, 'r') as f:
			lines = f.readlines()
		events = []
		for line in lines:
			events.append(eval(line))
		pygame.midi.init()
		pygame.midi.Output.

if __name__=='__main__':
	parser = MidiChordsParser(sys.argv[1])
	parser.next()
	import IPython as ipy
	ipy.embed()