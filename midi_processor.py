"""
midi_processor.py 
=====================

This file provides functionalities to process and play MIDI files using MIDO.

Classes:
    MIDIProcessor

Functions:
    main
    
Authors: Devin Martin and Wesley Jake Anding
"""

from mido import MidiFile, open_output, bpm2tempo
import threading
import time

class MIDIProcessor():
    """
    A class that processes MIDI files and plays the tracks in real time.

    Attributes
    ----------
    file_path : str
        The path to the MIDI file.
    midi_file : MidiFile
        The MidiFile object representing the MIDI file.
    """

    def __init__(self, file_path):
        """
        Initializes the MIDIProcessor with a MIDI file.

        Parameters
        ----------
        file_path : str
            The path to the MIDI file.
        """
        self.file_path = file_path
        self.midi_file = self.read_midi_file()
        self.bpm = None  # Is set in extract_track_messages

    def read_midi_file(self):
        """
        Reads a MIDI file and returns the MidiFile object.

        Returns
        -------
        MidiFile
            The MidiFile object representing the MIDI file, or None if an error occurs.
        """
        try:
            return MidiFile(self.file_path)
        except IOError:
            print(f"Error: Could not read file {self.file_path}.")
            return None

    def extract_track_messages(self, track_number, default_BPM=80):
        """
        Extracts messages from a specified MIDI track.

        Parameters
        ----------
        track_number : int
            The index of the track to be processed.
        default_BPM : int, optional
            The tempo in BPM (default is 80).

        Returns
        -------
        list
            A list of (message, delay) tuples representing the messages in the track.
        """
        if not self.midi_file:
            return []

        track = self.midi_file.tracks[track_number]
        messages = []

        # Look for tempo in MIDI file
        tempo = None
        for msg in self.midi_file.tracks[0]:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                self.bpm = bpm2tempo(tempo)
                break

        if tempo is None:
            tempo = default_BPM

        # ALERT: Tempo is slower for playability
        # tempo = tempo * 1.75
        tempo = bpm2tempo(default_BPM)

        ticks_per_beat = self.midi_file.ticks_per_beat
                
         # Specific handling for 'viva_la_vida.mid' track
        if self.file_path == 'Viva_la_vida.mid':
            for msg in self.midi_file.tracks[0]:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    break
                
        if self.file_path == 'september.mid':
            for msg in self.midi_file.tracks[0]:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    break
        
        if self.file_path == 'runaway.mid':
            for msg in self.midi_file.tracks[0]:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    break

        for msg in track:
            if msg.type == 'set_tempo':
                pass
                # ALERT: Tempo is slower for playability
                # tempo = tempo * 1.75
            elif not msg.is_meta:
                delay = msg.time * tempo / ticks_per_beat / 1e6
                messages.append((msg, delay))

        return messages

    def play_track(self, messages, outport):
        """
        Plays messages from a MIDI track in real time. 
        This is used for testing our extract_track_messages function.
        We can listen to how our interpretation of the MIDI file sounds compared to the original.

        Parameters
        ----------
        messages : list
            A list of (message, delay) tuples representing the messages in the track.
            Obtain this list using the extract_track_messages function.
        outport : str
            The MIDI output port name.
        """
        try:
            for msg, delay in messages:
                time.sleep(delay)
                outport.send(msg)
        except IOError:
            print(f"Error: Could not open MIDI output port {outport}.")

if __name__ == "__main__":
    """
    Example usage: play and test MIDI file track(s).

    1. Replace `midi_file_path` and `midi_port_name` with your own MIDI file and port name.
    2. Specify the track number you want to play (0-indexed).
    3. Use threading to play multiple tracks simultaneously for debugging/testing.
    """
    midi_file_path = 'songs/married_life.mid'
    midi_port_name = 'Microsoft GS Wavetable Synth 0'  # Replace with your MIDI port name
    
    outport = open_output(midi_port_name)

    processor = MIDIProcessor(midi_file_path)
    track_number = 1  # Specify the track number you want to play
    track_messages = processor.extract_track_messages(track_number)
    
    track_messages2 = processor.extract_track_messages(0)
    thread = threading.Thread(target=processor.play_track, args=(track_messages2, outport))
    thread.start()
    
    processor.play_track(track_messages, outport)
    
    print("\nTrack Messages 0:")
    print(track_messages2[:20])
    
    print("\nTrack Messages 1:")
    print(track_messages[:20])
