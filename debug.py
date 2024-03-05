# This code may be useful if you are struggling to run the program.... this code outputs the current avaialbe outport names,
# could be useful for setting up the prgoram correctly.

#Simply take the name of one of your outports (as a string) and set it to the OUTPORT variable at the very top of piano_game.py!

import mido

outports = mido.get_output_names()
inports = mido.get_input_names()

print("~~~~~~~")

if inports:
    print("Available input ports:")
    for inport in inports:
        print(inport)
else:
    print("No input ports found.")

print("~~~~~~~")

if outports:
    print("Available output ports:")
    for outports in outports:
        print(outports)
else:
    print("No output ports found.")
    
print("~~~~~~~")


"""
Example results after running: 
~~~~
Available output ports:
Microsoft GS Wavetable Synth 0
loopMIDI Port 1 1
~~~~
So, we can set

OUTPORT = "Microsoft GS Wavetable Synth 0" 

or 

OUTPORT = "loopMIDI Port 1 1"

in piano_game.py
"""
