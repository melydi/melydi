import numpy as np
from scipy.signal import get_window
from scipy.io.wavfile import read
from scipy.fftpack import fft

fs, data = read('sounds/goldberg.wav')
data = np.array(data, np.float)/max(data)
M = 2048 # ~50 ms window
w = get_window('hamming', M)
i_start = 146000
from pylab import *

x = w*data[i_start:i_start+M]
subplot(3,1,1)
plot(x)
dftbuffer = np.zeros(M)
hM1 = int((M+1)//2)
hM2 =int(M//2)
dftbuffer[:hM1] = x[hM2:]
dftbuffer[-hM2:] = x[:hM2]
subplot(3,1,2)
plot(dftbuffer)
X = fft(dftbuffer)
mX = 20*np.log10(abs(X[:M/2+1]))
pX = np.angle(X[:M/2+1])
subplot(3,1,3)
plot(mX)