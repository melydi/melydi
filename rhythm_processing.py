import numpy as np
import peakutils, pdb, os
from scipy.io.wavfile import read
from exceptions import NotImplementedError

window = 0.05 # sec
# peak_threshold = 400000000 # adc counts per sec
c1 = 65.4

def power_envelope(framerate, data):
	samples_per_window = int(framerate*window)
	stride = samples_per_window//2
	new_framerate = float(framerate)/stride
	num_strides = (len(data)-samples_per_window)//stride+1
	return new_framerate, np.array([np.std(data[i*stride:i*stride+samples_per_window]) for i in range(num_strides)])

def power_envelope_in_frequency_interval(framerate, data, interval):
	raise(NotImplementedError('this is unexceptable.'))
	samples_per_window = int(framerate*window)
	stride = samples_per_window//2
	new_framerate = float(framerate)/stride
	num_strides = (len(data)-samples_per_window)//stride+1
	return new_framerate, np.array([np.std(data[i*stride:i*stride+samples_per_window]) for i in range(num_strides)])

def derivative(framerate, data):
	dt = 1/float(framerate)
	return framerate, (data[1:]-data[:-1])/dt

def find_beats(framerate, data, min_separation_time):
	p_framerate, p_data = power_envelope(framerate, data)
	d_framerate, d_data = derivative(p_framerate, p_data)
	min_separation_index = int(min_separation_time*d_framerate)
	# threshold = peak_threshold/float(max(d_data))
	beat_indices = peakutils.indexes(d_data, thres=0.3, min_dist=min_separation_index)
	beats = [beat_index/float(d_framerate) for beat_index in beat_indices]
	return beats

def pitch_to_frequency(pitch):
	note = pitch[:-1]
	octave = int(pitch[-1])
	note_order_flats = ['c', 'db', 'd', 'eb', 'e', 'f', 'gb', 'g', 'ab', 'a', 'bb', 'b']
	note_order_sharps = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
	try:
		note_index = note_order_sharps.index(note)
	except:
		note_index = note_order_flats.index(note)
	c1 = 65.4
	pitch_frequency = c1*2**(octave-1+float(note_index)/12)
	return pitch_frequency

def pitch_intervals():
	center_frequencies = [c1*2**(octave-1+float(note_index)/12) for note_index in range(12) for octave in range(1,6)]
	lcf = np.log(np.array(center_frequencies))
	boundaries = [(lcf[i]+lcf[i+1])/2 for i in range(len(lcf)-1)]
	raise(NotImplementedError('unexceptable lack of initiative on the part of the coder.'))

def nearest_neighbor_rhythm(beats, bpm, offset, rhythmic_tolerance):
	block = 1.0/(bpm/60.0*2**rhythmic_tolerance) # in seconds
	rhythmic_guesses = np.array([round((beat-offset)/block)/2**rhythmic_tolerance for beat in beats])
	return rhythmic_guesses

def best_fit_dynamic_tempo(framerate, data, bpm_guess, beats_per_measure, rhythmic_tolerance):
	"""Fit bpm and offset to sound, one measure at a time, penalizing changes in either."""
	min_separation_time = 1.0/((bpm_guess/60.0)*2.0**rhythmic_tolerance)*0.8 # in seconds; accounts for 10% variability
	beats = find_beats(framerate, data, min_separation_time)
	current_bpm = bpm_guess
	current_offset = beats[0]
	rhythms = []
	while beats: # loop over all measures
		alpha = 1 # weight for matching beats
		beta = 1 # weight for changing bpm
		gamma = 1 # weight for changing offset
		current_beats = [b for b in beats if b < beats_per_measure*60/float(current_bpm)+current_offset]
		del beats[:len(current_beats)]
		num_beats = len(current_beats)
		# guess the rhythms using nearest neighbor and the current bpm
		rhythmic_guesses = nearest_neighbor_rhythm(current_beats, current_bpm, current_offset, rhythmic_tolerance)
		# add to previous rhythms
		rhythms.append(rhythmic_guesses)
		# fine-tune the offset and bpm by using a model that penalizes changes in both while rewarding fit
		A_fit = np.sqrt(alpha)*np.transpose(np.vstack([np.ones(num_beats), np.array(rhythmic_guesses)]))
		b_fit = np.reshape(np.sqrt(alpha)*current_beats, (num_beats,1))
		A_weight = np.array([[np.sqrt(gamma),0],[0,np.sqrt(beta)]])
		current_seconds_per_beat = 60/float(current_bpm)
		b_weight = np.array([[np.sqrt(gamma)*current_offset],[np.sqrt(beta)*current_seconds_per_beat]])
		A = np.vstack([A_fit, A_weight])
		b = np.vstack([b_fit, b_weight])
		# least squares
		current_offset, seconds_per_beat = np.dot(np.linalg.pinv(A),b)
		current_offset = current_offset[0]
		seconds_per_beat = seconds_per_beat[0]
		# update bpm and offset for next iteration
		current_bpm = 60.0/seconds_per_beat
		measure_offset = beats_per_measure*60/float(current_bpm)
		current_offset += measure_offset
	pdb.set_trace()
	return rhythms

def best_fit_dynamic_tempo_with_pitch(framerate, data, bpm_guess, beats_per_measure, rhythmic_tolerance):
	"""Fit bpm and offset to sound, one measure at a time, penalizing changes in either."""
	min_separation_time = 1.0/((bpm_guess/60.0)*2.0**rhythmic_tolerance)*0.8 # in seconds; accounts for 10% variability
	beats = find_beats(framerate, data, min_separation_time)
	current_bpm = bpm_guess
	current_offset = beats[0]
	rhythms = []
	while beats: # loop over all measures
		alpha = 1 # weight for matching beats
		beta = 1 # weight for changing bpm
		gamma = 1 # weight for changing offset
		cutoff = current_offset + beats_per_measure*60/float(current_bpm)
		current_beats = [b for b in beats if b < cutoff]
		del beats[:len(current_beats)]
		num_beats = len(current_beats)
		# guess the rhythms using nearest neighbor and the current bpm
		rhythmic_guesses = nearest_neighbor_rhythm(current_beats, current_bpm, current_offset, rhythmic_tolerance)
		# add to previous rhythms
		rhythms.append(rhythmic_guesses)
		# fine-tune the offset and bpm by using a model that penalizes changes in both while rewarding fit
		A_fit = np.sqrt(alpha)*np.transpose(np.vstack([np.ones(num_beats), np.array(rhythmic_guesses)]))
		b_fit = np.reshape(np.sqrt(alpha)*current_beats, (num_beats,1))
		A_weight = np.array([[np.sqrt(gamma),0],[0,np.sqrt(beta)]])
		current_seconds_per_beat = 60/float(current_bpm)
		b_weight = np.array([[np.sqrt(gamma)*current_offset],[np.sqrt(beta)*current_seconds_per_beat]])
		A = np.vstack([A_fit, A_weight])
		b = np.vstack([b_fit, b_weight])
		# least squares
		current_offset, seconds_per_beat = np.dot(np.linalg.pinv(A),b)
		current_offset = current_offset[0]
		seconds_per_beat = seconds_per_beat[0]
		# update bpm and offset for next iteration
		current_bpm = 60.0/seconds_per_beat
		measure_offset = beats_per_measure*60/float(current_bpm)
		current_offset += measure_offset
	pdb.set_trace()
	return rhythms

def user_prompt_input():
	framerate, data = read(os.path.expanduser(raw_input("Audio file to predict:\n")))
	bpm_guess = int(raw_input("BPM guess:\n"))
	beats_per_measure = int(raw_input("Beats per measure:\n"))
	rhythmic_tolerance = int(raw_input("Rhythmic tolerance:\n(rhythmic_tolerance = log_2(divisions_per_beat)) (e.g. eighth note => 2^1 per beat => rhythmic_tolerance = 1)\n"))
	return framerate, data, bpm_guess, beats_per_measure, rhythmic_tolerance

if __name__=='__main__':
	framerate, data = read(os.path.expanduser('/Users/rex/Desktop/test.wav'))
	bpm_guess = 100
	beats_per_measure = 4
	rhythmic_tolerance = 1
	rhythms = best_fit_dynamic_tempo(framerate, data, bpm_guess, beats_per_measure, rhythmic_tolerance)








