import mido, midi_backends

def play(midi_filename):
    outport = mido.open_output('Digital Piano')
    for msg in mido.MidiFile(midi_filename).play():
        outport.send(msg)
    outport.close()


if __name__=='__main__':
    play('test.mid')