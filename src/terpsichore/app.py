"""
BeeWare the Python Music Player.
"""
import toga
from toga.style import Pack
from toga.style.pack import CENTER, LEFT, RIGHT, COLUMN, ROW, Pack
from toga.fonts import SANS_SERIF
import pygame
import os
import threading
import time
import eyed3
import bs4
import requests
import re

class Terpsichore(toga.App): 

    def startup(self):
        """
        Construct and show the Toga application.
        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        self.main_window = toga.MainWindow(title=self.formal_name,
            size=(400,500))
        # could create an object that all others take as arguments,
        # to allow objects to communicate with each other
        self.donk = Donk(self.main_window)
        self.music = Music(self.main_window)
        self.bands = Webscraper(self.main_window)

        # Title button, for the "about" really.
        title_button = toga.Button(
            'TERPSICHORE',
            on_press=self.about,
            style=Pack(
                font_size=30,
                flex=1,
                )
            )

        # Main box of boxes
        main_box = toga.Box(
            children=[title_button, self.donk.nothing_box,
                self.music.music_box, self.bands.band_box],
            style=Pack(direction=COLUMN, alignment=CENTER, padding=5)
            )

        # Show the main window

        self.main_window.content = main_box
        self.main_window.show()
    
    def about(self, widget):
        self.main_window.info_dialog(
            "Terpischore",
            "Music time! Or whatever!"
            )

class Donk():

    """
    Class for the most pointless part of the app. Pointless, yet it stays.
    """
        
    def __init__(self, main_window): # note: to alter another class, add
        # the object as a parameter
        # This is just the test box items, doesn't do a lot.
        self.main_window = main_window
        self.nothing_label = toga.Label(
            'See what happens:',
            style=Pack(padding=(0, 5))
            )
        self.nothing_input = toga.TextInput(
            initial="Donk.",
            style=Pack(flex=1)
            )
        self.nothing_button = toga.Button(
            'Click me now.',
            on_press=self.say_nothing,
            style=Pack(padding=(0, 5))
            )

        # Nothing box with relevant items
        self.nothing_box = toga.Box(
            children=[
                self.nothing_label,
                self.nothing_input,
                self.nothing_button
                ],
            style=Pack(direction=ROW, alignment=CENTER, padding_top=5)
            )

    def say_nothing(self, widget):
        self.main_window.info_dialog(
            "Okay...",
            "I am a parrot: {}".format(self.nothing_input.value)
            )

class Music:

    """
    Class for the music player.
    """

    def __init__(self, main_window):

        pygame.init()

        self.main_window = main_window
        self.progress_bar = toga.ProgressBar(max=100, value=0,
            style=Pack(padding_top=5))
        # Create a thread for the music
        time_thread = threading.Thread(target=self.prog_check)
        time_thread.start()
        # Set useful variables
        self.is_loaded = False
        self.is_paused = False
        # This adjusts the position as necessary for fforwards and rewinds
        self.time_adjuster = 0
        # Volume tracker
        self.volume = 100

        # Music player buttons
        self.play_pause_button = toga.Button(
            '>/II',
            on_press=self.play_pause,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.rewind_button = toga.Button(
            '<<',
            on_press=self.rewind,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.ultra_rewind_button = toga.Button(
            '<<<',
            on_press=self.ultra_rewind,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.fforward_button = toga.Button(
            '>>',
            on_press=self.fforward,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.ultra_fforward_button = toga.Button(
            '>>>',
            on_press=self.ultra_fforward,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.stop_button = toga.Button(
            'Stop',
            on_press=self.stop_music,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        self.load_button = toga.Button(
            'Load',
            on_press=self.load_music,
            style=Pack(padding=(0,5), height=45, width=45)
        )

        # Music player box
        self.music_btn_box = toga.Box(
            children=[
                self.load_button,
                self.ultra_rewind_button,
                self.rewind_button,
                self.play_pause_button,
                self.fforward_button,
                self.ultra_fforward_button,
                self.stop_button,
                ],
            style=Pack(direction=ROW, alignment=CENTER)
        )

        self.lbl_playing = toga.Label("Currently Playing: ", style=Pack(
            text_align=CENTER,
            padding_top=5,
            flex=1))

        self.lbl_volume = toga.Label("Volume: " + str(self.volume), style=Pack(
            text_align=CENTER))

        self.btn_vol_up = toga.Button(
            '+',
            on_press=self.volume_up,
            style=Pack(padding=(0,5), height=30, width=30)
        )

        self.btn_vol_down = toga.Button(
            '-',
            on_press=self.volume_down,
            style=Pack(padding=(0,5), height=30, width=30)
        )

        self.volume_box = toga.Box(
            children=[
                self.btn_vol_down,
                self.lbl_volume,
                self.btn_vol_up],
            style=Pack(direction=ROW, alignment=CENTER, padding_top=5)
        )

        self.music_box = toga.Box(
            children=[
                self.music_btn_box,
                self.volume_box,
                self.progress_bar,
                self.lbl_playing
                ],
            style=Pack(direction=COLUMN, alignment=CENTER, padding_top=5)
        )

    def play_pause(self, *widget):
        """Play/Pause toggle."""
        if not pygame.mixer.music.get_busy() and self.is_loaded == True:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.play(loops=0)
                self.is_paused = False
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
    
    def rewind(self, widget):
        """Rewind time a bit by altering the time offset."""
        current_position = pygame.mixer.music.get_pos() // 1000
        self.time_adjuster -= 5
        if (current_position + self.time_adjuster) < 0.1:
            self.stop_music()
            self.play_pause()
        else:
            pygame.mixer.music.set_pos(current_position + self.time_adjuster)

    def ultra_rewind(self, widget):
        """Rewind time a lot by altering the time offset."""
        current_position = pygame.mixer.music.get_pos() // 1000
        self.time_adjuster -= 10
        if (current_position + self.time_adjuster) < 0.1:
            self.stop_music()
            self.play_pause()
        else:
            pygame.mixer.music.set_pos(current_position + self.time_adjuster)

    def fforward(self, widget):
        """Fastforward time a bit by altering the time offset."""
        current_position = pygame.mixer.music.get_pos() / 1000
        self.time_adjuster += 50
        if (current_position + self.time_adjuster + 1) > self.progress_bar.max:
            self.stop_music()
        else:
            pygame.mixer.music.set_pos(current_position + self.time_adjuster)

    def ultra_fforward(self, widget):
        """Fastforward time a lot by altering the time offset."""
        current_position = pygame.mixer.music.get_pos() / 1000
        self.time_adjuster += 100
        if (current_position + self.time_adjuster + 1) > self.progress_bar.max:
            self.stop_music()
        else:
            pygame.mixer.music.set_pos(current_position + self.time_adjuster)

    def stop_music(self, *widget):
        """Stops music."""
        pygame.mixer.music.stop()
        # Change this to false, as stopped and paused are treated differently.
        self.is_paused = False
        self.time_adjuster = 0
        self.progress_bar.value = 0

    def load_music(self, widget):
        """Open a dialog to let you choose a song to load."""
        try:
            self.current_song = self.main_window.open_file_dialog("Load Song")
        except Exception:
            self.main_window.info_dialog("Oops!", "Music, please!")
        else:
            self.is_loaded = True
            self.is_paused = False
            self.stop_music()
            pygame.mixer.music.load(self.current_song)
            self._music_tags(self.current_song)
            self.lbl_playing.text = f'Currently Playing: \
{self.song_title} by {self.song_artist}'
            pygame.mixer.music.set_volume(self.volume)
            return self._sound_length()

    def _music_tags(self, song):
        """Get the metadata from a song."""
        self.audio = eyed3.load(song)
        self.song_title = str(self.audio.tag.title)
        self.song_artist = str(self.audio.tag.artist)
        if self.song_artist == "None":
            self.song_artist = "Unknown"

    def _sound_length(self):   
        """Get length in seconds of current song."""
        self.song_as_sound = pygame.mixer.Sound(self.current_song)
        self.progress_bar.max = self.song_as_sound.get_length()   

    def prog_check(self):
        """Check progress of song concurrently, and update."""
        while True:
            time.sleep(0.1)
            try:
                self.progress_bar.value = ((pygame.mixer.music.get_pos() / 1000)
                    + self.time_adjuster)
            except:
                None
            if self.progress_bar.value > self.progress_bar.max - 0.2:
                    self.progress_bar.value = 0

    def volume_down(self, widget):
        """Decreases the music volume."""
        if self.volume > 0:
            self.volume -= 10
            pygame.mixer.music.set_volume(self.volume / 100)
            self.lbl_volume.text = f'Volume: {self.volume}'

    def volume_up(self, widget):
        """Increases the music volume."""
        if self.volume < 100:
            self.volume += 10
            pygame.mixer.music.set_volume(self.volume / 100)
            self.lbl_volume.text = f'Volume: {self.volume}'

class Webscraper:

    """
    Class to find the latest bands.
    Will use https://gigradar.co.uk/category/new-band-of-the-week/.
    """

    def __init__(self, main_window):
        # TODO: Webscraping popular music websites for latest bands
        self.url = "https://gigradar.co.uk/category/new-band-of-the-week/"
        self.band_string = "New Bands:\n"

        self.lbl_bands = toga.Label(self.band_string +
                '\n\n\n\n\n\n\n\n\n\n\n\n',
                style=Pack(
                font_size=10,
                text_align=CENTER,
                flex=1,
                ))
        
        self.get_band_elem()

        self.band_box = toga.Box(
            children=[
                self.lbl_bands,
                ],
            style=Pack(direction=COLUMN, alignment=CENTER, padding_top=15)
            )

    def get_band_elem(self, *widget):
        """Gets the band elements from 
        "https://gigradar.co.uk/category/new-band-of-the-week/"
        using Beautiful Soup and then puts them in the correct format
        to be displayed in the program.
        """
        res = requests.get(self.url)
        res.raise_for_status
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        band_elem = soup.find_all('h2', {"class": "entry-title"})
        for i in band_elem:
            band_extraction = re.split(r'<|>', str(i.contents[0]))
            band_reformat = band_extraction[2].replace("&amp;","and")
            band_reformat = band_reformat.replace(
                "New Band of the Week: ",
                ""
                )
            self.band_string += band_reformat + "\n"
        print(self.band_string)
        self.lbl_bands.text = self.band_string

def main():
    return Terpsichore('Terpsichore', 'org.beeware.graze')

if __name__ == '__main__':
    main().main_loop()