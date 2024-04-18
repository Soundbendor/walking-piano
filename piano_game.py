import pyglet
import mido
import datetime
import threading
from midi_processor import MIDIProcessor


class PianoGameUI(pyglet.event.EventDispatcher):
    """ A class for the piano game user interface """

    def __init__(self, window, midi_file_path, game_mode, inport_name, outport_name, player_count=1,  auto_play=False):
        """ 
        Initialize Pyglet window and other UI elements
        :param window: The Pyglet window to display the game in
        :param midi_file_path: The path to the MIDI file to play
        :param game_mode: The game mode to play (Challenge, Practice, FreePlay, JukeBox)
        :param inport_name: The name of the MIDI input port to use
        :param outport_name: The name of the MIDI output port to use
        :param player_count: The number of players in the game
        :param auto_play: Whether to automatically play the piano
        """

        # Create a window
        self.window = window

        # Open outport You may need to change this to your specific MIDI port in settings.
        if outport_name is not None:
            self.outport = mido.open_output(outport_name, autoreset=True) # Open the MIDI output port
        
        else:
            self.outport = None
            
        # Store the MIDI input port name
        # We will open this port in seperate thread to avoid blocking the main thread.
        # See play_piano_user() for more details.
        self.inport_name = inport_name

        self.player_count = player_count

        # Array for holding white keys
        self.white_keys = []

        # Array for holding black keys
        self.black_keys = []

        # SORTED array of all MIDI keys. Allows access by MIDI notes 21-108.
        self.all_midi_keys = []         
           
        # MIDI numbers for black keys (sharps/flats) in each octave
        self.black_keys_midi = [22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58,
                                61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106]

        # Placeholder array for notes currently being drawn.
        self.active_notes = {note: False for note in range(21, 109)}
        
        # Array for tracking notes currently being played by user.
        self.playing_notes = {note: False for note in range(21, 109)}
        
        self.active_note_events = {}  # New: Dictionary to track active note events

        # Array for notes as they approach the time for being played.
        # 0 = dont play, 1 = okay 2 = perfect
        self.incoming_notes = {note: {'note_timing': 0, 'note_played': 0} for note in range(21, 109)}

        """Temp for testing visuals"""
        self.active_notes_line_segments = {}

        # Initialize falling rectangle manager
        self.falling_rectangles_list = []

        """Todo: Get this note list working with 'extract_track_messages()' from MIDIprocessor class"""
        # Create note list
        self.note_list = []
        
        self.update_rectangles = self.update_rectangles

        # Create visual for active note array
        self.create_active_notes_line()

        # Create piano keys and start game.
        self.create_piano()
        
        # Flag for game state
        self.game_active = True
        
        self.paused = False

        self.window.push_handlers(self)

        self.window.push_handlers(on_draw=self.on_draw)
        
        self.clock_pause_manager = ClockPauseManager(self.update_rectangles)
        
        # Add custom event handler for window close. This will allow us to clean up the MIDI port, and allow user to return to menu with ESC/Window close
        def on_window_close():
            self.game_active = False
            window.on_close = lambda: window.close() #Reset the close function to default
            self.exit_game()
            self.window.close()

        window.on_close = on_window_close
        
        self.game_mode = game_mode
        
        # TEMPORARY TESTING IF TRUE
        self.testing_autoplay = auto_play
        
        self.okay_color_white = (255, 255, 0, 255)
        self.okay_color_black =  (100, 100, 0, 255)

        self.perfect_color_white = (0, 255, 0, 255)
        self.perfect_color_black = (0, 100, 0, 255)
        
        self.wrong_color_white = (255, 0, 0, 255)
        self.wrong_color_black = (100, 0, 0, 255)
        
        self.pausenote = -999
        
        # Initialize scoring system
        self.score = 0
        self.points_for_hit_perfect = 100  # Points awarded for accurately hitting a note 'perfect'
        self.points_for_hit_okay = 50  # Points awarded for accurately hitting a note 'okay'
        self.points_for_hit_bad = 0  # Points awarded for hitting a note 'badly'
        
        self.points_for_hold = 10   # Points awarded per second for holding the note correctly 
        
        if self.game_mode == "Challenge":
            # Schedule score update function
            pyglet.clock.schedule_interval(self.update_score, 1/4)
            
        # Load MIDI file / Starting game
        elif self.game_mode != "FreePlay" and self.game_mode!= "JukeBox" and midi_file_path is not None:
                  
            keyboard_thread = threading.Thread(target=self.play_piano_user)
            keyboard_thread.start()
          
            # Schedule updating rectangles function to move things down constantly.
            pyglet.clock.schedule_interval(self.update_rectangles, 1/60.0)
           
            # load file in; begin game
            self.load_midi_file(midi_file_path)
            
        elif self.game_mode == "FreePlay":
            # Open the input port for the piano user. Allow playing piano, but no game.
            keyboard_thread = threading.Thread(target=self.play_piano_user)
            keyboard_thread.start()
            
        elif self.game_mode == "JukeBox":            
            # Automatic piano playing mode. No user input.
            thread = threading.Thread(target=self.jukebox_mode, args=(midi_file_path,))
            thread.start()
         
    def load_midi_file(self, midi_file_path):
        """ 
        Load a MIDI file into the game. Utilizes the MIDIProcessor class from midi_processor.py
        :param midi_file_path: The path to the MIDI file to load
        """
        
        self.midi_processor = MIDIProcessor(midi_file_path)
        
        track_number = 0 # Assuming we only using the first track for now...
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
        """ Play the piano using the computer keyboard """

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

    def create_white_key(self, x, y, width, height, color):
        """ 
        Create a piano white key
        :param x: The x-coordinate of the key
        :param y: The y-coordinate of the key
        :param width: The width of the key
        :param height: The height of the key
        :param color: The color of the key
        """
        return pyglet.shapes.Rectangle(x, y, width, height, color=color)

    def create_black_key(self, x, y, width, height, color):
        """ 
        Create a piano black key
        :param x: The x-coordinate of the key
        :param y: The y-coordinate of the key
        :param width: The width of the key
        :param height: The height of the key
        :param color: The color of the key
        """
        return pyglet.shapes.Rectangle(x, y, width, height, color=color)

    def create_piano(self):
        """ Create full piano using black and white keys """

        # White Key size:
        white_key_width = 20
        white_key_height = 100

        # Black key size:
        black_key_width = white_key_width / 2
        black_key_height = 60

        # Piano location:
        x_position = (self.window.width - white_key_width * 52) / 2
        y_position = 0
        border_size = 1

        # 21 is the lowest MIDI note on our piano. Start out counting at 20 for 'zero'
        midi_key_counter = 20

        # Create the piano keys
        for i in range(52):  # 52 white keys in total
            # Create white key
            white_key = self.create_white_key(
                x_position + border_size, 0, white_key_width - 2 * border_size, white_key_height - 2 * border_size, (255, 255, 255))
            self.white_keys.append((white_key, i + 1))

            midi_key_counter += 1
            self.all_midi_keys.append((white_key, midi_key_counter))

            # Base case: place a black key between the first and second white keys
            if i == 0:
                black_key_x = x_position + white_key_width - border_size - black_key_width / 2
                black_key_y = y_position + white_key_height - black_key_height
                black_key = self.create_black_key(
                    black_key_x, black_key_y, black_key_width, black_key_height, (0, 0, 0))
                self.black_keys.append(black_key)

                midi_key_counter += 1
                self.all_midi_keys.append((black_key, midi_key_counter))

            # Repeating pattern: place black keys for the remaining white keys
            elif (1 <= (i - 1) % 7 <= 2) or (4 <= (i - 1) % 7 <= 6):
                # Algorithm Generated with precise instruction of GPT4.

                # Create black key
                if i < 51:  # Ensure there's a white key after the current one
                    black_key_x = x_position + white_key_width - border_size - black_key_width / 2
                    black_key_y = y_position + white_key_height - black_key_height
                    black_key = self.create_black_key(
                        black_key_x, black_key_y, black_key_width, black_key_height, (0, 0, 0))
                    self.black_keys.append(black_key)

                    midi_key_counter += 1
                    self.all_midi_keys.append((black_key, midi_key_counter))

            x_position += white_key_width

        # Draw the piano keys and labels

    def create_active_notes_line(self):
        """ Create the line where active notes will fall from """

        white_key_width = 20
        black_key_width = white_key_width / 2
        y_position = self.window.height # Position the line near the top of the window
        x_position = (self.window.width - white_key_width * 52) / 2
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

    def draw_piano(self):
        """ Draw the piano keys and labels. Utilized by the on_draw function."""

        self.window.clear()
        # Draw white keys
        for white_key, _ in self.white_keys:
            white_key.draw()

        # Draw black keys
        for black_key in self.black_keys:
            black_key.draw()

    def on_draw(self):
        """ Draw the game elements. Includes the piano, falling rectangles, and other buttons. Pyglet calls this function automatically every frame."""

        self.window.clear()
        
        if self.window.game_state == 'GAME':
            # Draw the piano
            self.draw_piano()

             #Draw our line segment
            for i in self.active_notes_line_segments:
                self.active_notes_line_segments[i].draw()

            # Draw falling rectangles
            for rectangle in self.falling_rectangles_list:
                rectangle.draw()
            
            
            if self.game_mode == "Challenge":
                # Draw score
                score_text = f"Score: {self.score}"
                score_label = pyglet.text.Label(score_text, x=10, y=self.window.height - 20, anchor_x='left', anchor_y='top')
                score_label.draw()

    def highlight_key(self, key_number):
        """
        Highlight a specific key based on the key number
        :param key_number: The number of the key to highlight
        :param color: The color to highlight the key with
        """
        color = (0, 0, 0)
        black_color = (0, 0, 0)

        # if key number in not in valid range, pass ~ error catching
        # Assign colors based on the note timing.
        if key_number not in range(21, 109): 
            pass
        else:
            if self.incoming_notes[key_number]['note_timing'] == 1:
                color = self.okay_color_white
                black_color = self.okay_color_black
                
                # Add points for playing the note 'okay', ONE TIME only.
                if self.incoming_notes[key_number]['note_played'] == 0:
                    self.incoming_notes[key_number]['note_played'] = 1
                    self.score += self.points_for_hit_okay
                
            elif self.incoming_notes[key_number]['note_timing'] == 2:
                color = self.perfect_color_white
                black_color = self.perfect_color_black
                
                # Add points for playing the note perfectly, ONE TIME only.
                if self.incoming_notes[key_number]['note_played'] == 0:
                    self.incoming_notes[key_number]['note_played'] = 1
                    self.score += self.points_for_hit_perfect
                    
            else:
                color = self.wrong_color_white
                black_color = self.wrong_color_black
        
        # Apply color to the key
        # Is it a black key? True/False...
        is_black_key = key_number in self.black_keys_midi 
        
        for key, midi_number in self.all_midi_keys:
            if midi_number == key_number:
                
                if is_black_key:
                    key.color = black_color
                else:
                    key.color = color
                return

    def unhighlight_key(self, key_number):
        """
        Unhighlight a specific key based on the key number
        :param key_number: The number of the key to unhighlight
        """
        # Is black key?
        is_black_key = key_number in self.black_keys_midi

        for key, midi_number in self.all_midi_keys:
            if midi_number == key_number:
                if is_black_key:
                    key.color = (0, 0, 0)
                else:
                    # Assuming white for unhighlighted color
                    key.color = (255, 255, 255)
                return
    
    # Function to prepare a falling rectangle for a specific note number
    def prepare_falling_rectangle(self, note_number, player):
        """
        Prepare a falling rectangle for a specific note number
        :param note_number: The MIDI note number to prepare a falling rectangle for
        :param player: The player number to prepare the rectangle for
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
            border_color=border_color
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

    def start_rectangle_game(self, dt, track_messages, player):
        """
        Play notes from a MIDI track in real time
        :param dt: The time delay between notes 
        :param track_messages: The MIDI messages to play
        :param player: The player number to play the notes
        """
        #print(f"{track_messages[0]}")

        total_delay = 0
        

        for msg, delay in track_messages:
        
            # We can't have delay zero or else 2 messages will get scheduled at the same time...
            # If two messages are scheduled at same time, there are bugs. Add tiny delay to avoid this... hope this delay doesn't accumulate and cause more issues. :')
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
        #Schedule end of the song?
        
    def start_rectangle_game_thread(self, dt, track_messages, player):
        """
        Start the game in a separate thread
        :param dt: The time delay between notes
        :param track_messages: The MIDI messages to play
        :param player: The player number to play the notes
        """
        game_thread = threading.Thread(target=self.start_rectangle_game, args=(dt, track_messages, player))
        game_thread.start()

    def flag_note(self, note_number, bool):
        """
        Flag a note as being played or not
        :param note_number: The MIDI note number to flag
        :param bool: The boolean value to flag the note with
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

    def schedule_flag_note_on(self, dt, note, velocity, player):
        """ 
        Schedule a note to be flagged as being played
        :param dt: The time delay between notes
        :param note: The MIDI note number to flag
        :param velocity: The velocity of the note
        :param player: The player number to flag the note for
        """
        new_rectangle = self.prepare_falling_rectangle(note, player)
        self.falling_rectangles_list.append(new_rectangle)
        self.flag_note(note, True)

    def schedule_flag_note_off(self, dt, note, velocity):
        """
        Schedule a note to be flagged as not being played
        :param dt: The time delay between notes
        :param note: The MIDI note number to flag
        :param velocity: The velocity of the note
        """
        self.flag_note(note, False)

    def update_rectangles(self, dt):
        """
        Update the falling rectangles
        :param dt: The time delay between updates
        """

        """
        We need to fix / adjust the logic when note_off and note_on occur so close together.
        
        Improve accuracy when note hits the line. We  need to subtract difference if  it goes under the line
        """
        
        cleanup_list = []

        move_speed = 100  # Speed of the falling rectangles
        for rectangle in (self.falling_rectangles_list):
            
           # print("Top of this rectangle is: ", rectangle.y + rectangle.height, " and the note number is: ", rectangle.note_number)
           # print("Bottom of this rectangle is: ", rectangle.y)
            
            
            if rectangle.lock is False:
                rectangle.height += move_speed * dt

            if rectangle.y >= 100:
                rectangle.y -= move_speed * dt

            if rectangle.y <= 170 and rectangle.y > 120 and self.incoming_notes[rectangle.note_number]['note_timing'] != 2:
                # we need to flag this note as 'close' to the line segment
                self.incoming_notes[rectangle.note_number]['note_timing'] = 1

            elif rectangle.y <= 120 and rectangle.y >= 80:
                self.incoming_notes[rectangle.note_number]['note_timing'] = 2
                
            if rectangle.height == 1:
                rectangle.color = (0, 255, 0)
                cleanup_list.append(rectangle)

            if rectangle.y <= 100 and rectangle.played == True:
            
                diff = 100 - rectangle.y
                rectangle.height -= diff
                rectangle.negative_y += diff
                rectangle.y = 100
    
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

            elif rectangle.y <= 100 and rectangle.played == False:
                
                diff = 100 - rectangle.y
                rectangle.height -= diff
                rectangle.y = 100
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
                    if key_in_question.color in (self.okay_color_white, self.okay_color_black, self.perfect_color_white, self.perfect_color_black) and self.paused == False:
                        print("You played the right note!")
                    else:
                        print("You didn't play the right note!")
                        self.pausenote = note_number
                        self.clock_pause_manager.pause()
                        self.paused = True
                                        
        for rectangle in cleanup_list:
            self.falling_rectangles_list.remove(rectangle)
            # del self.active_note_events[rectangle.unique_id]
            del rectangle
              
                      

    def exit_game(self):
        """ Exit the game and return to the main menu """

        self.clock_pause_manager.clear()
            #Additional cleanup if needed
            
        self.game_active = False

        if self.outport is not None:
            self.outport.reset()
            self.outport.close()

        self.window.remove_handlers(on_draw=self.on_draw)
        self.window.remove_handlers(self)
        
        self.window.clear()
        
        self.window.return_to_menu()
                
    #Custom Keybinds for Development...
    def on_key_press(self, symbol, modifiers):
        """
        Handle key press events
        :param symbol: The key that was pressed
        :param modifiers: Any modifier keys that were pressed
        """
        
        # PAUSE THE GAME
        if symbol == pyglet.window.key.P:
            print("P pressed")
            
            if not self.clock_pause_manager.paused:
                self.clock_pause_manager.pause()
                
                
                
            elif self.clock_pause_manager.paused:
                self.clock_pause_manager.resume()
                
                
             
            print("total seconds played", datetime.datetime.now() - self.clock_pause_manager.start_time)  
           
        # QUIT THE GAME // RETURN TO MENU
        if symbol == pyglet.window.key.BACKSPACE:
            print("Backspace pressed")
           
            self.exit_game()
    
    def update_score(self, dt):
        """ 
        Update the score based on the notes being played
        :param dt: The time delay between score updates
        """
        for note in self.playing_notes:
            if self.playing_notes[note] == True:
                # Refresh highlight
                
                if self.incoming_notes[note]['note_timing'] == 0:
                    self.highlight_key(note)
                
                if self.incoming_notes[note]['note_timing'] != 0:
                    self.score += self.points_for_hold
                        
    def jukebox_mode(self, midi_file_path):
        """
        Play a MIDI file in automatic mode
        :param midi_file_path: The path to the MIDI file to play
        """
        
        # We can change the color of our highlight keys here.
        self.perfect_color_white = (106, 90 , 205, 255)
        self.perfect_color_black = (75, 0, 130, 255)
        
        # The highlight function will use these colors to determine if the note was played correctly.
        # It usually highlights "Wrong" notes in red, and since the game is not running every note is being considered "wrong"
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
    """ A class to manage pausing and resuming the clock and scheduled functions. """

    def __init__(self, update_rectangles):
        """ Initialize the clock pause manager """

        self.scheduled_functions = []
        self.start_time = datetime.datetime.now()
        self.update_rectangles = update_rectangles
        self.paused = False
        self.pause_time = 0
        self.unpause_time = 0

    def schedule_function(self, func, delay):
        """ 
        Schedule a function to be called after a delay
        :param func: The function to call
        :param delay: The delay before the function is called
        """
        #print(f"Scheduling function {func} with delay {delay}")
       
        scheduled_funcID = pyglet.clock.schedule_once(func, delay)
        self.scheduled_functions.append((func, delay, scheduled_funcID))
        
    def pause(self):
        """Pause the clock and all scheduled functions."""

        if not self.paused:
            for func, _, _ in self.scheduled_functions:
                pyglet.clock.unschedule(func)
            pyglet.clock.unschedule(self.update_rectangles)
            self.paused = True
            self.pause_time = datetime.datetime.now()
   
    def resume(self):
        """Resume the clock and all scheduled functions with adjusted intervals."""

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
                        print(f"Rescheduling function {func}({temp_counter}) with delay {remaining_delay}")
                        print(f"Original delay: {delay}")
                        print(f"Start time was: {self.start_time.time()} and pause time was: {self.pause_time.time()}")
                        print(f"Time difference: {seconds_before_pause}")
                        print(f"New delay: {remaining_delay}")
                        print("The current time is: ", datetime.datetime.now().time())
                        print("-------------------")
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
        """Clear all scheduled functions and reset the clock."""

        for func, _, _ in self.scheduled_functions:
            pyglet.clock.unschedule(func)
        pyglet.clock.unschedule(self.update_rectangles)        
        self.scheduled_functions = []
        self.paused = False
