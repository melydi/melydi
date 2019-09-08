"""Splice midi into tracks of single voices."""

import mido

fname = '/Users/rex/src/melydi/data/midifiles/goldberg.mid'

mid = mido.MidiFile(fname)

# filter out meta tracks (just midi messages without notes)
# tracks = [track for track in mid.tracks if not all([msg.is_meta for msg in track])]

for i, track in enumerate(mid.tracks):
	print('Track {}, {} messages: {}'.format(i, len(track.name), track.name))
	# for msg in track:
		# if not msg.is_meta:
		# 	print(msg)