import sys, os, mido, time, pickle
import argparse
import subprocess
import signal
import midi_backends

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True


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

class MidiReader():
    def __init__(self, midi_input='Digital Piano'):
        """Determine input port/file and output file.

        Arguments:
        midi_input -- input filename or port name"""

        self.input = midi_input
        self.messages = []
        self.times = []

    def read(self):
        """Record midi events until a keyboard interrupt."""
        inport = mido.open_input(self.input)
        start_time = time.time()
        try:
            for msg in inport:
                now = time.time()
                self.messages.append(msg)
                print (msg)
                self.times.append(now-start_time)
        except KeyboardInterrupt:
            inport.close()

    def write_output(self, midi_output):
        """Write midi messages to a midi file."""
        write_output(self.messages, self.times, midi_output)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Record midi and audio')
    parser.add_argument('-i', '--midi_input', help='Midi input name', required=False, default='Digital Piano')
    parser.add_argument('-f', '--filename', help='Filename without extension under which \
            recording should be saved', default='test')
    parser.add_argument('r', '--record_audio', type=bool, default=False, help='If true, will record audio through microphone with sox')
    args = parser.parse_args()

    reader = MidiReader(midi_input=args.midi_input)
    if args.record_audio:
        subprocess.Popen(['sox', '-d', '{}.wav'.format(args.filename)])
    time.sleep(1)
    reader.read()
    reader.write_output('{}.mid'.format(args.filename))
