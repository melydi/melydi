from sklearn.cluster import KMeans
from collections import defaultdict

def extract_deltas(note_seq):
  times = [note.start_time for note in note_seq.notes]
  times = sorted(times)
  deltas = [times[i+1]-times[i] for i in range(len(times)-1)]
  return deltas

def find_largest_cluster_mean(cluster_to_deltas, cluster_to_size, n_clusters):
  max_cl = 0
  max_size = 0
  for cl in xrange(0, n_clusters):
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
  for i in xrange(len(deltas)):
    cl = kmeans.labels_[i]
    cluster_to_deltas[cl].append(deltas[i])
    cluster_to_size[cl] += 1
  unit_len = find_largest_cluster_mean(cluster_to_deltas, cluster_to_size, n_diff_lengths)
  note_lengths = []
  
  for d in deltas:
    ratio = d/float(unit_len)
    note_length = np.round(ratio * 2)
    note_lengths.append(note_length)
  note_lengths.append(unit_len * 2)
  
  return note_lengths


  notes_string = """c4 d e d |
c d e d |
c e d d |
c1"""

header = """
\\version "2.16.2"
\\language "english"
"""

body = """
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

track_format = """
notes= \\relative c' {{
{}
\\bar "|."
}}
"""


rhythm_map = {0: None, 1: '8', 2: '4', 3: '4.', 4: '2', 6: '2.', 8: '1'}

def note_sequence_to_ly(notes):
  """
  Returns lilypond code from a list of note tuples.
  Each note tuple follows the format ((note_name, note_octave), note_length (quantized))
  """
  note_pitches, note_lengths = zip(*notes)
  note_names, note_octaves = zip(*note_pitches)
  notes_string = ' '.join([note_names[i]+rhythm_map[note_lengths[i]] for i in range(len(notes))])
  track = track_format.format(notes_string)
  return header+track+body