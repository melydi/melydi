import pygame, pygame.midi, sys

def read_loop(out_file=None):
	if out_file:
		fd = open(out_file, 'a')
	else:
		fd = sys.stdout
	pygame.init()
	pygame.midi.init()
	inp = pygame.midi.Input(0)
	try:
		now = time.time()
		while True:
			if inp.poll():
				fd.write('\n'.join([str(a) for a in inp.read(1000)])+'\n')
			pygame.time.wait(10)
	except KeyboardInterrupt:
		fd.close()
		inp.close()

if __name__=='__main__':
	if len(sys.argv)>1:
		read_loop(out_file=sys.argv[1])
	else:
		read_loop()