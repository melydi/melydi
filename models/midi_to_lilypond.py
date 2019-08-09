import argparse

import numpy as np
from magenta.common import tf_utils
from magenta.music import audio_io
import magenta.music as mm
from magenta.music import midi_io
from magenta.music import sequences_lib
from sklearn.cluster import KMeans
from collections import defaultdict


def extract_deltas(note_seq):
  times = [note.start_time for note in note_seq.notes]
  times = sorted(times)
  deltas = [times[i+1]-times[i] for i in range(len(times)-1)]
  return deltas

def find_largest_cluster_mean(cluster_to_deltas, cluster_to_size, n_clusters):
  """
  Find the largest cluster, which should correspond to the most frequent note
  value
  """
  max_cl = 0
  max_size = 0
  for cl in range(0, n_clusters):
    if cluster_to_size[cl] > max_size:
      max_cl = cl
      max_size = cluster_to_size[cl]
  cl_mean = np.mean(cluster_to_deltas[max_cl])
  return cl_mean
  
def find_note_lengths(note_seq, n_diff_lengths=4):
  
  deltas = np.array(extract_deltas(note_seq))
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
    offset = 21
    letter_names = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
    octave = (midi_pitch-offset)//12
    letter_name = letter_names[(midi_pitch-offset)-octave*12].lower()
    return octave, letter_name
  
  
def get_note_pitch_names(note_seq):
  notes = [(note.pitch, note.start_time) for note in note_seq.notes]
  
  notes.sort(key=lambda elem: elem[1])
  pitches, _ = zip(*notes)
  
  pitch_names = [convert_pitch(p) for p in pitches]
  
  
  return pitch_names


def get_note_pitch_names_and_lengths(note_seq):
  note_pitch_names = get_note_pitch_names(note_seq)
  note_lengths = find_note_lengths(note_seq)
  print (note_pitch_names)
  print (note_lengths)
  
  return list(zip(note_pitch_names, note_lengths))
  
  
def lilypond_template():
  

  return header, body, track_format, rhythm_map


def note_sequence_to_lilypond_code(notes):
  """
  Returns lilypond code from a list of note tuples.
  Each note tuple follows the format ((note_name, note_octave), note_length 
    (quantized))
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
  notes= \\relative c' {{
  {}
  \\bar "|."
  }}
  """

  RHYTHM_MAP = {0: '0', 1: '8', 2: '4', 3: '4.', 4: '2', 6: '2.', 8: '1'}


  note_pitches, note_lengths = zip(*notes)
  note_octaves, note_names = zip(*note_pitches)
  notes_string = ' '.join([note_names[i] +RHYTHM_MAP[note_lengths[i]] for i in 
    range(len(notes)) if note_lengths[i] != 0])
  track = TRACK_FORMAT.format(notes_string)
  return HEADER + track + BODY

def convert_midi_to_ly(midi_input_path, ly_output_path):
  note_seq = midi_io.midi_file_to_note_sequence(midi_input_path)
  parsed_notes = get_note_pitch_names_and_lengths(note_seq)
  lilypond_code = note_sequence_to_lilypond_code(parsed_notes)
  print (lilypond_code)
  with open(ly_output_path, 'w+') as f:
    f.write(lilypond_code)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--midi_input_path", help="Absolute or relative path to "
    "midi file to convert to lilypond code", 
    default='../data/midifiles/transcription_alle_voegel.mid')
  parser.add_argument("-s", "--ly_output_path", help="Absolute or relative path "
    "to output text file to store lilypond code", default="output.ly")
  args = parser.parse_args()

  convert_midi_to_ly(args.midi_input_path, args.ly_output_path)


if __name__ == '__main__':
  main()
