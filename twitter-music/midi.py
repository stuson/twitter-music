import mido
import os
from time import sleep
from mido import Message
from sys import argv
from random import choice, choices

class Track(mido.MidiTrack):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def add_note(self, note=64, velocity=64, time=0, length=480):
        self.append(Message('note_on', note=note, velocity=velocity, time=time))
        self.append(Message('note_off', note=note, velocity=velocity, time=length))
    
    def add_chord(self, notes, length=480):
        for n in notes:
            self.append(
                Message(
                    'note_on',
                    note=n.get('note', 64),
                    velocity=n.get('velocity', 64),
                    time=n.get('time', 0),
                )
            )

        self.append(
            Message(
                'note_off',
                note=notes[0].get('note', 64),
                velocity=notes[0].get('velocity', 64),
                time=length
            )
        )

        for n in notes[1:]:
            self.append(
                Message(
                    'note_off',
                    note=n.get('note', 64),
                    velocity=n.get('velocity', 64),
                    time=0
                )
            )

class Scale:
    def __init__(self, scale_str):
        tonic_mod = ord(scale_str[0].lower()) - 97
        try:
            if scale_str[1] == '#':
                tonic_mod += 1
            elif scale_str[1] == 'b':
                tonic_mod -= 1
        except IndexError:
            pass

        self.scale = scale_str
        self.tonic = 58 + tonic_mod
        self.major = scale_str[0] == scale_str[0].upper()

        self.notes = [                   # e.g. for scale a/A
            self.tonic,                  # A/A
            self.tonic + 2,              # B/B
            self.tonic + 3 + self.major, # C/C#
            self.tonic + 5,              # D/D
            self.tonic + 7,              # E/E
            self.tonic + 8 + self.major, # F/F#
            self.tonic + 11,             # G#/G#
        ]
        
        root = {
            'i': 0,
            'ii': 1,
            'iii': 2,
            'iv': 3,
            'v': 4,
            'vi': 5,
            'vii': 6,
        }

        chords = {
            key: [ self.notes[val], self.notes[val] + 3, self.notes[val] + 7 ]
            for key, val
            in root.items()
        }

        chords.update(
            {
                key.upper(): [ self.notes[val], self.notes[val] + 4, self.notes[val] + 7 ]
                for key, val
                in root.items()
            }
        )

        self.chords = chords
    
    def get_chord(self, chord_str, velocity=60, length=480):
        chord = [
            {
                'note': note,
                'velocity': velocity
            }
            for note
            in self.chords[chord_str]
        ]

        return chord

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

    dmaj = Scale('D')

    seq = [
        'I','-','I','-',
        'V','-','V','-',
        'IV','-','IV','-',
        'iv','-','iv','-',
    ]

    for ch in seq:
        if ch != '-':
            track.add_chord(
                dmaj.get_chord(ch)
            )
        else:
            track.add_chord(
                [{'velocity': 0}]
            )

    midi.tracks.append(track)    

    if '--play' in argv:
        play_file(midi)

    midi.save(
        os.path.join(os.path.dirname(__file__), 'data/midi_output/test.mid')
    )
    

if __name__ == "__main__":
    main()