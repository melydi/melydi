import sys, os, mido, time, pickle
import argparse
import subprocess
import signal
import midi_backends


def write_output(messages, times, output_file):
    """Writes messages and times to a midi file."""
    ticks_per_second = 256
    tempo = mido.bpm2tempo(ticks_per_second)
    ticks = [int(mido.second2tick(time, ticks_per_second, tempo)) for time in times]
    with open(output_file, 'w') as f:
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        # track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        last_tick = 0
        for (tick, message) in zip(ticks, messages):
            m = message.copy()
            m.time = tick-last_tick
            last_tick = tick
            track.append(m)
        mid.save(output_file)

class MidiRecorder():
    def __init__(self, midi_input='Digital Piano'):
        """
        Class to record midi events from a midi input device e.g. digital piano
        and write to a midi file.

        Args:
            midi_input (str): input filename or port name
        
        """
        self.input = midi_input
        self.messages = []
        self.times = []

    def record(self):
        """
        Record midi events until a keyboard interrupt.
        """
        inport = mido.open_input(self.input)
        start_time = time.time()
        print ("Midi recording started") 
        try:
            for msg in inport:
                now = time.time()
                self.messages.append(msg)
                print (msg)
                self.times.append(now-start_time)
        except KeyboardInterrupt:
            inport.close()

    def write_output(self, midi_output):
        """
        Write midi messages to a midi file.
        
        Args:
            midi_output (str): Midi output file name

        """
        write_output(self.messages, self.times, midi_output)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Record midi and audio')
    parser.add_argument('-i', '--midi_input', help='Midi input name', required=False, default='Digital Piano')
    parser.add_argument('-f', '--filename', help='Filename without extension under which \
            recording should be saved', default='test')
    parser.add_argument('-r', '--record_audio', type=bool, default=False, help='If True, will record audio through microphone with sox')
    parser.add_argument('-s', '--synthesize', type=bool, default=True, help='If True, will use fluidsynth to synthesize the recorded midi')
    parser.add_argument('-sf', '--soundfont', type=str, default='/usr/local/Cellar/fluid-synth/1.1.11/share/soundfonts/default.sf2', \
            help='Soundfont filename full path')
    args = parser.parse_args()

    recorder = MidiRecorder(midi_input=args.midi_input)
    if args.record_audio:
        subprocess.Popen(['sox', '-d', '{}.wav'.format(args.filename)])
    recorder.record()
    midi_filename = '{}.mid'.format(args.filename)
    recorder.write_output(midi_filename)
    if args.synthesize:
        synth_filename = '{}_synth.wav'.format(args.filename)
        subprocess.call(['fluidsynth', '-ni', args.soundfont, midi_filename, '-F', synth_filename, '-r', '44100'])
