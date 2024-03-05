from mido import MidiFile, open_output, bpm2tempo
import threading
import time
import os
import pyglet

   
class MIDIProcessor(pyglet.event.EventDispatcher):
    """
    A class that processes MIDI files and plays the tracks in real time.

    Attributes:
        file_path (str): The path to the MIDI file.
        midi_file (MidiFile): The MidiFile object representing the MIDI file.
    """
    
    def __init__(self, file_path):
        """
        Initializes the MIDIProcessor with a MIDI file.

        Args:
            file_path (str): The path to the MIDI file.
        """
        
        self.file_path = file_path
        self.midi_file = self.read_midi_file()

    def read_midi_file(self):
        """
        Reads a MIDI file and returns the MidiFile object.

        Returns:
            MidiFile: The MidiFile object representing the MIDI file, or None if an error occurs.
        """
        try:
            return MidiFile(self.file_path)
        except IOError:
            print(f"Error: Could not read file {self.file_path}.")
            return None

    def extract_track_messages(self, track_number, default_tempo=120):
        """
        Extracts messages from a specified MIDI track.

        Args:
            track_number (int): The index of the track to be processed.
            default_tempo (int): The default tempo in BPM.

        Returns:
            list: A list of (message, delay) tuples representing the messages in the track.
        """
        if not self.midi_file:
            return []

        track = self.midi_file.tracks[track_number]
        messages = []
        
        #Look for tempo in midi file
        for msg in self.midi_file.tracks[0]:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

        #tempo = bpm2tempo(100)
        tempo = tempo * 1.75


        ticks_per_beat = self.midi_file.ticks_per_beat
        
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                
                """ ALERT ALERT ALERT """
                # !!!!!!! THIS IS DESIGN CHOICE !!!!!!! Tempo is slower for play ablity
                tempo = tempo * 1.75
                """ ALERT ALERT ALERT """
                
            
            elif not msg.is_meta:
                delay = msg.time * tempo / ticks_per_beat / 1e6
                messages.append((msg, delay))

        return messages

    def play_track(self, messages, outport):
        """
        Plays messages from a MIDI track in real time.

        Args:
            messages (list): A list of (message, delay) tuples representing the messages in the track.
            port_name (str): The MIDI output port name.
        """
        try:
                for msg, delay in messages:
                    time.sleep(delay)
                    #print(f"{msg}")
                    outport.send(msg)

        except IOError:
            print(f"Error: Could not open MIDI output port {port_name}.")


# Example usage
if __name__ == "__main__":
    midi_file_path = 'still_standing.mid'
    midi_port_name = 'loopMIDI Port 1 1'  # Replace with your MIDI port name
    
    outport = open_output(midi_port_name)

    processor = MIDIProcessor(midi_file_path)
    track_number = 1 # Specify the track number you want to play
    track_messages = processor.extract_track_messages(track_number)
    
    track_messages2 = processor.extract_track_messages(0)
    thread = threading.Thread(target=processor.play_track, args=(track_messages2, outport))
    thread.start()
    
    processor.play_track(track_messages, outport)
