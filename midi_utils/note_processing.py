import mido, pickle, time
import numpy as np
from midi_read import MidiReader
from midi_constants import *

def convert_pitch(midi_pitch):
    octave = (midi_pitch-MIDI_OFFSET)//12
    letter_name = LETTER_NAMES[(midi_pitch-MIDI_OFFSET)-octave*12]
    return octave, letter_name

def is_note_on(message):
    return message.velocity>0

def get_note_on_events(messages, times):
    note_on_indices = [i for i in range(len(times)) if is_note_on(messages[i])]
    return zip(*[(messages[i], times[i]) for i in note_on_indices])

def get_chords(messages, times):
    m, t = get_note_on_events(messages, times)
    t = np.array(t)
    diffs = t[1:]-t[:-1]
    simultaneous = diffs<DELTA_T_MAX
    chord_start_indices = [i for i in range(1, len(simultaneous)) if (simultaneous[i] and not simultaneous[i-1])]
    chords = []
    for start in chord_start_indices:
        chord = []
        i = 0
        while simultaneous[start+i]:
            chord.append(m[start+i])
            i += 1
            if start+i>=len(simultaneous):
                break
        chord.append(m[start+i])
        chords.append(chord)
    return chords

def print_chord(chord):
    notes = [convert_pitch(note) for note in sorted([n.note for n in chord])]
    print (', '.join([note[1]+str(note[0]) for note in notes]))
