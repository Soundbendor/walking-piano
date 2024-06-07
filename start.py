"""
Start.py: 
========================

This file contains the main menu and game logic for the Walking Piano Game.
The main menu allows the user to select between different game modes, 
such as Challenge Mode, Practice Mode, FreePlay, Settings, JukeBox, and Exit. 
The user can navigate through the menu using the mouse and select different options.

Classes:
    ClickableLabel
    WalkingPianoGame

Functions:
    csv_to_song_database
    
Authors: Devin Martin and Wesley Jake Anding
"""

import pyglet
import mido
from piano_game import PianoGameUI
import os
import signal
import csv 

song_database = {
    # Easy songs
    1: {"name": "A Happy Bass Melody", "artist": "G. Turk - Adapted", "file": "A_Happy_Bass_Melody.mid", "difficulty": "Easy", "players": 1},
    2: {"name": "A Happy Treble Melody", "artist": "G. Turk - Adapted", "file": "A_Happy_Treble_Melody.mid", "difficulty": "Easy", "players": 1},
    3: {"name": "A Lion", "artist": "Nursery Rhyme (Easy)", "file": "A_Lion.mid", "difficulty": "Easy", "players": 1},
    4: {"name": "Mary had a little lamb", "artist": "Nursery Rhyme (Easy)", "file": "mary_lamb.mid", "difficulty": "Easy", "players": 1},
    5: {"name": "Morning", "artist": "Edvard Grieg - Adapted", "file": "morning.mid", "difficulty": "Easy", "players": 1},
    6: {"name": "My Heart Will Go On", "artist": "Celine Dion", "file": "My_Heart_Will_Go_On_Piano.mid", "difficulty": "Easy", "players": 2},
    7: {"name": "Ode to Joy", "artist": "Ludwig van Beethoven - Adapted", "file": "Ode_to_joy.mid", "difficulty": "Easy", "players": 1},
    8: {"name": "Peter Peter Pumpkin Eater", "artist": "Nursery Rhyme (Easy)", "file": "PeterPeter.mid", "difficulty": "Easy", "players": 1},
    9: {"name": "Piano Polka", "artist": "Kevin Olson", "file": "piano_polka.mid", "difficulty": "Easy", "players": 1},
    10: {"name": "Pure Imagination", "artist": "Leslie Bricusse & Anthony Newley", "file": "Pure_Imagination_Piano_Solo_-_Beginner.mid", "difficulty": "Easy", "players": 2},
    11: {"name": "Silent Night", "artist": "Traditional", "file": "silent_night.mid", "difficulty": "Easy", "players": 2},
    12: {"name": "The Wishing Well", "artist": "Nursery Rhyme (Easy)", "file": "TheWishingWell.mid", "difficulty": "Easy", "players": 1},
    13: {"name": "Twinkle Twinkle Little Star", "artist": "Nursery Rhyme", "file": "twinkle_twinkle.mid", "difficulty": "Easy", "players": 2},
    14: {"name": "Yankee Doodle", "artist": "Mary Leaf", "file": "Yankee_Doodle.mid", "difficulty": "Easy", "players": 1},
    15: {"name": "You've Got A Friend In Me", "artist": "Randy Newman", "file": "You_ve_Got_A_Friend_In_Me_Easy_Piano_Sheet_Music.mid", "difficulty": "Easy", "players": 2},


    # Challenge songs
    16: {"name": "7 Years", "artist": "Lukas Graham", "file": "7_Years.mid", "difficulty": "Challenge", "players": 2},
    17: {"name": "A Whole New World", "artist": "Aladdin", "file": "whole_new_world.mid", "difficulty": "Challenge", "players": 2},
    18: {"name": "All of Me", "artist": "John Legend", "file": "All_of_Me_John_Legend.mid", "difficulty": "Challenge", "players": 2},
    19: {"name": "All of Me", "artist": "John Legend", "file": "All_of_me_-_John_Legend.mid", "difficulty": "Challenge", "players": 2},
    20: {"name": "Can't Help Falling in Love", "artist": "Elvis Presley", "file": "Cant_Help_Falling_In_Love.mid", "difficulty": "Challenge", "players": 2},
    21: {"name": "Captured Memories", "artist": "Zelda: Breath of the Wild", "file": "Zelda_Breath_of_the_Wild_-_Captured_Memories_piano.mid", "difficulty": "Challenge", "players": 2},
    22: {"name": "Christmas Don't Be Late", "artist": "The Chipmunks", "file": "christmas_dont_be_late.mid", "difficulty": "Challenge", "players": 2},
    23: {"name": "Clark (Minecraft)", "artist": "C418", "file": "clark_minecraft.mid", "difficulty": "Challenge", "players": 2},
    24: {"name": "Cornfield Chase (Interstellar)", "artist": "Hans Zimmer", "file": "cornfield_chase.mid", "difficulty": "Challenge", "players": 2},
    25: {"name": "Counting Stars", "artist": "OneRepublic", "file": "Counting_Stars_longer.mid", "difficulty": "Challenge", "players": 2},
    26: {"name": "Dancing in the Moonlight", "artist": "Toploader", "file": "Dancing_in_the_Moonlight_-_Toploader_-_Easy_Piano.mid", "difficulty": "Challenge", "players": 2},
    27: {"name": "Dry Hands", "artist": "C418", "file": "Dry_Hands.mid", "difficulty": "Challenge", "players": 2},
    28: {"name": "Evil Morty's Theme", "artist": "Rick and Morty", "file": "Evil_Morty_s_ThemeFor_the_Damaged_Coda_-_Easy_Piano.mid", "difficulty": "Challenge", "players": 2},
    29: {"name": "Game of Thrones Theme", "artist": "Ramin Djawadi", "file": "game_of_thrones.mid", "difficulty": "Challenge", "players": 2},
    30: {"name": "Glimpse of Us", "artist": "Joji", "file": "Glimpse_of_Us__Joji_Piano_Accompaniment.mid", "difficulty": "Challenge", "players": 2},
    31: {"name": "Hallelujah", "artist": "Leonard Cohen", "file": "hallelujah.mid", "difficulty": "Challenge", "players": 2},
    32: {"name": "Hanachirusato", "artist": "Genshin Impact", "file": "Genshin_Impact_-_Hanachirusato_Piano.mid", "difficulty": "Challenge", "players": 2},
    33: {"name": "Heart and Soul", "artist": "Hoagy Carmichael", "file": "Heart_and_Soul_Piano.mid", "difficulty": "Challenge", "players": 2},
    34: {"name": "He's a Pirate", "artist": "Klaus Badelt", "file": "hes_a_pirate.mid", "difficulty": "Challenge", "players": 2},
    35: {"name": "How To Save A Life", "artist": "The Fray", "file": "How_To_Save_A_Life_-_The_Fray.mid", "difficulty": "Challenge", "players": 2},
    36: {"name": "I'm Still Standing", "artist": "Elton John", "file": "still_standing.mid", "difficulty": "Challenge", "players": 2},
    37: {"name": "Interstellar Theme", "artist": "Hans Zimmer", "file": "Interstellar_Theme_Easy_Piano.mid", "difficulty": "Challenge", "players": 2},
    38: {"name": "Jurassic Park Theme", "artist": "John Williams", "file": "Jurassic_Park_Theme_for_Beginner_EASY_Piano.mid", "difficulty": "Challenge", "players": 2},
    39: {"name": "La Vie En Rose", "artist": "Édith Piaf", "file": "La_vie_en_rose_Piano_Intermediate.mid", "difficulty": "Challenge", "players": 2},
    40: {"name": "Let Her Go", "artist": "Passenger", "file": "Let_Her_Go_Passenger.mid", "difficulty": "Challenge", "players": 2},
    41: {"name": "Love Yourself", "artist": "Justin Bieber", "file": "Love_Yourself.mid", "difficulty": "Challenge", "players": 2},
    42: {"name": "Mad at Disney", "artist": "salem ilese", "file": "mad_at_disney_copy.mid", "difficulty": "Challenge", "players": 2},
    43: {"name": "Married Life", "artist": "Michael Giacchino (Up)", "file": "married_life.mid", "difficulty": "Challenge", "players": 2},
    44: {"name": "Megalovania Theme from Undertale", "artist": "Toby Fox", "file": "Megalovania_Theme_from_Undertale__easy_piano.mid", "difficulty": "Challenge", "players": 2},
    45: {"name": "Minuet in G Minor", "artist": "Bach", "file": "Bach_Minuet_in_G_Minor.mid", "difficulty": "Challenge", "players": 2},
    46: {"name": "Moon River", "artist": "Henry Mancini", "file": "Moon_River(1).mid", "difficulty": "Challenge", "players": 2},
    47: {"name": "My Heart Will Go On", "artist": "Celine Dion", "file": "heart_will_go_on.mid", "difficulty": "Challenge", "players": 2},
    48: {"name": "No Time to Die", "artist": "Billie Eilish", "file": "No_Time_to_Die_Piano_-_James_Bond_Theme_-_Billie_Eilish_with_Lyrics.mid", "difficulty": "Challenge", "players": 2},
    49: {"name": "One Last Time", "artist": "Ariana Grande", "file": "One_Last_Time.mid", "difficulty": "Challenge", "players": 2},
    50: {"name": "Perfect", "artist": "Ed Sheeran", "file": "Perfect_-_Ed_Sheeran_PIANO.mid", "difficulty": "Challenge", "players": 2},
    51: {"name": "Pirates of the Caribbean", "artist": "Klaus Badelt", "file": "Pirates_of_the_Caribbean.mid", "difficulty": "Challenge", "players": 2},
    52: {"name": "Piano Man", "artist": "Billy Joel", "file": "piano_man.mid", "difficulty": "Challenge", "players": 2},
    53: {"name": "Running Up That Hill", "artist": "Kate Bush", "file": "Running_up_that_hill.mid", "difficulty": "Challenge", "players": 2},
    54: {"name": "SAD!", "artist": "XXXTENTACION", "file": "SAD_-_XXXTENTACION_Piano.mid", "difficulty": "Challenge", "players": 2},
    55: {"name": "Sadness and Sorrow", "artist": "Naruto", "file": "Sadness_and_Sorrow_for_PIANO_SOLO.mid", "difficulty": "Challenge", "players": 2},
    56: {"name": "See You Again", "artist": "Wiz Khalifa ft. Charlie Puth", "file": "See_You_Again.mid", "difficulty": "Challenge", "players": 2},
    57: {"name": "Set Fire To The Rain", "artist": "Adele", "file": "Set_Fire_To_The_Rain.mid", "difficulty": "Challenge", "players": 2},
    58: {"name": "Snowman", "artist": "Sia", "file": "Sia_-_Snowman.mid", "difficulty": "Challenge", "players": 2},
    59: {"name": "Someone Like You", "artist": "Adele", "file": "Someone_Like_You_easy_piano.mid", "difficulty": "Challenge", "players": 2},
    60: {"name": "Somewhere Over the Rainbow", "artist": "Harold Arlen", "file": "Somewhere_over_the_Rainbow.mid", "difficulty": "Challenge", "players": 2},
    61: {"name": "Song for Beginners", "artist": "Nikodem Kulczyk", "file": "beginner.mid", "difficulty": "Challenge", "players": 2},
    62: {"name": "Super Mario Bros. Main Theme", "artist": "Nintendo", "file": "Super_Mario_Bros.__Main_Theme.mid", "difficulty": "Challenge", "players": 2},
    63: {"name": "Super Mario Theme Song", "artist": "Koji Kondo", "file": "Super_Mario_Theme_Song.mid", "difficulty": "Challenge", "players": 2},
    64: {"name": "Sweden (Minecraft)", "artist": "C418", "file": "sweden_minecraft.mid", "difficulty": "Challenge", "players": 2},
    65: {"name": "The Avatar's Love", "artist": "Avatar: The Last Airbender", "file": "The_Avatars_love.mid", "difficulty": "Challenge", "players": 2},
    66: {"name": "The Legend of Zelda Main Theme", "artist": "Nintendo", "file": "The_Legend_of_Zelda_Main_Theme_Easy.mid", "difficulty": "Challenge", "players": 2},
    67: {"name": "The Most Wonderful Time of the Year", "artist": "Andy Williams", "file": "The_Most_Wonderful_Time_of_the_Year_-_easy_piano_C_maj.mid", "difficulty": "Challenge", "players": 2},
    68: {"name": "Uptown Girl", "artist": "Billy Joel", "file": "Uptown_Girl(1).mid", "difficulty": "Challenge", "players": 2},
    69: {"name": "Uptown Girl", "artist": "Westlife", "file": "uptown_girl.mid", "difficulty": "Challenge", "players": 2},
    70: {"name": "Viva la Vida", "artist": "Coldplay", "file": "Viva_la_vida.mid", "difficulty": "Challenge", "players": 2},
    71: {"name": "Wet Hands", "artist": "C418", "file": "Wet_Hands_Minecraft.mid", "difficulty": "Challenge", "players": 2},
    72: {"name": "Zelda's Lullaby", "artist": "The Legend of Zelda: Ocarina of Time", "file": "Zeldas_Lullaby_The_Legend_of_Zelda_Ocarina_of_Time_-_Easy_version.mid", "difficulty": "Challenge", "players": 2},


    # Impossible songs
    75: {"name": "20th Century Fox Fanfare", "artist": "Unknown", "file": "20th_Century_Fox_Fanfare_Simple_Piano.mid", "difficulty": "Impossible", "players": 2},
    76: {"name": "A Cruel Angel's Thesis - Neon Genesis Evangelion", "artist": "Unknown", "file": "A_Cruel_Angels_Thesis_-_Neon_Genesis_Evangelion_Piano_Cover.mid", "difficulty": "Impossible", "players": 2},
    77: {"name": "All the World's a Stage", "artist": "Genshin Impact", "file": "genshin.mid", "difficulty": "Impossible", "players": 2},
    78: {"name": "Autumn Leaves", "artist": "Jazz Piano", "file": "Autumn_Leaves_Jazz_Piano.mid", "difficulty": "Impossible", "players": 2},
    79: {"name": "Bach Toccata and Fugue in D Minor", "artist": "Bach", "file": "Bach_Toccata_and_Fugue_in_D_Minor_Piano_solo.mid", "difficulty": "Impossible", "players": 2},
    80: {"name": "Ballad of the Wind Fish", "artist": "The Legend of Zelda", "file": "The_Legend_of_Zelda_Links_Awakening-Ballad_of_the_Wind_Fish_Piano.mid", "difficulty": "Impossible", "players": 2},
    81: {"name": "Beethoven Symphony No. 5 1st movement", "artist": "Beethoven", "file": "Beethoven_Symphony_No._5_1st_movement_Piano_solo.mid", "difficulty": "Impossible", "players": 2},
    82: {"name": "Bluebird", "artist": "Naruto", "file": "bluebird_naruto.mid", "difficulty": "Impossible", "players": 2},
    83: {"name": "Canon in D", "artist": "Unknown", "file": "Canon_in_D.mid", "difficulty": "Impossible", "players": 2},
    84: {"name": "Cowboy Bebop TANK", "artist": "Unknown", "file": "Cowboy_Bebop_TANK.mid", "difficulty": "Impossible", "players": 2},
    85: {"name": "Dancing in the Moonlight", "artist": "Toploader", "file": "Dancing_in_the_Moonlight.mid", "difficulty": "Impossible", "players": 2},
    86: {"name": "Deference for Darkness", "artist": "Halo 3 ODST", "file": "Deference_for_Darkness_from_Halo_3_ODST_for_Piano.mid", "difficulty": "Impossible", "players": 2},
    87: {"name": "Don't Stop Believing", "artist": "Journey", "file": "Dont_Stop_Believing_Piano_Guitar_Vocals.mid", "difficulty": "Impossible", "players": 2},
    88: {"name": "Fallen Down", "artist": "Undertale", "file": "Fallen_Down_-_Undertale_Piano_Solo.mid", "difficulty": "Impossible", "players": 2},
    89: {"name": "From the New World - 4th Movement", "artist": "Unknown", "file": "From_the_New_World_-_4th_Movement.mid", "difficulty": "Impossible", "players": 2},
    90: {"name": "Golden Hour", "artist": "JVKE", "file": "Golden_HOUR.mid", "difficulty": "Impossible", "players": 2},
    91: {"name": "Good News", "artist": "Mac Miller", "file": "Good_News_-_Mac_Miller_-_Easy_piano.mid", "difficulty": "Impossible", "players": 2},
    92: {"name": "Gravity Falls Opening", "artist": "Intermediate Piano Solo", "file": "Gravity_Falls_Opening_-_Intermediate_Piano_Solo.mid", "difficulty": "Impossible", "players": 2},
    93: {"name": "Great Fairy Fountain", "artist": "The Legend of Zelda", "file": "The_Legend_of_Zelda_Great_Fairy_Fountain_Piano_Cover.mid", "difficulty": "Impossible", "players": 2},
    94: {"name": "Gusty Garden Galaxy", "artist": "Super Mario Galaxy", "file": "Gusty_Garden_Galaxy_From_Super_Mario_Galaxy_for_piano.mid", "difficulty": "Impossible", "players": 2},
    95: {"name": "Here With Me", "artist": "D4vd", "file": "here_with_me.mid", "difficulty": "Impossible", "players": 2},
    96: {"name": "idontwannabeyouanymore", "artist": "Billie Eilish", "file": "idontwannabeyouanymore.mid", "difficulty": "Impossible", "players": 2},
    97: {"name": "Isn't She Lovely", "artist": "Unknown", "file": "Isnt_She_Lovely.mid", "difficulty": "Impossible", "players": 2},
    98: {"name": "Jojo's Bizarre Adventure G", "artist": "Unknown", "file": "jojo.mid", "difficulty": "Impossible", "players": 2},
    99: {"name": "Jump Up, Super Star! (Super Mario Odyssey)", "artist": "Unknown", "file": "Jump_Up_Super_Star_-Super_Mario_Odyssey-.mid", "difficulty": "Impossible", "players": 2},
    100: {"name": "Kick Back (TV Size)", "artist": "Unknown", "file": "Kick_Back__TV_Size.mid", "difficulty": "Impossible", "players": 2},
    101: {"name": "Littleroot Town", "artist": "Pokemon ORAS", "file": "Littleroot_Town_-_Pokmon_ORAS_for_piano.mid", "difficulty": "Impossible", "players": 2},
    102: {"name": "Lost in Paradise", "artist": "Unknown", "file": "Lost_in_Paradise.mid", "difficulty": "Impossible", "players": 2},
    103: {"name": "Main Theme From Interstellar", "artist": "Hans Zimmer", "file": "Main_Theme_From_Interstellar__Hans_Zimmer_Piano.mid", "difficulty": "Impossible", "players": 2},
    104: {"name": "Man In The Mirror (Jazz Version)", "artist": "Michael Jackson", "file": "Man_In_The_Mirror_Jazz_version_arr._Brent_Edstrom_-_Michael_Jackson_Piano_Solo.mid", "difficulty": "Impossible", "players": 2},
    105: {"name": "Merry Go Round of Life", "artist": "Howl's Moving Castle", "file": "Merry_Go_Round_of_Life_Howls_Moving_Castle_Piano_Tutorial_.mid", "difficulty": "Impossible", "players": 2},
    106: {"name": "Mii Channel", "artist": "Nintendo", "file": "Mii_Channel_piano.mscz.mid", "difficulty": "Impossible", "players": 2},
    107: {"name": "Moon River", "artist": "Johnny Mercer and Henry Mancini", "file": "moon_river.mid", "difficulty": "Impossible", "players": 2},
    108: {"name": "My Heart Will Go On", "artist": "Unknown", "file": "MY_HEART_WILL_GO_ON.mid", "difficulty": "Impossible", "players": 2},
    109: {"name": "Never See Me Again", "artist": "Kanye West", "file": "Never_See_Me_Again__Kanye_West.mid", "difficulty": "Impossible", "players": 2},
    110: {"name": "Number One (Thousand Year Blood War ver.)", "artist": "Bleach OST", "file": "number_one_bleach.mid", "difficulty": "Impossible", "players": 2},
    111: {"name": "Ode to Joy Easy Variation", "artist": "Unknown", "file": "Ode_to_Joy_Easy_variation.mid", "difficulty": "Impossible", "players": 2},
    112: {"name": "One Piece - Overtaken", "artist": "Unknown", "file": "One_Piece_-_Overtaken.mid", "difficulty": "Impossible", "players": 2},
    113: {"name": "Perfect", "artist": "Ed Sheeran", "file": "Perfect_-_Ed_Sheeran_PIANO.mid", "difficulty": "Impossible", "players": 2},
    114: {"name": "Piano Sonata No. 11 K. 331 3rd Movement Rondo alla Turca", "artist": "Mozart", "file": "Piano_Sonata_No._11_K._331_3rd_Movement_Rondo_alla_Turca.mid", "difficulty": "Impossible", "players": 2},
    115: {"name": "Pokemon Red and Blue Title Theme", "artist": "Pokemon", "file": "Pokemon_Red_and_Blue_-_Title_Theme_for_piano.mid", "difficulty": "Impossible", "players": 2},
    116: {"name": "Pokemon Theme Song", "artist": "Pokemon", "file": "Pokemon_Theme_Song_piano.mid", "difficulty": "Impossible", "players": 2},
    117: {"name": "Promenade I", "artist": "Unknown", "file": "Promenade_I.mid", "difficulty": "Impossible", "players": 2},
    118: {"name": "River Flows in You", "artist": "Yiruma", "file": "River_Flows_in_You_-_Yiruma_-_10th_Anniversary_Version_Piano.mid", "difficulty": "Impossible", "players": 2},
    119: {"name": "Runaway", "artist": "Kanye West", "file": "runaway.mid", "difficulty": "Impossible", "players": 2},
    700: {"name": 'Running up that hill', "artist": 'Kate Bush', "file": 'Running_Up_That_Hill__A_Deal_With_God__Piano_Solo.mid', "difficulty": 'Impossible', "players": 2},
    120: {"name": "September", "artist": "Earth, Wind & Fire", "file": "september.mid", "difficulty": "Impossible", "players": 2},
    121: {"name": "Set Fire to the Rain", "artist": "Adele", "file": "52__Adele__Set_Fire_to_the_Rain.mid", "difficulty": "Impossible", "players": 2},
    122: {"name": "Skyrim Medley", "artist": "The Elder Scrolls V: Skyrim", "file": "Skyrim_Medley-_Dragonborn_The_Dragonborn_Comes_From_Past_to_Present_Far_Horizons.mid", "difficulty": "Impossible", "players": 2},
    123: {"name": "Somewhere Over the Rainbow", "artist": "Harold Arlen", "file": "Somewhere_over_the_Rainbow.mid", "difficulty": "Impossible", "players": 2},
    124: {"name": "Song of Storms", "artist": "Koji Kondo", "file": "Song_of_Storms_-_The_Legend_of_Zelda_Ocarine_of_Time__Koji_Kondo_-_Accordion_Solo.mid", "difficulty": "Impossible", "players": 2},
    125: {"name": "Super Mario Bros. Main Theme", "artist": "Nintendo", "file": "Super_Mario_Bros.__Main_Theme.mid", "difficulty": "Impossible", "players": 2},
    126: {"name": "The Legend of Zelda Main Theme", "artist": "Nintendo", "file": "The_Legend_of_Zelda_Main_Theme_Easy.mid", "difficulty": "Impossible", "players": 2},
    127: {"name": "The Most Wonderful Time of the Year", "artist": "Andy Williams", "file": "The_Most_Wonderful_Time_of_the_Year_-_easy_piano_C_maj.mid", "difficulty": "Impossible", "players": 2},
    128: {"name": "The Observatory", "artist": "Super Mario Galaxy", "file": "The_Observatory_-_Super_Mario_Galaxy.mid", "difficulty": "Impossible", "players": 2},
    129: {"name": "The Pink Panther Theme", "artist": "Henry Mancini", "file": "The_Pink_Panther_Theme_-_Henry_Mancini_-_Piano_version.mid", "difficulty": "Impossible", "players": 2},
    130: {"name": "Undertale", "artist": "Undertale", "file": "Undertale_Undertale_Piano.mid", "difficulty": "Impossible", "players": 2},
    131: {"name": "Verdanturf Town", "artist": "Pokemon ORAS", "file": "Verdanturf_Town_-_Pokemon_ORAS_for_piano.mid", "difficulty": "Impossible", "players": 2},
    132: {"name": "Wii Sports Theme", "artist": "Nintendo", "file": "Wii_Sports_Theme_piano.mid", "difficulty": "Impossible", "players": 2},
    133: {"name": "You've Got A Friend In Me", "artist": "Randy Newman", "file": "friend_in_me.mid", "difficulty": "Impossible", "players": 2},
    134: {"name": "Zoltraak - Frieren OST", "artist": "Unknown", "file": "Zoltraak_-_Frieren_OST.mid", "difficulty": "Impossible", "players": 2}
}

def csv_to_song_database(csv_filename):
    """
    Converts a CSV file into a song database dictionary.

    Parameters
    ----------
    csv_filename : str
        The path to the CSV file.

    Returns
    -------
    dict
        A dictionary representing the song database.
    """
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

#jukebox_song_database[1] = {"name": "test_song", "artist": "NULL", "file": "rush_e.mid"}

class ClickableLabel:
    """
    A class representing a clickable label in the game UI.

    Attributes
    ----------
    label : pyglet.text.Label
        The Pyglet label object.
    song_id : int
        The ID of the song associated with the label.
    original_color : tuple
        The original color of the label.
    highlight_color : tuple
        The color of the label when highlighted.
    highlightable : bool
        Whether the label is highlightable or not.
    """
    def __init__(self, text, song_id, font_size, x, y, anchor_x, anchor_y, batch, color=(255, 255, 255, 255), highlightable=True):
        """
        Initializes a ClickableLabel instance.

        Parameters
        ----------
        text : str
            The text to be displayed.
        song_id : int
            The ID of the song associated with the label.
        font_size : int
            The font size of the text.
        x : int
            The x-coordinate of the label.
        y : int
            The y-coordinate of the label.
        anchor_x : str
            The x-anchor of the label.
        anchor_y : str
            The y-anchor of the label.
        batch : pyglet.graphics.Batch
            The batch to which the label belongs.
        color : tuple, optional
            The color of the label (default is (255, 255, 255, 255)).
        highlightable : bool, optional
            Whether the label is highlightable or not (default is True).
        """
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
        """
        Checks if the label was clicked based on the provided coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the click.
        y : int
            The y-coordinate of the click.

        Returns
        -------
        bool
            True if the label was clicked, False otherwise.
        """
        return (
            self.label.x - self.label.content_width // 2 < x < self.label.x + self.label.content_width // 2
            and self.label.y - self.label.content_height // 2 < y < self.label.y + self.label.content_height // 2
        )

    def update_highlight(self, x, y):
        """
        Updates the label's highlight state based on the provided coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the mouse.
        y : int
            The y-coordinate of the mouse.
        """
        
        '''Change the color of the label when mouse is over it, preserving original color otherwise.'''
        if self.highlightable:  # Only update highlight if the label is marked as highlightable
            if (self.label.x - self.label.content_width // 2 < x < self.label.x + self.label.content_width // 2
                and self.label.y - self.label.content_height // 2 < y < self.label.y + self.label.content_height // 2):
                self.label.color = self.highlight_color
            else:
                self.label.color = self.original_color
            

class WalkingPianoGame(pyglet.window.Window):
    """
    A class representing the Walking Piano Game
    This is sets up the menu and many parameters 
    that can be changed within the settings before 
    playing the piano game.

    Attributes
    ----------
    menu_batch : pyglet.graphics.Batch
        Batch for the main menu.
    song_select_batch : pyglet.graphics.Batch
        Batch for the song selection menu.
    song_select_batch_jukebox : pyglet.graphics.Batch
        Batch for the jukebox song selection menu.
    settings_batch : pyglet.graphics.Batch
        Batch for the settings menu.
    player_mode_batch : pyglet.graphics.Batch
        Batch for the player mode selection menu.
    game_modes : list
        List of game modes.
    selected_game_mode : str
        The currently selected game mode.
    game_state : str
        The current state of the game.
    player_count : int
        The number of players.
    autoplay : bool
        Whether autoplay is enabled.
    controller_size : str
        The size of the controller.
    menu_options_labels : list
        List of labels for the main menu options.
    song_options_labels : list
        List of labels for the song selection menu.
    song_options_labels_jukebox : list
        List of labels for the jukebox song selection menu.
    settings_options_labels : list
        List of labels for the settings menu options.
    player_mode_options_labels : list
        List of labels for the player mode selection menu.
    game : PianoGameUI
        The current game instance.
    outport : str
        The MIDI output port.
    inport : str
        The MIDI input port.
    """
    def __init__(self, *args, **kwargs):
        
        """
        Initializes the WalkingPianoGame instance.

        Parameters
        ----------
        *args : list
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.
        """
        
        super().__init__(*args, **kwargs)
        
        self.menu_batch = pyglet.graphics.Batch()
        self.song_select_batch = pyglet.graphics.Batch()
        self.song_select_batch_jukebox = pyglet.graphics.Batch()
        self.settings_batch = pyglet.graphics.Batch()
        self.player_mode_batch = pyglet.graphics.Batch()
        self.difficulty_batch = pyglet.graphics.Batch()
                
        self.game_modes = ['Challenge Mode', 'Practice', 'FreePlay', 'Settings', 'JukeBox', 'Exit']
        
        self.selected_game_mode = None
        self.game_state = 'MENU'
        self.player_count = 1  # Default to 1 player
        self.autoplay = False  # Default to no autoplay
        self.controller_size = '49 key'  # Default to smaller 49 key version
        self.selected_difficulty = 'Easy'  # Default to easy difficulty

        self.current_page = 0
        self.songs_per_page = 25
        
        self.menu_options_labels = []
        self.song_options_labels = []
        self.song_options_labels_jukebox = []
        self.settings_options_labels = []
        self.player_mode_options_labels = []
        self.difficulty_options_labels = []
        
        self.game = None
        
        self.setup_menu()
        self.setup_song_selection()
        self.setup_jukebox_song_selection()
        self.setup_player_mode_selection()
        self.setup_difficulty_selection()
        
        self.outport = mido.get_output_names()[0] if mido.get_output_names() else None
        self.inport = mido.get_input_names()[0] if mido.get_input_names() else None
        
        
    def setup_menu(self):
        """
        Sets up the main menu labels.
        """
       # Main menu title
        self.main_menu_title = ClickableLabel("WALKING PIANO", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.menu_batch, highlightable=False)
        
        # Menu options
        y_offset = 150  # Adjusted to make space for the title
        for index, mode in enumerate(self.game_modes):
            label = ClickableLabel(mode, None, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.menu_batch)
            self.menu_options_labels.append(label)

    def setup_song_selection(self):
        """
        Sets up the song selection labels.
        """
        self.song_options_labels.clear()  # Clear existing labels if any

        # Pagination vars
        self.songs_per_page = 25
        valid_songs = self.filter_songs_based_on_mode_and_players()
        song_keys = list(valid_songs.keys())
        self.total_pages = (len(song_keys) + self.songs_per_page - 1) // self.songs_per_page

        # Song selection title
        self.song_selection_title = ClickableLabel("Choose your song:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.song_select_batch, highlightable=False)

        # Create song labels for the current page
        start_index = self.current_page * self.songs_per_page
        end_index = min(start_index + self.songs_per_page, len(song_keys))

        for i, song_id in enumerate(song_keys[start_index:end_index], start=1):
            song_info = valid_songs[song_id]
            y_position = self.height - 100 - 30 * i
            label = ClickableLabel(f"{song_info['name']} - {song_info['artist']}", song_id, 18, self.width // 2, y_position, 'center', 'center', self.song_select_batch)
            self.song_options_labels.append(label)

        # Pagination buttons
        self.prev_page_button = ClickableLabel("Previous", None, 18, self.width // 2 - 200, 50, 'center', 'center', self.song_select_batch)
        self.next_page_button = ClickableLabel("Next", None, 18, self.width // 2 + 200, 50, 'center', 'center', self.song_select_batch)
        if self.current_page > 0:
            self.song_options_labels.append(self.prev_page_button)
        if self.current_page < self.total_pages - 1:
            self.song_options_labels.append(self.next_page_button)

        # Return to menu button
        self.home_button = ClickableLabel("Back", None, 24, self.width // 2, 30, 'center', 'center', self.song_select_batch)
        self.song_options_labels.append(self.home_button)
        
            
    def setup_jukebox_song_selection(self, current_page=0):
        """
        Sets up the jukebox song selection labels with pagination.

        Parameters
        ----------
        current_page : int, optional
            The current page of the song selection (default is 0).
        """
        # Song selection title
        self.song_selection_title_jukebox = ClickableLabel("Choose your song:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.song_select_batch_jukebox, highlightable=False)

        # Pagination vars
        self.current_page_jukebox = current_page
        self.songs_per_page = 20
        self.total_pages_jukebox = (len(jukebox_song_database) + self.songs_per_page - 1) // self.songs_per_page

        # Create song labels for the current page
        self.song_options_labels_jukebox = []
        for song_id in range(current_page * self.songs_per_page + 1, (current_page + 1) * self.songs_per_page + 1):
            song_info = jukebox_song_database.get(song_id, {})
            label = ClickableLabel(f"{song_info.get('name', '')} - {song_info.get('artist', '')}", None, 18, self.width // 2, self.height - (song_id - current_page * self.songs_per_page) * 30 - 100, 'center', 'center', self.song_select_batch_jukebox)
            self.song_options_labels_jukebox.append(label)

        # Pagination buttons
        self.prev_page_button_jukebox = ClickableLabel("Previous", None, 18, self.width // 2 - 200, 50, 'center', 'center', self.song_select_batch_jukebox)
        self.next_page_button_jukebox = ClickableLabel("Next", None, 18, self.width // 2 + 200, 50, 'center', 'center', self.song_select_batch_jukebox)
        if self.current_page_jukebox > 0:
            self.song_options_labels_jukebox.append(self.prev_page_button_jukebox)
        if self.current_page_jukebox < self.total_pages_jukebox - 1:
            self.song_options_labels_jukebox.append(self.next_page_button_jukebox)

        # Return to menu button
        self.home_button_jukebox = ClickableLabel("Return to Menu", None, 24, self.width // 2, 30, 'center', 'center', self.song_select_batch_jukebox)
        self.song_options_labels_jukebox.append(self.home_button_jukebox)

    def setup_settings(self):
        """
        Sets up the settings menu labels.
        """
        
        #Clear batch
        self.settings_batch = pyglet.graphics.Batch()
        
        
        y_offset = 120  # Adjust for where settings options start
        all_out_ports = mido.get_output_names()
        all_in_ports = mido.get_input_names()
        
        # Settings title
        self.settings_title = ClickableLabel("Settings", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.settings_batch, highlightable=False)

        # Output MIDI Ports
        y_position = self.height - y_offset
        self.settings_options_labels.append(ClickableLabel("Select your MIDI Output Port:", None, 24, self.width // 2, y_position, 'center', 'center', self.settings_batch, highlightable=False))
        y_position -= 30
        if all_out_ports:
            for port in all_out_ports:
                color = (0, 130, 255, 255) if port == self.outport else (255, 255, 255, 255)
                label = ClickableLabel(port, None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ClickableLabel("None", None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))

        # Input MIDI Ports
        y_position -= 40  # Extra spacing before listing input ports
        self.settings_options_labels.append(ClickableLabel("Select your MIDI Input Port:", None, 24, self.width // 2, y_position, 'center', 'center', self.settings_batch, highlightable=False))
        y_position -= 30
        if all_in_ports:
            for port in all_in_ports:
                color = (0, 130, 255, 255) if port == self.inport else (255, 255, 255, 255)
                label = ClickableLabel(port, None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=color)
                self.settings_options_labels.append(label)
                y_position -= 30
        else:
            self.settings_options_labels.append(ClickableLabel("None", None, 18, self.width // 2, y_position, 'center', 'center', self.settings_batch, color=(255, 0, 0, 255)))
        
        
        # Autoplay and Controller Size options on the same horizontal level
        y_position -= 60  # Adjust y_position accordingly for next set of options

        # Autoplay option
        self.settings_options_labels.append(ClickableLabel("Autoplay:", None, 24, self.width // 2 - 150, y_position, 'center', 'center', self.settings_batch, highlightable=False))
        y_position -= 30
        true_color = (0, 255, 0, 255) if self.autoplay else (255, 255, 255, 255)
        self.true_label = ClickableLabel("True", None, 18, self.width // 2 - 200, y_position, 'center', 'center', self.settings_batch, color=true_color)
        self.settings_options_labels.append(self.true_label)
        false_color = (255, 0, 0, 255) if not self.autoplay else (255, 255, 255, 255)
        self.false_label = ClickableLabel("False", None, 18, self.width // 2 - 100, y_position, 'center', 'center', self.settings_batch, color=false_color)
        self.settings_options_labels.append(self.false_label)

        # Controller Size option
        self.settings_options_labels.append(ClickableLabel("Controller Size:", None, 24, self.width // 2 + 150, y_position + 30, 'center', 'center', self.settings_batch, highlightable=False))
        size_88_color = (255, 255, 255, 255) if self.controller_size == '49 key' else (0, 255, 0, 255)
        self.size_88_label = ClickableLabel("88 key", None, 18, self.width // 2 + 100, y_position, 'center', 'center', self.settings_batch, color=size_88_color)
        self.settings_options_labels.append(self.size_88_label)
        size_49_color = (0, 255, 0, 255) if self.controller_size == '49 key' else (255, 255, 255, 255)
        self.size_49_label = ClickableLabel("49 key", None, 18, self.width // 2 + 200, y_position, 'center', 'center', self.settings_batch, color=size_49_color)
        self.settings_options_labels.append(self.size_49_label)

        
        #Return to menu button
        self.home_button = ClickableLabel("Return to Menu", None, 24, self.width // 2, 50, 'center', 'center', self.settings_batch)
        self.settings_options_labels.append(self.home_button)
           
    def setup_player_mode_selection(self):
        """
        Sets up the player mode selection labels.
        """
        
        choose_players_title = ClickableLabel("Select number of players:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.player_mode_batch, highlightable=False)
        self.player_mode_options_labels.append(choose_players_title)
        
        modes = ['1 Player', '2 Player']
        y_offset = 125
        for index, mode in enumerate(modes):
            label = ClickableLabel(mode, None, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.player_mode_batch)
            self.player_mode_options_labels.append(label)
            
        return_to_menu = ClickableLabel("Back", None, 24, self.width // 2, self.height - 2.5 * 50 - y_offset, 'center', 'center', self.player_mode_batch)
        self.player_mode_options_labels.append(return_to_menu)
    
    def setup_difficulty_selection(self):
        """
        Sets up the difficulty selection labels.
        """
        choose_difficulty = ClickableLabel("Select your difficulty:", None, 32, self.width // 2, self.height - 50, 'center', 'center', self.difficulty_batch, highlightable=False)
        self.difficulty_options_labels.append(choose_difficulty)
        
        difficulties = ['Easy', 'Challenge', 'Impossible']
        y_offset = 125
        
        for index, difficulty in enumerate(difficulties):
            label = ClickableLabel(difficulty, None, 24, self.width // 2, self.height - index * 50 - y_offset, 'center', 'center', self.difficulty_batch)
            self.difficulty_options_labels.append(label)
            
        return_to_menu = ClickableLabel("Back", None, 24, self.width // 2,  self.height - 3.5 * 50 - y_offset, 'center', 'center', self.difficulty_batch)
        self.difficulty_options_labels.append(return_to_menu)
        
    def filter_songs_based_on_mode_and_players(self):
        """
        Filters the song database based on the selected game mode and number of players.

        Returns
        -------
        dict
            A dictionary of valid songs based on the selected game mode and number of players.
        """
        filtered_songs = {}
        
        if self.selected_game_mode == 'Practice':
            # Filter for 'Easy' songs for Practice mode regardless of player count
            for song_id, song_info in song_database.items():
                if song_info['difficulty'] == 'Easy':
                    filtered_songs[song_id] = song_info
                    
        elif self.selected_game_mode == 'Challenge':
            # In Challenge Mode, filter songs based on the number of players
            for song_id, song_info in song_database.items():
                if song_info['difficulty'] == self.selected_difficulty:
                    if self.player_count == 1:
                        filtered_songs[song_id] = song_info
                    elif self.player_count == 2 and song_info['players'] == 2:
                        filtered_songs[song_id] = song_info
                    
        elif self.selected_game_mode in ['FreePlay', 'JukeBox']:
            # For FreePlay or JukeBox, show all songs
            filtered_songs = song_database
            
            
        return filtered_songs


    def get_song_id_from_label(self, label):
        """
        Retrieves the song ID from the given label.

        Parameters
        ----------
        label : ClickableLabel
            The label from which to retrieve the song ID.

        Returns
        -------
        int
            The ID of the song associated with the label.
        """
        return label.song_id


    def on_draw(self):
        """
        Handles the drawing of the game window based on the current game state.
        """

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
            
        if self.game_state == 'DIFFICULTY_SELECTION':
            self.clear()
            self.difficulty_batch.draw()

            
        elif self.game_state == 'GAME':
            # print("Game is running")
            # May need to edit this when adding more functionality in future...
            pass


    def on_mouse_press(self, x, y, button, modifiers):
        """
        Handles mouse press events based on the current game state.

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
                        
                        self.start_game(None, 'FreePlay', self.inport, self.outport, self.controller_size)
                        
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
                        self.game_state = 'DIFFICULTY_SELECTION'
                        return
                    elif clicked_text == '2 Player':
                        self.player_count = 2
                        self.selected_game_mode = 'Challenge'
                        self.game_state = 'DIFFICULTY_SELECTION'
                        return
                    elif clicked_text == 'Back':
                        self.return_to_menu()
                        return
                    
        elif self.game_state == 'DIFFICULTY_SELECTION':
            for label in self.difficulty_options_labels:
                if label.is_clicked(x, y):
                    if label.label.text == 'Back':
                        self.game_state = 'PLAYER_MODE_SELECTION'
                        return

                    else:
                        self.selected_difficulty = label.label.text
                        self.setup_song_selection()  # Proceed to song selection after choosing difficulty
                        self.game_state = 'SONG_SELECTION'
                        return
                
             
                
        elif self.game_state == 'SONG_SELECTION':
            for label in self.song_options_labels:
                if label.is_clicked(x, y):
                    if label.label.text == "Back":
                        if self.selected_game_mode == 'Practice':
                            self.current_page = 0
                            self.return_to_menu()
                        else:
                            self.current_page = 0
                            self.game_state = 'DIFFICULTY_SELECTION'
                        return
                    elif label == self.prev_page_button:
                        if self.current_page > 0:
                            self.current_page -= 1
                            self.setup_song_selection()
                        return
                    elif label == self.next_page_button:
                        if self.current_page < self.total_pages - 1:
                            self.current_page += 1
                            self.setup_song_selection()
                        return
                    else:
                        song_id = self.get_song_id_from_label(label)
                        song_info = song_database.get(song_id, None)
                        if song_info:
                            print(f"You clicked {song_info['name']} by {song_info['artist']}")
                            self.start_game(song_info['file'], self.selected_game_mode, self.inport, self.outport, self.controller_size, self.player_count, self.autoplay)
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
                        self.handle_prev_page_jukebox()
                        return
                    elif label.label.text == "Next":
                        print("Next page")
                        self.handle_next_page_jukebox()
                        return
                    else:
                        print(f"You clicked {jukebox_song_database[song_id + (self.current_page_jukebox*self.songs_per_page)]['name']} by {jukebox_song_database[song_id + (self.current_page_jukebox*self.songs_per_page)]['artist']}")
                        self.start_game(jukebox_song_database[song_id+ (self.current_page_jukebox*self.songs_per_page)]['file'], self.selected_game_mode, self.inport, self.outport, '88 key', self.player_count, self.autoplay)
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
            
                # Controller Size handling
            elif self.size_88_label.is_clicked(x, y):
                self.controller_size = '88 key'
                self.setup_settings()  # Refresh settings to update highlighted selection
                return
            
            elif self.size_49_label.is_clicked(x, y):
                self.controller_size = '49 key'
                self.setup_settings()  # Refresh settings to update highlighted selection
                return
                
                
    def on_mouse_motion(self, x, y, dx, dy):
        """
        Handles mouse motion events to update label highlights based on the current game state.

        Parameters
        ----------
        x : int
            The x-coordinate of the mouse.
        y : int
            The y-coordinate of the mouse.
        dx : int
            The change in the x-coordinate of the mouse.
        dy : int
            The change in the y-coordinate of the mouse.
        """
        
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
        
        if self.game_state == 'DIFFICULTY_SELECTION':
            for label in self.difficulty_options_labels:
                label.update_highlight(x, y)

                                 
    def start_game(self, midi_file, game_mode, inport, outport, controller_size = '88 key', player_count=1, autoplay=False):
        
        """
        Starts the game with the selected settings.

        Parameters
        ----------
        midi_file : str
            The MIDI file to play.
        game_mode : str
            The selected game mode.
        inport : str
            The MIDI input port.
        outport : str
            The MIDI output port.
        controller_size : str, optional
            The size of the controller (default is '88 key').
        player_count : int, optional
            The number of players (default is 1).
        autoplay : bool, optional
            Whether autoplay is enabled (default is False).
        """

        # Initialize and run the game with the selected MIDI file
        #Adjust game state for tracking whats happening
        self.game_state = 'GAME'
        
        #Create the game
        #Pass in the song and selected game mode
        self.game = PianoGameUI(self, midi_file, game_mode, inport, outport, controller_size, player_count, autoplay)
        print("Game is running")

    def return_to_menu(self):
        """
        Returns to the main menu.
        """
        # Logic to return to the main menu
        self.current_page = 0
        self.current_page_jukebox = 0
        self.game = None
        self.player_count = 1
        self.game_state = 'MENU'
        pass

    def handle_prev_page_jukebox(self):
        if self.current_page_jukebox > 0:
            self.current_page_jukebox -= 1
            self.setup_jukebox_song_selection(self.current_page_jukebox)

    def handle_next_page_jukebox(self):
        if self.current_page_jukebox < self.total_pages_jukebox - 1:
            self.current_page_jukebox += 1
            self.setup_jukebox_song_selection(self.current_page_jukebox)
            pass

if __name__ == "__main__":
    
    """
    Main entry point for the Walking Piano Game.

    Initializes the game and sets up the signal handler for graceful termination.
    """

    # Added for easily terminating the program with CTRL+C...
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
