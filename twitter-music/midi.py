import mido
import os
from time import sleep
from mido import Message
from sys import argv
from random import choice

class Track(mido.MidiTrack):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def add_note(self, note=64, velocity=64, time=0, length=480):
        self.append(Message('note_on', note=note, velocity=velocity, time=time))
        self.append(Message('note_off', note=note, velocity=velocity, time=length))
    
    def add_chord(self, notes):
        # TODO: Some logic required here.
        #       The notes should have a note_off event tied to their note_on time.
        #       Since time is actually a time delta keep track fo when note_off
        #       actually be used.
        pass

def play_file(midi):
    timidity_ports = [port for port in mido.get_output_names() if 'TiMidity' in port]

    print(timidity_ports)

    if not timidity_ports:
        print('Please run "timidity -iA" in a terminal.')

    port = mido.open_output(timidity_ports[0])
    
    # First note seems to be slower than the rest when played
    # Having a small sleep after opening the port seems to fix 
    sleep(1)

    for msg in midi.play():
        print(msg)
        port.send(msg)

def main():
    mido.set_backend('mido.backends.rtmidi')

    midi = mido.MidiFile()
    track = Track()

    track.append(Message('program_change', program=12))

    notes = [60, 64, 67, 70, 72]
    times = [0, 0, 0, 0, 120, 240, 360, 480]
    durations = [120, 240, 360, 480, 480, 480, 480]
    
    for i in range(20):
        track.add_note(note=choice(notes), time=choice(times), length=choice(durations))

    midi.tracks.append(track)    

    if '--play' in argv:
        play_file(midi)

    midi.save(
        os.path.join(os.path.dirname(__file__), 'data/midi_output/test.mid')
    )
    

if __name__ == "__main__":
    main()