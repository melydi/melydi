from scipy.io.wavfile import read, write

def read_wav(fname):
	fs, x = read(fname)
	return fs, x

def save_wav(fs, x, fname):
	write(fs, x, fname)