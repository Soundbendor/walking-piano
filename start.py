import pyglet
from piano_game import PianoGameUI
import os
import signal
import gc
import mido
import csv 

# Sample database of songs
song_database = {
    1: {"name": "Mary had a little lamb", "artist": "Nursery Rhyme (Easy)", "file": "mary_lamb.mid", "difficulty": "Easy", "players": 1},
    2: {"name": "Peter Peter Pumpkin Eater", "artist": "Nursery Rhyme (Easy)", "file": "PeterPeter.mid", "difficulty": "Easy", "players": 1},
    3: {"name": "The Wishing Well", "artist": "Nursery Rhyme (Easy)", "file": "TheWishingWell.mid", "difficulty": "Easy", "players": 1},
    4: {"name": "A Lion", "artist": "Nursery Rhyme (Easy)", "file": "A_Lion.mid", "difficulty": "Easy", "players": 1},
    5: {"name": "Song for Beginners ", "artist": "Nikodem Kulczyk", "file": "beginner.mid", "difficulty": "Easy", "players": 2},
    6: {"name": "Minuet in G Minor", "artist": "Bach", "file": "Bach_Minuet_in_G_Minor.mid", "difficulty": "Medium", "players": 2},
    7: {"name": "Cornfield Chase", "artist": "Hans Zimmer (Interstellar)", "file": "cornfield_chase.mid", "difficulty": "Medium", "players": 2},
    8: {"name": " Dry Hands", "artist": "C418" , "file": "Dry_Hands.mid", "difficulty": "Medium", "players": 2},
    9: {"name": "Golden Hour", "artist": "JVKE", "file": "Golden_HOUR.mid", "difficulty": "Hard", "players": 2},   #Jukebox example
    10: {"name": "Morning", "artist": "Edvard Grieg - Adapted", "file": "morning.mid", "difficulty": "Easy", "players": 1},
    11: {"name": "Piano Polka", "artist": "Kevin Olson", "file": "piano_polka.mid", "difficulty": "Easy", "players": 1},
    12: {"name": "Yankee Doodle", "artist": "Mary Leaf", "file": "Yankee_Doodle.mid", "difficulty": "Easy", "players": 1},
    13: {"name": "A Happy Bass Melody", "artist": "G. Turk - Adapted", "file": "A_Happy_Bass_Melody.mid", "difficulty": "Easy", "players": 1},
    14: {"name": "A Happy Treble Melody", "artist": "G. Turk - Adapted", "file": "A_Happy_Treble_Melody.mid", "difficulty": "Easy", "players": 1},
    15: {"name": "Ode to Joy", "artist": "Ludwig van Beethoven - Adapted", "file": "Ode_to_joy.mid", "difficulty": "Easy", "players": 1},
    
    #10: {"name": "If I ain't got you", "artist": "Alicia Keys", "file": "if_i_aint_got_you.mid", "difficulty": "Hard", "players": 2},   #Jukebox example
   
    #10: {"name": "Best Part", "artist": "Daniel Caesar", "file": "best_part.mid", "difficulty": "Hard", "players": 2},   #Jukebox example

    
    #10: {"name": "Im Still Standing", "artist": "Elton John", "file": "still_standing.mid", "players": 2},  


#REDACTED 5: {"name": "NULL", "artist": "Debussy", "file": "debussy.mid"},
     
}

def csv_to_song_database(csv_filename):
    song_database = {}
    with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        song_id = 1
        for row in csv_reader:
            song_database[song_id] = {
                "name": row["canonical_title"],
                "artist": row["canonical_composer"] + "(" + row["year"] + ")",
                "file": "../jukebox_songs/" + row["midi_filename"] 
            }
            song_id += 1
    return song_database

csv_filename = 'maestro-v3_songs.csv' 
jukebox_song_database = csv_to_song_database(csv_filename)

class ScrollableLabel:
    def __init__(self, text, song_id, font_size, x, y, anchor_x, anchor_y, batch, color=(255, 255, 255, 255), highlightable=True):
        self.label = pyglet.text.Label(text,
                                       font_name='Arial',
                                       font_size=font_size,
                                       x=x,
                                       y=y,
                                       anchor_x=anchor_x,
                                       anchor_y=anchor_y,
                                       color=color, 
                                       batch=batch)
        
        self.song_id = song_id  # Storing song ID in label for easy access
        self.original_color = color  # Store the original color
        self.highlight_color = (200, 200, 200, 255)  # Define the highlight color
        self.highlightable = highlightable  # Flag to control if the label should be highlightable

    def is_clicked(self, x, y):
        return (
            self.label.x - self.label.content_width // 2 < x < self.label.x + self.label.content_width // 2
            and self.label.y - self.label.content_height // 2 < y < self.label.y + self.label.content_height // 2
        )

    def update_highlight(self, x, y):
        '''Change the color of the label when mouse is over it, preserving original color otherwise.'''
        if self.highlightable:  # Only update highlight if the label is marked as highlightable
            if (self.label.x - self.label.content_width // 2 < x < self.label.x + self.label.content_width // 2
                and self.label.y - self.label.content_height // 2 < y < self.label.y + self.label.content_height // 2):
                self.label.color = self.highlight_color
            else:
                self.label.color = self.original_color
            

class WalkingPianoGame(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.menu_batch = pyglet.graphics.Batch()
        self.song_select_batch = pyglet.graphics.Batch()
        self.song_select_batch_jukebox = pyglet.graphics.Batch()
        self.settings_batch = pyglet.graphics.Batch()
        self.player_mode_batch = pyglet.graphics.Batch()
        
        
        self.game_modes = ['Challenge Mode', 'Practice', 'FreePlay', 'Settings', 'JukeBox', 'Exit']
        
        self.selected_game_mode = None
        self.game_state = 'MENU'
        self.player_count = 1  # Default to 1 player
        self.autoplay = False  # Default to no autoplay

        
        self.menu_options_labels = []
        self.song_options_labels = []
        self.song_options_labels_jukebox = []
        self.settings_options_labels = []
        self.player_mode_options_labels = []
        
        self.game = None
        
        self.setup_menu()
        self.setup_song_selection()
        self.setup_jukebox_song_selection()
        self.setup_player_mode_selection()
        
        self.outport = mido.get_output_names()[0] if mido.get_output_names() else None
        self.inport = mido.get_input_names()[0] if mido.get_input_names() else None
        
        
    def setup_menu(self):
       # Main menu title
        self.main_menu_title = ScrollableLabel("WALKING PIANO", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.menu_batch, highlightable=False)
        
        # Menu options
        y_offset = 150  # Adjusted to make space for the title
        for index, mode in enumerate(self.game_modes):
            label = ScrollableLabel(mode, None, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.menu_batch)
            self.menu_options_labels.append(label)

    def setup_song_selection(self):
        # Song selection title
        self.song_options_labels.clear()  # Clear existing labels
        self.song_selection_title = ScrollableLabel("Choose your song:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.song_select_batch, highlightable=False)
        
        # Filter songs based on the current mode and players
        valid_songs = self.filter_songs_based_on_mode_and_players()
        
        # Calculate start position for the first song label
        start_y = self.height - 100  # Start 100 pixels below the title
        label_height = 30  # Height between labels
        
        # Song options
        for index, (song_id, song_info) in enumerate(valid_songs.items(), start=1):
            y_position = start_y - index * label_height
            label = ScrollableLabel(f"{song_info['name']} - {song_info['artist']}", song_id, 18, self.width // 2, y_position, 'center', 'center', self.song_select_batch)
            self.song_options_labels.append(label)
        
        # Home button at the bottom
        home_button_y = start_y - len(valid_songs) * label_height - 50  # Extra space before the home button
        self.home_button = ScrollableLabel("Return to Menu", None, 24, self.width // 2, home_button_y, 'center', 'center', self.song_select_batch)
        self.song_options_labels.append(self.home_button)
            
    def setup_jukebox_song_selection(self, current_page=0):
        # Song selection title
        self.song_selection_title_jukebox = ScrollableLabel("Choose your song:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.song_select_batch_jukebox, highlightable=False)

        # Pagination vars
        self.current_page = current_page
        self.songs_per_page = 20
        self.total_pages = len(jukebox_song_database) // self.songs_per_page + 1

        # Create song labels for the current page
        self.song_options_labels_jukebox = []
        for song_id in range(current_page * self.songs_per_page + 1, (current_page + 1) * self.songs_per_page + 1):
            song_info = jukebox_song_database.get(song_id, {})
            label = ScrollableLabel(f"{song_info.get('name', '')} - {song_info.get('artist', '')}", None, 18, self.width // 2, self.height - (song_id - current_page * self.songs_per_page) * 30 - 100, 'center', 'center', self.song_select_batch_jukebox)  # Adjusted y-offset for song labels
            self.song_options_labels_jukebox.append(label)

        # Pagination buttons
        self.prev_page_button = ScrollableLabel("Previous", None, 18, self.width // 2 - 200, 50, 'center', 'center', self.song_select_batch_jukebox)
        self.next_page_button = ScrollableLabel("Next", None, 18, self.width // 2 + 200, 50, 'center', 'center', self.song_select_batch_jukebox)
        self.song_options_labels_jukebox.append(self.prev_page_button)
        self.song_options_labels_jukebox.append(self.next_page_button)

        self.home_button = ScrollableLabel("Return to Menu", None, 24, self.width // 2, 50, 'center', 'center', self.song_select_batch_jukebox)
        self.song_options_labels_jukebox.append(self.home_button)


    def setup_settings(self):
        
        #Clear batch
        self.settings_batch = pyglet.graphics.Batch()
        
        
        y_offset = 120  # Adjust for where settings options start
        all_out_ports = mido.get_output_names()
        all_in_ports = mido.get_input_names()
        
        # Settings title
        self.settings_title = ScrollableLabel("Settings", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.settings_batch, highlightable=False)

        # Output MIDI Ports
        y_position = self.height - y_offset
        self.settings_options_labels.append(ScrollableLabel("Select your MIDI Output Port:", None, 24, self.width // 2, y_position, 'center', 'center', self.settings_batch, highlightable=False))
        y_position -= 30
        if all_out_ports:
            for port in all_out_ports:
                color = (0, 130, 255, 255) if port == self.outport else (255, 255, 255, 255)
                label = ScrollableLabel(port, None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ScrollableLabel("None", None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))

        # Input MIDI Ports
        y_position -= 40  # Extra spacing before listing input ports
        self.settings_options_labels.append(ScrollableLabel("Select your MIDI Input Port:", None, 24, self.width // 2, y_position, 'center', 'center', self.settings_batch, highlightable=False))
        y_position -= 30
        if all_in_ports:
            for port in all_in_ports:
                color = (0, 130, 255, 255) if port == self.inport else (255, 255, 255, 255)
                label = ScrollableLabel(port, None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ScrollableLabel("None", None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))
        
        
        # Autoplay option
        y_position -= 60  # Adjust y_position accordingly
        self.settings_options_labels.append(ScrollableLabel("Autoplay:", None, 24, self.width // 2, y_position, 'center', 'center', self.settings_batch, highlightable=False))

        # True option
        y_position -= 30
        true_color = (0, 255, 0, 255) if self.autoplay else (255, 255, 255, 255)
        self.true_label = ScrollableLabel("True", None, 18, self.width // 2 - 50, y_position, 'center', 'center', self.settings_batch, color=true_color)
        self.settings_options_labels.append(self.true_label)

        # False option
        false_color = (255, 0, 0, 255) if not self.autoplay else (255, 255, 255, 255)
        self.false_label = ScrollableLabel("False", None, 18, self.width // 2 + 50, y_position, 'center', 'center', self.settings_batch, color=false_color)
        self.settings_options_labels.append(self.false_label)
        
        self.home_button = ScrollableLabel("Return to Menu", None, 24, self.width // 2, 50, 'center', 'center', self.settings_batch)
        self.settings_options_labels.append(self.home_button)
           
    def setup_player_mode_selection(self):
        
        choose_players_title = ScrollableLabel("Select number of players:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.player_mode_batch, highlightable=False)
        self.player_mode_options_labels.append(choose_players_title)
        
        modes = ['1 Player', '2 Player', 'Return to Menu']
        y_offset = 125
        for index, mode in enumerate(modes):
            label = ScrollableLabel(mode, None, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.player_mode_batch)
            self.player_mode_options_labels.append(label)       
        
    def filter_songs_based_on_mode_and_players(self):
        filtered_songs = {}
        
        if self.selected_game_mode == 'Practice':
            # Filter for 'Easy' songs for Practice mode regardless of player count
            for song_id, song_info in song_database.items():
                if song_info['difficulty'] == 'Easy':
                    filtered_songs[song_id] = song_info
        elif self.selected_game_mode == 'Challenge':
            # In Challenge Mode, filter songs based on the number of players
            for song_id, song_info in song_database.items():
                if self.player_count == 2:
                    # Show only 2-player songs
                    if song_info['players'] == 2:
                        filtered_songs[song_id] = song_info
            
                elif self.player_count == 1:
                    # Show ALL songs, both 1-player songs and 2 player songs
                    filtered_songs[song_id] = song_info
                    
        elif self.selected_game_mode in ['FreePlay', 'JukeBox']:
            # For FreePlay or JukeBox, show all songs
            filtered_songs = song_database
            
            
        return filtered_songs


    def get_song_id_from_label(self, label):
        return label.song_id


    def on_draw(self):
        
        if self.game_state == 'MENU':
            self.clear()
            self.menu_batch.draw()
            

        if self.game_state == 'SONG_SELECTION':
            self.clear()
            self.song_select_batch.draw()
            
        if self.game_state == 'SONG_SELECTION_JUKEBOX':
            self.clear()
            self.song_select_batch_jukebox.draw()
            
        if self.game_state == 'SETTINGS':
            self.clear()
            self.settings_batch.draw()
        
        if self.game_state == 'PLAYER_MODE_SELECTION':
            self.clear()
            self.player_mode_batch.draw()
            
        elif self.game_state == 'GAME':
            # print("Game is running")
            # May need to edit this when adding more functionality in future...
            pass

    def on_mouse_press(self, x, y, button, modifiers):
            if self.game_state == 'MENU':
                for index, label in enumerate(self.menu_options_labels):
                    if label.is_clicked(x, y):
                          
                        game_mode = self.game_modes[index]
                        
                        if game_mode == 'Challenge Mode':
                            
                            # Code for Challenge Mode
                            print(f"Game Mode Selected: {self.game_modes[index]}")
                            self.game_state = 'PLAYER_MODE_SELECTION' 
                            self.selected_game_mode = 'Challenge'
                            
                        elif game_mode == 'Practice':
                            
                            # Code for Practice Mode
                            print(f"Game Mode Selected: {self.game_modes[index]}")
                            self.selected_game_mode = 'Practice'
                            self.setup_song_selection()  # Refresh the song list for Practice mode
                            self.game_state = 'SONG_SELECTION'

                         
                        elif game_mode == 'FreePlay':
                            # Code for FreePlay Mode
                            print(f"Game Mode Selected: {self.game_modes[index]}")
                            
                            self.start_game(None, 'FreePlay', self.inport, self.outport)
                            
                        elif game_mode == 'Settings':
                            #Code for Settings
                            self.setup_settings()
                            self.game_state = 'SETTINGS'
                        
                        elif game_mode == 'JukeBox':
                            #Code for JukeBox
                            print(f"Game Mode Selected: {self.game_modes[index]}")
                            self.game_state = 'SONG_SELECTION_JUKEBOX'
                            self.selected_game_mode = 'JukeBox'
                            
                            
                        elif game_mode == 'Exit':
                            # Code for Exit
                            print("Exiting...")
                            pyglet.app.exit()
                            return
            
            elif self.game_state == 'PLAYER_MODE_SELECTION':
                for label in self.player_mode_options_labels:
                    if label.is_clicked(x, y):
                        clicked_text = label.label.text
                        if clicked_text == '1 Player':
                            self.player_count = 1
                            self.selected_game_mode = 'Challenge'  # Ensure game mode is explicitly set
                            self.setup_song_selection()  # Refresh song list based on new settings
                            self.game_state = 'SONG_SELECTION'
                            return
                        elif clicked_text == '2 Player':
                            self.player_count = 2
                            self.selected_game_mode = 'Challenge'
                            self.setup_song_selection()
                            self.game_state = 'SONG_SELECTION'
                            return
                        elif clicked_text == 'Return to Menu':
                            self.return_to_menu()
                            return


                    
            elif self.game_state == 'SONG_SELECTION':
                for index, label in enumerate(self.song_options_labels):
                    if label.is_clicked(x, y):
                        # Check for a return to menu command
                        if label.label.text == "Return to Menu":
                            self.return_to_menu()
                            return
                        else:
                            # Fetch the corresponding song ID from the label itself or by maintaining a map
                            # Assuming you have a method or a way to map label to song_id correctly
                            song_id = self.get_song_id_from_label(label)  # You need to implement this method

                            # Access the song info using the song_id
                            song_info = song_database.get(song_id, None)
                            if song_info:
                                print(f"You clicked {song_info['name']} by {song_info['artist']}")
                                self.start_game(song_info['file'], self.selected_game_mode, self.inport, self.outport, self.player_count, self.autoplay)
                            else:
                                print("Error: Song info not found.")
                            return

            
            elif self.game_state == 'SONG_SELECTION_JUKEBOX':
                for song_id, label in enumerate(self.song_options_labels_jukebox, start=1):
                    if label.is_clicked(x, y):
                        if label.label.text == "Return to Menu":
                            self.return_to_menu()
                            return
                        elif label.label.text == "Previous":
                            print("Previous page")
                            self.handle_prev_page()
                            return
                        elif label.label.text == "Next":
                            print("Next page")
                            self.handle_next_page()
                            return
                        else:
                            print(f"You clicked {jukebox_song_database[song_id + (self.current_page*self.songs_per_page)]['name']} by {jukebox_song_database[song_id + (self.current_page*self.songs_per_page)]['artist']}")
                            self.start_game(jukebox_song_database[song_id+ (self.current_page*self.songs_per_page)]['file'], self.selected_game_mode, self.inport, self.outport, self.player_count, self.autoplay)
                            return
                    
            
            elif self.game_state == "SETTINGS":
                # Handling clicks on output ports
                for label in self.settings_options_labels:
                    if label.is_clicked(x, y):
                        clicked_text = label.label.text
                        all_out_ports = mido.get_output_names()
                        all_in_ports = mido.get_input_names()
                        
                        if clicked_text in all_out_ports:
                            self.outport = clicked_text  # Update the currently selected output port
                            print(f"Selected Output Port: {clicked_text}")
                            self.setup_settings()  # Refresh settings to update highlighted selection
                            return
                        elif clicked_text in all_in_ports:
                            self.inport = clicked_text  # Update the currently selected input port
                            print(f"Selected Input Port: {clicked_text}")
                            self.setup_settings()  # Refresh settings to update highlighted selection
                            return
                        
                        elif clicked_text == "Return to Menu":
                            self.return_to_menu()
                            return
                    
                if self.true_label.is_clicked(x, y):
                    self.autoplay = True
                    self.setup_settings()  # Refresh settings to update highlighted selection
                    return
                elif self.false_label.is_clicked(x, y):
                    self.autoplay = False
                    self.setup_settings()  # Refresh settings to update highlighted selection
                    return
                
                
    def on_mouse_motion(self, x, y, dx, dy):
        
        if self.game_state == 'MENU':
            for label in self.menu_options_labels:
                label.update_highlight(x, y)
        
        if self.game_state == 'SONG_SELECTION':
            for label in self.song_options_labels:
                label.update_highlight(x, y)
        
        if self.game_state == 'PLAYER_MODE_SELECTION':
            for label in self.player_mode_options_labels:
                label.update_highlight(x, y)
        
        if self.game_state == 'SONG_SELECTION_JUKEBOX':
            for label in self.song_options_labels_jukebox:
                label.update_highlight(x, y)
        
        if self.game_state == 'SETTINGS':
            for label in self.settings_options_labels:
                label.update_highlight(x, y)

                                 
    def start_game(self, midi_file, game_mode, inport, outport, player_count=1, autoplay=False):
        # Initialize and run the game with the selected MIDI file
        #Adjust game state for tracking whats happening
        self.game_state = 'GAME'
        
        #Create the game
        #Pass in the song and selected game mode
        self.game = PianoGameUI(self, midi_file, game_mode, inport, outport,  player_count, autoplay)
        print("Game is running")

    def return_to_menu(self):
        # Logic to return to the main menu
        self.game_state = 'MENU'
        # Reset the game state
        self.player_count = 1
        self.game = None
        pass

    def handle_prev_page(self):
        # Logic to handle previous page of songs
        if self.current_page > 0:
            self.current_page -= 1
            self.setup_jukebox_song_selection(self.current_page)
        pass

    def handle_next_page(self):
        # Logic to handle next page of songs
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.setup_jukebox_song_selection(self.current_page)
        pass

if __name__ == "__main__":

    # Terminating the program with CTRL+C...
    def signal_handler(sig, frame):
        # Force all threads to exit immediately
        os._exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    
    #Change into song directory so that the game can find the songs.
    #This method might need to be changed depending on how the game is run.
    
    #Change to working directory of start.py
    os.chdir(os.path.dirname(__file__))
    #Change to songs directory for access of song files within game.
    os.chdir("songs")

    game = WalkingPianoGame(fullscreen=True, resizable=True, caption="Walking Piano")
    #game = WalkingPianoGame(width = 1920, height = 1080, resizable=True, caption="Walking Piano")

    pyglet.app.run()
