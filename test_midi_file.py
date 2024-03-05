import mido
import os

#change directory main directory
os.chdir(os.path.dirname(__file__))

#Change directory to songs
os.chdir('songs')

#play midi song in outport
outport = mido.open_output('loopMIDI Port 1 1')
mid = mido.MidiFile('still_standing.mid')
for msg in mid.play():
    outport.send(msg)
    
    
