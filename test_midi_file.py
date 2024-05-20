import mido
import os

#change directory to home directory
os.chdir(os.path.dirname(__file__))

#change directory to songs directory
os.chdir("songs")

#Testing jukebox songs example : '../jukebox_songs/2018/MIDI-Unprocessed_Chamber3_MID--AUDIO_10_R3_2018_wav--1.midi')

#play midi song in your outport
#for help setting up outport, checkout debug.py
outport = mido.open_output('loopMIDI Port 1 1')
mid = mido.MidiFile('stevie.mid')
for msg in mid.play():
    outport.send(msg)
    
    
