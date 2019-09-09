import argparse

import numpy as np
from magenta.common import tf_utils
from magenta.music import audio_io
import magenta.music as mm
from magenta.music import midi_io
from magenta.music import sequences_lib
from sklearn.cluster import KMeans
from collections import defaultdict

MIDI_OFFSET = 21
MIDI_LETTER_NAMES = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

def extract_deltas(note_seq, num_notes):
  """
    Args:
      note_seq: NoteSequence input
      num_notes: Number of notes in the note sequence to consider from beginning

    Returns:
      List of time deltas between notes.
  """
  times = [note.start_time for note in note_seq.notes[:num_notes]]
  times = sorted(times)
  deltas = [times[i+1]-times[i] for i in range(len(times)-1)]
  return deltas

def find_largest_cluster_mean(cluster_to_deltas, cluster_to_size, n_clusters):
  """
  Find the largest cluster, which should correspond to the most frequent note
  value

  Args:
    cluster_to_deltas: maps cluster index to list of deltas in that cluster
    cluster_to_size: maps cluster index to cluster size
    n_clusters: number of clusters

  Returns:
    Mean of cluster values as a float.

  """
  max_cl = 0
  max_size = 0
  for cl in range(0, n_clusters):
    if cluster_to_size[cl] > max_size:
      max_cl = cl
      max_size = cluster_to_size[cl]
  cl_mean = np.mean(cluster_to_deltas[max_cl])
  return cl_mean
  
def find_note_lengths(note_seq, num_notes, n_diff_lengths=4):
  """
  Args:
    note_seq: NoteSequence input
    num_notes: Number of notes in the NoteSequence to consider from beginning
    n_diff_lengths: How many different notelengths to cluster into

  Returns:
    List of note_lengths expressed as ints.
  """
  deltas = np.array(extract_deltas(note_seq, num_notes))
  kmeans = KMeans(n_clusters=n_diff_lengths, random_state=0).fit(np.array(deltas).reshape(-1, 1))
  cluster_to_deltas = defaultdict(list)
  cluster_to_size = defaultdict(int)
  for i in range(len(deltas)):
    cl = kmeans.labels_[i]
    cluster_to_deltas[cl].append(deltas[i])
    cluster_to_size[cl] += 1
  unit_len = find_largest_cluster_mean(cluster_to_deltas, cluster_to_size, n_diff_lengths)
  note_lengths = []
  
  for d in deltas:
    ratio = d/float(unit_len)
    note_length = np.round(ratio * 2)
    note_lengths.append(int(note_length))
  note_lengths.append(2)
  
  return note_lengths


def convert_pitch(midi_pitch):
  """
  Converts midi pitch to letter names with octaves for lilypond.

  Args:
    midi_pitch: the pitch of a note in midi, expressed as an int
  
  Returns:
    Octave and letter name tuple
  """
  offset = 21
  letter_names = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
  octave = (midi_pitch-offset)//12
  letter_name = letter_names[(midi_pitch-offset)-octave*12].lower()
  return octave, letter_name

def convert_to_midi_pitch(octave, letter_name):
  """
  Converts letter name and octave to midi pitch.
  """
  return 12*octave + MIDI_OFFSET + MIDI_LETTER_NAMES.index(letter_name)
  
  
def get_note_pitch_names(note_seq, num_notes):
  """
  Extracts letter octave pitchesfrom a NoteSequence with midi pitches.

  Args:
    note_seq: NoteSequence input
    num_notes: Number of notes in the NoteSequence to consider from beginning

  Returns:
    List of pitch_name tuples of (octave, letter_name)
  """

  notes = [(note.pitch, note.start_time) for note in note_seq.notes[:num_notes]]
  
  notes.sort(key=lambda elem: elem[1])
  pitches, _ = zip(*notes)
  
  pitch_names = [convert_pitch(p) for p in pitches]
    
  return pitch_names


def get_note_pitch_names_and_lengths(note_seq, num_notes):
  """
  Extracts pitches and note lengths from a NoteSequence object.

  Args:
    note_seq: NoteSequence input
    num_notes: Number of notes in the NoteSequence to consider from beginning

  Returns:
    List of tuples of (note_pitch_name, note_length), where note_pitch_name is a
      tuple of (note_octave, letter_name)

  """
  note_pitch_names = get_note_pitch_names(note_seq, num_notes)
  note_lengths = find_note_lengths(note_seq, num_notes)
  print (note_pitch_names)
  print (note_lengths)
  
  return list(zip(note_pitch_names, note_lengths))
  
def lilypond_pitch(octave, name):
  lilypond_octave = octave-4
  if lilypond_octave>=0:
    suffix = "'"*lilypond_octave
  else:
    suffix = ","*abs(lilypond_octave)
  return name + suffix


def note_sequence_to_lilypond_code(notes):
  """
  Produces compilable lilypond code from a list of note tuples.

  Args:
    notes: List of tuples of (note_pitch_name, note_length), where note_pitch_name is a
      tuple of (note_octave, letter_name)

  Returns:
    Lilypond code representing the passed in sequence of notes.

  """

  HEADER = """
  \\version "2.16.2"
  \\language "english"
  """

  BODY = """
  \\score {

  \\new PianoStaff << 
    \\new Staff = "upper" { 
      \\clef treble
      \\notes
    } 
  >>
    \\layout {
      #(layout-set-staff-size 25.2)
  \\context {
        \\Score
        \\override SpacingSpanner
                  #'base-shortest-duration = #(ly:make-moment 1 16)
      }
    }
  }
  """

  TRACK_FORMAT = """
  notes= {{
  {}
  \\bar "|."
  }}
  """

  RHYTHM_MAP = {0: '0', 1: '8', 2: '4', 3: '4.', 4: '2', 6: '2.', 8: '1', 12: '1.'}

  note_pitches, note_lengths = zip(*notes)
  note_octaves, note_names = zip(*note_pitches)

  note_string = ''

  for i in range(len(notes)):
    note = notes[i]
    pitch, length = note
    octave, name = pitch

    if length==0:
      continue

    new_note = lilypond_pitch(octave, name) + RHYTHM_MAP[length]
    note_string += ' ' + new_note

  track = TRACK_FORMAT.format(note_string)
  return HEADER + track + BODY

def convert_midi_to_ly(midi_input_path, ly_output_path, num_notes=-1):
  """
  Given a midi file, produces the score as lilypond_code and saves it to a file.

  Args:
    midi_input_path: Path to input midi file.
    ly_output_path: Path to output lilypond code file.

  """

  note_seq = midi_io.midi_file_to_note_sequence(midi_input_path)
  if num_notes == -1:
    num_notes = len(note_seq.notes)

  parsed_notes = get_note_pitch_names_and_lengths(note_seq, num_notes)
  lilypond_code = note_sequence_to_lilypond_code(parsed_notes)
  print (lilypond_code)
  with open(ly_output_path, 'w+') as f:
    f.write(lilypond_code)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--midi_input_path", help="Absolute or relative path to "
    "midi file to convert to lilypond code", 
    default='../data/midifiles/transcription_alle_voegel.mid')
  parser.add_argument("-n", "--num_notes", help="Number of notes to convert.", type=int, default=-1)
  parser.add_argument("-s", "--ly_output_path", help="Absolute or relative path "
    "to output text file to store lilypond code", default="output.ly")
  args = parser.parse_args()

  convert_midi_to_ly(args.midi_input_path, args.ly_output_path, args.num_notes)


if __name__ == '__main__':
  main()
