from collections import OrderedDict 
from lark.lexer import Token

# Dossiers

dossiers = []
dossier_next_sheet = None
dossier_previous_sheet = None

dossier_next_suspect = None
dossier_previous_suspect = None

dossier_current_sheet = None
dossier_current_suspect = None

# Savegames

load_game = None
save_game = None

# Masks

exits = []
inventory = []
masks = []
sareas = []

# Sounds

sounds = dict()
police_radio_path =  "inface/radio/police/"
am_radio_path =  "inface/radio/comm_/"
phone_path =  "inface/telephon/"
phone_sound = "phone.wav" 
played_sounds = []

# Movies

video_to_play = None
played_movies = []
movie_repeated_exit = None

# Settings

modified = False
mode = 0
definitions = OrderedDict()
next_setting = None
current_setting = None
gorigin = None
settings = OrderedDict()
save_path = None
save_name = "re-private-eye-game.json" 

# Media

height = None
width = None
cdrom_path = None 
screen = None
font = None
current_view_frame = None
game_frame = "inface/general/inface2.bmp"
cursors = None
