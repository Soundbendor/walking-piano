import mido
import os

#change directory main directory
os.chdir(os.path.dirname(__file__))

#play midi song in outport
outport = mido.open_output('loopMIDI Port 1 1')
mid = mido.MidiFile('./jukebox_songs/2018/MIDI-Unprocessed_Chamber3_MID--AUDIO_10_R3_2018_wav--1.midi')
for msg in mid.play():
    outport.send(msg)
    
    
