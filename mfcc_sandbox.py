import python_speech_features as psf
from pitch_processing import load_audio
import matplotlib.pyplot as plt
import os

foldername = '/Users/rex/src/melydi/data_old/piano_notes/5_octaves/'

files = os.listdir(foldername)

def get_pitch(fn):
	basename = fn[:-4]
	octave = int(basename[-1])
	pitch = basename[:-1]
	return pitch, octave

for fn in files[:5]:
	pitch, octave = get_pitch(fn)
	fullfile = os.path.join(foldername, fn)
	framerate, data = load_audio(fullfile)
	mfcc_feat = psf.mfcc(data, samplerate=framerate, nfft=2048)
	fbank_feat = psf.logfbank(data, framerate, nfft=2048, nfilt=100)
	plt.plot(fbank_feat[150,:], label="{}{}".format(pitch,octave))
plt.legend()
plt.show()
