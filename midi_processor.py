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
import os

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
        self.global_tempo_changes = []
        self.extract_global_tempo()
        

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
    
    def extract_global_tempo(self):
        track = self.midi_file.tracks[0]
        elapsed_ticks = 0
        cumulative_time = 0.0  # Cumulative time in seconds
        current_tempo = bpm2tempo(120)  # Default tempo (microseconds per beat)

        for msg in track:
            if msg.time > 0:
                cumulative_time += (msg.time * current_tempo) / (self.midi_file.ticks_per_beat * 1e6)
            if msg.type == 'set_tempo':
                self.global_tempo_changes.append((cumulative_time, msg.tempo))
                print(f"Tempo change to {msg.tempo} at {cumulative_time:.2f} seconds")
                current_tempo = msg.tempo  # Update current tempo
            elapsed_ticks += msg.time

   
    def extract_track_messages(self, track_number):
        """
        Extracts messages from the specified track, applying global tempo changes accurately,
        calculating the correct delays for each event, ensuring the playback tempo feels correct.
        """
        track = self.midi_file.tracks[track_number]
        messages = []
        elapsed_ticks = 0  # Total ticks since the last reset
        current_tempo = bpm2tempo(120)  # Start with a default tempo

        # Initialize tempo change handling
        tempo_change_index = 0
        if self.global_tempo_changes:
            # Start with the first tempo change if it exists
            _, current_tempo = self.global_tempo_changes[tempo_change_index]

        for msg in track:
            elapsed_ticks += msg.time

            # Check for and apply tempo changes
            while (tempo_change_index < len(self.global_tempo_changes) and
                elapsed_ticks >= self.global_tempo_changes[tempo_change_index][0] * self.midi_file.ticks_per_beat):
                _, current_tempo = self.global_tempo_changes[tempo_change_index]
                tempo_change_index += 1

            if msg.type in ['note_on', 'note_off']:
                # Calculate delay using current tempo and ticks per beat
                delay = (elapsed_ticks * current_tempo) / (self.midi_file.ticks_per_beat * 1e6)
                messages.append((msg, delay))
                elapsed_ticks = 0  # Reset ticks after processing a note

        return messages

    def play_track(self, messages, outport):
        """
        Plays messages from a MIDI track in real time, and prints tempo changes when they occur.
        
        Parameters
        ----------
        messages : list
            A list of (message, delay) tuples representing the messages in the track.
            Obtain this list using the extract_track_messages function.
        outport : str
            The MIDI output port name.
        """
        total_time_elapsed = 0.0
        current_tempo_index = 0

        for msg, delay in messages:
            time.sleep(delay)
            total_time_elapsed += delay
            outport.send(msg)

            while (current_tempo_index < len(self.global_tempo_changes) and
                total_time_elapsed >= self.global_tempo_changes[current_tempo_index][0]):
                _, tempo = self.global_tempo_changes[current_tempo_index]
                print(f"Tempo change to {tempo} at {total_time_elapsed:.2f} seconds")
                current_tempo_index += 1


if __name__ == "__main__":
    """
    Example usage: play and test MIDI file track(s).

    1. Replace `midi_file_path` and `midi_port_name` with your own MIDI file and port name.
    2. Specify the track number you want to play (0-indexed).
    3. Use threading to play multiple tracks simultaneously for debugging/testing.
    """
    
    os.chdir('songs')
    
    midi_file_path = 'best_part_jacob.mid'
    midi_port_name = 'Microsoft GS Wavetable Synth 0'  # Replace with your MIDI port name
    
    outport = open_output(midi_port_name)

    processor = MIDIProcessor(midi_file_path)
    track_number = 1  # Specify the track number you want to play
    
    track_messages1 = processor.extract_track_messages(track_number)
    
    
    track_messages0 = processor.extract_track_messages(0)
    
    print('===============================')
    
    thread = threading.Thread(target=processor.play_track, args=(track_messages0, outport))
    thread.start()
    
    processor.play_track(track_messages1, outport)
    
    print("\nTrack Messages 0:")
    for message in track_messages0[:20]:
        print(message)
    
    print("\nTrack Messages 1:")
    #for message in track_messages1[:20]:
    #    print(message)