import sys, os, mido, time, pickle

possible_backends = ['mido.backends.pygame', 'mido.backends.rtmidi', 'mido.backends.portmidi', 'mido.backends.rtmidi_python', 'mido.backends.amidi']
found_backend = False
for backend in possible_backends:
	try:
		mido.set_backend(backend)
		found_backend = True
		break
	except:
		pass
if not found_backend:
	print "Error: could not find valid backend for mido."
	exit(0)

def write_output(messages, times, output_file):
	"""Writes messages and times to a midi file."""
	ticks_per_second = 256
	tempo = mido.bpm2tempo(ticks_per_second)
	ticks = [int(mido.second2tick(time, ticks_per_second, tempo)) for time in times]
	with open(output_file, 'w') as f:
		mid = mido.MidiFile()
		track = mido.MidiTrack()
		mid.tracks.append(track)
		# track.append(mido.MetaMessage('set_tempo', tempo=tempo))
		last_tick = 0
		for (tick, message) in zip(ticks, messages):
			m = message.copy()
			m.time = tick-last_tick
			last_tick = tick
			track.append(m)
		mid.save(output_file)

class MidiReader():
	def __init__(self, midi_input='Digital Piano', midi_output='test.mid'):
		"""Determine input port/file and output file.

		Arguments:
		midi_input -- input filename or port name"""

		self.input = midi_input
		self.output = midi_output
		self.messages = []
		self.times = []

	def read(self):
		"""Record midi events until a keyboard interrupt."""
		inport = mido.open_input(self.input)
		start_time = time.time()
		try:
			for msg in inport:
				now = time.time()
				self.messages.append(msg)
				self.times.append(now-start_time)
		except KeyboardInterrupt:
			inport.close()
			self.write_output()

	def write_output(self):
		"""Write midi messages to a midi file."""
		write_output(self.messages, self.times, self.output)

if __name__=='__main__':
	reader = MidiReader()
	reader.read()