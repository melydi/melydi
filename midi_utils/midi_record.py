
"""
Example usage:

python midi_record.py \
    -i 'Digital Piano USB-MIDI' \
    -ins piano \
    -mt melody \
    -fp c_major_scale

"""
import sys, os, mido, time, pickle
import uuid
import argparse
import subprocess
import signal
import midi_backends
import datetime
import json


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
    parser.add_argument('-fp', '--filename_prefix', help='Filename prefix', default='recording')
    parser.add_argument('-r', '--record_audio', type=bool, default=False, help='If True, will record audio through microphone with sox')
    parser.add_argument('-s', '--synthesize', type=bool, default=True, help='If True, will use fluidsynth to synthesize the recorded midi')
    parser.add_argument('-sfd', '--soundfonts_dir', type=str, default='../soundfonts', \
            help='Path to directory where soundfonts are saved')
    parser.add_argument('-od', '--output_dir', type=str, default='../recorded_data', \
            help='Path to directory where soundfonts are saved')
    parser.add_argument('-sfn', '--soundfont_name', type=str, default='general_user_v1.471', \
            help='Soundfont name without file ending, e.g. general_user_v1.471')
    parser.add_argument('-ins', '--instrument', type=str, required=True, help='Instrument type, e.g. piano or violin')
    parser.add_argument('-mt', '--music_type', type=str, required=True, help='Music type, e.g. melody or harmony')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    recorder = MidiRecorder(midi_input=args.midi_input)
    if args.record_audio:
        subprocess.Popen(['sox', '-d', '{}.wav'.format(args.filename)])
    recorder.record()

    file_uuid = str(uuid.uuid4())
    base_filename = '{}_{}'.format(args.filename_prefix, file_uuid)


    midi_filename = '{}.mid'.format(base_filename)
    midi_file_path = os.path.join(args.output_dir, midi_filename)
    recorder.write_output(midi_file_path)

    if args.synthesize:
        synth_filename = '{}_synth_{}.wav'.format(base_filename, args.soundfont_name)
        synth_file_path = os.path.join(args.output_dir, synth_filename)
        soundfont_path = os.path.join(args.soundfonts_dir, '{}.sf2'.format(args.soundfont_name))
        print (soundfont_path)
        subprocess.call(['fluidsynth', '-ni', soundfont_path, midi_file_path, '-F', synth_file_path, '-r', '44100'])

    meta_data = {}
    print(datetime.datetime.now())
    meta_data['uuid'] = file_uuid
    meta_data['timestamp'] = str(datetime.datetime.now())
    meta_data['filename_prefix'] = args.filename_prefix
    meta_data['instrument'] = args.instrument
    meta_data['music_type'] = args.music_type
    meta_data['tempo'] = '<>'
    meta_data['synthetic_versions'] = [args.soundfont_name]

    with open('{}.json'.format(os.path.join(args.output_dir, base_filename)), 'w') as file:
     file.write(json.dumps(meta_data, indent=4)) 




