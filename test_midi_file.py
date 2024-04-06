import mido
import os

#change directory main directory
os.chdir(os.path.dirname(__file__))

#os.chdir("songs")
os.chdir("songs")


#Testing jukebox songs example : '../jukebox_songs/2018/MIDI-Unprocessed_Chamber3_MID--AUDIO_10_R3_2018_wav--1.midi')

#play midi song in outport
outport = mido.open_output('Microsoft GS Wavetable Synth 0')
mid = mido.MidiFile('got_you.mid')
for msg in mid.play():
    outport.send(msg)
    
    
