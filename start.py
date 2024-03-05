import pyglet
from piano_game import PianoGameUI
import os
import signal
import gc
import mido

# Sample database of songs
song_database = {
    1: {"name": "Mary had a little lamb", "artist": "???", "file": "mary_lamb.mid"},
    2: {"name": "Peter Peter Pumpkin Eater", "artist": "???", "file": "PeterPeter.mid"},
    3: {"name": "The Wishing Well", "artist": "???", "file": "TheWishingWell.mid"},
    4: {"name": "A Lion", "artist": "???", "file": "A_Lion.mid"},
    5: {"name": "Minuet in G Minor", "artist": "Bach", "file": "Bach_Minuet_in_G_Minor.mid"},
    6:  {"name": "Song for Beginners ", "artist": "Nikodem Kulczyk", "file": "beginner.mid"},
    7: {"name": "Cornfield Chase", "artist": "Hans Zimmer (Interstellar)", "file": "cornfield_chase.mid"},
    8: {"name": " Dry Hands", "artist": "C418" , "file": "Dry_Hands.mid"},
    9: {"name": "Golden Hour", "artist": "JVKE", "file": "Golden_HOUR.mid"},   #Jukebox example

#REDACTED 5: {"name": "NULL", "artist": "Debussy", "file": "debussy.mid"},
#REDACTED 6: {"name": "sir Duke", "artist": "stevie wonder", "file": "stevie.mid"},  
#REDACTED 8: {"name": "Im Still Standing", "artist": "Elton John", "file": "still_standing.mid"},  
#REDACTED 1: {"name": "Best Part", "artist": "Daniel Caesar", "file": "best_part.mid"},
}




class ScrollableLabel:
    def __init__(self, text, font_size, x, y, anchor_x, anchor_y, batch, color=(255, 255, 255, 255)):
        self.label = pyglet.text.Label(text,
                                       font_name='Arial',
                                       font_size=font_size,
                                       x=x,
                                       y=y,
                                       anchor_x=anchor_x,
                                       anchor_y=anchor_y,
                                       color=color, 
                                       batch=batch)

    def is_clicked(self, x, y):
        return (
            self.label.x - self.label.content_width // 2 < x < self.label.x +
            self.label.content_width // 2
            and self.label.y - self.label.content_height // 2 < y < self.label.y + self.label.content_height // 2
        )


class WalkingPianoGame(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.menu_batch = pyglet.graphics.Batch()
        self.song_select_batch = pyglet.graphics.Batch()
        self.settings_batch = pyglet.graphics.Batch()
        self.player_mode_batch = pyglet.graphics.Batch()
        
        self.game_modes = ['Challenge Mode', 'Practice', 'FreePlay', 'Settings', 'JukeBox', 'Exit']
        
        self.selected_game_mode = None
        self.game_state = 'MENU'
        self.player_count = 1  # Default to 1 player
        self.autoplay = False  # Default to no autoplay

        
        self.menu_options_labels = []
        self.song_options_labels = []
        self.settings_options_labels = []
        self.player_mode_options_labels = []
        
        self.game = None
        
        self.setup_menu()
        self.setup_song_selection()
        self.setup_player_mode_selection()
        
        self.outport = mido.get_output_names()[0] if mido.get_output_names() else None
        self.inport = mido.get_input_names()[0] if mido.get_input_names() else None
        
        
    def setup_menu(self):
       # Main menu title
        self.main_menu_title = ScrollableLabel("WALKING PIANO", 32, self.width // 2, self.height - 50, 'center', 'center', self.menu_batch)
        
        # Menu options
        y_offset = 150  # Adjusted to make space for the title
        for index, mode in enumerate(self.game_modes):
            label = ScrollableLabel(mode, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.menu_batch)
            self.menu_options_labels.append(label)

    def setup_song_selection(self):
        # Song selection title
        self.song_selection_title = ScrollableLabel("Choose your song:", 32, self.width // 2, self.height - 50, 'center', 'center', self.song_select_batch)
        
        # Song options
        for song_id, song_info in song_database.items():
            label = ScrollableLabel(f"{song_info['name']} - {song_info['artist']}", 18, self.width // 2, self.height - song_id * 30 - 100, 'center', 'center', self.song_select_batch)  # Adjusted y-offset for song labels
            self.song_options_labels.append(label)
            
        self.home_button = ScrollableLabel("Return to Menu", 24, self.width // 2, 50, 'center', 'center', self.song_select_batch)
        self.song_options_labels.append(self.home_button)
             
    def setup_settings(self):
        
        #Clear batch
        self.settings_batch = pyglet.graphics.Batch()
        
        
        y_offset = 120  # Adjust for where settings options start
        all_out_ports = mido.get_output_names()
        all_in_ports = mido.get_input_names()
        
        # Settings title
        self.settings_title = ScrollableLabel("Settings", 32, self.width // 2, self.height - 50, 'center', 'center', self.settings_batch)

        # Output MIDI Ports
        y_position = self.height - y_offset
        self.settings_options_labels.append(ScrollableLabel("Select your MIDI Output Port:", 24, self.width // 2, y_position, 'center', 'center', self.settings_batch))
        y_position -= 30
        if all_out_ports:
            for port in all_out_ports:
                color = (0, 130, 255, 255) if port == self.outport else (255, 255, 255, 255)
                label = ScrollableLabel(port, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ScrollableLabel("None", 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))

        # Input MIDI Ports
        y_position -= 40  # Extra spacing before listing input ports
        self.settings_options_labels.append(ScrollableLabel("Select your MIDI Input Port:", 24, self.width // 2, y_position, 'center', 'center', self.settings_batch))
        y_position -= 30
        if all_in_ports:
            for port in all_in_ports:
                color = (0, 130, 255, 255) if port == self.inport else (255, 255, 255, 255)
                label = ScrollableLabel(port, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ScrollableLabel("None", 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))
        
        
        # Autoplay option
        y_position -= 60  # Adjust y_position accordingly
        self.settings_options_labels.append(ScrollableLabel("Autoplay:", 24, self.width // 2, y_position, 'center', 'center', self.settings_batch))

        # True option
        y_position -= 30
        true_color = (0, 255, 0, 255) if self.autoplay else (255, 255, 255, 255)
        self.true_label = ScrollableLabel("True", 18, self.width // 2 - 50, y_position, 'center', 'center', self.settings_batch, color=true_color)
        self.settings_options_labels.append(self.true_label)

        # False option
        false_color = (255, 0, 0, 255) if not self.autoplay else (255, 255, 255, 255)
        self.false_label = ScrollableLabel("False", 18, self.width // 2 + 50, y_position, 'center', 'center', self.settings_batch, color=false_color)
        self.settings_options_labels.append(self.false_label)
        
        self.home_button = ScrollableLabel("Return to Menu", 24, self.width // 2, 50, 'center', 'center', self.settings_batch)
        self.settings_options_labels.append(self.home_button)
           
    def setup_player_mode_selection(self):
        
        choose_players_title = ScrollableLabel("Select number of players:", 32, self.width // 2, self.height - 50, 'center', 'center', self.player_mode_batch)
        self.player_mode_options_labels.append(choose_players_title)
        
        modes = ['1 Player', '2 Player', 'Return to Menu']
        y_offset = 125
        for index, mode in enumerate(modes):
            label = ScrollableLabel(mode, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.player_mode_batch)
            self.player_mode_options_labels.append(label)       
           
    def on_draw(self):
        
        if self.game_state == 'MENU':
            self.clear()
            self.menu_batch.draw()
            

        if self.game_state == 'SONG_SELECTION':
            self.clear()
            self.song_select_batch.draw()
            
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
                            self.game_state = 'SONG_SELECTION'
                            self.selected_game_mode = 'Practice'
                         
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
                            self.game_state = 'SONG_SELECTION'
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
                        if clicked_text == '1 Player' or clicked_text == '2 Player':
                            # Handle 1-player or 2-player mode selection here
                            print(f"Selected {clicked_text} mode")
                            self.player_count = 1 if clicked_text == '1 Player' else 2
                            self.game_state = 'SONG_SELECTION'  # Or any other appropriate state
                            return
                        
                        elif clicked_text == 'Return to Menu':
                            self.return_to_menu()
                            return
                    
            elif self.game_state == 'SONG_SELECTION':
                for song_id, label in enumerate(self.song_options_labels, start=1):
                    if label.is_clicked(x, y):
                        if label.label.text == "Return to Menu":
                            self.return_to_menu()
                            return
                        else:
                            print(f"You clicked {song_database[song_id]['name']} by {song_database[song_id]['artist']}")
                            self.start_game(song_database[song_id]['file'], self.selected_game_mode, self.inport, self.outport, self.player_count, self.autoplay)
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

    game = WalkingPianoGame(width=1080, height=590,
                caption="Walking Piano Game")
    pyglet.app.run()
