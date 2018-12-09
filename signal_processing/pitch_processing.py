import numpy as np
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt
import IPython as ipy
from scipy.signal import get_window

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
    fs, data = read(filename)
    if len(data.shape)>1:
        data = np.array(data[:,0], dtype=float)
    else:
        data = np.array(data, dtype=float)
    return fs, data

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

def get_onset(fs, x):
    power = x**2
    dt = 10e-3
    powers = np.array([np.average(power[int(dt*fs*i):int(dt*fs*(i+1))]) for i in range(int(len(power)/(dt*fs)))])
    times = dt*np.arange(int(len(power)/(dt*fs)))
    # plt.subplot(3,1,1)
    # plt.plot(np.arange(len(x))/float(fs), power)
    # plt.subplot(3,1,2)
    # plt.plot(times, powers)
    # plt.subplot(3,1,3)
    return times[np.argmax(powers[1:]-powers[:-1])]

def spectrum(fs, x, width):
    l1 = len(x)//2
    l2 = len(x)-l1
    xx = np.zeros(width)
    xx[:l2] = x[-l2:]
    xx[-l1:] = x[:l1]
    y = np.fft.fft(xx)
    mY = 20*np.log(np.abs(y[:l2+1])+1e-15)
    pY = np.angle(y[:l2+1])*180/np.pi
    freq = np.arange(width)[:l2+1]*float(fs)/width
    return freq, mY, pY

def is_peak(vals, index, lookaround=5):
    if index<lookaround or index>len(vals)-lookaround-1:
        return False
    return all(vals[index]>vals[index-lookaround:index]) and all(vals[index]>vals[index+1:index+lookaround+1])

def irregularity_statistic(l):
    l_std = np.std(l)
    l_mean = np.mean(l)
    return l_std/l_mean

def peak_quality(list_of_peaks):
    """Quantify the 'peakness' of the peak. WIP
    |list_of_peak| list of tuples of the form (x, y)"""
    #ideas:
    # define this based on just the peak values (not based on the spectrum)
    # pass
    all_x_values, all_y_values = sorted(zip(*list_of_peaks), key=lambda item: item[0])
    distances = [all_x_values[i+1]-all_x_values[i] for i in range(len(all_x_values)-1)]
    delta_x_metric = irregularity_statistic(distances)
    print(delta_x_metric)
    slopes = [(all_y_values[i+1]-all_y_values[i])/(all_x_values[i+1]-all_x_values[i]) for i in range(len(all_x_values)-1)]
    slopes_metric = irregularity_statistic(slopes)
    print(slopes_metric)

def get_peaks(fs, x, threshold=-80):
    width = int(2**np.ceil(np.log(len(x))/np.log(2)))
    width = 2048*8
    x_windowed = x*get_window('hamming', len(x))
    freq, mY, pY = spectrum(fs, x_windowed, width)
    mY = mY-max(mY)
    f_peaks = []
    dBs = []
    list_of_peaks = []
    for i in range(1,len(freq)-1):
        if is_peak(mY, i) and mY[i]>threshold:
            fs = np.array(freq[i-1:i+2])
            ys = np.array(mY[i-1:i+2])
            M = np.array([fs**2, fs, np.ones(3)]).transpose()
            out = np.linalg.pinv(M).dot(ys.transpose())
            f0 = out[1]/(-2*out[0])
            dB = out[2]-out[1]**2/4/out[0]
            f_peaks.append(f0)
            dBs.append(dB)
            list_of_peaks.append((i, f0))
            # f_peaks.append(freq[i])
            # dBs.append(mY[i])
    peak_quality(list_of_peaks)
    plt.plot(freq, mY)
    plt.plot(f_peaks, dBs, 'r+')
    plt.show()
    return np.array(f_peaks), np.array(dBs)

def newtons_method(f, guess, delta=1e-12, iterations=3):
    for _ in range(iterations):
        evals = np.array([f(guess-delta), f(guess), f(guess+delta)])
        xs = np.array([guess-delta, guess, guess+delta])
        M = np.array([xs**2, xs, np.ones(3)]).transpose()
        out = np.linalg.pinv(M).dot(evals.transpose())
        guess = out[1]/(-2*out[0])
    return guess

def get_f0(fs, x):
    f_peaks, dBs = get_peaks(fs, x)
    # import IPython as ipy; ipy.embed()
    diffs = [f_peaks[i+1]-f_peaks[i] for i in range(len(f_peaks)-1)]
    # plt.hist(diffs)
    # plt.show()
    guess = np.median(diffs)
    f0 = guess
    # f = lambda omega: sum(np.cos(2*np.pi*omega*f_peaks)*dBs)
    # f0 = 1.0/newtons_method(f, guess)
    return f0

if __name__=='__main__':
    # framerate, data = load_audio('data_old/test.wav')
    # c1 = 65.4; min_frequency = c1*2
    # power_traces = power_traces(framerate, data, min_frequency, 2)
    # import matplotlib.pyplot as plt
    # plt.ion()
    # for trace in power_traces:
    #     plt.plot(trace)
    # ipy.embed()

    fname = '../data_old/piano_notes/one_octave/A2.wav'
    fs, x = read(fname)
    print (fs)
    x = np.array(x, np.float)
    x /= max(abs(x))
    ton = get_onset(fs, x)
    f0 = get_f0(fs, x[int(ton*fs):int(ton*fs)+2048])
    print (f0)
