# walking-piano

The walking piano software project is built entirely using python and it's packages. Ensure you have python installed and install the following dependencies. 

A quick demo of some songs within the game can be found here: https://drive.google.com/file/d/1XKRd0-tS2Q-1Sg519iIPSfwJgtSdjQ85/view?usp=sharing

A more in depth video explaining about the project here: https://drive.google.com/file/d/1GRSkiWKka5izWtTdP_5gMmL0I-2AXRgO/view?usp=sharing

Documentation: https://thricegreatest.github.io/WalkingPianoDocs/start_module.html

## Dependencies
* pyglet
* mido
* python-rtmidi

`pip install -r requirements.txt`

## Required devices

Interacting with the project to it's full extent requires you to have a midi keyboard device plugged into your computer. 
The software is designed to automatically select your midi device and we have also added a section in the settings for selection as well. 

## Running the Project

Starting the project is as easy as 

`python start.py` 

This will run your program in fullscreen mode by default. 

To ease testing and debugging and for easier view of the terminal, in the `start.py` file you may comment out this line 

`    game = WalkingPianoGame(fullscreen=True, resizable=True, caption="Walking Piano")
` 

and uncomment this line 

`    #game = WalkingPianoGame(width = 1920, height = 1080, resizable=True, caption="Walking Piano")
` 






