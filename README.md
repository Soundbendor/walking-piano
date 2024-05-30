# walking-piano

The walking piano software project is built entirely using python and it's packages. Ensure you have python installed and install the following dependencies. 

## Dependencies
* pyglet
* mido
* python-rtmidi

`pip install -r requirements.txt`

## Required devices

Running the project requires you to have a midi keyboard device plugged into your computer. The software is designed to automatically select your midi device and we have also added a section in the settings for selection as well. 

## Running the Project

Starting the project is as easy as 

`python start.py` 

This will run your program in fullscreen. 

To ease testing and debugging in the `start.py` file you may comment out this line 

`    game = WalkingPianoGame(fullscreen=True, resizable=True, caption="Walking Piano")
` 

and uncomment this line 

`    #game = WalkingPianoGame(width = 1920, height = 1080, resizable=True, caption="Walking Piano")
` 

for easier view of the terminal. 


