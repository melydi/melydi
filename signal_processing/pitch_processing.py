import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import IPython as ipy

MAX_FREQUENCY = 10e3

def calculate_spectrogram(framerate, data, chunk_len, stride, window_func=np.hamming):
    """Calculate spectra of length |chunk_len|. Shift each window by |stride|.
    """
    num_chunks = int((len(data)-chunk_len)/float(stride))+1
    window = window_func(chunk_len)
    chunks = [data[i*stride:i*stride+chunk_len] for i in range(num_chunks)]
    windowed_chunks = [window*chunk for chunk in chunks]
    # fourier transform each chunk, get abs magnitude
    spectra = np.array([np.abs(np.fft.fft(chunk)) for chunk in windowed_chunks])
    return spectra

def dominant_frequency(framerate, data):
    window_len = 0.1 # sec
    spectrogram = calculate_spectrogram(framerate, data, window_len)
    # find slice corresponding to onset of note
    max_spectrum = spectrogram[np.argmax([sum(spectrum) for spectrum in spectrogram])]
    # determine largest peak in spectrogram at that slice
    peak_index = np.argmax(max_spectrum)
    # convert peak index to frequency
    frequency = peak_index/window_len
    return frequency

def map_pitch(frequency):
    # generate pitch dictionary
    note_order = ['c', ('db', 'c#'), 'd', ('eb', 'd#'), 'e', 'f', ('gb', 'f#'), 'g', ('ab', 'g#'), 'a', ('bb', 'a#'), 'b']
    c1 = 65.4
    pitches = {}
    for octave in range(1,6): # 5 octaves
        for note_index in range(len(note_order)):
            note = note_order[note_index]
            pitches[(note,octave)] = c1*2**(octave-1+float(note_index)/12)
    # determine closest pitch in log space
    closest = sorted([(pitch, np.abs(np.log(pitches[pitch])-np.log(frequency))) for pitch in pitches.keys()], key = lambda item: item[1])[0][0]
    return closest

def load_audio(filename):
    """Loads audio file as single channel"""
    framerate, data = read(filename)
    if len(data.shape)>1:
        data = np.array(data[:,0], dtype=float)
    else:
        data = np.array(data, dtype=float)
    return framerate, data

def power_traces(framerate, data, min_frequency, num_octaves):
    """TODO: only integrate on small window around frequencies.
    determine more likely notes via mdp."""
    chunk_len = int(0.1*framerate)
    stride = int(0.05*framerate)
    spectra = calculate_spectrogram(framerate, data, chunk_len, stride)
    num_frequencies = num_octaves*12
    log_frequencies = [np.log(min_frequency)+np.log(2)*(-1./24)]
    log_frequencies += [np.log(min_frequency)+np.log(2)*((k+1./2)/12.0) for k in range(num_frequencies)]
    boundary_indices = [np.exp(log_f)*chunk_len/float(framerate) for log_f in log_frequencies]
    ipy.embed()
    powers = lambda spectrum: [np.sum(spectrum[boundary_indices[i]:boundary_indices[i+1]]**2)/float(framerate)/chunk_len for i in range(len(boundary_indices)-1)]
    power_traces = np.array([powers(spectrum) for spectrum in spectra])
    permuted = zip(*power_traces)
    return permuted

if __name__=='__main__':
    # filename = '../piano_notes/audiohijack/fs1.wav'
    # framerate, data = load_audio(filename)
    # frequency = dominant_frequency(framerate, data)
    # print map_pitch(frequency)

    framerate, data = load_audio('data_old/test.wav')
    c1 = 65.4; min_frequency = c1*2
    power_traces = power_traces(framerate, data, min_frequency, 2)
    import matplotlib.pyplot as plt
    plt.ion()
    for trace in power_traces:
        plt.plot(trace)
    # ipy.embed()