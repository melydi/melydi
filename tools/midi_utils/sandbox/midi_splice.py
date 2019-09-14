"""Splice midi into tracks of single voices."""

import mido
from functools import reduce

fname = '/Users/rex/src/melydi/data/midifiles/goldberg.mid'

mid = mido.MidiFile(fname)

def iterate_messages(func, condition):
	results = []
	for track in mid.tracks:
		for msg in track:
			if condition(msg):
				results.append(func(msg))
	return results

# # filter out meta tracks (just midi messages without notes)
# tracks = [track for track in mid.tracks if not all([msg.is_meta for msg in track])]

# for i, track in enumerate(mid.tracks):
# 	print('Track {}, {} messages: {}'.format(i, len(track.name), track.name))
# 	# for msg in track:
# 		# if not msg.is_meta:
# 		# 	print(msg)

# # print out some meta messages ... maybe they have real data
# for track in mid.tracks:
# 	for msg in track:
# 		if msg.is_meta:
# 			import IPython as ipy
# 			ipy.embed()


# # looks like there is some important meta data there... building a table to analyze
# msg_dicts = []
# for track in mid.tracks:
# 	for msg in track:
# 		if msg.is_meta:
# 			msg_dicts.append(msg.dict())

# # get unique keys
# keys = set(reduce(lambda x, y: x+y, [list(msg_dict.keys()) for msg_dict in msg_dicts]))
# print(keys)

# # do the same for non-meta messsages...

# msg_dicts = []
# for track in mid.tracks:
# 	for msg in track:
# 		if not msg.is_meta:
# 			msg_dicts.append(msg.dict())
# keys = set(reduce(lambda x, y: x+y, [list(msg_dict.keys()) for msg_dict in msg_dicts]))
# print(keys)

# calculate the number of unique note messages
non_meta = iterate_messages(lambda msg: msg.dict(), lambda msg: not msg.is_meta)
# print(len(non_meta)) # 2214
notes = iterate_messages(lambda msg: msg.dict(), lambda msg: 'note' in msg.dict())
# print(len(notes)) # 2208

# # six non-meta messages are in notes... find them
# for msg in non_meta:
# 	if not (msg in notes):
# 		print(msg)
# # {'type': 'program_change', 'time': 0, 'program': 6, 'channel': 0}
# # {'type': 'control_change', 'time': 0, 'control': 7, 'value': 100, 'channel': 0}
# # {'type': 'control_change', 'time': 0, 'control': 10, 'value': 69, 'channel': 0}
# # {'type': 'program_change', 'time': 0, 'program': 6, 'channel': 1}
# # {'type': 'control_change', 'time': 0, 'control': 7, 'value': 100, 'channel': 1}
# # {'type': 'control_change', 'time': 0, 'control': 10, 'value': 59, 'channel': 1}

# # those are all program or control messages... looking at some meta messages to understand
meta = iterate_messages(lambda msg: msg.dict(), lambda msg: msg.is_meta)
# for msg in meta[:5]:
# 	print(msg)
# # {'type': 'track_name', 'name': 'untitled', 'time': 0}
# # {'type': 'smpte_offset', 'frame_rate': 25, 'hours': 32, 'minutes': 0, 'seconds': 3, 'frames': 0, 'sub_frames': 0, 'time': 0}
# # {'type': 'time_signature', 'numerator': 3, 'denominator': 4, 'clocks_per_click': 24, 'notated_32nd_notes_per_beat': 8, 'time': 0}
# # {'type': 'key_signature', 'key': 'G', 'time': 0}

# those are musical score markers

# # looking at some more...
# for msg in meta[-5:]:
# 	print(msg)
# # {'type': 'track_name', 'name': 'Original Filename: 988-v01.mid', 'time': 0}
# # {'type': 'end_of_track', 'time': 0}
# # {'type': 'midi_port', 'port': 0, 'time': 0}
# # {'type': 'track_name', 'name': 'Last Modified: September 3, 1997', 'time': 0}
# # {'type': 'end_of_track', 'time': 0}

# those are all annotations

# # how many unique note start events are there?
# note_on = []
# for msg in notes:
# 	if 'type' in msg:
# 		if msg['type']=='note_on':
# 			note_on.append(msg)
# print(len(note_on)) # 2208

# # There are 2208 note_on messages and 2208 messages with 'note' in the dictionary. Where are all the note_off messages? They must be encoded in another key... maybe velicyt?
# velocities = [msg['velocity'] for msg in notes]
# print(set(velocities))
# # {0, 100}

# It must be that '100' refers to note on and '0' refers to note off

# In order to parse these notes correctly, I want to understand the remaining keys:
# {'time', 'note', 'channel'}

print(set([note['time'] for note in notes]))
# {0, 480, 360, 240, 120, 1080}
print(set([note['note'] for note in notes]))
# {38, 40, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 86}
print(set([note['channel'] for note in notes]))
# {0, 1}

# Analysis from Claviatura reveals that channel 0 is the right hand, channel 1 the left hand.
# It also shows that the lowest note is D2, corresponding to '38' in this midi track

# From wikipedia: MIDI notes are numbered from 0 to 127 assigned to C-1 to G9.
# https://en.wikipedia.org/wiki/MIDI#Messages

# According to this convention, C2 would be 0+12*3 = 36, so D2 would be 38, aligning with wikipedia.

# In order to extract a single midi voice, one only needs to restrict midi reading to a single channel, assuming the midi file is formatted like 'goldberg.mid'!