import numpy as np
from scipy.io.wavfile import read
from scipy.fftpack import fft
from scipy.signal import get_window

fname = '/Users/rex/src/melydi/data_old/piano_chords/amaj.wav'
fs, x = read(fname)
x = x/max(abs(x))

def STFT(x, w, H, N):
    W = len(w)
    w = w/max(w)
    num_windows = int(np.floor((len(x)-W+1)/H))
    Xs = []
    m = (W+1)//2
    m2 = W-m
    for i in range(num_windows):
        frame = w*x[i*H:i*H+W]
        buff = np.zeros(N)
        buff[:m] = frame[-m:]
        buff[-m2:] = frame[:m2]
        X = fft(buff)
        Xs.append(X)
    return np.array(Xs)

M = 501
N = 1024
H = 256
w = get_window('hamming', M)
Xs = STFT(x, w, H, N)
mXs = 20*np.log10(abs(Xs)+1e-16)
mXs = mXs[:,:N//2+1]

from pylab import *
matshow(mXs[:,:100].transpose())
show()
# import IPython as ipy
# ipy.embed()