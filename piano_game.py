"""
piano_game.py
========================

This file contains the implementation of the PianoGameUI class, which is responsible for handling the user interface
and game logic for the Walking Piano game. The class integrates with Pyglet for rendering the UI and Mido for MIDI 
input/output handling.

Classes:
    PianoGameUI: Manages the piano game UI, including drawing the piano, handling MIDI input, and game mechanics.
    ClockPauseManager: Manages the clock and scheduled functions, allowing pausing and resuming of the game.

Functions:
    None (all functionality is encapsulated within classes).

Author: Devin Martin and Wesley Jake Anding
"""

import pyglet
import mido
import datetime
import threading
from midi_processor import MIDIProcessor


class PianoGameUI(pyglet.event.EventDispatcher):

    def __init__(self, window, midi_file_path, game_mode, inport_name, outport_name, controller_size, player_count=1,  auto_play=False):
        
        """
        PianoGameUI is responsible for handling the  entire game portion of the Walking Piano project,
        this includes the user interface and all  logic for the piano game.
        """
        
        print("Initializing Piano Game...")
        
        # Create a window
        self.window = window
        
        self.window.push_handlers(self.on_key_press)
        
        #Batch for all graphics
        self.white_keys_batch = pyglet.graphics.Batch()
        self.black_keys_batch = pyglet.graphics.Batch()
        self.game_elements_batch = pyglet.graphics.Batch()
        self.rectangles_batch = pyglet.graphics.Batch()

        #Open outport You may need to change this to your specific MIDI port in settings.
        if outport_name is not None:
            self.outport = mido.open_output(outport_name, autoreset=True) # Open the MIDI output port
        
        else:
            self.outport = None
            
        # Store the MIDI input port name
        #We will open this port in seperate thread to avoid blocking the main thread.
        #See play_piano_user() for more details.
        self.inport_name = inport_name

        self.player_count = player_count

        self.fps_display = pyglet.window.FPSDisplay(window=self.window)  # Display the FPS

        self.visibility_lines = []  # Array for holding visibility lines
      
        self.controller_size = controller_size
      
        #If controller size is 49 key, we will use bigger keys for clearer visibility and more inuitive playing.
        if self.controller_size == '49 key': self.white_key_height = 400  
        else: self.white_key_height = 245
        
        self.white_key_width = self.white_key_height * 0.146 #Ideally width should be height * about 0.146; matches true dimensions of piano keys.
      
        self.number_of_white_keys = 52

        # Array for holding white keys
        self.white_keys = []

        # Array for holding black keys
        self.black_keys = []

        # SORTED array of all MIDI keys. Allows access by MIDI notes 21-108.
        self.all_midi_keys = []     
           
        # MIDI numbers for black keys (sharps/flats) in each octave
        self.black_keys_midi = [22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58,
                                61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106]

        #All the note names... "b" is placeholder for the flat symbol, which can be printed formally using '\u266D'.
        self.note_names = {
                21: "A", 22: "A#/Bb", 23: "B", 24: "C", 25: "C#/Db", 26: "D", 27: "D#/Eb", 28: "E", 29: "F", 30: "F#/Gb", 31: "G", 32: "G#/Ab",
            33: "A", 34: "A#/Bb", 35: "B", 36: "C", 37: "C#/Db", 38: "D", 39: "D#/Eb", 40: "E", 41: "F", 42: "F#/Gb", 43: "G", 44: "G#/Ab",
            45: "A", 46: "A#/Bb", 47: "B", 48: "C", 49: "C#/Db", 50: "D", 51: "D#/Eb", 52: "E", 53: "F", 54: "F#/Gb", 55: "G", 56: "G#/Ab",
            57: "A", 58: "A#/Bb", 59: "B", 60: "C", 61: "C#/Db", 62: "D", 63: "D#/Eb", 64: "E", 65: "F", 66: "F#/Gb", 67: "G", 68: "G#/Ab",
            69: "A", 70: "A#/Bb", 71: "B", 72: "C", 73: "C#/Db", 74: "D", 75: "D#/Eb", 76: "E", 77: "F", 78: "F#/Gb", 79: "G", 80: "G#/Ab",
            81: "A", 82: "A#/Bb", 83: "B", 84: "C", 85: "C#/Db", 86: "D", 87: "D#/Eb", 88: "E", 89: "F", 90: "F#/Gb", 91: "G", 92: "G#/Ab",
            93: "A", 94: "A#/Bb", 95: "B", 96: "C", 97: "C#/Db", 98: "D", 99: "D#/Eb", 100: "E", 101: "F", 102: "F#/Gb", 103: "G", 104: "G#/Ab",
            105: "A", 106: "A#/Bb", 107: "B", 108: "C"
        }
        
        # Note label colors
        self.note_label_colors = {
            'A': (5,166,245,255),   # Light Blue
            'B': (1,167,89,255),     # Green
            'C': (213,18,132,255),   # Pink
            'D': (240,114,36,255),   # Orange
            'E': (128,42,146,255),   # Purple
            'F': (137,198,61,255), # Light Green
            'G': (46,45,143,255)    # Dark Purple
        }
        
        self.middle_c_special_label = None  # Label for middle C; will create within the create piano loop

        # Placeholder array for notes currently being drawn.
        self.active_notes = {note: False for note in range(21, 109)}
        
        #Array for tracking notes currently being played by user.
        self.playing_notes = {note: False for note in range(21, 109)}
        
        self.active_note_events = {}  # New: Dictionary to track active note events

        # Array for notes as they approach the time for being played.
        # 0 = dont play, 1 = okay 2 = perfect
        self.incoming_notes = {note: {'note_timing': 0, 'note_played': 0} for note in range(21, 109)}

        """#Temp for testing visuals"""
        self.active_notes_line_segments = {}

        # Intialize falling rectangle manager
        self.falling_rectangles_list = []

        """Todo: Get this note list working with 'extract_track_messages()' from MIDIprocessor class"""
        # Create note list
        self.note_list = []
        
        self.update_rectangles = self.update_rectangles

        # Create visual for active note array
        self.create_active_notes_line()

        # Create piano keys and start game.
        self.create_piano()
        
        #Flag for game state
        self.game_active = True
        
        self.paused = False

        self.window.push_handlers(self)

        self.window.push_handlers(on_draw=self.on_draw)
        
        self.clock_pause_manager = ClockPauseManager(self.update_rectangles)
        
        #Add custom event handler for window close. This will allow us to clean up the MIDI port, and allow user to return to menu with ESC/Window close
        def on_window_close():
            self.game_active = False
            window.on_close = lambda: window.close() #Reset the close function to default
            self.exit_game()
            self.window.close()

        window.on_close = on_window_close
        
        
        self.game_mode = game_mode
        
        # TEMPORARY TESTING IF TRUE
        self.testing_autoplay = auto_play
        
        self.okay_color_white = (255, 255, 0)
        self.okay_color_black =  (100, 100, 0)

        self.perfect_color_white = (0, 255, 0)
        self.perfect_color_black = (0, 100, 0)
        
        self.wrong_color_white = (255, 0, 0)
        self.wrong_color_black = (100, 0, 0)
        
        self.pausenote = -999
        
        # Initialize scoring system
        self.score = 0
        self.points_for_hit_perfect = 100  # Points awarded for accurately hitting a note 'perfect'
        self.points_for_hit_okay = 50  # Points awarded for accurately hitting a note 'okay'
        self.points_for_hit_bad = 0  # Points awarded for hitting a note 'badly'
        
        self.points_for_hold = 10   # Points awarded per second for holding the note correctly 
        
        #Define back button
        self.back_button = pyglet.shapes.Rectangle(10, self.window.height - 40, 100, 30, color=(50, 50, 50), batch = self.game_elements_batch)

        self.back_button_label = pyglet.text.Label(
            "Back", font_name='Times New Roman', font_size=18,
            x=60, y=self.window.height - 25, anchor_x='center', anchor_y='center', batch = self.game_elements_batch
        )

        #Handle mouse press for back button
        self.window.push_handlers(on_mouse_press=self.on_mouse_press)
         
        # Flag for game over
        self.game_over = False
        
        # Game over label
        self.game_over_label = pyglet.text.Label(
            "GAME OVER", 
            font_name='Times New Roman', 
            font_size=48, 
            x=self.window.width // 2, 
            y=self.window.height // 2, 
            anchor_x='center', 
            anchor_y='center', 
            color=(255, 255, 255, 255),  # Red color
        )
        
        self.threads = []
        
        print(self.game_mode)
        #INITIALIZE GAME MODES
        if self.game_mode == "Challenge":
            
            #Schedule score update function
            pyglet.clock.schedule_interval(self.update_score, 1/4)
            
        #Load MIDI file / Starting game
        if self.game_mode != "FreePlay" and self.game_mode!= "JukeBox" and midi_file_path is not None:
                  
            keyboard_thread = threading.Thread(target=self.play_piano_user)
            self.threads.append(keyboard_thread)
            keyboard_thread.start()
          
            #Schedule updating rectangles function to move things down constantly.
            pyglet.clock.schedule_interval(self.update_rectangles, 1/60.0)
           
            #load file in; begin game
            self.load_midi_file(midi_file_path)
            
        elif self.game_mode == "FreePlay":
            #Open the input port for the piano user. Allow playing piano, but no game.
            keyboard_thread = threading.Thread(target=self.play_piano_user)
            self.threads.append(keyboard_thread)
            keyboard_thread.start()
            
        elif self.game_mode == "JukeBox":            
            #Automatic piano playing mode. No user input.
            jukebox_thread = threading.Thread(target=self.jukebox_mode, args=(midi_file_path,))
            self.threads.append(jukebox_thread)
            jukebox_thread.start()
        
        


    def load_midi_file(self, midi_file_path):
        """
        Load a MIDI file into the game.
        Utilizes the MIDIProcessor class from midi_processor.py

        Parameters
        ----------
        midi_file_path : str
            The path to the MIDI file.
        """
        
        
        self.midi_processor = MIDIProcessor(midi_file_path)
        
        track_number = 0 #Assuming we only using the first track for now...
        track_messages = self.midi_processor.extract_track_messages(track_number)
        
        track_messages2 = []

        if track_messages == []:
            track_number = 1
            track_messages2 = self.midi_processor.extract_track_messages(track_number)
            
            
            
        if self.player_count == 1:
            if track_messages != []:
                pyglet.clock.schedule_once(self.start_rectangle_game_thread, 0, track_messages, 1)
                
            elif track_messages2 != []:
                pyglet.clock.schedule_once(self.start_rectangle_game_thread, 0, track_messages2, 1)
                
            else:
                print("This song is could not be played. Tracks zero and 1 are both unavailable.")
                self.exit_game()
        
        
        elif self.player_count == 2:
            
            try:
                track_messages2 = self.midi_processor.extract_track_messages(1)
                
                if track_messages2 != [] and track_messages != []:
                    pyglet.clock.schedule_once(self.start_rectangle_game_thread, 0, track_messages, 1)
                    pyglet.clock.schedule_once(self.start_rectangle_game_thread, 0, track_messages2, 2)
                else:
                    print("This song is not suitable for two players.")
                    self.exit_game()

            except:
                print("This song is not suitable for two players.")
                self.exit_game()
                
            finally:
                'Do nothing...'

        
    def play_piano_user(self):
        """
        Allow user to  play the piano using the MIDI keyboard.
        Starts a seperate thread to avoid blocking the main thread.
        Allows user to play the piano in real time with no interference with/from the game.
        """
        
        import time  # Import time module for sleep
        
        if self.inport_name is not None:
            try:
                inport = mido.open_input(self.inport_name)  # Open the MIDI input port
                print("Input port opened successfully.")
                while self.game_active:
                    msg = inport.poll()  # Non-blocking receive, immediately returns None if no message is available

                    if msg:
                        # Check for note_on and note_off events:
                        if msg.type == "note_on" and msg.velocity != 0:
                            self.highlight_key(msg.note)  # Highlight the key
                            self.outport.send(msg)  # Send the message out if necessary
                            self.playing_notes[msg.note] = True

                            if self.paused == True and self.pausenote == msg.note:
                                print("Resuming game...")
                                self.clock_pause_manager.resume()
                                self.paused = False
                                """Race condition betwween pause and unpause..."""

                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            self.unhighlight_key(msg.note)  # Unhighlight the key
                            self.outport.send(msg)  # Send the message out if necessary
                            self.playing_notes[msg.note] = False

                    time.sleep(0.0001)  # Sleep for a very short time to prevent high CPU usage
            finally:
                inport.close()  # Ensure the input port is closed properly
                print("Thread ended.")  # Confirm the thread has ended

    # Function to create a single piano white key
    def create_white_key(self, x, y, width, height, color):
        """
        Create a piano white key.

        Parameters
        ----------
        x : int
            The x-coordinate of the key.
        y : int
            The y-coordinate of the key.
        width : int
            The width of the key.
        height : int
            The height of the key.
        color : tuple
            The color of the key.

        Returns
        -------
        pyglet.shapes.Rectangle
            The created white key.
        """
        return pyglet.shapes.Rectangle(x, y, width, height, color=color, batch = self.white_keys_batch)

    # Function to create a single piano black key
    def create_black_key(self, x, y, width, height, color):
        """
        Create a piano black key.

        Parameters
        ----------
        x : int
            The x-coordinate of the key.
        y : int
            The y-coordinate of the key.
        width : int
            The width of the key.
        height : int
            The height of the key.
        color : tuple
            The color of the key.

        Returns
        -------
        pyglet.shapes.Rectangle
            The created black key.
        """
        return pyglet.shapes.Rectangle(x, y, width, height, color=color, batch = self.black_keys_batch)
    
    def get_note_label_color(self, note_name):
        """
        Get the color for the note label.
        Default to black if not found.

        Parameters
        ----------
        note_name : str
            The name of the note.

        Returns
        -------
        tuple
            The color of the note label.
        """
        return self.note_label_colors.get(note_name[0], (0, 0, 0, 255))  # Default to black if not found

    # Function to create the entire piano, using single white and black keys.
    def create_piano(self):
        """
        Utilize create_white_key and create_black_key to create the entire piano with all keys.
        There are two modes for the piano, 49 key and 88 key.
        A parameter passed into the class will determine which mode to use.
        See attribute 'controller_size' for more details.
        """

        number_white_keys = 52  # 52 white keys in total

        #I black keys should be 2/3 height of the white key and half the whidth.

        # White Key size:
        white_key_width = self.white_key_width
        white_key_height = self.white_key_height

        # Black key size:
        black_key_width = white_key_width / 2
        black_key_height = white_key_height * (2 / 3)

        # Piano location:
        
        # Center the piano in the window
        x_position = (self.window.width - white_key_width * number_white_keys) / 2
        
        """
        Here we can define the size of the piano. If we are using the small piano mode, we will attempt center the 49 key piano in the window. Questionable logic but it looks right...
        If we are using the full piano mode, we will use the full width of the window. 
        """ 
        if self.controller_size == '49 key': #If we are using the small piano mode...
            x_position = (self.window.width - white_key_width * number_white_keys) / 2 + (white_key_width * 2.5) #Center the piano in the window. Logic weird but it looks right
            
        else: #If we are using the full piano mode...
            x_position = (self.window.width - white_key_width * number_white_keys) / 2
        
        y_position = 0
        border_size = 1

        # 21 is the lowest MIDI note on our piano. Start out couting at 20 for 'zero'
        midi_key_counter = 20
        
        # Create the piano keys
        for i in range(number_white_keys):  # 52 white keys in total

            # Create white key
            white_key = self.create_white_key(
                x_position + border_size, 0, white_key_width - 2 * border_size, white_key_height - 2 * border_size, (255, 255, 255))
            midi_key_counter += 1
            
            """
            Again here we can make changes based on size of piano we desire
            If we are using the small piano mode, we will gray out the keys that are not in the range of the small piano!
            """
            if self.controller_size == '49 key': #If we are using the small piano mode...
                if midi_key_counter <= 35 or 85 <= midi_key_counter : #If we are using the small piano mode...
                    white_key.color = (100, 100, 100) #Gray out the keys that are not in the range of the small piano.
                    
            else:
                #white_key.color = (255, 255, 255) The keys are already white as defined above on initialization... no need to change them.
                pass
                
            self.all_midi_keys.append((white_key, midi_key_counter))
            
            
            #This is not part of the piano itself, but lines to help the user see. To the right of every line is the C key.
            if (midi_key_counter - 24) % 12 == 0:
                self.visibility_lines.append(pyglet.shapes.Line(
                x_position, self.white_key_height, x_position, self.window.height, width=1, color=(123, 123, 123), batch = self.game_elements_batch))  # Add this line
                
            
            # Add note name label for white key
            note_name = self.note_names[midi_key_counter]
            note_label_color = self.get_note_label_color(note_name)
            
            if midi_key_counter == 60:  # Special case for labelling middle C
                
                # Draw the colored circle for middle C
                circle = pyglet.shapes.Circle(
                    x=x_position + white_key_width / 2,
                    y=y_position + white_key_height / 7,
                    radius=16,  # Adjust radius as needed
                    color=note_label_color[:3],  # Use the color defined for C
                    batch = self.white_keys_batch
                )
                
                self.middle_c_special_label = circle
                
                # Draw the note label in white
                note_label = pyglet.text.Label(
                    note_name,
                    font_name='Georgia',
                    bold=True,
                    font_size=23,
                    x= (x_position + white_key_width / 2) - 2, # Adjust x position as needed... it was looking weird.
                    y=y_position + white_key_height / 7,
                    anchor_x='center',
                    anchor_y='center',
                    color=(255, 255, 255, 255),  # White color
                    batch = self.white_keys_batch
                )
                
                self.white_keys.append((white_key, note_label))
            else:
                note_label = pyglet.text.Label(
                    note_name,
                    font_name='Georgia',
                    bold=True,
                    font_size=23,
                    x=x_position + white_key_width / 2,
                    y=y_position + white_key_height / 7,
                    anchor_x='center',
                    anchor_y='center',
                    color=note_label_color,
                    batch = self.white_keys_batch
                )
                self.white_keys.append((white_key, note_label))
            
            # Base case: place a black key between the first and second white keys
            if i == 0:
                
                #Create black key
                black_key_x = x_position + white_key_width - border_size - black_key_width / 2
                black_key_y = y_position + white_key_height - black_key_height
                black_key = self.create_black_key(
                    black_key_x, black_key_y, black_key_width, black_key_height, (0, 0, 0))

                midi_key_counter += 1
                self.all_midi_keys.append((black_key, midi_key_counter))
                

                """
                # Add note name label for black key
                note_label = pyglet.text.Label(
                    self.note_names[midi_key_counter],
                    font_name='Times New Roman',
                    font_size=23,
                    x=black_key_x + black_key_width / 2,
                    y=black_key_y + black_key_height - 10,
                    anchor_x='center',
                    anchor_y='center',
                    color=(255, 255, 255, 255)
                )
                """
                note_label = None
                
                #Insert black key into list with note label
                self.black_keys.append((black_key, note_label))

            # Repeating pattern: place black keys for the remaining white keys
            elif (1 <= (i - 1) % 7 <= 2) or (4 <= (i - 1) % 7 <= 6):
                # Algorithm Generated with precise instruction of GPT4.

                # Create black key
                if i < 51:  # Ensure there's a white key after the current one
                    black_key_x = x_position + white_key_width - border_size - black_key_width / 2
                    black_key_y = y_position + white_key_height - black_key_height
                    black_key = self.create_black_key(
                        black_key_x, black_key_y, black_key_width, black_key_height, (0, 0, 0))

                    midi_key_counter += 1
                    self.all_midi_keys.append((black_key, midi_key_counter))

                    """
                    # Add note name label for black key
                    note_label = pyglet.text.Label(
                        self.note_names[midi_key_counter],
                        font_name='Times New Roman',
                        font_size=10,
                        x=black_key_x + black_key_width / 2,
                        y=black_key_y + black_key_height - 10,
                        anchor_x='center',
                        anchor_y='center',
                        color=(255, 255, 255, 255)
                    )
                    """
                    note_label = None

                    self.black_keys.append((black_key, note_label))
                    
            # Move to the next key position
            x_position += white_key_width

        # Draw the piano keys and labels

    # Function to draw 'imaginary' line where our notes will fall from
    def create_active_notes_line(self):
        """
        Create 'imaginary' line where notes will fall from.
        This lines up with the piano keys and utilizes very similar logic to the create_piano function.
        """
        
        number_white_keys = 52  # 52 white keys in total
        
        white_key_width = self.white_key_width
        black_key_width = white_key_width / 2

        y_position = self.window.height # Position the line near the top of the window
        x_position = (self.window.width - white_key_width * number_white_keys) / 2

        """
        Similar to the create_piano function, we will setup based on the size of the piano we are using.
        """        
        if  self.controller_size == '49 key':
            x_position = (self.window.width - white_key_width * number_white_keys) / 2 + (white_key_width * 2.5) #Center the piano in the window
        
        else:
            x_position = (self.window.width - white_key_width * number_white_keys) / 2
        
        border_size = 1
        height = 6
        midi_key_counter = 21  # Starting MIDI note for the lowest white key

        # Create the active notes line segments
        for i in range(52):  # Iterate over the 52 positions for white keys
            # Create segment for white key
            white_key_segment = pyglet.shapes.Rectangle(
                x_position + border_size, y_position, white_key_width - 2 * border_size, height, color=(255, 255, 255))
            self.active_notes_line_segments[midi_key_counter] = white_key_segment
            midi_key_counter += 1  # Increment MIDI key counter for each key

            # Check if a black key should be placed
            if i == 0 or (1 <= (i - 1) % 7 <= 2) or (4 <= (i - 1) % 7 <= 6):
                if i < 51:  # Ensure there's a white key after the current one
                    # Create segment for black key
                    black_key_x = x_position + white_key_width - border_size - black_key_width / 2
                    black_key_segment = pyglet.shapes.Rectangle(
                        black_key_x, y_position, black_key_width, height, color=(0, 0, 0))
                    self.active_notes_line_segments[midi_key_counter] = black_key_segment
                    midi_key_counter += 1  # Increment MIDI key counter for black key

            # Move to the next key position
            x_position += white_key_width

            
    # Function to draw all aspects of the game. This includes pianos, rectangles and any other buttons. This method is called automatically by Pyglet every frame.
    def on_draw(self):
        """
        Draw all aspects of the game. This method is called automatically by Pyglet every frame.
        """

        self.window.clear()
        
        if self.window.game_state == 'GAME':
            
            self.rectangles_batch.draw()
            self.white_keys_batch.draw()
            self.black_keys_batch.draw()
            self.game_elements_batch.draw()
            
            #self.fps_display.draw()

            """
           if self.game_mode == "Challenge":
                # Draw score
                score_text = f"{self.score}"
                score_label = pyglet.text.Label(
                    score_text,
                    font_name='Times New Roman',
                    font_size=36,
                    x=self.window.width - 10,
                    y=self.window.height - 10,
                    anchor_x='right',
                    anchor_y='top',
                    color=(255, 255, 255, 255)  # White color
                )
                score_label.draw()
        
                """        
            
            # Draw Game Over message if the game is over
            if self.game_over:
                self.game_over_label.draw()

            
      

                
    # Function to highlight a specific key based on the key number
    def highlight_key(self, key_number):
        """
        Highlight a specific key based on the key number.

        Parameters
        ----------
        key_number : int
            The number of the key to highlight.
        """
        
        color = (0, 0, 0)
        black_color = (0, 0, 0)
        
        # if key number in not in valid range, pass ~ error catching
        if key_number not in range(21, 109): 
            return # Do nothing if the key number is out of range
        
        
        #Check if game is in FreePlay mode. If so, we will highlight all keys the same color.
        if self.game_mode == "FreePlay":
            color = self.perfect_color_white
            black_color = self.perfect_color_black
        
        # Else if not freeplay, assign colors based on the note timing.
        else:
            if self.incoming_notes[key_number]['note_timing'] == 1:
                color = self.okay_color_white
                black_color = self.okay_color_black
                
                #Add points for playing the note 'okay', ONE TIME only.
                if self.incoming_notes[key_number]['note_played'] == 0:
                    self.incoming_notes[key_number]['note_played'] = 1
                    self.score += self.points_for_hit_okay
                
            elif self.incoming_notes[key_number]['note_timing'] == 2:
                color = self.perfect_color_white
                black_color = self.perfect_color_black
                
                #Add points for playing the note perfectly, ONE TIME only.
                if self.incoming_notes[key_number]['note_played'] == 0:
                    self.incoming_notes[key_number]['note_played'] = 1
                    self.score += self.points_for_hit_perfect
                    
            else:
                color = self.wrong_color_white
                black_color = self.wrong_color_black
        

        #Apply color to the key
        #Is it a black key? True/False...
        is_black_key = key_number in self.black_keys_midi 
        
        for key, midi_number in self.all_midi_keys:
            if midi_number == key_number:
                
                if is_black_key:
                    key.color = black_color
                else:
                    key.color = color
                return

    # Function to unhighlight a specific key based on the key number
    def unhighlight_key(self, key_number):
        """
        Unhighlight a specific key based on the key number.

        Parameters
        ----------
        key_number : int
            The number of the key to unhighlight.
        """
        # Is black key?
        is_black_key = key_number in self.black_keys_midi

        for key, midi_number in self.all_midi_keys:
            if midi_number == key_number:
                if is_black_key:
                    key.color = (0, 0, 0)
                else:
                    # We need to check if the key is outside the small piano range, and if so return it to grayed.
                    if self.controller_size == '49 key':
                        if midi_number <= 35 or 85 <= midi_number:
                            key.color = (100, 100, 100)
                        else:
                            key.color = (255, 255, 255)
                    else: #If we are using the full piano mode, every key is white.
                        key.color = (255, 255, 255)
                return
    
    # Function to prepare a falling rectangle for a specific note number
    def prepare_falling_rectangle(self, note_number, player):
        """
        Prepare a falling rectangle for a specific note number.

        Parameters
        ----------
        note_number : int
            The number of the note.
        player : int
            The player number.

        Returns
        -------
        pyglet.shapes.BorderedRectangle
            The created falling rectangle.
        """
       
        # Where it's at?
        reference_segment = self.active_notes_line_segments[note_number]

        x_pos = reference_segment.x
        y_pos = reference_segment.y
        width = reference_segment.width
        height = 0  # Initial height of the rectangle
        
        if player == 1:
            inner_color = (137, 207, 240)  # Inner color for white keys

            if note_number in self.black_keys_midi:
                inner_color = (70, 130, 255)  # Different inner color for black keys
        
        elif player == 2:
            inner_color = (255, 130, 67)
            
            if note_number in self.black_keys_midi:
                inner_color = (150, 80, 33)

        border_color = (0, 0, 0)  # Black border for visibility
        border_thickness = 2  # Thickness of the border

        # Create the bordered rectangle
        new_rectangle = pyglet.shapes.BorderedRectangle(
            x=x_pos, 
            y=y_pos, 
            width=width, 
            height=height, 
            border=border_thickness, 
            color=inner_color, 
            border_color=border_color,
            batch = self.rectangles_batch
        )

        # Custom attributes for logic handling
        new_rectangle.note_number = note_number
        new_rectangle.lock = False
        new_rectangle.played = False
        new_rectangle.note_off = False
        new_rectangle.negative_y = 0

        timestamp = datetime.datetime.now().timestamp()
        unique_id = f"{note_number}_{timestamp}"
        new_rectangle.unique_id = unique_id
        
        self.active_note_events[unique_id] = {'rectangle': new_rectangle, 'note_number': note_number, 'locked': False, 'played': False}
        return new_rectangle

    # Function to schedule notes for our Piano game. 
    def start_rectangle_game(self, dt, track_messages, player):
        
        """
        Function to schedule notes for our Piano game. 
        This function is called during initialization by the MIDIProcessor class.

        Parameters
        ----------
        dt : float 
            The delta time.
        track_messages : list
            The list of track messages.
        player : int
            The player number.
        """
        

        total_delay = 0
        buffer_time = 7  # 10 seconds buffer time for end of song
        

        for msg, delay in track_messages:
        
            #We can't have delay zero or else 2 messages will get scheduled at the same time...
            #If two messages are scheduled at same time, there are bugs. Add tiny delay to avoid this... hope this delay doesn't accumulate and cause more issues. :')
            if delay == 0:
                delay = 0.000001
                
            total_delay += delay
        
            
            if msg.type == 'note_on' and msg.velocity != 0:
                    
                func = lambda dt, note=msg.note, velocity=msg.velocity, player=player: self.schedule_flag_note_on(dt, note, velocity, player)                
                self.clock_pause_manager.schedule_function(func, delay=total_delay)
                
                #pyglet.clock.schedule_once(self.schedule_flag_note_on, total_delay, note=msg.note, velocity=msg.velocity)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                
                
                func = lambda dt, note=msg.note, velocity=msg.velocity: self.schedule_flag_note_off(dt, note, velocity)                
                self.clock_pause_manager.schedule_function(func, delay=total_delay)
                                                        
                #pyglet.clock.schedule_once(self.schedule_flag_note_off, total_delay, note=msg.note)
                
            
        #print(f"Total delay: {total_delay}")
    
        # Schedule end of the song with buffer time using ClockPauseManager
        self.clock_pause_manager.schedule_function(self.end_of_song, total_delay + buffer_time)
        
    def start_rectangle_game_thread(self, dt, track_messages, player):
        """
        Wrapper function for threading.
        Just calls start_rectangle_game with the given parameters and starts the seperate game thread.

        Parameters
        ----------
        dt : float
            The delta time.
        track_messages : list
            The list of track messages.
        player : int
            The player number.
        """
        game_thread = threading.Thread(target=self.start_rectangle_game, args=(dt, track_messages, player))
        game_thread.start()
        
    def end_of_song(self, dt):
        """
        Acknowledge the end of the song.
        Once the song is over, on_draw will display the game over message.

        Parameters
        ----------
        dt : float
            The delta time.
        """
        
        # Acknowledge end of the song
        self.game_over = True
    
    # Function to flag a note as being played or not
    def flag_note(self, note_number, bool):
        """
        Flag a note as being played or not.

        Parameters
        ----------
        note_number : int
            The number of the note.
        bool : bool
            Flag indicating if the note is played.
        """
        # Directly flagging note_on or note_off without iterating every time
        unique_id = None
        # Attempt to find the most recent matching note_number event that's not locked yet
        for event_id, event_data in sorted(self.active_note_events.items(), key=lambda x: x[0], reverse=True): 
            if f"{note_number}_" in event_id and not event_data['locked']:
                unique_id = event_id
                if bool is False and unique_id:
                    self.active_note_events[unique_id]['locked'] = True
                    self.active_note_events[unique_id]['rectangle'].lock = True
                    
                break
            
        if bool:
            pass

    # Function to schedule a note to be flagged as being played 
    def schedule_flag_note_on(self, dt, note, velocity, player):
        """
        Schedule a note to be flagged as being played.

        Parameters
        ----------
        dt : float
            The delta time.
        note : int
            The note number.
        velocity : int
            The velocity of the note.
        player : int
            The player number.
        """
        new_rectangle = self.prepare_falling_rectangle(note, player)
        self.falling_rectangles_list.append(new_rectangle)
        self.flag_note(note, True)

    # Function to schedule a note to be flagged as not being played
    def schedule_flag_note_off(self, dt, note, velocity):
        """
        Schedule a note to be flagged as not being played.

        Parameters
        ----------
        dt : float
            The delta time.
        note : int
            The note number.
        velocity : int
            The velocity of the note.
        """
        self.flag_note(note, False)

    # Function to update the falling rectangles
    def update_rectangles(self, dt):
        """
        Update the falling rectangles.
        This function is called every frame to update the falling rectangles.
        Most of the logic for the game is handled here.
        A deep understanding of the game logic is recommended before making changes here.

        Parameters
        ----------
        dt : float
            The delta time.
        """
        
        cleanup_list = []

        move_speed = 150  # Speed of the falling rectangles
        for rectangle in (self.falling_rectangles_list):
            
           # print("Top of this rectangle is: ", rectangle.y + rectangle.height, " and the note number is: ", rectangle.note_number)
           # print("Bottom of this rectangle is: ", rectangle.y)
            
            
            if rectangle.lock is False:
                rectangle.height += move_speed * dt

            if rectangle.y >= self.white_key_height:
                rectangle.y -= move_speed * dt

            if rectangle.y <= self.white_key_height + 70 and rectangle.y > self.white_key_height + 20 and self.incoming_notes[rectangle.note_number]['note_timing'] != 2:
                # we need to flag this note as 'close' to the line segment
                self.incoming_notes[rectangle.note_number]['note_timing'] = 1

            elif rectangle.y <= self.white_key_height + 20 and rectangle.y >= self.white_key_height - 20:
                self.incoming_notes[rectangle.note_number]['note_timing'] = 2
                
            if rectangle.height == 1:
                """THIS WAS A TEST! REMOVE THIS LATER!"""
                # please see this comment ^ !!
                # !
                rectangle.color = (0, 255, 0)
                cleanup_list.append(rectangle)

            if rectangle.y <= self.white_key_height and rectangle.played == True:
            
                diff = self.white_key_height - rectangle.y
                rectangle.height -= diff
                rectangle.negative_y += diff
                rectangle.y = self.white_key_height
    
                if rectangle.height > 0 and rectangle.negative_y > 20:
                    self.incoming_notes[rectangle.note_number]['note_timing'] = 1

                #Setup for next rectangle being played...
                if rectangle.height <= 0:
                    rectangle.height = 0
                    self.incoming_notes[rectangle.note_number]['note_timing'] = 0
                    self.incoming_notes[rectangle.note_number]['note_played'] = 0
                    
                    if self.testing_autoplay == True and rectangle.note_off == False and self.playing_notes[rectangle.note_number] == True:
                        rectangle.note_off = True
                        off_message = mido.Message('note_off', note= rectangle.note_number)
                        self.outport.send(off_message)
                        self.playing_notes[rectangle.note_number] = False
                        self.unhighlight_key(rectangle.note_number)
                        
                    cleanup_list.append(rectangle)

            elif rectangle.y <= self.white_key_height and rectangle.played == False:
                
                diff = self.white_key_height - rectangle.y
                rectangle.height -= diff
                rectangle.y = self.white_key_height
                rectangle.negative_y += diff
                
                if rectangle.height < 0:
                    #Catch this visual error?
                    rectangle.height = 0
            
                if self.playing_notes[rectangle.note_number] == False:
                    
                    rectangle.played = True
                    if self.testing_autoplay == True:
                        on_message = mido.Message('note_on', note= rectangle.note_number)
                        self.outport.send(on_message)
                        self.highlight_key(rectangle.note_number)
                        self.playing_notes[rectangle.note_number] = True
                        continue
    

                """LOGIC FOR PRACTICE GAME MODE"""
                if self.game_mode == "Practice":
                    (key_in_question, note_number) = self.all_midi_keys[rectangle.note_number - 21]
                    #print key in question color
                    #print("Key in question color is: ", key_in_question.color)
                    #print("The colors we are checking for are: ", self.okay_color_white, self.okay_color_black, self.perfect_color_white, self.perfect_color_black)
                    if key_in_question.color in (self.okay_color_white, self.okay_color_white + (255,),
                                                 self.okay_color_black, self.okay_color_black +  (255,),
                                                 self.perfect_color_white, self.perfect_color_white +  (255,),
                                                 self.perfect_color_black, self.perfect_color_black +  (255,)
                                                ) and self.paused == False:
                        print("You played the right note!")
                    else:
                        print("You didn't play the right note!")
                        self.pausenote = note_number
                        self.clock_pause_manager.pause()
                        self.paused = True
                                        
        for rectangle in cleanup_list:
            self.falling_rectangles_list.remove(rectangle)
            rectangle.delete()
            del rectangle
              
    # Method for handling mouse press to quit the game... can also use backspace but this is more intuitive.
    def on_mouse_press(self, x, y, button, modifiers):
        """
        Handle mouse press to quit the game.

        Parameters
        ----------
        x : int
            The x-coordinate of the mouse press.
        y : int
            The y-coordinate of the mouse press.
        button : int
            The mouse button pressed.
        modifiers : int
            Any modifier keys pressed.
        """
        
        # Check if the back button is clicked
        if (10 <= x <= 110) and (self.window.height - 40 <= y <= self.window.height - 10):
            self.exit_game()
            return


    def exit_game(self):
        """
        Exit the game and clean up resources.
        """
        self.game_active = False

        # Terminate all running threads
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1)

        self.threads = []

        self.clock_pause_manager.clear()
        
        if self.outport is not None:
            self.outport.reset()
            self.outport.close()

        self.active_notes = {note: False for note in range(21, 109)}
        self.playing_notes = {note: False for note in range(21, 109)}
        self.incoming_notes = {note: {'note_timing': 0, 'note_played': 0} for note in range(21, 109)}

        for rectangle in self.falling_rectangles_list:
            rectangle.delete()
        self.falling_rectangles_list.clear()

        # Reinitialize batches to reset graphics
        self.white_keys_batch = pyglet.graphics.Batch()
        self.black_keys_batch = pyglet.graphics.Batch()
        self.game_elements_batch = pyglet.graphics.Batch()
        self.rectangles_batch = pyglet.graphics.Batch()

        self.active_note_events.clear()
        self.score = 0

        self.window.remove_handlers(on_draw=self.on_draw, on_key_press=self.on_key_press)
        self.window.pop_handlers()
        self.game_over = False
        self.window.return_to_menu()
        print("Game exited cleanly.")

                
    #Custom Keybinds for Development...
    def on_key_press(self, symbol, modifiers):
    
        """
        Handle custom keybinds for development.

        Parameters
        ----------
        symbol : int
            The key symbol pressed.
        modifiers : int
            Any modifier keys pressed.
        """
  
        #Custom keybinds for development:    
        #QUIT THE GAME // RETURN TO MENU
        if symbol == pyglet.window.key.BACKSPACE:
            print("Backspace pressed")
            self.exit_game()
                
        #PAUSE THE GAME ~ USEFUL FOR DEBUGGING PRACTICE MODE:
        if symbol == pyglet.window.key.B:
            print("B pressed")
        
        """
        if symbol == pyglet.window.key.P:
            print("P pressed")
            
            if not self.clock_pause_manager.paused:
                self.clock_pause_manager.pause()
                
                
                
            elif self.clock_pause_manager.paused:
                self.clock_pause_manager.resume()
                
                
             
            print("total seconds played", datetime.datetime.now() - self.clock_pause_manager.start_time)  
        """
        
    
    def update_score(self, dt):
        """
        Update the score based on currently playing notes.

        Parameters
        ----------
        dt : float
            The delta time.
        """
        
        for note in self.playing_notes:
            if self.playing_notes[note] == True:
                #Refresh highlight
                
                if self.incoming_notes[note]['note_timing'] == 0:
                    self.highlight_key(note)
                
                if self.incoming_notes[note]['note_timing'] != 0:
                    self.score += self.points_for_hold
        

                
    def jukebox_mode(self, midi_file_path):
        """
        Play the piano automatically in jukebox mode.

        Parameters
        ----------
        midi_file_path : str
            The path to the MIDI file to be played.
        """
        
        #We can change the color of our highlight keys here if needed
        # self.perfect_color_white = (106, 90 , 205)
        # self.perfect_color_black = (75, 0, 130)
        
        #The highlight function will use these colors to determine if the note was played correctly.
        #It usually highlights "Wrong" notes in red, and since the game is not running every note is being considered "wrong"
        #but we can change that here to all notes are highlighted any color we desire.
        self.wrong_color_black = self.perfect_color_black
        self.wrong_color_white = self.perfect_color_white
    
        if midi_file_path is not None and self.outport is not None:
        
            song = mido.MidiFile(midi_file_path)
            
            for msg in song.play():
                
                #If the game is not active, stop playing the song! Error catching
                if self.game_active == False:
                    return
            
                #Else play  the song.
                elif msg.type == "note_on" and msg.velocity != 0:
                    self.highlight_key(msg.note)
                    
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    self.unhighlight_key(msg.note)
                  
                    
                self.outport.send(msg)
        
            
class ClockPauseManager():
    """
    ClockPauseManager is responsible for managing the clock and scheduled functions,
    allowing pausing and resuming of the game. Mostly used for the Piano game in practice mode.
    The implementation is based on the Pyglet clock and scheduling functions.
    
    This method is buggy and needs to be improved in future development!

    Attributes
    ----------
    scheduled_functions : list
        List of scheduled functions.
    start_time : datetime.datetime
        The start time of the game.
    update_rectangles : callable
        Method to update rectangles.
    paused : bool
        Flag indicating if the game is paused.
    pause_time : datetime.datetime
        The time when the game was paused.
    unpause_time : datetime.datetime
        The time when the game was unpaused.
    """
    
    def __init__(self, update_rectangles):
        """
        Initialize the ClockPauseManager.

        Parameters
        ----------
        update_rectangles : callable
            Method to update rectangles.
        """
        self.scheduled_functions = []
        self.start_time = datetime.datetime.now()
        self.update_rectangles = update_rectangles
        self.paused = False
        self.pause_time = 0
        self.unpause_time = 0



    def schedule_function(self, func, delay):
        """
        Schedule a function with a delay.

        Parameters
        ----------
        func : callable
            The function to be scheduled.
        delay : float
            The delay in seconds.
        """
        #print(f"Scheduling function {func} with delay {delay}")
       
        scheduled_funcID = pyglet.clock.schedule_once(func, delay)
        self.scheduled_functions.append((func, delay, scheduled_funcID))
        
    def pause(self):
        """
        Pause the clock and all scheduled functions.
        """
        
        if not self.paused:
            for func, _, _ in self.scheduled_functions:
                pyglet.clock.unschedule(func)
            pyglet.clock.unschedule(self.update_rectangles)
            self.paused = True
            self.pause_time = datetime.datetime.now()


            
            
    def resume(self):
        """
        Resume the clock and all scheduled functions with adjusted intervals.
        """
        
        seconds_before_pause = self.pause_time - self.start_time
        seconds_before_pause = seconds_before_pause.total_seconds()
        pyglet.clock.schedule_interval(self.update_rectangles, 1/60.0)

        new_scheduled_functions = []
        
        temp_counter = 0
        
        if self.paused:
            self.paused = False

            for i, (func, delay, scheduled_funcID) in enumerate(self.scheduled_functions):
                
                # Reschedule with the remaining time 
                #print(f"Rescheduling function {func} with delay {delay} and time difference {seconds_before_pause}")
                remaining_delay = delay - seconds_before_pause
            
                if remaining_delay >= 0:
                    # If there's remaining delay, reschedule the function
                    pyglet.clock.schedule_once(func, remaining_delay)
                    # Add the adjusted function back into the new list
                    new_scheduled_functions.append((func, remaining_delay, scheduled_funcID))
                    
                    if temp_counter <= 1:
                        """  
                        print(f"Rescheduling function {func}({temp_counter}) with delay {remaining_delay}")
                        print(f"Original delay: {delay}")
                        print(f"Start time was: {self.start_time.time()} and pause time was: {self.pause_time.time()}")
                        print(f"Time difference: {seconds_before_pause}")
                        print(f"New delay: {remaining_delay}")
                        print("The current time is: ", datetime.datetime.now().time())
                        print("-------------------")
                        """
                        temp_counter += 1
                    
                else:
                    # Log or handle the case where the function's scheduled time has passed
                    #print(f"Skipping rescheduling of {func} due to elapsed delay.")
                    pass

            # Replace the original scheduled functions list with the new, adjusted list
            self.scheduled_functions = new_scheduled_functions

            # Reset the start time and unpause
            self.start_time = datetime.datetime.now()

    def clear(self):    
        """
        Clear all scheduled functions and reset the pause state.
        """
        for func, _, _ in self.scheduled_functions:
            pyglet.clock.unschedule(func)
        pyglet.clock.unschedule(self.update_rectangles)        
        self.scheduled_functions = []
        self.paused = False
