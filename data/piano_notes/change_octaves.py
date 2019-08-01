import os

foldername = "/Users/rex/src/melydi/data_old/piano_notes/5_octaves"

for filename in sorted(os.listdir(foldername), reverse=True):
	octave = int(filename[-5])
	# print octave
	newfilename = filename[:-5] + str(octave + 1) + filename[-4:]
	print ("{} -> {}".format(filename, newfilename))
	os.rename(os.path.join(foldername, filename), os.path.join(foldername, newfilename))